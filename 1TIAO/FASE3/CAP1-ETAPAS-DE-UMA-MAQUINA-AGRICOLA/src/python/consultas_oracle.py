"""
consultas_oracle.py - Parte 2: execucao das consultas de gestao agricola.

Executa as 6 consultas definidas em src/sql/consultas_gestao.sql (uma para cada
informacao relevante listada no README) e grava os resultados consolidados em:
  - docs/evidencias/evidencia_consultas_gestao.txt
  - docs/evidencias/consulta_01_agua_por_mes.csv
  - docs/evidencias/consulta_02_variacao_ph.csv
  - docs/evidencias/consulta_03_top_dias_irrigacao.csv
  - docs/evidencias/consulta_04_nutrientes_e_acoes.csv
  - docs/evidencias/consulta_05_consumo_insumos_culturas.csv
  - docs/evidencias/consulta_06_avaliacoes_fase2.csv

Se ORACLE_PASSWORD estiver definida no ambiente, as consultas rodam diretamente
no servidor Oracle da FIAP (oracle.fiap.com.br:1521/ORCL). Caso contrario,
rodam sobre o banco espelho local populado por carga_oracle.py, usando uma
funcao auxiliar TO_CHAR para manter compatibilidade com o dialeto SQL.

Execucao:
    python src/python/consultas_oracle.py
"""

import os
import sqlite3

import oracledb
import pandas as pd

import config
from carga_oracle import DSN_PADRAO, USUARIO_PADRAO

CONSULTAS = [
    (
        "consulta_01_agua_por_mes",
        "INFO 1 - Quantidade total de agua aplicada e acionamentos da bomba em cada mes",
        """
        SELECT
            TO_CHAR(DATA_HORA_INICIO, 'YYYY-MM')         AS ANO_MES,
            COUNT(*)                                     AS QTD_ACIONAMENTOS,
            SUM(DURACAO_HORAS)                           AS TOTAL_HORAS_BOMBA,
            ROUND(AVG(DURACAO_HORAS), 2)                 AS DURACAO_MEDIA_H,
            SUM(VOLUME_AGUA_LITROS)                      AS AGUA_APLICADA_LITROS,
            ROUND(SUM(VOLUME_AGUA_M3), 2)                AS AGUA_APLICADA_M3,
            SUM(TEVE_FERTIRRIGACAO)                      AS CICLOS_FERTIRRIGACAO
        FROM FT3_ACIONAMENTO_BOMBA
        GROUP BY TO_CHAR(DATA_HORA_INICIO, 'YYYY-MM')
        ORDER BY ANO_MES
        """,
    ),
    (
        "consulta_02_variacao_ph",
        "INFO 2 - Variacao mensal do nivel de pH do solo e horas sob alerta de acidez",
        """
        SELECT
            TO_CHAR(DATA_HORA, 'YYYY-MM')                AS ANO_MES,
            COUNT(*)                                     AS TOTAL_LEITURAS,
            ROUND(MIN(PH_SUAVIZADO), 2)                  AS PH_MINIMO,
            ROUND(AVG(PH_SUAVIZADO), 2)                  AS PH_MEDIO,
            ROUND(MAX(PH_SUAVIZADO), 2)                  AS PH_MAXIMO,
            SUM(CASE WHEN PH_SUAVIZADO < 6.0 OR PH_SUAVIZADO > 7.0 THEN 1 ELSE 0 END) AS HORAS_ALERTA_PH
        FROM FT3_LEITURA_SENSOR
        GROUP BY TO_CHAR(DATA_HORA, 'YYYY-MM')
        ORDER BY ANO_MES
        """,
    ),
    (
        "consulta_03_top_dias_irrigacao",
        "INFO 3 - Top 10 dias com maior tempo de bomba ligada e maior consumo de agua",
        """
        SELECT * FROM (
            SELECT
                TO_CHAR(DATA_HORA, 'YYYY-MM-DD')         AS DATA_DIA,
                SUM(ESTADO_BOMBA)                        AS HORAS_BOMBA_LIGADA,
                SUM(ESTADO_BOMBA) * 5000                 AS AGUA_APLICADA_LITROS,
                ROUND(MIN(UMIDADE_TRATADA), 2)           AS UMIDADE_MIN_DIA,
                ROUND(AVG(UMIDADE_TRATADA), 2)           AS UMIDADE_MEDIA_DIA,
                ROUND(AVG(PH_SUAVIZADO), 2)              AS PH_MEDIO_DIA
            FROM FT3_LEITURA_SENSOR
            GROUP BY TO_CHAR(DATA_HORA, 'YYYY-MM-DD')
            HAVING SUM(ESTADO_BOMBA) > 0
            ORDER BY HORAS_BOMBA_LIGADA DESC, UMIDADE_MIN_DIA ASC
        ) WHERE ROWNUM <= 10
        """,
    ),
    (
        "consulta_04_nutrientes_e_acoes",
        "INFO 4 - Relacao entre disponibilidade de nutrientes (P, K, N) e acoes do sistema",
        """
        SELECT
            ACAO_SISTEMA,
            COUNT(*)                                     AS HORAS_REGISTRADAS,
            ROUND(AVG(UMIDADE_TRATADA), 2)               AS UMIDADE_MEDIA,
            ROUND(AVG(PH_SUAVIZADO), 2)                  AS PH_MEDIO,
            SUM(CASE WHEN FOSFORO_OK = 0 THEN 1 ELSE 0 END)    AS HORAS_DEFICIT_P,
            SUM(CASE WHEN POTASSIO_OK = 0 THEN 1 ELSE 0 END)   AS HORAS_DEFICIT_K,
            SUM(CASE WHEN NITROGENIO_OK = 0 THEN 1 ELSE 0 END) AS HORAS_DEFICIT_N
        FROM FT3_LEITURA_SENSOR
        GROUP BY ACAO_SISTEMA
        ORDER BY HORAS_REGISTRADAS DESC
        """,
    ),
    (
        "consulta_05_consumo_insumos_culturas",
        "INFO 5 - Culturas com maior consumo de insumos e dose media por hectare (Fases 1 e 2)",
        """
        SELECT
            CULTURA,
            INSUMO,
            UNIDADE_INSUMO,
            COUNT(*)                                     AS QTD_TALHOES,
            ROUND(SUM(AREA_HA), 2)                       AS AREA_TOTAL_HA,
            ROUND(SUM(QTD_INSUMO), 2)                    AS CONSUMO_TOTAL_INSUMO,
            ROUND(SUM(QTD_INSUMO) / SUM(AREA_HA), 2)     AS DOSE_MEDIA_POR_HA
        FROM FT3_MANEJO_CULTURA
        GROUP BY CULTURA, INSUMO, UNIDADE_INSUMO
        ORDER BY CONSUMO_TOTAL_INSUMO DESC
        """,
    ),
    (
        "consulta_06_avaliacoes_fase2",
        "INFO 6 - Monitoramento dos talhoes e avaliacoes de perda na colheita (Fase 2)",
        """
        SELECT
            A.COD_AVALIACAO,
            A.CODIGO_TALHAO,
            M.FAZENDA,
            M.VARIEDADE,
            TO_CHAR(A.DATA_AVALIACAO, 'YYYY-MM-DD')      AS DATA_AVALIACAO,
            A.COLHEDORA,
            A.OPERADOR,
            A.PERDA_T_HA,
            A.PERDA_PCT,
            A.PREJUIZO_RS,
            A.CLASSIFICACAO
        FROM FT3_AVALIACAO_FASE2 A
        LEFT JOIN FT3_MANEJO_CULTURA M
            ON A.CODIGO_TALHAO = M.CODIGO_TALHAO
        ORDER BY A.DATA_AVALIACAO DESC
        """,
    ),
]


