"""
Módulo responsável pela geração dos gráficos a partir dos arquivos CSV
produzidos pelo simulador de substituição de páginas.

Utiliza matplotlib para criar gráficos limpos e didáticos:
- Um gráfico de linhas por trace (frames vs falhas de página por algoritmo).
- Um gráfico para o experimento de sensibilidade (intervalo e bits vs falhas).
"""

import argparse
import csv
import os
import sys
from typing import Dict, List


def carregar_resultados_csv(caminho_csv: str) -> Dict[str, Dict[str, Dict[int, int]]]:
    """
    Carrega o CSV de resultados e organiza os dados em estrutura aninhada:
    dados[trace][algoritmo][frames] = falhas
    """
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")

    dados: Dict[str, Dict[str, Dict[int, int]]] = {}

    with open(caminho_csv, "r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            trace = linha["trace"]
            frames = int(linha["frames"])
            algoritmo = linha["algoritmo"]
            falhas = int(linha["falhas"])

            if trace not in dados:
                dados[trace] = {}
            if algoritmo not in dados[trace]:
                dados[trace][algoritmo] = {}

            dados[trace][algoritmo][frames] = falhas

    return dados


def carregar_sensibilidade_csv(caminho_csv: str) -> Dict[str, Dict[str, Dict[int, Dict[int, int]]]]:
    """
    Carrega o CSV de sensibilidade e organiza os dados:
    dados[chave_trace][variante][n_bits][intervalo] = falhas
    """
    if not os.path.exists(caminho_csv):
        return {}

    dados: Dict[str, Dict[str, Dict[int, Dict[int, int]]]] = {}

    with open(caminho_csv, "r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            chave_trace = f"{linha['trace']} ({linha['frames']} frames)"
            variante = linha.get("variante", "com R")
            n_bits = int(linha["n_bits"])
            intervalo = int(linha["intervalo"])
            falhas = int(linha["falhas"])

            if chave_trace not in dados:
                dados[chave_trace] = {}
            if variante not in dados[chave_trace]:
                dados[chave_trace][variante] = {}
            if n_bits not in dados[chave_trace][variante]:
                dados[chave_trace][variante][n_bits] = {}

            dados[chave_trace][variante][n_bits][intervalo] = falhas

    return dados


def gerar_graficos_traces(
    caminho_csv: str,
    pasta_saida: str = "resultados",
) -> List[str]:
    """
    Gera um gráfico de linhas para cada trace presente no CSV.
    Eixo X: número de frames (escala log2)
    Eixo Y: número de falhas de página
    """
    import matplotlib.pyplot as plt

    os.makedirs(pasta_saida, exist_ok=True)
    dados = carregar_resultados_csv(caminho_csv)
    graficos_gerados = []

    # Configurações de estilo para cada algoritmo na ordem especificada
    estilos = {
        "FIFO": {"cor": "#e74c3c", "marcador": "o", "estilo": "-", "label": "FIFO"},
        "LRU aproximado": {"cor": "#16a085", "marcador": "^", "estilo": "-", "label": "LRU aprox. (com R)"},
        "LRU aproximado puro": {"cor": "#e67e22", "marcador": "v", "estilo": "--", "label": "LRU aprox. puro"},
        "OPT": {"cor": "#27ae60", "marcador": "D", "estilo": "-.", "label": "OPT"},
        "LRU exato": {"cor": "#2980b9", "marcador": "s", "estilo": "-", "label": "LRU exato"},
    }

    for trace, algos in dados.items():
        fig, ax = plt.subplots(figsize=(9.5, 5.5))

        # Obter todos os valores de frames ordenados
        todos_frames = sorted(
            {f for algo_dados in algos.values() for f in algo_dados.keys()}
        )

        for nome_algo, config in estilos.items():
            if nome_algo in algos:
                valores = [algos[nome_algo].get(f, None) for f in todos_frames]
                ax.plot(
                    todos_frames,
                    valores,
                    label=config.get("label", nome_algo),
                    color=config["cor"],
                    marker=config["marcador"],
                    linestyle=config["estilo"],
                    linewidth=2,
                    markersize=6,
                )

        ax.set_title(f"Falhas de Página vs Frames — Trace: {trace}", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Número de Frames (Escala Log₂)", fontsize=11)
        ax.set_ylabel("Número de Falhas de Página", fontsize=11)
        ax.set_xscale("log", base=2)
        ax.set_xticks(todos_frames)
        ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
        ax.minorticks_off()
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Algoritmo", fontsize=9.5, title_fontsize=10)
        plt.tight_layout()

        caminho_grafico = os.path.join(pasta_saida, f"grafico_{trace}.png")
        plt.savefig(caminho_grafico, dpi=300)
        plt.close()
        graficos_gerados.append(caminho_grafico)
        print(f"[Gráficos] Salvo: {caminho_grafico}")

    return graficos_gerados


def gerar_grafico_sensibilidade(
    caminho_csv: str,
    pasta_saida: str = "resultados",
) -> List[str]:
    """
    Gera o gráfico do experimento de sensibilidade do LRU aproximado (Aging),
    variando o intervalo de tique e o número de bits de histórico para as
    duas variantes (com R e puro) em dois painéis lado a lado.
    """
    import matplotlib.pyplot as plt

    if not os.path.exists(caminho_csv):
        return []

    dados = carregar_sensibilidade_csv(caminho_csv)
    if not dados:
        return []

    os.makedirs(pasta_saida, exist_ok=True)
    graficos_gerados = []

    cores = ["#16a085", "#2980b9", "#8e44ad", "#d35400"]
    marcadores = ["o", "s", "^", "D"]

    for chave_trace, variantes_dados in dados.items():
        # Cria dois painéis lado a lado: com R (esquerda) e puro (direita)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), sharey=False)

        config_paineis = [
            (ax1, "com R", "LRU Aproximado (com R - Principal)"),
            (ax2, "puro", "LRU Aproximado Puro (sem R - Comparativo)"),
        ]

        for ax, var_nome, titulo_painel in config_paineis:
            bits_dados = variantes_dados.get(var_nome, {})
            todos_intervalos = sorted(
                {it for int_dados in bits_dados.values() for it in int_dados.keys()}
            )

            for i, (n_bits, int_dados) in enumerate(sorted(bits_dados.items())):
                valores = [int_dados.get(it, None) for it in todos_intervalos]
                cor = cores[i % len(cores)]
                marcador = marcadores[i % len(marcadores)]

                ax.plot(
                    [str(it) for it in todos_intervalos],
                    valores,
                    label=f"{n_bits} bits",
                    color=cor,
                    marker=marcador,
                    linewidth=2,
                    markersize=6,
                )

            ax.set_title(titulo_painel, fontsize=11.5, fontweight="bold", pad=10)
            ax.set_xlabel("Intervalo de Envelhecimento (Acessos)", fontsize=10.5)
            ax.set_ylabel("Número de Falhas de Página", fontsize=10.5)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(title="Histórico", fontsize=9, title_fontsize=9.5)

        fig.suptitle(
            f"Sensibilidade do LRU Aproximado — {chave_trace}",
            fontsize=13,
            fontweight="bold",
            y=0.98,
        )
        plt.tight_layout()

        caminho_grafico = os.path.join(pasta_saida, "grafico_sensibilidade.png")
        plt.savefig(caminho_grafico, dpi=300)
        plt.close()
        graficos_gerados.append(caminho_grafico)
        print(f"[Gráficos] Salvo: {caminho_grafico}")

    return graficos_gerados


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera gráficos a partir dos resultados da simulação de paginação."
    )
    parser.add_argument(
        "--csv",
        default="resultados/resultados.csv",
        help="Caminho do arquivo CSV de resultados principais (padrão: resultados/resultados.csv)",
    )
    parser.add_argument(
        "--sensibilidade-csv",
        default="resultados/sensibilidade.csv",
        help="Caminho do arquivo CSV de sensibilidade (padrão: resultados/sensibilidade.csv)",
    )
    parser.add_argument(
        "--saida",
        default="resultados",
        help="Pasta onde os gráficos serão salvos (padrão: resultados/)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"Erro: Arquivo CSV '{args.csv}' não encontrado.", file=sys.stderr)
        print("Execute primeiro a simulação (main.py) para gerar os dados.", file=sys.stderr)
        sys.exit(1)

    print("Gerando gráficos...")
    gerar_graficos_traces(args.csv, args.saida)

    if os.path.exists(args.sensibilidade_csv):
        gerar_grafico_sensibilidade(args.sensibilidade_csv, args.saida)

    print("Todos os gráficos foram gerados com sucesso!")


if __name__ == "__main__":
    main()
