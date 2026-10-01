"""
Simulador de Algoritmos de Substituição de Páginas de Memória
Disciplina: Sistemas Operacionais

Executa os experimentos comparando FIFO, LRU Aproximado (Aging),
OPT (Ótimo de Belady) e LRU Exato, variando o número de quadros (frames)
e avaliando as falhas de página sobre traces reais de acesso à memória.
"""

import argparse
import csv
import glob
import os
import sys
import time
from typing import Dict, List, Tuple

from algoritmos import (
    precalcular_proximo_uso,
    simular_fifo,
    simular_lru,
    simular_lru_aprox,
    simular_opt,
)
from graficos import gerar_grafico_sensibilidade, gerar_graficos_traces
from leitor import ler_trace


def salvar_resultados_csv(
    caminho_csv: str,
    registros: List[Tuple[str, int, str, int, float]],
) -> None:
    """
    Salva os resultados em arquivo CSV.
    Colunas: trace, frames, algoritmo, falhas, taxa_falhas
    """
    os.makedirs(os.path.dirname(os.path.abspath(caminho_csv)), exist_ok=True)
    with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["trace", "frames", "algoritmo", "falhas", "taxa_falhas"])
        for trace, frames, algo, falhas, taxa in registros:
            escritor.writerow([trace, frames, algo, falhas, f"{taxa:.4f}"])


def salvar_sensibilidade_csv(
    caminho_csv: str,
    registros: List[Tuple[str, int, str, int, int, int, float]],
) -> None:
    """
    Salva os resultados do experimento de sensibilidade em CSV.
    Colunas: trace, frames, variante, n_bits, intervalo, falhas, taxa_falhas
    """
    os.makedirs(os.path.dirname(os.path.abspath(caminho_csv)), exist_ok=True)
    with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["trace", "frames", "variante", "n_bits", "intervalo", "falhas", "taxa_falhas"])
        for trace, frames, variante, n_bits, intervalo, falhas, taxa in registros:
            escritor.writerow([trace, frames, variante, n_bits, intervalo, falhas, f"{taxa:.4f}"])


def executar_sensibilidade(
    caminho_trace: str,
    frames: int,
    lista_bits: List[int],
    lista_intervalos: List[int],
    pasta_saida: str,
) -> None:
    """
    Executa o experimento de sensibilidade do LRU aproximado (Aging)
    para as duas variantes (com R e puro), variando n_bits e o intervalo.
    """
    nome_trace = os.path.basename(caminho_trace).replace(".trace", "")
    print("\n" + "=" * 105)
    print(f" EXPERIMENTO DE SENSIBILIDADE: LRU APROXIMADO (AGING)")
    print(f" Trace: {nome_trace} | Frames: {frames}")
    print("=" * 105)

    print(f"Lendo trace '{caminho_trace}'...")
    paginas = ler_trace(caminho_trace)
    total_acessos = len(paginas)
    print(f"Total de acessos carregados: {total_acessos:,}")

    registros = []
    variantes = [
        ("com R", True, "LRU Aproximado (Aging com R - Versão Principal)"),
        ("puro", False, "LRU Aproximado Puro (Aging sem R - Versão Comparativa)"),
    ]

    for nome_var, considerar_ref, titulo_tabela in variantes:
        print(f"\n--- {titulo_tabela} ---")
        tabela: Dict[int, Dict[int, Tuple[int, float]]] = {}

        for n_bits in lista_bits:
            tabela[n_bits] = {}
            for intervalo in lista_intervalos:
                falhas = simular_lru_aprox(
                    paginas,
                    frames,
                    n_bits=n_bits,
                    intervalo=intervalo,
                    considerar_ref=considerar_ref,
                )
                taxa = (falhas / total_acessos) * 100 if total_acessos > 0 else 0.0
                registros.append((nome_trace, frames, nome_var, n_bits, intervalo, falhas, taxa))
                tabela[n_bits][intervalo] = (falhas, taxa)

        # Imprimir tabela formatada no terminal
        header = f"{'Bits':<8}"
        for it in lista_intervalos:
            header += f" | {f'Intervalo {it}':<24}"
        print(header)
        print("-" * len(header))

        for n_bits in lista_bits:
            linha = f"{f'{n_bits} bits':<8}"
            for it in lista_intervalos:
                falhas, taxa = tabela[n_bits][it]
                conteudo = f"{falhas:,} ({taxa:.2f}%)"
                linha += f" | {conteudo:<24}"
            print(linha)

    caminho_csv = os.path.join(pasta_saida, "sensibilidade.csv")
    salvar_sensibilidade_csv(caminho_csv, registros)
    print(f"\nResultados de sensibilidade salvos em: {caminho_csv}")