def _to_char_sqlite(valor, formato):
    """Emula TO_CHAR(timestamp, 'YYYY-MM' | 'YYYY-MM-DD') no espelho SQLite."""
    if valor is None:
        return None
    texto = str(valor)
    if formato == "YYYY-MM":
        return texto[:7]
    if formato == "YYYY-MM-DD":
        return texto[:10]
    return texto


def abrir_conexao():
    """Abre conexao Oracle se ORACLE_PASSWORD estiver definida; senao usa o espelho."""
    usuario = os.environ.get("ORACLE_USER", USUARIO_PADRAO)
    dsn = os.environ.get("ORACLE_DSN", DSN_PADRAO)
    senha = os.environ.get("ORACLE_PASSWORD", "")
    if senha:
        try:
            conn = oracledb.connect(user=usuario, password=senha, dsn=dsn)
            return conn, "ORACLE"
        except Exception as exc:
            print(f"Aviso: falha ao conectar no Oracle ({exc}); usando espelho local.")
    arq_sqlite = config.DIR_PROCESSED / "farmtech_fase3_local.db"
    conn = sqlite3.connect(arq_sqlite)
    conn.create_function("TO_CHAR", 2, _to_char_sqlite)
    return conn, "SQLITE"


def executar_consulta(conn, dialeto, sql):
    """Adapta clausula ROWNUM para LIMIT quando executado no espelho SQLite."""
    sql_exec = sql
    if dialeto == "SQLITE" and "WHERE ROWNUM <= 10" in sql_exec:
        sql_exec = sql_exec.replace("WHERE ROWNUM <= 10", "LIMIT 10")
    cur = conn.cursor()
    cur.execute(sql_exec)
    colunas = [d[0] for d in cur.description]
    linhas = cur.fetchall()
    cur.close()
    return pd.DataFrame(linhas, columns=colunas)


def main():
    config.DIR_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    conn, dialeto = abrir_conexao()
    blocos = [
        "==============================================================================",
        "EVIDENCIA DAS CONSULTAS DE GESTAO AGRICOLA - FARMTECH SOLUTIONS (FASE 3)",
        "==============================================================================",
        f"Motor SQL utilizado na execucao: {dialeto}",
        "",
    ]

    for codigo_arq, titulo, sql in CONSULTAS:
        df_res = executar_consulta(conn, dialeto, sql)
        caminho_csv = config.DIR_EVIDENCIAS / f"{codigo_arq}.csv"
        df_res.to_csv(caminho_csv, index=False)

        blocos.append("------------------------------------------------------------------------------")
        blocos.append(titulo)
        blocos.append("------------------------------------------------------------------------------")
        blocos.append(df_res.to_string(index=False))
        blocos.append(f"[Arquivo exportado: docs/evidencias/{caminho_csv.name}]")
        blocos.append("")

    conn.close()
    texto = "\n".join(blocos)
    arq_evidencia = config.DIR_EVIDENCIAS / "evidencia_consultas_gestao.txt"
    arq_evidencia.write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()

