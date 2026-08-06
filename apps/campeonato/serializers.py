from rest_framework import serializers


class ProbabilidadeSerializer(serializers.Serializer):
    titulo = serializers.FloatField()
    libertadores = serializers.FloatField()
    pre_libertadores = serializers.FloatField()
    sul_americana = serializers.FloatField()
    rebaixamento = serializers.FloatField()
    posicao_media = serializers.FloatField()


class SimulacaoSerializer(serializers.Serializer):
    criada_em = serializers.DateTimeField()
    rodadas_disputadas = serializers.IntegerField()
    n_simulacoes = serializers.IntegerField()
    resultado = serializers.DictField(child=ProbabilidadeSerializer())
