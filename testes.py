"""
Testes unitários simples para os algoritmos de substituição de páginas.
Executado sem frameworks externos, utilizando apenas asserções (assert).
"""

import random
from algoritmos import (
    precalcular_proximo_uso,
    simular_fifo,
    simular_lru,
    simular_lru_aprox,
    simular_opt,
)


def testar_cadeia_classica() -> None:
    """
    Testa a sequência clássica de Silberschatz/Tanenbaum com 3 frames:
    7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1

    Resultados teóricos esperados:
    - FIFO: 15 falhas de página
    - OPT: 9 falhas de página
    - LRU exato: 12 falhas de página
    """
    cadeia = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    frames = 3

    falhas_fifo = simular_fifo(cadeia, frames)
    falhas_opt = simular_opt(cadeia, frames)
    falhas_lru = simular_lru(cadeia, frames)

    # LRU aproximado: variantes com R e pura
    falhas_lru_aprox_1_r = simular_lru_aprox(cadeia, frames, n_bits=8, intervalo=1, considerar_ref=True)
    falhas_lru_aprox_1_puro = simular_lru_aprox(cadeia, frames, n_bits=8, intervalo=1, considerar_ref=False)
    falhas_lru_aprox_padrao_r = simular_lru_aprox(cadeia, frames, n_bits=8, intervalo=1000, considerar_ref=True)
    falhas_lru_aprox_padrao_puro = simular_lru_aprox(cadeia, frames, n_bits=8, intervalo=1000, considerar_ref=False)

    print(f"Cadeia clássica (frames={frames}):")
    print(f"  FIFO:                     {falhas_fifo} falhas (esperado: 15)")
    print(f"  OPT:                      {falhas_opt} falhas (esperado: 9)")
    print(f"  LRU exato:                {falhas_lru} falhas (esperado: 12)")
    print(f"  LRU aprox (it=1, com R):  {falhas_lru_aprox_1_r} falhas")
    print(f"  LRU aprox (it=1, puro):   {falhas_lru_aprox_1_puro} falhas")
    print(f"  LRU aprox (it=1000, com R): {falhas_lru_aprox_padrao_r} falhas")
    print(f"  LRU aprox (it=1000, puro):  {falhas_lru_aprox_padrao_puro} falhas")

    assert falhas_fifo == 15, f"FIFO esperado 15, obtido {falhas_fifo}"
    assert falhas_opt == 9, f"OPT esperado 9, obtido {falhas_opt}"
    assert falhas_lru == 12, f"LRU esperado 12, obtido {falhas_lru}"

    # Justificativas dos valores:
    # 1. Com intervalo=1: cada acesso sofre envelhecimento imediatamente. Como n_bits=8
    #    cobre a distância de reuso desta cadeia de 20 acessos, ambas as variantes
    #    reproduzem as 12 falhas do LRU exato.
    assert falhas_lru_aprox_1_r == 12
    assert falhas_lru_aprox_1_puro == 12

    # 2. Com intervalo=1000: em 20 acessos nunca ocorre tique de envelhecimento.
    #    Todas as páginas têm o mesmo histórico relativo e o desempate recai
    #    sobre a ordem de chegada (FIFO), resultando nas mesmas 15 falhas do FIFO.
    assert falhas_lru_aprox_padrao_r == 15
    assert falhas_lru_aprox_padrao_puro == 15

    # O algoritmo ótimo é o limite inferior
    assert falhas_opt <= falhas_fifo
    assert falhas_opt <= falhas_lru
    assert falhas_opt <= falhas_lru_aprox_padrao_r
    assert falhas_opt <= falhas_lru_aprox_padrao_puro
    print("  -> Teste da cadeia clássica passou com sucesso!\n")


def testar_anomalia_belady() -> None:
    """
    Demonstra a Anomalia de Belady no algoritmo FIFO.
    Sequência: 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5

    Comportamento anômalo:
    - Com 3 frames: 9 falhas
    - Com 4 frames: 10 falhas (mais frames geram MAIS falhas de página!)
    """
    cadeia = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]

    falhas_fifo_3 = simular_fifo(cadeia, 3)
    falhas_fifo_4 = simular_fifo(cadeia, 4)
    falhas_opt_3 = simular_opt(cadeia, 3)
    falhas_opt_4 = simular_opt(cadeia, 4)

    # Ambas as variantes do aging
    falhas_lru_r_3 = simular_lru_aprox(cadeia, 3, considerar_ref=True)
    falhas_lru_r_4 = simular_lru_aprox(cadeia, 4, considerar_ref=True)
    falhas_lru_puro_3 = simular_lru_aprox(cadeia, 3, considerar_ref=False)
    falhas_lru_puro_4 = simular_lru_aprox(cadeia, 4, considerar_ref=False)

    print("Anomalia de Belady no FIFO:")
    print(f"  FIFO com 3 frames: {falhas_fifo_3} falhas (esperado: 9)")
    print(f"  FIFO com 4 frames: {falhas_fifo_4} falhas (esperado: 10)")

    assert falhas_fifo_3 == 9, f"FIFO 3 frames esperado 9, obtido {falhas_fifo_3}"
    assert falhas_fifo_4 == 10, f"FIFO 4 frames esperado 10, obtido {falhas_fifo_4}"
    assert falhas_fifo_4 > falhas_fifo_3, "Esperada anomalia de Belady (mais falhas com mais frames)"

    # Em ambos os casos de frames, OPT deve ser <= outros
    assert falhas_opt_3 <= falhas_fifo_3
    assert falhas_opt_4 <= falhas_fifo_4
    assert falhas_opt_3 <= falhas_lru_r_3
    assert falhas_opt_4 <= falhas_lru_r_4
    assert falhas_opt_3 <= falhas_lru_puro_3
    assert falhas_opt_4 <= falhas_lru_puro_4

    # com considerar_ref=False, resultado idêntico ao puro anterior
    assert falhas_lru_puro_3 == 9
    assert falhas_lru_puro_4 == 10
    print("  -> Teste da Anomalia de Belady passou com sucesso!\n")


