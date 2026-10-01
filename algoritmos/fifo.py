"""
Algoritmo FIFO (First-In, First-Out).

Substitui a página que está na memória há mais tempo (a mais antiga carregada).
"""

import collections
from typing import List


def simular_fifo(paginas: List[int], num_frames: int) -> int:
    """
    Simula o algoritmo FIFO (First-In, First-Out).

    Por que funciona assim:
    A ideia mais simples de gerência de memória é tratar os frames como uma
    fila: a primeira página que entrou é a primeira a ser escolhida como vítima
    ao faltar espaço. Acertos em páginas já presentes NÃO alteram a fila.
    Apesar de simples e barato de implementar, desconsidera a localidade temporal
    e pode sofrer da Anomalia de Belady.

    Estrutura:
    - collections.deque: mantém a ordem cronológica de chegada das páginas.
    - set: conjunto para consulta rápida O(1) de páginas residentes na memória.

    Args:
        paginas: Sequência de acessos a páginas de memória.
        num_frames: Quantidade de quadros de memória disponíveis.

    Returns:
        Total de falhas de página ocorridas.
    """
    if num_frames <= 0 or not paginas:
        return 0

    memoria_set = set()
    fila = collections.deque()
    falhas = 0

    for pagina in paginas:
        if pagina not in memoria_set:
            falhas += 1
            if len(memoria_set) == num_frames:
                # Memória cheia: remove a página mais antiga (frente da fila)
                vitima = fila.popleft()
                memoria_set.remove(vitima)

            memoria_set.add(pagina)
            fila.append(pagina)

    return falhas
