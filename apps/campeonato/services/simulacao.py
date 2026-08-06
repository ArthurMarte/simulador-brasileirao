"""Simulação de Monte Carlo do restante do campeonato.

Para cada jogo que falta, sorteia um placar a partir de duas distribuições de
Poisson (uma por time). Repete a temporada N vezes e conta em quantas cada
time terminou em cada posição.
"""

import numpy as np

from apps.campeonato.regras import FAIXAS, PONTOS_EMPATE, PONTOS_VITORIA
from apps.campeonato.services.forcas import Forca


def lambdas_da_partida(
    forca_casa: Forca,
    forca_fora: Forca,
    media_liga: float,
    fator_mandante: float,
) -> tuple[float, float]:
    """Gols esperados de cada lado."""
    lambda_casa = forca_casa.ataque * forca_fora.defesa * media_liga * fator_mandante
    lambda_fora = forca_fora.ataque * forca_casa.defesa * media_liga
    return max(lambda_casa, 0.05), max(lambda_fora, 0.05)


def classificar(pontos: dict[str, int], saldo: dict[str, int]) -> list[str]:
    """Ordena os times por pontos e, no empate, por saldo de gols."""
    return sorted(pontos, key=lambda t: (-pontos[t], -saldo[t], t))


def simular(
    times: list[str],
    pontos_atuais: dict[str, int],
    saldo_atual: dict[str, int],
    jogos_restantes: list[tuple[str, str]],
    forcas: dict[str, Forca],
    media_liga: float,
    fator_mandante: float = 1.25,
    n: int = 10_000,
    seed: int | None = None,
) -> dict[str, dict]:
    """Roda a simulação e devolve, por time, a probabilidade de cada faixa.

    `seed` fixa a aleatoriedade — essencial para tornar os testes determinísticos.
    """
    rng = np.random.default_rng(seed)
    contagem = {time: dict.fromkeys(FAIXAS, 0) for time in times}
    posicoes = {time: [] for time in times}

    # Pré-calcula os lambdas: eles não mudam entre as simulações.
    lambdas = [
        (casa, fora, *lambdas_da_partida(forcas[casa], forcas[fora], media_liga, fator_mandante))
        for casa, fora in jogos_restantes
    ]

    for _ in range(n):
        pontos = dict(pontos_atuais)
        saldo = dict(saldo_atual)

        for casa, fora, lam_casa, lam_fora in lambdas:
            gc = int(rng.poisson(lam_casa))
            gf = int(rng.poisson(lam_fora))

            saldo[casa] += gc - gf
            saldo[fora] += gf - gc

            if gc > gf:
                pontos[casa] += PONTOS_VITORIA
            elif gf > gc:
                pontos[fora] += PONTOS_VITORIA
            else:
                pontos[casa] += PONTOS_EMPATE
                pontos[fora] += PONTOS_EMPATE

        tabela = classificar(pontos, saldo)
        for indice, time in enumerate(tabela, start=1):
            posicoes[time].append(indice)
            for faixa, (inicio, fim) in FAIXAS.items():
                if inicio <= indice <= fim:
                    contagem[time][faixa] += 1

    return {
        time: {
            **{faixa: round(contagem[time][faixa] / n * 100, 2) for faixa in FAIXAS},
            "posicao_media": round(float(np.mean(posicoes[time])), 2),
        }
        for time in times
    }
