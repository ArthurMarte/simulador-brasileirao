"""Simulação é aleatória: fixamos a seed para determinismo e testamos propriedades."""

import pytest

from apps.campeonato.services.forcas import Forca
from apps.campeonato.services.simulacao import classificar, lambdas_da_partida, simular

TIMES = ["a", "b", "c", "d"]
JOGOS = [("a", "b"), ("c", "d"), ("b", "c"), ("d", "a")]
ZERADO = dict.fromkeys(TIMES, 0)


def _simular(**kwargs):
    base = dict(
        times=TIMES,
        pontos_atuais=ZERADO,
        saldo_atual=ZERADO,
        jogos_restantes=JOGOS,
        media_liga=1.3,
        n=300,
        seed=42,
    )
    base.update(kwargs)
    return simular(**base)


def test_mesma_seed_produz_mesmo_resultado(forcas_neutras):
    primeiro = _simular(forcas=forcas_neutras)
    segundo = _simular(forcas=forcas_neutras)

    assert primeiro == segundo


def test_seeds_diferentes_produzem_resultados_diferentes(forcas_neutras):
    primeiro = _simular(forcas=forcas_neutras, seed=1)
    segundo = _simular(forcas=forcas_neutras, seed=2)

    assert primeiro != segundo


def test_probabilidade_de_titulo_soma_cem(forcas_neutras):
    resultado = _simular(forcas=forcas_neutras)

    total = sum(dados["titulo"] for dados in resultado.values())
    assert total == pytest.approx(100, abs=0.5)


def test_probabilidades_estao_no_intervalo_valido(forcas_neutras):
    resultado = _simular(forcas=forcas_neutras)

    for dados in resultado.values():
        assert 0 <= dados["titulo"] <= 100
        assert 1 <= dados["posicao_media"] <= len(TIMES)


def test_lider_isolado_tem_mais_chance_que_lanterna(forcas_neutras):
    pontos = {"a": 30, "b": 0, "c": 0, "d": 0}

    resultado = _simular(forcas=forcas_neutras, pontos_atuais=pontos)

    assert resultado["a"]["titulo"] > resultado["b"]["titulo"]


def test_time_muito_superior_domina(forcas_neutras):
    forcas = {**forcas_neutras, "a": Forca(ataque=3.0, defesa=0.3, jogos=10)}

    resultado = _simular(forcas=forcas)

    assert resultado["a"]["titulo"] > resultado["b"]["titulo"]


def test_fator_mandante_favorece_a_casa():
    forca = Forca(ataque=1.0, defesa=1.0, jogos=10)

    lam_casa, lam_fora = lambdas_da_partida(forca, forca, media_liga=1.3, fator_mandante=1.25)

    assert lam_casa > lam_fora


def test_lambda_nunca_e_zero():
    fraco = Forca(ataque=0.0, defesa=0.0, jogos=10)

    lam_casa, lam_fora = lambdas_da_partida(fraco, fraco, media_liga=0.0, fator_mandante=1.25)

    assert lam_casa > 0
    assert lam_fora > 0


def test_classificar_desempata_por_saldo():
    pontos = {"a": 10, "b": 10}
    saldo = {"a": 1, "b": 5}

    assert classificar(pontos, saldo) == ["b", "a"]
