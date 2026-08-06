from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.campeonato.models import Simulacao
from apps.campeonato.serializers import SimulacaoSerializer
from apps.campeonato.tasks import CACHE_KEY_PROBABILIDADES

CACHE_TTL = 60 * 30


class HealthView(APIView):
    @extend_schema(responses={200: None})
    def get(self, request):
        return Response({"status": "ok"})


class ProbabilidadesView(APIView):
    """Probabilidades de todos os times na simulação mais recente."""

    @extend_schema(responses={200: SimulacaoSerializer})
    def get(self, request):
        if (cacheado := cache.get(CACHE_KEY_PROBABILIDADES)) is not None:
            return Response(cacheado)

        simulacao = Simulacao.objects.order_by("-criada_em").first()
        if simulacao is None:
            return Response(
                {"detail": "Nenhuma simulação disponível ainda."},
                status=status.HTTP_404_NOT_FOUND,
            )

        dados = SimulacaoSerializer(simulacao).data
        cache.set(CACHE_KEY_PROBABILIDADES, dados, CACHE_TTL)
        return Response(dados)


class TimeView(APIView):
    """Recorte da simulação para um único time."""

    @extend_schema(responses={200: None})
    def get(self, request, slug: str):
        simulacao = Simulacao.objects.order_by("-criada_em").first()
        if simulacao is None:
            return Response(
                {"detail": "Nenhuma simulação disponível ainda."},
                status=status.HTTP_404_NOT_FOUND,
            )

        dados = simulacao.resultado.get(slug)
        if dados is None:
            return Response(
                {"detail": f"Time '{slug}' não encontrado na simulação."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "time": slug,
                "rodadas_disputadas": simulacao.rodadas_disputadas,
                "atualizado_em": simulacao.criada_em,
                **dados,
            }
        )
