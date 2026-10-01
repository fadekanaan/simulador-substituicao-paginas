"""
Algoritmo LRU Aproximado (Aging / Envelhecimento com Bit de Referência).

Simula a técnica prática adotada por sistemas operacionais reais com
interrupções periódicas de relógio e contadores de bits de histórico.
"""

from typing import Dict, List


def simular_lru_aprox(
    paginas: List[int],
    num_frames: int,
    n_bits: int = 8,
    intervalo: int = 1000,
    considerar_ref: bool = True,
) -> int:
    """
    Simula o algoritmo LRU aproximado (Aging com bit de referência).

    Por que funciona assim:
    O algoritmo de Envelhecimento (Aging) aproxima o LRU usando interrupções de
    relógio periódicas. Cada página possui um contador de n_bits bits e um bit
    de referência R.
    - A cada acesso à memória: o sistema marca bit_ref = 1.
    - A cada 'intervalo' acessos (tique de relógio): o contador sofre deslocamento
      à direita (>> 1) e o bit_ref entra como bit mais significativo (MSB); em
      seguida, bit_ref é zerado.

    Variante Principal ('Aging com R' - considerar_ref=True):
    Na ocorrência de uma falha de página, o SO consegue ler o bit R no momento
    da substituição. Ao compor uma chave virtual ((contador >> 1) | (bit_ref << msb_shift)),
    o bit R do intervalo atual entra como MSB virtual, evitando que páginas
    referenciadas recentemente (inclusive recém-carregadas com contador=0 e bit_ref=1)
    sejam expulsas prematuramente antes do próximo tique de relógio.

    Variante Comparativa ('Aging Puro' - considerar_ref=False):
    Considera estritamente o valor do contador acumulado até o último tique,
    deixando páginas novas vulneráveis à expulsão entre dois tiques.

    Estrutura:
    - memoria[pagina] = [contador, bit_ref, ordem_chegada]

    Args:
        paginas: Sequência de acessos a páginas de memória.
        num_frames: Quantidade de quadros de memória disponíveis.
        n_bits: Quantidade de bits do contador de histórico (padrão: 8).
        intervalo: Frequência em acessos para a rotina de envelhecimento (padrão: 1000).
        considerar_ref: Se True, considera o bit R atual na escolha da vítima (padrão: True).

    Returns:
        Total de falhas de página ocorridas.
    """
    if num_frames <= 0 or not paginas:
        return 0

    # memoria: pagina -> [contador, bit_ref, ordem_chegada]
    memoria: Dict[int, List[int]] = {}
    falhas = 0
    relogio_chegada = 0
    msb_shift = n_bits - 1
    mascara_bits = (1 << n_bits) - 1

    for idx, pagina in enumerate(paginas, start=1):
        if pagina in memoria:
            # Acerto: marca que a página foi referenciada neste intervalo
            memoria[pagina][1] = 1
        else:
            # Falha de página
            falhas += 1
            if len(memoria) == num_frames:
                # Escolha da vítima:
                # Se considerar_ref=True: o bit R atual entra como MSB virtual
                # Se considerar_ref=False: considera apenas o contador acumulado
                # Empates são resolvidos por ordem de chegada na memória (FIFO)
                if considerar_ref:
                    vitima = min(
                        memoria,
                        key=lambda p: (
                            ((memoria[p][0] >> 1) | (memoria[p][1] << msb_shift)),
                            memoria[p][2],
                        ),
                    )
                else:
                    vitima = min(
                        memoria,
                        key=lambda p: (memoria[p][0], memoria[p][2]),
                    )
                del memoria[vitima]

            relogio_chegada += 1
            # Entra na memória com bit_ref = 1 e contador = 0
            memoria[pagina] = [0, 1, relogio_chegada]

        # A cada 'intervalo' acessos à memória: envelhece todas as páginas residentes
        if idx % intervalo == 0:
            for dados in memoria.values():
                contador = dados[0]
                bit_ref = dados[1]
                # Desloca para a direita e insere o bit de referência no MSB
                dados[0] = ((contador >> 1) | (bit_ref << msb_shift)) & mascara_bits
                # Limpa o bit de referência para o próximo período
                dados[1] = 0

    return falhas
