"""
Algoritmo Ótimo de Belady (OPT / MIN).

Substitui a página residente cujo próximo uso está mais distante no futuro.
Serve como limite inferior teórico (referência ideal para avaliação).
"""

from typing import Dict, List, Optional


def precalcular_proximo_uso(paginas: List[int]) -> List[float]:
    """
    Pré-calcula a posição do próximo acesso de cada página na sequência.

    Percorre a lista de acessos de trás para frente. Para cada posição i,
    armazena o índice do próximo acesso à mesma página ou infinito se ela
    nunca mais for referenciada.

    Args:
        paginas: Sequência de acessos a páginas de memória.

    Returns:
        Lista com o índice do próximo acesso para cada posição i.
    """
    n = len(paginas)
    proximo_uso: List[float] = [float("inf")] * n
    ultima_ocorrencia: Dict[int, int] = {}

    for i in range(n - 1, -1, -1):
        p = paginas[i]
        if p in ultima_ocorrencia:
            proximo_uso[i] = ultima_ocorrencia[p]
        ultima_ocorrencia[p] = i

    return proximo_uso


def simular_opt(
    paginas: List[int],
    num_frames: int,
    proximo_uso: Optional[List[float]] = None,
) -> int:
    """
    Simula o algoritmo Ótimo de Belady (OPT / MIN).

    Por que funciona assim:
    O algoritmo ótimo escolhe como vítima a página cujo próximo acesso ocorrerá
    mais longe no tempo futuro (ou que nunca mais será acessada). Ele garante
    o menor número teórico de falhas de página possível para qualquer sequência.
    É impossível de ser implementado na prática em sistemas operacionais reais
    porque o sistema não pode prever o futuro dos programas, mas serve como
    limite inferior teórico indispensável para medir a qualidade dos outros
    algoritmos.

    Implementação:
    - Utiliza o vetor proximo_uso pré-calculado para evitar buscas caras.
    - Guarda para cada página residente o índice do seu próximo uso.
    - Na falha de página com memória cheia, escolhe a vítima via max().

    Args:
        paginas: Sequência de acessos a páginas de memória.
        num_frames: Quantidade de quadros de memória disponíveis.
        proximo_uso: Vetor pré-calculado de próximos acessos (opcional).

    Returns:
        Total de falhas de página ocorridas.
    """
    if num_frames <= 0 or not paginas:
        return 0

    if proximo_uso is None:
        proximo_uso = precalcular_proximo_uso(paginas)

    # Dicionário mapeando: pagina_residente -> indice_do_proximo_acesso
    memoria: Dict[int, float] = {}
    falhas = 0

    for i, pagina in enumerate(paginas):
        if pagina in memoria:
            # Acerto: atualiza quando esta página será usada novamente no futuro
            memoria[pagina] = proximo_uso[i]
        else:
            # Falha de página
            falhas += 1
            if len(memoria) == num_frames:
                # Escolhe a página que vai demorar mais para ser reutilizada
                vitima = max(memoria, key=memoria.get)
                del memoria[vitima]

            memoria[pagina] = proximo_uso[i]

    return falhas
