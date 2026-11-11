"""
executar_pipeline.py - Executa todas as etapas da Fase 3 em sequencia.

Ordem de execucao:
  1. exportar_serial.py       -> Extrai dados do log do Monitor Serial Wokwi
  2. gerar_complemento.py     -> Complementa ate 4 meses marcando origem=SIMULADO
  3. tratamento_dados.py      -> Limpeza Pandas/NumPy, media movel e indicadores
  4. visualizacao.py          -> Gera os 4 graficos Matplotlib/Seaborn
  5. carga_oracle.py          -> Cria tabelas e executa carga repetivel (MERGE)
  6. consultas_oracle.py      -> Executa as 6 consultas de gestao agricola

Execucao:
    python src/python/executar_pipeline.py
"""

import exportar_serial
import gerar_complemento
import tratamento_dados
import visualizacao
import carga_oracle
import consultas_oracle


def main():
    print("\n>>> [1/6] Exportando leituras brutas do Monitor Serial Wokwi...")
    exportar_serial.main()

    print("\n>>> [2/6] Gerando complemento simulado documentado (4 meses)...")
    gerar_complemento.main()

    print("\n>>> [3/6] Executando tratamento Pandas/NumPy e indicadores de manejo...")
    tratamento_dados.main()

    print("\n>>> [4/6] Gerando visualizacoes com Matplotlib e Seaborn...")
    visualizacao.main()

    print("\n>>> [5/6] Executando carga repetivel no banco de dados...")
    carga_oracle.main()

    print("\n>>> [6/6] Executando consultas SQL de gestao da fazenda...")
    consultas_oracle.main()

    print("\nPipeline completo da Fase 3 executado com sucesso.")


if __name__ == "__main__":
    main()

