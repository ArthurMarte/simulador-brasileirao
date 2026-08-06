# Simulador do Brasileirão

Simula por Monte Carlo os jogos que faltam no Campeonato Brasileiro Série A e responde:
**qual a chance do seu time ser campeão, ir à Libertadores ou cair para a Série B?**

```bash
curl http://localhost:8000/api/times/palmeiras/
```

```json
{
  "time": "palmeiras",
  "rodadas_disputadas": 22,
  "titulo": 34.18,
  "libertadores": 91.44,
  "pre_libertadores": 5.02,
  "sul_americana": 3.11,
  "rebaixamento": 0.0,
  "posicao_media": 2.87
}
```

---

## Como funciona

```
   partidas encerradas
          │
          ▼
┌──────────────────────┐
│ 1. Força de cada time│   ataque e defesa relativos à média da liga
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 2. Gols esperados    │   λ_casa = ataque_casa × defesa_fora × média × fator_mandante
│    por partida       │   λ_fora = ataque_fora × defesa_casa × média
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 3. Monte Carlo       │   sorteia placares via Poisson, monta a tabela final,
│    10.000 temporadas │   repete 10.000 vezes e conta as posições
└──────────┬───────────┘
           ▼
   probabilidades por faixa (título, G6, Z4) + posição média
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/probabilidades/` | Simulação mais recente, todos os times |
| GET | `/api/times/{slug}/` | Recorte de um único time |
| GET | `/api/health/` | Smoke test do deploy |
| GET | `/api/docs/` | Swagger |

## Stack

Django 5 · DRF · PostgreSQL · Redis · Celery + Beat · NumPy ·
Docker · pytest (gate de 80%) · ruff · GitHub Actions · drf-spectacular

## Rodando localmente

```bash
cp .env.example .env      # preencha API_FUTEBOL_TOKEN
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py shell -c \
  "from apps.campeonato.services.ingestao import sincronizar_partidas; sincronizar_partidas()"
docker compose exec web python manage.py simular --n 10000 --seed 42
```

A atualização diária roda automaticamente às 6h (Celery Beat), depois dos jogos da noite.

## Testes

```bash
docker compose exec web pytest
```

Nenhum teste faz chamada de rede real. A simulação é aleatória, então os testes fixam a
`seed` para garantir determinismo e verificam separadamente as **propriedades estatísticas**
do resultado — a soma das probabilidades de título dá 100%, um líder isolado tem mais chance
que o lanterna, nenhuma probabilidade escapa do intervalo 0–100.

## Limitações conhecidas

- O modelo ignora lesões, suspensões, calendário de copas e mando de campo alterado.
- As forças usam média simples da temporada, sem peso maior para jogos recentes.
- Poisson independente subestima ligeiramente a frequência de empates
  (o ajuste de Dixon-Coles corrige isso — está no roadmap).

Veja [`docs/DECISOES.md`](docs/DECISOES.md) para os trade-offs.

## Roadmap

- Ajuste de Dixon-Coles para correlação entre os placares
- Média móvel ponderada (jogos recentes pesam mais)
- Endpoint de tabela alternativa (só jogos em casa, só returno, empate valendo 2 pontos)
- Calibração: comparar as previsões com o que de fato aconteceu

## Licença

MIT
