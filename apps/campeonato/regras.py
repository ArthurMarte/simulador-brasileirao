"""Regras do Campeonato Brasileiro Série A.

Isoladas aqui para que mudanças de formato não espalhem pelo código.
"""

TOTAL_TIMES = 20
TOTAL_RODADAS = 38

# Faixas de classificação por posição final (1-indexado)
FAIXAS = {
    "titulo": (1, 1),
    "libertadores": (1, 6),
    "pre_libertadores": (7, 8),
    "sul_americana": (9, 14),
    "rebaixamento": (17, 20),
}

PONTOS_VITORIA = 3
PONTOS_EMPATE = 1
