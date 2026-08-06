from apps.campeonato.services.forcas import calcular_forcas


def _partida(casa, fora, gc, gf):
    return {"mandante": casa, "visitante": fora, "gols_mandante": gc, "gols_visitante": gf}


def test_sem_partidas_retorna_vazio():
    forcas, media = calcular_forcas([])
    assert forcas == {}
    assert media == 0.0


def test_times_identicos_tem_forca_um():
    partidas = [_partida("a", "b", 1, 1), _partida("b", "a", 1, 1)]

    forcas, media = calcular_forcas(partidas)

    assert media == 1.0
    assert forcas["a"].ataque == 1.0
    assert forcas["a"].defesa == 1.0


def test_ataque_forte_gera_indice_maior_que_um():
    partidas = [_partida("a", "b", 4, 0), _partida("b", "a", 0, 2)]

    forcas, _ = calcular_forcas(partidas)

    assert forcas["a"].ataque > 1.0
    assert forcas["b"].ataque < 1.0
    assert forcas["a"].defesa < forcas["b"].defesa


def test_jogo_sem_gols_nao_quebra():
    forcas, media = calcular_forcas([_partida("a", "b", 0, 0)])

    assert media == 0.0
    assert forcas["a"].ataque == 1.0
