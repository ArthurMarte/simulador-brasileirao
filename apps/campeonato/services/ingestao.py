"""Cliente da football-data.org (API v4).

Autenticação: header `X-Auth-Token`.
Base URL: https://api.football-data.org/v4
Competição: BSA = Campeonato Brasileiro Série A.

O plano gratuito é limitado por REQUISIÇÕES POR MINUTO (não por dia), então o
tratamento de HTTP 429 importa mais aqui do que controle de cota diária.
"""

import requests
from django.conf import settings
from django.utils.text import slugify

from apps.campeonato.models import Partida, Time

# A API usa FINISHED para partida concluída. AWARDED = resultado decidido
# por decisão administrativa (W.O.), que também conta como encerrada.
STATUS_ENCERRADOS = {"FINISHED", "AWARDED"}


class IngestaoError(Exception):
    """Falha ao obter dados da API externa."""


class CotaExcedida(IngestaoError):
    """Limite de requisições por minuto atingido."""


def _get(caminho: str, params: dict | None = None) -> dict:
    try:
        resposta = requests.get(
            f"{settings.FOOTBALL_DATA_BASE_URL}{caminho}",
            headers={"X-Auth-Token": settings.FOOTBALL_DATA_TOKEN},
            params=params or {},
            timeout=30,
        )
    except requests.RequestException as exc:
        raise IngestaoError(f"Falha de rede ao consultar a football-data.org: {exc}") from exc

    if resposta.status_code == 429:
        # A API informa quantos segundos faltam para liberar.
        espera = resposta.headers.get("X-RequestCounter-Reset", "?")
        raise CotaExcedida(f"Limite por minuto atingido. Tente de novo em {espera}s.")

    if resposta.status_code == 403:
        raise IngestaoError(
            "Recurso fora do seu plano. Confira se a competição e a temporada "
            "estão incluídas no free tier."
        )

    try:
        resposta.raise_for_status()
    except requests.HTTPError as exc:
        raise IngestaoError(f"A football-data.org respondeu com erro: {exc}") from exc

    return resposta.json()


def sincronizar_partidas(temporada: int | None = None) -> int:
    """Importa/atualiza as partidas do Brasileirão. Devolve quantas foram tocadas.

    Uma única requisição traz o campeonato inteiro. Sem o filtro `season`,
    a API devolve a temporada corrente — o comportamento que queremos no job diário.
    """
    params = {"season": temporada} if temporada else {}
    corpo = _get(f"/competitions/{settings.FOOTBALL_DATA_COMPETICAO}/matches", params)

    total = 0
    for item in corpo.get("matches", []):
        encerrada = item["status"] in STATUS_ENCERRADOS
        placar = item["score"]["fullTime"]

        mandante = _upsert_time(item["homeTeam"])
        visitante = _upsert_time(item["awayTeam"])

        Partida.objects.update_or_create(
            id_externo=item["id"],
            defaults={
                # matchday já vem como inteiro — sem parsing de texto.
                "rodada": item.get("matchday") or 0,
                "mandante": mandante,
                "visitante": visitante,
                "gols_mandante": placar["home"] if encerrada else None,
                "gols_visitante": placar["away"] if encerrada else None,
                "encerrada": encerrada,
                "data": item.get("utcDate"),
            },
        )
        total += 1

    return total


def _upsert_time(dados: dict) -> Time:
    # shortName é mais limpo que name: "Palmeiras" em vez de "SE Palmeiras".
    nome = dados.get("shortName") or dados["name"]
    time, _ = Time.objects.update_or_create(
        id_externo=dados["id"],
        defaults={
            "nome": nome,
            "sigla": (dados.get("tla") or nome[:3]).upper()[:5],
            "slug": slugify(nome),
            "escudo_url": dados.get("crest") or "",
        },
    )
    return time
