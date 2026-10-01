# Simulador de Algoritmos de Substituição de Páginas de Memória

Simulador didático desenvolvido em Python 3 para a disciplina de **Sistemas Operacionais**. O objetivo é avaliar experimentalmente o impacto de diferentes políticas de substituição de páginas na taxa de falhas de página (*page faults*), variando o número de quadros (*frames*) sobre *traces* reais de acesso à memória.

O projeto foi construído priorizando clareza, simplicidade e facilidade de explicação: utiliza apenas a biblioteca padrão do Python e `matplotlib` para visualização gráfica.

---

## Estrutura do Repositório

```text
simulador-substituicao-paginas/
├── algoritmos/            # Pacote modular com cada algoritmo isolado
│   ├── __init__.py        # Reexporta as funções de simulação
│   ├── fifo.py            # Algoritmo FIFO (First-In, First-Out)
│   ├── opt.py             # Algoritmo Ótimo de Belady (OPT / MIN)
│   ├── lru_aprox.py       # Algoritmo LRU Aproximado (Aging com bit de referência)
│   └── lru.py             # Algoritmo LRU Exato (OrderedDict)
├── leitor.py              # Leitor de traces (conversão de endereços hex para números de página)
├── main.py                # Interface de linha de comando (argparse) e orquestrador dos experimentos
├── graficos.py            # Geração de gráficos em PNG via matplotlib
├── testes.py              # Testes unitários com asserções teóricas e anomalia de Belady
├── requirements.txt       # Dependências do projeto (matplotlib)
├── relatorio.md           # Esqueleto do relatório acadêmico para entrega do trabalho
├── .gitignore             # Configuração para ignorar traces (*.trace), caches e saídas
├── traces/                # Pasta contendo os arquivos .trace (ignorados pelo Git)
│   └── .gitkeep
└── resultados/            # Pasta onde são salvos os arquivos CSV e gráficos gerados
```

---

## Algoritmos Implementados

1. **FIFO (First-In, First-Out):**
   - Utiliza uma fila (`collections.deque`) para manter a ordem de chegada e um conjunto (`set`) para buscas rápidas em $O(1)$.
   - A vítima substituída é a página carregada há mais tempo na memória. Acertos a páginas residentes não alteram sua posição.
   - Pode apresentar a **Anomalia de Belady**.

2. **OPT (Ótimo de Belady / MIN):**
   - Algoritmo teórico ideal: a vítima é a página cujo próximo uso está mais distante no tempo futuro (ou que nunca mais será acessada).
   - Pré-calcula a posição da próxima ocorrência de cada página percorrendo o trace de trás para frente.
   - Inviável na prática por exigir conhecimento prévio do futuro, mas indispensável como **limite inferior teórico** para avaliar os demais algoritmos.

3. **LRU Aproximado (Aging com Bit de Referência):**
   - Baseado no algoritmo de envelhecimento visto em aula com histórico de $n$ bits (padrão: 8) e bit de referência $R$, deslocados periodicamente a cada `intervalo` acessos (padrão: 1000).
   - O projeto implementa duas variantes:
     - **Variante Principal ("com R" - `LRU aproximado`):** utiliza o bit $R$ atual como bit mais significativo virtual na escolha da vítima, impedindo a expulsão prematura de páginas recém-carregadas entre dois tiques de relógio.
     - **Variante Comparativa ("puro" - `LRU aproximado puro`):** considera exclusivamente o contador acumulado nos tiques anteriores, servindo de linha de base para mensurar o impacto da limitação de granularidade.

4. **LRU Exato (Least Recently Used):**
   - Implementado com `collections.OrderedDict`.
   - A cada acesso, move a página para o final (`move_to_end`). Ao faltar espaço, remove a primeira página (a menos recentemente utilizada).
   - Serve como referência direta para comparar a fidelidade das aproximações do LRU.

---

## Formato dos Traces

Os arquivos de trace (`.trace`) devem ser posicionados dentro do diretório `traces/`.
- Exemplos: `bzip.trace`, `gcc.trace`, `sixpack.trace`, `swim.trace`, `bigone.trace`.
- Cada linha contém um endereço hexadecimal de 32 bits e o tipo de acesso (`R` para leitura, `W` para escrita):
  ```text
  31348900 W
  07b243a0 R
  ```
