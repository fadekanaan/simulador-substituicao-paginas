"""
Módulo responsável pela leitura e interpretação dos arquivos de trace.

Cada linha de um arquivo de trace contém um endereço de memória de 32 bits
em hexadecimal e o tipo de operação (R para leitura, W para escrita),
por exemplo: "31348900 W".

Com páginas de tamanho fixo de 4096 bytes (2^12), os 12 bits menos
significativos correspondem ao deslocamento (offset) dentro da página.
Portanto, o número da página virtual é obtido deslocando o endereço
12 bits para a direita (endereco >> 12).
"""

from typing import List


def ler_trace(caminho_arquivo: str) -> List[int]:
    """
    Lê um arquivo de trace e retorna a sequência completa de páginas acessadas.

    Linhas vazias ou com formato inválido são desconsideradas.
    Acessos repetidos à mesma página são mantidos intactos, pois algoritmos
    como o LRU aproximado (Aging) dependem da contagem precisa de acessos
    à memória para o avanço dos intervalos de tempo.

    Args:
        caminho_arquivo: Caminho para o arquivo .trace.

    Returns:
        Lista de inteiros representando os números das páginas acessadas.
    """
    paginas: List[int] = []

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue

            partes = linha.split()
            if not partes:
                continue

            try:
                # O primeiro elemento é o endereço em formato hexadecimal
                endereco = int(partes[0], 16)
                # Página de 4096 bytes: descarta os 12 bits de deslocamento
                numero_pagina = endereco >> 12
                paginas.append(numero_pagina)
            except ValueError:
                # Ignora linhas malformadas sem interromper a leitura
                continue

    return paginas
