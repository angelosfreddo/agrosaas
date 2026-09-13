#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FarmTech Solutions - Aplicação de Gestão de Agricultura Digital
Projeto FIAP - Fase 1

Este módulo implementa o gerenciamento de plantio e manejo de insumos
para 2 culturas agrícolas (Café e Milho), utilizando vetores de dados
e um menu CRUD interativo no terminal.
"""

import sys
import os

# ==============================================================================
# ESTRUTURA DE DADOS EM VETORES (LISTAS PARALELAS)
# ==============================================================================
vetor_ids = []           # ID identificador único do registro
vetor_culturas = []      # Nome da cultura ('Café' ou 'Milho')
vetor_areas_m2 = []      # Área calculada em metros quadrados (m²)
vetor_areas_ha = []      # Área convertida em hectares (ha)
vetor_insumos = []       # Nome do insumo (ex: 'Fosfato', 'Pulverização Fungicida')
vetor_qtd_insumo = []    # Quantidade calculada do insumo
vetor_unidades = []      # Unidade de medida do insumo ('Litros', 'Kg')


def limpar_tela():
    """Limpa o terminal para melhor navegabilidade."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    """Pausa a execução aguardando interação do usuário."""
    input("\nPressione ENTER para continuar...")


# ==============================================================================
# CÁLCULOS GEOMÉTRICOS E DE MANEJO DE INSUMOS
# ==============================================================================
def calcular_area_cafe():
    """
    Cálculo de Área para Café: Figura Retangular.
    Área = Comprimento x Largura
    """
    print("\n--- CÁLCULO DE ÁREA (CULTURA: CAFÉ - ÁREA RETANGULAR) ---")
    while True:
        try:
            comprimento = float(input("Digite o comprimento do terreno (em metros): "))
            largura = float(input("Digite a largura do terreno (em metros): "))
            if comprimento <= 0 or largura <= 0:
                print("⚠️ As dimensões devem ser maiores que zero.")
                continue
            area_m2 = comprimento * largura
            return area_m2, comprimento, largura
        except ValueError:
            print("⚠️ Entrada inválida! Digite um número válido.")


def calcular_area_milho():
    """
    Cálculo de Área para Milho: Figura Trapezoidal.
    Área = ((Base Maior + Base Menor) * Altura) / 2
    """
    print("\n--- CÁLCULO DE ÁREA (CULTURA: MILHO - ÁREA TRAPEZOIDAL) ---")
    while True:
        try:
            b_maior = float(input("Digite a Base Maior do terreno (em metros): "))
            b_menor = float(input("Digite a Base Menor do terreno (em metros): "))
            altura = float(input("Digite a Altura/Comprimento do terreno (em metros): "))
            if b_maior <= 0 or b_menor <= 0 or altura <= 0:
                print("⚠️ As dimensões devem ser maiores que zero.")
                continue
            area_m2 = ((b_maior + b_menor) * altura) / 2.0
            return area_m2
        except ValueError:
            print("⚠️ Entrada inválida! Digite um número válido.")


def calcular_manejo_cafe(area_m2, comprimento):
    """
    Cálculo de Manejo para Café: Pulverização de Defensivo por Ruas de Lavoura.
    Litros = (Dosagem mL/m * Metros por Rua * Qtd de Ruas) / 1000
    """
    print("\n--- CÁLCULO DE MANEJO DE INSUMOS (CAFÉ - PULVERIZAÇÃO) ---")
    insumo = "Pulverização Fungicida"
    unidade = "Litros"
    while True:
        try:
            dosagem_ml_m = float(input("Digite a dosagem de pulverização (em mL por metro): "))
            qtd_ruas = int(input("Digite a quantidade de ruas na lavoura de café: "))
            if dosagem_ml_m <= 0 or qtd_ruas <= 0:
                print("⚠️ Valores devem ser maiores que zero.")
                continue
            
            total_metros_ruas = comprimento * qtd_ruas
            total_litros = (dosagem_ml_m * total_metros_ruas) / 1000.0
            print(f"➜ Total de metros de ruas: {total_metros_ruas:.2f} m")
            print(f"➜ Quantidade total de defensivo necessária: {total_litros:.2f} Litros")
            return insumo, total_litros, unidade
        except ValueError:
            print("⚠️ Entrada inválida! Digite valores numéricos válidos.")


def calcular_manejo_milho(area_ha):
    """
    Cálculo de Manejo para Milho: Adubação (N-P-K / Fosfato) em Kg/ha.
    Total Kg = Dosagem em Kg/ha * Área em Hectares
    """
    print("\n--- CÁLCULO DE MANEJO DE INSUMOS (MILHO - ADUBAÇÃO FOSFATADA) ---")
    insumo = "Fosfato / Adubação NPK"
    unidade = "Kg"
    while True:
        try:
            dosagem_kg_ha = float(input("Digite a dosagem recomendada de adubo (em Kg por Hectare): "))
            if dosagem_kg_ha <= 0:
                print("⚠️ A dosagem deve ser maior que zero.")
                continue
            total_kg = dosagem_kg_ha * area_ha
            print(f"➜ Área total em hectares: {area_ha:.4f} ha")
            print(f"➜ Quantidade total de adubo necessária: {total_kg:.2f} Kg")
            return insumo, total_kg, unidade
        except ValueError:
            print("⚠️ Entrada inválida! Digite um número válido.")


# ==============================================================================
# MENU CRUD (OPÇÕES 1 A 5)
# ==============================================================================
def opcao_cadastrar_dados():
    """Opção 1: Entrada de dados nos vetores."""
    print("=" * 60)
    print("      ENTRADA DE DADOS - CADASTRAR NOVO MANEJO AGRÍCOLA")
    print("=" * 60)
    print("Escolha a cultura agrícola:")
    print("1. Café (Área Retangular + Manejo de Pulverização)")
    print("2. Milho (Área Trapezoidal + Manejo de Adubação Fosfatada)")
    
    opcao_cultura = input("Opção (1 ou 2): ").strip()
    
    if opcao_cultura == '1':
        cultura = "Café"
        area_m2, comprimento, largura = calcular_area_cafe()
        area_ha = area_m2 / 10000.0
        insumo, qtd_insumo, unidade = calcular_manejo_cafe(area_m2, comprimento)
        
    elif opcao_cultura == '2':
        cultura = "Milho"
        area_m2 = calcular_area_milho()
        area_ha = area_m2 / 10000.0
        insumo, qtd_insumo, unidade = calcular_manejo_milho(area_ha)
    else:
        print("❌ Opção de cultura inválida! Operação cancelada.")
        return

    # Inserção nos vetores
    novo_id = len(vetor_ids) + 1
    vetor_ids.append(novo_id)
    vetor_culturas.append(cultura)
    vetor_areas_m2.append(area_m2)
    vetor_areas_ha.append(area_ha)
    vetor_insumos.append(insumo)
    vetor_qtd_insumo.append(qtd_insumo)
    vetor_unidades.append(unidade)
    
    print("\n✅ Registro cadastrado com sucesso no vetor de dados!")
    print(f"   ID: {novo_id} | Cultura: {cultura} | Área: {area_ha:.4f} ha | Insumo: {qtd_insumo:.2f} {unidade}")


def opcao_listar_dados():
    """Opção 2: Saída de dados (Leitura do vetor no terminal)."""
    print("=" * 75)
    print("              SAÍDA DE DADOS - RELATÓRIO DE MANEJOS")
    print("=" * 75)
    
    if len(vetor_ids) == 0:
        print("ℹ️ Nenhum dado cadastrado nos vetores no momento.")
        return

    header = f"{'POS (Vetor)':<11} | {'ID':<4} | {'CULTURA':<8} | {'ÁREA (m²)':<12} | {'ÁREA (ha)':<10} | {'INSUMO':<22} | {'QTD NECESSÁRIA'}"
    print(header)
    print("-" * len(header))
    
    for i in range(len(vetor_ids)):
        posicao = i
        id_reg = vetor_ids[i]
        cultura = vetor_culturas[i]
        area_m2 = vetor_areas_m2[i]
        area_ha = vetor_areas_ha[i]
        insumo = vetor_insumos[i]
        qtd = vetor_qtd_insumo[i]
        unid = vetor_unidades[i]
        
        print(f"{posicao:<11} | {id_reg:<4} | {cultura:<8} | {area_m2:<12.2f} | {area_ha:<10.4f} | {insumo:<22} | {qtd:.2f} {unid}")
    print("-" * len(header))
    print(f"Total de registros armazenados no vetor: {len(vetor_ids)}")


def opcao_atualizar_dado():
    """Opção 3: Atualização de dados numa posição qualquer do vetor."""
    opcao_listar_dados()
    if len(vetor_ids) == 0:
        return
    
    print("\n--- ATUALIZAÇÃO DE REGISTRO EM POSIÇÃO DO VETOR ---")
    try:
        pos = int(input("Digite o índice da posição do vetor que deseja atualizar: "))
        if pos < 0 or pos >= len(vetor_ids):
            print("❌ Posição inválida! Índice fora dos limites do vetor.")
            return
        
        print(f"\nAtualizando registro da posição [{pos}] (Cultura atual: {vetor_culturas[pos]}):")
        print("Digite os novos dados para substituição:")
        
        nova_area_m2 = float(input("Nova área total (em m²): "))
        if nova_area_m2 <= 0:
            print("❌ Área deve ser positiva.")
            return
        
        nova_area_ha = nova_area_m2 / 10000.0
        nova_qtd_insumo = float(input(f"Nova quantidade de insumo ({vetor_unidades[pos]}): "))
        if nova_qtd_insumo <= 0:
            print("❌ Quantidade deve ser positiva.")
            return

        # Atualização direta na posição do vetor
        vetor_areas_m2[pos] = nova_area_m2
        vetor_areas_ha[pos] = nova_area_ha
        vetor_qtd_insumo[pos] = nova_qtd_insumo
        
        print(f"\n✅ Posição [{pos}] do vetor atualizada com sucesso!")
        
    except ValueError:
        print("❌ Entrada inválida! Digite um número inteiro para o índice.")


def opcao_deletar_dado():
    """Opção 4: Deleção de dados do vetor de dados."""
    opcao_listar_dados()
    if len(vetor_ids) == 0:
        return

    print("\n--- DELEÇÃO DE REGISTRO DO VETOR ---")
    try:
        pos = int(input("Digite o índice da posição do vetor que deseja deletar: "))
        if pos < 0 or pos >= len(vetor_ids):
            print("❌ Posição inválida! Índice fora dos limites do vetor.")
            return

        # Remoção do elemento na posição pos em todos os vetores paralelos
        id_removido = vetor_ids.pop(pos)
        cultura_removida = vetor_culturas.pop(pos)
        vetor_areas_m2.pop(pos)
        vetor_areas_ha.pop(pos)
        vetor_insumos.pop(pos)
        vetor_qtd_insumo.pop(pos)
        vetor_unidades.pop(pos)
        
        print(f"\n✅ Registro ID {id_removido} ({cultura_removida}) removido da posição [{pos}] do vetor!")

    except ValueError:
        print("❌ Entrada inválida! Digite um índice válido.")


def salvar_dados_csv():
    """Exporta os dados dos vetores para um arquivo CSV para leitura no R."""
    caminho_csv = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dados_fazenda.csv")
    os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)
    
    with open(caminho_csv, "w", encoding="utf-8") as f:
        f.write("id,cultura,area_m2,area_ha,insumo,qtd_insumo,unidade\n")
        for i in range(len(vetor_ids)):
            f.write(f"{vetor_ids[i]},{vetor_culturas[i]},{vetor_areas_m2[i]:.2f},{vetor_areas_ha[i]:.4f},{vetor_insumos[i]},{vetor_qtd_insumo[i]:.2f},{vetor_unidades[i]}\n")
    print(f"📊 Dados exportados para o R com sucesso em: {caminho_csv}")


def carregar_dados_iniciais_demo():
    """Popula os vetores com dados de demonstração iniciais caso estejam vazios."""
    if len(vetor_ids) > 0:
        return
    dados_demo = [
        (1, "Café", 25000.0, 2.5, "Pulverização Fungicida", 125.0, "Litros"),
        (2, "Milho", 45000.0, 4.5, "Fosfato / Adubação NPK", 1350.0, "Kg"),
        (3, "Café", 18000.0, 1.8, "Pulverização Fungicida", 90.0, "Litros"),
        (4, "Milho", 32000.0, 3.2, "Fosfato / Adubação NPK", 960.0, "Kg"),
        (5, "Café", 50000.0, 5.0, "Pulverização Fungicida", 250.0, "Litros"),
    ]
    for item in dados_demo:
        vetor_ids.append(item[0])
        vetor_culturas.append(item[1])
        vetor_areas_m2.append(item[2])
        vetor_areas_ha.append(item[3])
        vetor_insumos.append(item[4])
        vetor_qtd_insumo.append(item[5])
        vetor_unidades.append(item[6])


# ==============================================================================
# MENU PRINCIPAL DO SISTEMA
# ==============================================================================
def main():
    carregar_dados_iniciais_demo()
    salvar_dados_csv()

    while True:
        limpar_tela()
        print("==========================================================")
        print("           FARMTECH SOLUTIONS - AGRICULTURA DIGITAL       ")
        print("          SISTEMA DE GESTÃO DE PLANTIO E INSUMOS          ")
        print("==========================================================")
        print("1. Entrada de dados (Cadastrar nova cultura/manejo)")
        print("2. Saída de dados (Exibir vetor no terminal)")
        print("3. Atualização de dados numa posição do vetor")
        print("4. Deleção de dados de uma posição do vetor")
        print("5. Sair do programa")
        print("==========================================================")
        
        opcao = input("Digite o número da opção desejada (1-5): ").strip()
        
        if opcao == '1':
            limpar_tela()
            opcao_cadastrar_dados()
            salvar_dados_csv()
            pausar()
        elif opcao == '2':
            limpar_tela()
            opcao_listar_dados()
            pausar()
        elif opcao == '3':
            limpar_tela()
            opcao_atualizar_dado()
            salvar_dados_csv()
            pausar()
        elif opcao == '4':
            limpar_tela()
            opcao_deletar_dado()
            salvar_dados_csv()
            pausar()
        elif opcao == '5':
            limpar_tela()
            salvar_dados_csv()
            print("\n👋 Encerrando a aplicação FarmTech Solutions... Dados salvos com sucesso!")
            print("Obrigado por utilizar nosso sistema.")
            sys.exit(0)
        else:
            print("❌ Opção inválida! Escolha uma opção de 1 a 5.")
            pausar()


# Garante preenchimento e exportação inicial
carregar_dados_iniciais_demo()
salvar_dados_csv()

if __name__ == "__main__":
    main()