- O tamanho padrão da página é de **4.096 bytes (4 KB)**. O número da página virtual é extraído descartando os 12 bits de deslocamento:
  $$\text{numero\_pagina} = \text{endereco} \gg 12$$
- A sequência completa de acessos é mantida integralmente, sem colapsar repetições consecutivas.

> **Importante:** Arquivos `.trace` não são commitados no repositório (estão no `.gitignore`).

---

## Instalação e Requisitos

Requer **Python 3.8+** e a biblioteca **matplotlib**.

```bash
# 1. Crie e ative um ambiente virtual (opcional, mas recomendado)
python3 -m venv venv
source venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt
```

---

## Como Executar

### 1. Executar os Testes Unitários
Os testes verificam os casos clássicos da literatura (cadeia de Silberschatz/Tanenbaum com 3 quadros, anomalia de Belady no FIFO e a propriedade de minimalidade do OPT):

```bash
python3 testes.py
```

### 2. Execução Rápida de Exemplo
Executa apenas um trace específico com um subconjunto de frames para testes rápidos:

```bash
python3 main.py --traces traces/bzip.trace --frames 4 16 64 256
```

### 3. Execução Completa dos Experimentos
Executa todos os traces presentes em `traces/` com a lista padrão de frames (`4, 8, 16, 32, 64, 128, 256`):

```bash
python3 main.py
```

### 4. Executar com Experimento de Sensibilidade
Varia o número de bits ($n_{\text{bits}} \in \{2, 4, 8, 16\}$) e o intervalo de tiques ($\text{intervalo} \in \{100, 1000, 10000\}$) do LRU aproximado:

```bash
python3 main.py --sensibilidade
```

### 5. Gerar ou Atualizar Apenas os Gráficos
Caso já tenha gerado o arquivo CSV de resultados, você pode regerar os gráficos a qualquer momento:

```bash
python3 graficos.py --csv resultados/resultados.csv --saida resultados/
```

---

## Argumentos Disponíveis no `main.py`

| Argumento | Tipo | Padrão | Descrição |
| :--- | :---: | :---: | :--- |
| `--traces` | Lista | Todos em `traces/*.trace` | Lista de arquivos de trace para processar |
| `--frames` | Lista (int) | `4 8 16 32 64 128 256` | Quantidades de quadros de memória avaliadas |
| `--bits` | Inteiro | `8` | Número de bits do histórico do LRU aproximado |
| `--intervalo` | Inteiro | `1000` | Intervalo de acessos para o envelhecimento no LRU aproximado |
| `--saida` | Texto | `resultados` | Diretório para salvar os arquivos CSV e PNG |
| `--sensibilidade` | Flag | Desativado | Executa o estudo de sensibilidade variando bits e intervalos |
| `--trace-sensibilidade`| Texto | Primeiro trace | Trace utilizado no teste de sensibilidade |
| `--frames-sensibilidade`| Inteiro | `64` | Frames utilizados no teste de sensibilidade |
| `--sem-graficos` | Flag | Desativado | Não gera os gráficos PNG ao final da simulação |

---

## Saídas Geradas

- **Terminal:** Tabela legível com 5 colunas de algoritmos (FIFO, LRU aproximado com R, LRU aproximado puro, OPT, LRU exato) e as taxas percentuais de falhas de página (%).
- **CSV:**
  - `resultados/resultados.csv`: colunas `trace, frames, algoritmo, falhas, taxa_falhas` (com os 5 algoritmos: FIFO, LRU aproximado, LRU aproximado puro, OPT, LRU exato).
  - `resultados/sensibilidade.csv`: colunas `trace, frames, variante, n_bits, intervalo, falhas, taxa_falhas` (com `variante` = "com R" ou "puro").
- **Gráficos (PNG):**
  - `resultados/grafico_<trace>.png`: curvas de desempenho comparando os 5 algoritmos em escala log2 no eixo de frames.
  - `resultados/grafico_sensibilidade.png`: dois painéis comparativos lado a lado mostrando a sensibilidade do Aging com R vs Aging Puro em função do intervalo e dos bits.
