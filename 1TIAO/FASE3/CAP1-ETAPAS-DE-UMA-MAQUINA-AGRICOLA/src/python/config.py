"""
config.py - Parametros centrais do projeto FarmTech Solutions (Fase 3).

Todos os scripts importam este modulo para usar os mesmos caminhos de arquivos,
as mesmas faixas fisicas dos sensores e as mesmas premissas de manejo
(vazao da bomba, limites agronomicos). Assim, uma mudanca de premissa e feita
em um unico lugar.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos (relativos a pasta da atividade, independente de onde o script roda)
# ---------------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parents[2]          # .../CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA
DIR_DATA = RAIZ / "data"
DIR_RAW = DIR_DATA / "raw"
DIR_PROCESSED = DIR_DATA / "processed"
DIR_FASES = DIR_DATA / "fases_anteriores"
DIR_DOCS = RAIZ / "docs"
DIR_GRAFICOS = DIR_DOCS / "graficos"
DIR_EVIDENCIAS = DIR_DOCS / "evidencias"
DIR_SQL = RAIZ / "src" / "sql"

# Log copiado do Monitor Serial do Wokwi (texto puro, como foi colado)
ARQ_MONITOR_SERIAL = DIR_RAW / "monitor_serial_wokwi.txt"
# CSV com SOMENTE as linhas exportadas do Wokwi
ARQ_BRUTO_WOKWI = DIR_RAW / "leituras_brutas_wokwi.csv"
# CSV bruto completo (Wokwi + complemento simulado marcado na coluna "origem")
ARQ_BRUTO = DIR_RAW / "leituras_brutas.csv"

# Saidas do tratamento
ARQ_TRATADO = DIR_PROCESSED / "leituras_tratadas.csv"
ARQ_ACIONAMENTOS = DIR_PROCESSED / "acionamentos_bomba.csv"
ARQ_IND_DIARIO = DIR_PROCESSED / "indicadores_diarios.csv"
ARQ_IND_MENSAL = DIR_PROCESSED / "indicadores_mensais.csv"
ARQ_FAIXAS_UMIDADE = DIR_PROCESSED / "faixas_umidade.csv"
ARQ_CORRELACAO = DIR_PROCESSED / "matriz_correlacao.csv"
ARQ_RELATORIO_LIMPEZA = DIR_PROCESSED / "relatorio_limpeza.txt"

# Dados herdados das Fases 1 e 2
ARQ_FASE1_MANEJO = DIR_FASES / "fase1" / "dados_fazenda.csv"
ARQ_FASE2_BASE = DIR_FASES / "fase2" / "base_local.json"
ARQ_FASE2_COLETA = DIR_FASES / "fase2" / "coleta_campo_exemplo.json"
ARQ_FASE2_PARAMETROS = DIR_FASES / "fase2" / "parametros.json"
ARQ_FASE2_LOG = DIR_FASES / "fase2" / "log_operacoes.txt"

# ---------------------------------------------------------------------------
# Colunas do CSV impresso pelo firmware (src/iot_esp32/sketch.ino)
# ---------------------------------------------------------------------------
COLUNAS_SERIAL = ["data_hora", "umidade", "ph", "fosforo", "potassio",
                  "nitrogenio", "bomba", "chuva", "acao"]

# ---------------------------------------------------------------------------
# Faixas fisicas dos sensores (valores fora disso sao leituras invalidas)
# ---------------------------------------------------------------------------
FAIXA_UMIDADE = (0.0, 100.0)    # DHT22: 0 a 100 %
FAIXA_PH = (0.0, 14.0)          # escala de pH (LDR mapeado de 0-4095 para 0-14)
VALORES_BINARIOS = (0, 1)       # P, K, N, bomba e chuva

# ---------------------------------------------------------------------------
# Regras agronomicas do firmware (Milho - Embrapa)
# ---------------------------------------------------------------------------
UMIDADE_LIGA = 40.0             # abaixo disso a bomba liga
UMIDADE_DESLIGA = 60.0          # a partir disso a bomba desliga
PH_MIN_IDEAL = 6.0
PH_MAX_IDEAL = 7.0

# ---------------------------------------------------------------------------
# Premissas de manejo definidas pelo grupo
# ---------------------------------------------------------------------------
HORAS_POR_CICLO = 1.0           # relogio simulado: cada ciclo do loop = 1 hora
VAZAO_BOMBA_L_H = 5000.0        # vazao da bomba: 5.000 L/h (5 m3/h)
JANELA_MEDIA_MOVEL = 6          # media movel de 6 leituras (6 horas)
LIMITE_INTERPOLACAO = 3         # preenche no maximo 3 horas seguidas sem leitura

# Periodo minimo do historico (>= 3 meses, exigencia da atividade)
INICIO_HISTORICO = "2026-01-01 00:00"
FIM_HISTORICO = "2026-04-30 23:00"

# Cultura monitorada pelo circuito IoT
CULTURA_IOT = "Milho"

