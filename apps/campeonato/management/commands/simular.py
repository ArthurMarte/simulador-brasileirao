from django.core.management.base import BaseCommand

from apps.campeonato.tasks import rodar_simulacao


class Command(BaseCommand):
    help = "Roda a simulação de Monte Carlo com os dados já importados."

    def add_arguments(self, parser):
        parser.add_argument("--n", type=int, default=None, help="Número de simulações")
        parser.add_argument("--seed", type=int, default=None, help="Semente aleatória")

    def handle(self, *args, **options):
        resultado = rodar_simulacao(n=options["n"], seed=options["seed"])
        for time, dados in sorted(resultado.items(), key=lambda kv: -kv[1]["titulo"]):
            self.stdout.write(
                f"{time:<20} título {dados['titulo']:>6.2f}%  "
                f"G6 {dados['libertadores']:>6.2f}%  Z4 {dados['rebaixamento']:>6.2f}%"
            )
