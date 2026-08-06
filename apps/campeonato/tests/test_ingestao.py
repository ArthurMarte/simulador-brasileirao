import json
from pathlib import Path

import pytest
import responses
from django.conf import settings

from apps.campeonato.models import Partida, Time
from apps.campeonato.services.ingestao import (
    CotaExcedida,
    IngestaoError,
    sincronizar_partidas,
)

URL = (
    f"{settings.FOOTBALL_DATA_BASE_URL}"
    f"/competitions/{settings.FOOTBALL_DATA_COMPETICAO}/matches"
)


@pytest.fixture
def matches_api() -> dict:
    caminho = Path(__file__).parent / "fixtures" / "matches_football_data.json"
    return json.loads(caminho.read_text())


@pytest.mark.django_db
@responses.activate
def test_sincronizar_cria_times_e_partidas(matches_api):
    responses.add(responses.GET, URL, json=matches_api, status=200)

    total = sincronizar_partidas()

    assert total == 3
    assert Time.objects.count() == 4
    assert Partida.objects.filter(encerrada=True).count() == 2
    assert Partida.objects.filter(encerrada=False).count() == 1


@pytest.mark.django_db
@responses.activate
def test_usa_short_name_e_tla(matches_api):
    responses.add(responses.GET, URL, json=matches_api, status=200)

    sincronizar_partidas()

    palmeiras = Time.objects.get(id_externo=1776)
    assert palmeiras.nome == "Palmeiras"
    assert palmeiras.sigla == "PAL"
    assert palmeiras.slug == "palmeiras"


@pytest.mark.django_db
@responses.activate
def test_partida_futura_nao_grava_placar(matches_api):
    responses.add(responses.GET, URL, json=matches_api, status=200)

    sincronizar_partidas()

    futura = Partida.objects.get(id_externo=500003)
    assert futura.gols_mandante is None
    assert futura.rodada == 2


@pytest.mark.django_db
@responses.activate
def test_sincronizar_e_idempotente(matches_api):
    responses.add(responses.GET, URL, json=matches_api, status=200)
    responses.add(responses.GET, URL, json=matches_api, status=200)

    sincronizar_partidas()
    sincronizar_partidas()

    assert Partida.objects.count() == 3
    assert Time.objects.count() == 4


@pytest.mark.django_db
@responses.activate
def test_limite_por_minuto_vira_cota_excedida():
    responses.add(
        responses.GET, URL, status=429, headers={"X-RequestCounter-Reset": "37"}
    )

    with pytest.raises(CotaExcedida, match="37"):
        sincronizar_partidas()


@pytest.mark.django_db
@responses.activate
def test_recurso_fora_do_plano_vira_ingestao_error():
    responses.add(responses.GET, URL, status=403)

    with pytest.raises(IngestaoError, match="plano"):
        sincronizar_partidas()
