"""
Pacote contendo os algoritmos de substituição de páginas de memória.

Exporta as funções de simulação para cada política:
- simular_fifo: First-In, First-Out
- simular_opt: Ótimo de Belady
- precalcular_proximo_uso: Função auxiliar para pré-cálculo do OPT
- simular_lru_aprox: LRU Aproximado (Aging com bit de referência)
- simular_lru: LRU Exato
"""

from .fifo import simular_fifo
from .lru import simular_lru
from .lru_aprox import simular_lru_aprox
from .opt import precalcular_proximo_uso, simular_opt

__all__ = [
    "simular_fifo",
    "simular_opt",
    "precalcular_proximo_uso",
    "simular_lru_aprox",
    "simular_lru",
]
