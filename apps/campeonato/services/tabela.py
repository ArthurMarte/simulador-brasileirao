"""Monta a tabela atual a partir das partidas encerradas no banco."""

from apps.campeonato.models import Partida
from apps.campeonato.regras import PONTOS_EMPATE, PONTOS_VITORIA


def estado_atual() -> tuple[dict[str, int], dict[str, int], list[dict]]:
    """Devolve (pontos, saldo, partidas_encerradas) indexados por slug do time."""
    pontos: dict[str, int] = {}
    saldo: dict[str, int] = {}
    encerradas: list[dict] = []

    partidas = Partida.objects.filter(encerrada=True).select_related("mandante", "visitante")

    for p in partidas:
        casa, fora = p.mandante.slug, p.visitante.slug
        gc, gf = p.gols_mandante, p.gols_visitante

        for time in (casa, fora):
            pontos.setdefault(time, 0)
            saldo.setdefault(time, 0)

        saldo[casa] += gc - gf
        saldo[fora] += gf - gc

        if gc > gf:
            pontos[casa] += PONTOS_VITORIA
        elif gf > gc:
            pontos[fora] += PONTOS_VITORIA
        else:
            pontos[casa] += PONTOS_EMPATE
            pontos[fora] += PONTOS_EMPATE

        encerradas.append(
            {
                "mandante": casa,
                "visitante": fora,
                "gols_mandante": gc,
                "gols_visitante": gf,
            }
        )

    return pontos, saldo, encerradas


def jogos_restantes() -> list[tuple[str, str]]:
    return [
        (p.mandante.slug, p.visitante.slug)
        for p in Partida.objects.filter(encerrada=False).select_related("mandante", "visitante")
    ]
