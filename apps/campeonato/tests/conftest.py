import json
from pathlib import Path

import pytest
from django.core.cache import cache

from apps.campeonato.models import Partida, Time
from apps.campeonato.services.forcas import Forca

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def limpar_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def partidas_api() -> dict:
    return json.loads((FIXTURES / "partidas_api.json").read_text())


@pytest.fixture
def forcas_neutras() -> dict[str, Forca]:
    """Todos os times idênticos — útil para testar propriedades da simulação."""
    return {slug: Forca(ataque=1.0, defesa=1.0, jogos=10) for slug in ("a", "b", "c", "d")}


@pytest.fixture
def campeonato_minimo(db):
    """Quatro times, dois jogos encerrados e dois a disputar."""
    times = {
        slug: Time.objects.create(slug=slug, nome=slug.upper(), sigla=slug.upper(), id_externo=i)
        for i, slug in enumerate(("a", "b", "c", "d"), start=1)
    }
    Partida.objects.create(
        id_externo=1, rodada=1, mandante=times["a"], visitante=times["b"],
        gols_mandante=2, gols_visitante=1, encerrada=True,
    )
    Partida.objects.create(
        id_externo=2, rodada=1, mandante=times["c"], visitante=times["d"],
        gols_mandante=0, gols_visitante=0, encerrada=True,
    )
    Partida.objects.create(
        id_externo=3, rodada=2, mandante=times["b"], visitante=times["c"], encerrada=False,
    )
    Partida.objects.create(
        id_externo=4, rodada=2, mandante=times["d"], visitante=times["a"], encerrada=False,
    )
    return times
