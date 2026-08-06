from django.urls import path

from apps.campeonato.views import HealthView, ProbabilidadesView, TimeView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("probabilidades/", ProbabilidadesView.as_view(), name="probabilidades"),
    path("times/<slug:slug>/", TimeView.as_view(), name="time-detalhe"),
]
