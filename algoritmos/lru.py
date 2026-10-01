"""
Algoritmo LRU Exato (Least Recently Used).

Substitui a página que não é utilizada há mais tempo.
Serve como benchmark para avaliar a proximidade do LRU aproximado.
"""

import collections
from typing import List


def simular_lru(paginas: List[int], num_frames: int) -> int:
    """
    Simula o algoritmo LRU exato (Least Recently Used).

    Por que funciona assim:
    Baseia-se no princípio da localidade temporal: páginas acessadas
    recentemente têm alta probabilidade de serem acessadas novamente em breve.
    A página vítima é aquela que está há mais tempo sem nenhum acesso.
    Serve como referência perfeita para avaliar o quão perto o LRU aproximado
    chega do comportamento ideal do LRU.

    Estrutura:
    - collections.OrderedDict: mantém as páginas ordenadas pelo último acesso.
      A cada acerto, move_to_end coloca a página no final (mais recente).
      Na substituição, popitem(last=False) remove o primeiro elemento (menos recente).

    Args:
        paginas: Sequência de acessos a páginas de memória.
        num_frames: Quantidade de quadros de memória disponíveis.

    Returns:
        Total de falhas de página ocorridas.
    """
    if num_frames <= 0 or not paginas:
        return 0

    memoria: collections.OrderedDict[int, bool] = collections.OrderedDict()
    falhas = 0

    for pagina in paginas:
        if pagina in memoria:
            # Acerto: atualiza a página para o final da lista (mais recente)
            memoria.move_to_end(pagina)
        else:
            # Falha de página
            falhas += 1
            if len(memoria) == num_frames:
                # Memória cheia: remove o elemento menos recentemente usado (primeiro)
                memoria.popitem(last=False)

            memoria[pagina] = True

    return falhas
