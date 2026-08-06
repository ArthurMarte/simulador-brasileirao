from django.db import models


class Time(models.Model):
    slug = models.SlugField(unique=True)
    nome = models.CharField(max_length=80)
    sigla = models.CharField(max_length=5)
    escudo_url = models.URLField(blank=True)
    id_externo = models.IntegerField(unique=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class Partida(models.Model):
    id_externo = models.IntegerField(unique=True)
    rodada = models.PositiveSmallIntegerField()
    mandante = models.ForeignKey(Time, on_delete=models.CASCADE, related_name="jogos_casa")
    visitante = models.ForeignKey(Time, on_delete=models.CASCADE, related_name="jogos_fora")
    gols_mandante = models.PositiveSmallIntegerField(null=True, blank=True)
    gols_visitante = models.PositiveSmallIntegerField(null=True, blank=True)
    encerrada = models.BooleanField(default=False)
    data = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["rodada", "data"]
        indexes = [models.Index(fields=["encerrada"])]

    def __str__(self) -> str:
        placar = (
            f"{self.gols_mandante}x{self.gols_visitante}" if self.encerrada else "a realizar"
        )
        return f"R{self.rodada} {self.mandante.sigla} {placar} {self.visitante.sigla}"


class Simulacao(models.Model):
    """Snapshot das probabilidades num momento do campeonato."""

    criada_em = models.DateTimeField(auto_now_add=True)
    rodadas_disputadas = models.PositiveSmallIntegerField()
    n_simulacoes = models.PositiveIntegerField()
    seed = models.BigIntegerField(null=True, blank=True)
    resultado = models.JSONField(default=dict)

    class Meta:
        ordering = ["-criada_em"]
        get_latest_by = "criada_em"

    def __str__(self) -> str:
        return f"Simulação após {self.rodadas_disputadas} rodadas"