def testar_casos_borda() -> None:
    """
    Testa casos de borda:
    - Sequência vazia
    - Sequência com uma única página repetida
    - Memória com mais frames do que o total de páginas distintas
    """
    print("Testando casos de borda:")

    # 1. Sequência vazia
    vazia = []
    assert simular_fifo(vazia, 3) == 0
    assert simular_opt(vazia, 3) == 0
    assert simular_lru(vazia, 3) == 0
    assert simular_lru_aprox(vazia, 3, considerar_ref=True) == 0
    assert simular_lru_aprox(vazia, 3, considerar_ref=False) == 0

    # 2. Página única repetida muitas vezes (só deve falhar no primeiro acesso)
    unica = [42] * 100
    assert simular_fifo(unica, 3) == 1
    assert simular_opt(unica, 3) == 1
    assert simular_lru(unica, 3) == 1
    assert simular_lru_aprox(unica, 3, considerar_ref=True) == 1
    assert simular_lru_aprox(unica, 3, considerar_ref=False) == 1

    # 3. Frames suficientes para todas as páginas distintas (nunca há substituição)
    diversas = [1, 2, 3, 4, 1, 2, 3, 4, 2, 1]
    frames = 10  # cabem todas as 4 distintas
    distintas = len(set(diversas))
    assert simular_fifo(diversas, frames) == distintas
    assert simular_opt(diversas, frames) == distintas
    assert simular_lru(diversas, frames) == distintas
    assert simular_lru_aprox(diversas, frames, considerar_ref=True) == distintas
    assert simular_lru_aprox(diversas, frames, considerar_ref=False) == distintas

    print("  -> Casos de borda passaram com sucesso!\n")


def testar_propriedade_otimo() -> None:
    """
    Garante formalmente que o algoritmo Ótimo (OPT) é sempre menor ou igual
    a todos os outros algoritmos em múltiplas sequências variadas (incluindo
    sequências com alta localidade temporal e espacial).
    """
    print("Testando propriedade de minimalidade do OPT:")
    rng = random.Random(42)

    for i in range(15):
        # Gera sequências aleatórias com localidade (concentração em working sets)
        tamanho = rng.randint(60, 250)
        universo = rng.randint(6, 20)
        
        # Simula localidade alternando blocos de páginas favoritas
        favoritas = [rng.randint(1, universo) for _ in range(3)]
        sequencia = []
        for _ in range(tamanho):
            if rng.random() < 0.7:
                sequencia.append(rng.choice(favoritas))
            else:
                sequencia.append(rng.randint(1, universo))
                
        frames = rng.randint(2, 8)
        intervalo = rng.randint(2, 15)

        prox = precalcular_proximo_uso(sequencia)
        opt = simular_opt(sequencia, frames, prox)
        fifo = simular_fifo(sequencia, frames)
        lru = simular_lru(sequencia, frames)
        lru_aprox_r = simular_lru_aprox(sequencia, frames, n_bits=8, intervalo=intervalo, considerar_ref=True)
        lru_aprox_puro = simular_lru_aprox(sequencia, frames, n_bits=8, intervalo=intervalo, considerar_ref=False)

        assert opt <= fifo, f"Caso {i}: OPT ({opt}) > FIFO ({fifo})"
        assert opt <= lru, f"Caso {i}: OPT ({opt}) > LRU ({lru})"
        assert opt <= lru_aprox_r, f"Caso {i}: OPT ({opt}) > LRU aprox com R ({lru_aprox_r})"
        assert opt <= lru_aprox_puro, f"Caso {i}: OPT ({opt}) > LRU aprox puro ({lru_aprox_puro})"

    print("  -> Propriedade OPT <= outros verificada em sequências aleatórias com localidade!\n")


def main() -> None:
    print("========================================")
    print("  Executando Suíte de Testes do Simulador")
    print("========================================\n")
    testar_cadeia_classica()
    testar_anomalia_belady()
    testar_casos_borda()
    testar_propriedade_otimo()
    print("========================================")
    print("  TODOS OS TESTES PASSARAM COM SUCESSO! ")
    print("========================================")


if __name__ == "__main__":
    main()
