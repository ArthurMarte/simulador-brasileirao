import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("simulador")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "atualizar-e-simular-diariamente": {
        "task": "apps.campeonato.tasks.atualizar_e_simular",
        # 6h da manhã: depois de qualquer jogo da noite anterior
        "schedule": crontab(hour=6, minute=0),
    },
}