def obter_traces_padrao() -> List[str]:
    """Retorna lista de todos os arquivos .trace na pasta traces/ ordenados."""
    arquivos = sorted(glob.glob(os.path.join("traces", "*.trace")))
    return arquivos


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulador de Algoritmos de Substituição de Páginas (FIFO, LRU aprox, OPT, LRU exato)."
    )
    parser.add_argument(
        "--traces",
        nargs="+",
        default=None,
        help="Caminhos dos arquivos de trace (padrão: todos os .trace em traces/)",
    )
    parser.add_argument(
        "--frames",
        nargs="+",
        type=int,
        default=[4, 8, 16, 32, 64, 128, 256],
        help="Lista de quantidade de frames para simulação (padrão: 4 8 16 32 64 128 256)",
    )
    parser.add_argument(
        "--bits",
        type=int,
        default=8,
        help="Número de bits do contador de Aging no LRU aproximado (padrão: 8)",
    )
    parser.add_argument(
        "--intervalo",
        type=int,
        default=1000,
        help="Intervalo de acessos para envelhecimento no LRU aproximado (padrão: 1000)",
    )
    parser.add_argument(
        "--saida",
        type=str,
        default="resultados",
        help="Diretório para salvar tabelas CSV e gráficos (padrão: resultados/)",
    )
    parser.add_argument(
        "--sensibilidade",
        action="store_true",
        help="Executa o experimento de sensibilidade para o LRU aproximado",
    )
    parser.add_argument(
        "--trace-sensibilidade",
        type=str,
        default=None,
        help="Arquivo de trace específico para o experimento de sensibilidade (padrão: primeiro trace)",
    )
    parser.add_argument(
        "--frames-sensibilidade",
        type=int,
        default=64,
        help="Quantidade de frames fixa para o experimento de sensibilidade (padrão: 64)",
    )
    parser.add_argument(
        "--sem-graficos",
        action="store_true",
        help="Desativa a geração automática de gráficos PNG ao final dos experimentos",
    )

    args = parser.parse_args()

    # Identificar traces
    lista_traces = args.traces
    if lista_traces is None:
        lista_traces = obter_traces_padrao()

    if not lista_traces:
        print("Erro: Nenhum arquivo de trace encontrado na pasta traces/ ou especificado via --traces.", file=sys.stderr)
        print("Certifique-se de que os arquivos .trace estão dentro do diretório 'traces/'.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.saida, exist_ok=True)
    caminho_csv = os.path.join(args.saida, "resultados.csv")
    todos_registros_csv: List[Tuple[str, int, str, int, float]] = []

    print("\n" + "=" * 105)
    print(" INICIALIZANDO SIMULAÇÃO DE SUBSTITUIÇÃO DE PÁGINAS")
    print(f" Traces a processar: {len(lista_traces)}")
    print(f" Configurações de frames: {args.frames}")
    print(f" LRU Aproximado: {args.bits} bits, intervalo={args.intervalo} acessos")
    print(f" Pasta de saída: {args.saida}/")
    print("=" * 105)

    tempo_inicio_geral = time.time()

    for idx_trace, caminho_trace in enumerate(lista_traces, start=1):
        nome_trace = os.path.basename(caminho_trace).replace(".trace", "")
        print(f"\n[{idx_trace}/{len(lista_traces)}] Carregando trace: {nome_trace} ({caminho_trace})")

        t_leitura0 = time.time()
        paginas = ler_trace(caminho_trace)
        t_leitura = time.time() - t_leitura0
        total_acessos = len(paginas)

        if total_acessos == 0:
            print(f"  Aviso: Trace '{caminho_trace}' está vazio ou não possui acessos válidos. Ignorando.")
            continue

        print(f"  -> {total_acessos:,} acessos lidos em {t_leitura:.2f}s.")
        print("  -> Pré-calculando próximo uso para o algoritmo Ótimo (OPT)... ", end="", flush=True)
        t_opt0 = time.time()
        proximo_uso = precalcular_proximo_uso(paginas)
        t_opt = time.time() - t_opt0
        print(f"Concluído em {t_opt:.2f}s.")

        # Tabela no terminal para este trace
        divisoria = "-" * 122
        print("\n" + divisoria)
        print(f" RESULTADOS: {nome_trace} ({total_acessos:,} acessos à memória)")
        print(divisoria)
        print(f"{'Frames':<8} | {'FIFO':<20} | {'LRU Aprox. (com R)':<21} | {'LRU Aprox. (Puro)':<21} | {'OPT (Belady)':<20} | {'LRU Exato':<20}")
        print(divisoria)

        for num_frames in args.frames:
            # 1. FIFO
            falhas_fifo = simular_fifo(paginas, num_frames)
            taxa_fifo = (falhas_fifo / total_acessos) * 100

            # 2. LRU Aproximado (com R - Principal)
            falhas_aprox_r = simular_lru_aprox(
                paginas, num_frames, n_bits=args.bits, intervalo=args.intervalo, considerar_ref=True
            )
            taxa_aprox_r = (falhas_aprox_r / total_acessos) * 100

            # 3. LRU Aproximado Puro (sem R - Comparativo)
            falhas_aprox_puro = simular_lru_aprox(
                paginas, num_frames, n_bits=args.bits, intervalo=args.intervalo, considerar_ref=False
            )
            taxa_aprox_puro = (falhas_aprox_puro / total_acessos) * 100

            # 4. OPT
            falhas_opt = simular_opt(paginas, num_frames, proximo_uso=proximo_uso)
            taxa_opt = (falhas_opt / total_acessos) * 100

            # 5. LRU Exato
            falhas_lru = simular_lru(paginas, num_frames)
            taxa_lru = (falhas_lru / total_acessos) * 100

            # Registra no CSV nesta ordem exata:
            todos_registros_csv.append((nome_trace, num_frames, "FIFO", falhas_fifo, taxa_fifo))
            todos_registros_csv.append((nome_trace, num_frames, "LRU aproximado", falhas_aprox_r, taxa_aprox_r))
            todos_registros_csv.append((nome_trace, num_frames, "LRU aproximado puro", falhas_aprox_puro, taxa_aprox_puro))
            todos_registros_csv.append((nome_trace, num_frames, "OPT", falhas_opt, taxa_opt))
            todos_registros_csv.append((nome_trace, num_frames, "LRU exato", falhas_lru, taxa_lru))

            # Exibe linha da tabela
            cel_fifo = f"{falhas_fifo:,} ({taxa_fifo:.2f}%)"
            cel_aprox_r = f"{falhas_aprox_r:,} ({taxa_aprox_r:.2f}%)"
            cel_aprox_puro = f"{falhas_aprox_puro:,} ({taxa_aprox_puro:.2f}%)"
            cel_opt = f"{falhas_opt:,} ({taxa_opt:.2f}%)"
            cel_lru = f"{falhas_lru:,} ({taxa_lru:.2f}%)"

            print(
                f"{num_frames:<8} | {cel_fifo:<20} | {cel_aprox_r:<21} | {cel_aprox_puro:<21} | {cel_opt:<20} | {cel_lru:<20}"
            )

        print(divisoria)

    # Salva CSV principal
    salvar_resultados_csv(caminho_csv, todos_registros_csv)
    print(f"\nResultados principais salvos com sucesso em: {caminho_csv}")

    # Experimento de sensibilidade opcional
    if args.sensibilidade:
        trace_sens = args.trace_sensibilidade
        if trace_sens is None:
            trace_sens = lista_traces[0]
        executar_sensibilidade(
            caminho_trace=trace_sens,
            frames=args.frames_sensibilidade,
            lista_bits=[2, 4, 8, 16],
            lista_intervalos=[100, 1000, 10000],
            pasta_saida=args.saida,
        )

    # Geração dos gráficos
    if not args.sem_graficos:
        print("\nGerando gráficos informativos com matplotlib...")
        try:
            gerar_graficos_traces(caminho_csv, args.saida)
            caminho_sens_csv = os.path.join(args.saida, "sensibilidade.csv")
            if args.sensibilidade and os.path.exists(caminho_sens_csv):
                gerar_grafico_sensibilidade(caminho_sens_csv, args.saida)
            print("Gráficos gerados com sucesso na pasta:", args.saida)
        except Exception as e:
            print(f"Aviso: Não foi possível gerar os gráficos: {e}", file=sys.stderr)

    tempo_total = time.time() - tempo_inicio_geral
    print(f"\nSimulação concluída com sucesso em {tempo_total:.2f}s!")


if __name__ == "__main__":
    main()
