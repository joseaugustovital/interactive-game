import random


def gerar_porta():
    # Gera um número de porta aleatório na faixa de portas dinâmicas e/ou privadas: 49152–65535
    return random.randint(49152, 65535)


# Armazena o valor da porta gerada em random_port
result = gerar_porta()
