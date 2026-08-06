from celery import shared_task
from django.conf import settings
from django.core.cache import cache

from apps.campeonato.models import Partida, Simulacao
from apps.campeonato.services.forcas import calcular_forcas
from apps.campeonato.services.ingestao import sincronizar_partidas
from apps.campeonato.services.simulacao import simular
from apps.campeonato.services.tabela import estado_atual, jogos_restantes

CACHE_KEY_PROBABILIDADES = "probabilidades:atual"


@shared_task
def atualizar_e_simular(n: int | None = None, seed: int | None = None) -> dict:
    """Roda diariamente: importa resultados novos e recalcula as probabilidades."""
    sincronizar_partidas()
    return rodar_simulacao(n=n, seed=seed)


def rodar_simulacao(n: int | None = None, seed: int | None = None) -> dict:
    n = n or settings.SIMULACOES_PADRAO
    pontos, saldo, encerradas = estado_atual()
    restantes = jogos_restantes()

    if not encerradas:
        raise ValueError("Nenhuma partida encerrada — impossível estimar as forças.")

    forcas, media_liga = calcular_forcas(encerradas)
    times = sorted(pontos)

    resultado = simular(
        times=times,
        pontos_atuais=pontos,
        saldo_atual=saldo,
        jogos_restantes=restantes,
        forcas=forcas,
        media_liga=media_liga,
        fator_mandante=settings.FATOR_MANDANTE,
        n=n,
        seed=seed,
    )

    rodadas = (
        Partida.objects.filter(encerrada=True).order_by("-rodada").values_list("rodada", flat=True)
    )
    Simulacao.objects.create(
        rodadas_disputadas=rodadas[0] if rodadas else 0,
        n_simulacoes=n,
        seed=seed,
        resultado=resultado,
    )
    cache.delete(CACHE_KEY_PROBABILIDADES)
    return resultado
