# Decisões técnicas

## Por que Poisson e não um modelo de machine learning

Gols em futebol são eventos raros e independentes dentro de uma partida — exatamente o
caso de uso da distribuição de Poisson. Um modelo de ML exigiria muito mais dados,
seria mais difícil de explicar e provavelmente não superaria o Poisson num campeonato
de 380 jogos por temporada. Explicabilidade venceu sofisticação: qualquer pessoa
entende por que o time recebeu aquela probabilidade.

Limitação assumida: Poisson independente subestima empates, porque os dois placares são
tratados como não correlacionados. O ajuste de Dixon-Coles corrige placares baixos
(0-0, 1-0, 1-1) e está no roadmap.

## Por que 10.000 simulações

Com 10.000 iterações, o erro padrão de uma probabilidade próxima de 50% fica em torno
de 0,5 ponto percentual — precisão muito acima do que o próprio modelo justifica.
Aumentar para 100.000 multiplicaria o tempo de execução sem ganho real, já que o erro
dominante vem da estimativa das forças, não da amostragem.

## Por que fixar a seed nos testes

Código que usa aleatoriedade não pode ser testado por igualdade sem controle da fonte
aleatória. Usamos `numpy.random.default_rng(seed)` e injetamos a semente, o que permite
dois tipos de teste complementares:

1. **Determinismo** — mesma seed, mesmo resultado; seeds diferentes, resultados diferentes.
2. **Propriedades estatísticas** — invariantes que valem para qualquer seed: as
   probabilidades de título somam 100%, ficam entre 0 e 100, e um time muito superior
   tem chance maior que um time médio.

O segundo tipo é mais valioso: testa o que o código *significa*, não o número que ele
por acaso produziu.

## Por que guardar snapshot em vez de simular sob demanda

Uma simulação de 10.000 temporadas leva segundos. Rodar isso a cada requisição seria
desperdício, já que o resultado só muda quando entra uma rodada nova. O job diário
grava um `Simulacao`, e a API só lê. Bônus: o histórico de snapshots permite montar
depois a evolução da probabilidade ao longo do campeonato — um gráfico ótimo sem
mudar a modelagem.

## Por que a média simples e não uma média móvel ponderada

Ponderar jogos recentes é quase certamente melhor, mas introduz um hiperparâmetro
(o fator de decaimento) que eu não teria como calibrar sem backtest. Preferi começar
com o modelo mais simples que funciona e deixar a melhoria documentada no roadmap,
em vez de adicionar complexidade não validada.

## Por que o fator mandante é configurável

O mando de campo no Brasileirão pesa mais que na maioria das ligas europeias, e esse
peso varia entre temporadas. Deixar `FATOR_MANDANTE` como variável de ambiente permite
recalibrar sem alterar código — e torna o valor uma decisão explícita, não uma
constante escondida no meio da simulação.

## Por que ingestão idempotente

O job diário roda sempre sobre o campeonato inteiro, não sobre um delta. Usar
`update_or_create` com o `id_externo` da API garante que rodar duas vezes produza o
mesmo estado — importante porque falha de rede, retry do Celery e execução manual
acontecem. Há teste explícito para isso.
