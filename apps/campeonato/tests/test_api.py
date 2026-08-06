import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.campeonato.tasks import rodar_simulacao


@pytest.fixture
def client():
    return APIClient()


def test_health(client):
    assert client.get(reverse("health")).status_code == 200


@pytest.mark.django_db
def test_probabilidades_sem_simulacao_retorna_404(client):
    assert client.get(reverse("probabilidades")).status_code == 404


@pytest.mark.django_db
def test_probabilidades_apos_simular(client, campeonato_minimo):
    rodar_simulacao(n=200, seed=7)

    resposta = client.get(reverse("probabilidades"))

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["n_simulacoes"] == 200
    assert "a" in corpo["resultado"]


@pytest.mark.django_db
def test_detalhe_do_time(client, campeonato_minimo):
    rodar_simulacao(n=200, seed=7)

    resposta = client.get(reverse("time-detalhe", args=["a"]))

    assert resposta.status_code == 200
    assert resposta.json()["time"] == "a"


@pytest.mark.django_db
def test_time_inexistente_retorna_404(client, campeonato_minimo):
    rodar_simulacao(n=200, seed=7)

    assert client.get(reverse("time-detalhe", args=["inexistente"])).status_code == 404


@pytest.mark.django_db
def test_simulacao_sem_partidas_encerradas_falha(db):
    with pytest.raises(ValueError):
        rodar_simulacao(n=10, seed=1)
