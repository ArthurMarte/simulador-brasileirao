"""Estima força de ataque e defesa de cada time a partir dos jogos disputados.

Modelo: para cada time, ataque = gols marcados por jogo / média da liga;
defesa = gols sofridos por jogo / média da liga. Valores acima de 1 indicam
ataque melhor (ou defesa pior) que a média.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Forca:
    ataque: float
    defesa: float
    jogos: int


def calcular_forcas(partidas: list[dict]) -> tuple[dict[str, Forca], float]:
    """Recebe partidas encerradas e devolve as forças e a média de gols da liga.

    Cada partida é um dict com: mandante, visitante, gols_mandante, gols_visitante.
    """
    marcados: dict[str, int] = {}
    sofridos: dict[str, int] = {}
    jogos: dict[str, int] = {}
    total_gols = 0

    for p in partidas:
        casa, fora = p["mandante"], p["visitante"]
        gc, gf = p["gols_mandante"], p["gols_visitante"]

        for time in (casa, fora):
            marcados.setdefault(time, 0)
            sofridos.setdefault(time, 0)
            jogos.setdefault(time, 0)

        marcados[casa] += gc
        sofridos[casa] += gf
        marcados[fora] += gf
        sofridos[fora] += gc
        jogos[casa] += 1
        jogos[fora] += 1
        total_gols += gc + gf

    if not partidas:
        return {}, 0.0

    media_liga = total_gols / (len(partidas) * 2)
    if media_liga == 0:
        return {t: Forca(1.0, 1.0, jogos[t]) for t in jogos}, 0.0

    forcas = {
        time: Forca(
            ataque=(marcados[time] / jogos[time]) / media_liga,
            defesa=(sofridos[time] / jogos[time]) / media_liga,
            jogos=jogos[time],
        )
        for time in jogos
    }
    return forcas, media_liga
