-- ============================================================================
-- PROJETO FASE 3 - ETAPAS DE UMA MAQUINA AGRICOLA (FARMTECH SOLUTIONS)
-- Script de Consultas de Gestao Agricola (Parte 2)
-- Cada consulta responde a uma das 6 informacoes relevantes de gestao
-- ============================================================================

-- CONSULTA 1: Quantidade total de agua aplicada, numero de acionamentos e
-- duracao media de irrigacao em cada mes (Info Relevante 1).
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
ORDER BY ANO_MES;

-- CONSULTA 2: Variacao mensal do pH do solo (minimo, medio, maximo) e horas
-- fora da faixa ideal de 6.0 a 7.0 para planejamento de calagem (Info Relevante 2).
SELECT
    TO_CHAR(DATA_HORA, 'YYYY-MM')                AS ANO_MES,
    COUNT(*)                                     AS TOTAL_LEITURAS,
    ROUND(MIN(PH_SUAVIZADO), 2)                  AS PH_MINIMO,
    ROUND(AVG(PH_SUAVIZADO), 2)                  AS PH_MEDIO,
    ROUND(MAX(PH_SUAVIZADO), 2)                  AS PH_MAXIMO,
    SUM(CASE WHEN PH_SUAVIZADO < 6.0 OR PH_SUAVIZADO > 7.0 THEN 1 ELSE 0 END) AS HORAS_ALERTA_PH
FROM FT3_LEITURA_SENSOR
GROUP BY TO_CHAR(DATA_HORA, 'YYYY-MM')
ORDER BY ANO_MES;

-- CONSULTA 3: Top 10 dias com maior tempo de bomba ligada e maior volume de
-- agua aplicado na lavoura (Info Relevante 3).
SELECT
    TO_CHAR(DATA_HORA, 'YYYY-MM-DD')             AS DATA_DIA,
    SUM(ESTADO_BOMBA)                            AS HORAS_BOMBA_LIGADA,
    SUM(ESTADO_BOMBA) * 5000                     AS AGUA_APLICADA_LITROS,
    ROUND(MIN(UMIDADE_TRATADA), 2)               AS UMIDADE_MIN_DIA,
    ROUND(AVG(UMIDADE_TRATADA), 2)               AS UMIDADE_MEDIA_DIA,
    ROUND(AVG(PH_SUAVIZADO), 2)                  AS PH_MEDIO_DIA
FROM FT3_LEITURA_SENSOR
GROUP BY TO_CHAR(DATA_HORA, 'YYYY-MM-DD')
HAVING SUM(ESTADO_BOMBA) > 0
ORDER BY HORAS_BOMBA_LIGADA DESC, UMIDADE_MIN_DIA ASC
FETCH FIRST 10 ROWS ONLY;

-- CONSULTA 4: Relacao entre deficit nutricional (P, K, N), previsao de chuva e
-- modalidades de acionamento do sistema (Info Relevante 4).
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
ORDER BY HORAS_REGISTRADAS DESC;

-- CONSULTA 5: Culturas com maior consumo de insumos, area total plantada e
-- dosagem media por hectare nas Fases 1 e 2 (Info Relevante 5).
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
ORDER BY CONSUMO_TOTAL_INSUMO DESC;

-- CONSULTA 6: Monitoramento consolidado dos talhoes e avaliacoes de perda na
-- colheita mecanizada integrados da Fase 2 (Info Relevante 6).
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
ORDER BY A.DATA_AVALIACAO DESC;

