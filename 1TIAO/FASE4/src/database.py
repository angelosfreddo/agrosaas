#!/usr/bin/env python3
"""
Módulo de Banco de Dados — FarmTech Solutions (Fase 4).
Implementa o esquema relacional definitivo da fazenda conectando culturas, talhões,
sensores, leituras históricas (Fase 3), acionamentos de irrigação, ocorrências de campo
e previsões do modelo de Inteligência Artificial, com hashes SHA-256 de integridade.
"""

import os
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "farmtech_fase4.db")

def calcular_hash_ocorrencia(data_hora, talhao, tipo, gravidade, observacao, operador, salt="farmtech_secret"):
    """
    Gera um hash SHA-256 criptográfico para garantir a inviolabilidade e integridade
    do registro de ocorrência de campo (requisito de segurança cibernética).
    """
    raw_str = f"{data_hora}|{talhao}|{tipo}|{gravidade}|{observacao}|{operador}|{salt}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_banco():
    """
    Cria a estrutura de tabelas do Modelo Entidade-Relacionamento (MER) definitivo da Fase 4.
    """
    conn = get_connection()
    cur = conn.cursor()

    # 1. Tabela de Culturas
    cur.execute("""
    CREATE TABLE IF NOT EXISTS FT4_CULTURA (
        ID_CULTURA INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME_CULTURA VARCHAR(50) NOT NULL UNIQUE,
        VARIEDADE VARCHAR(50) NOT NULL,
        CICLO_DIAS INTEGER NOT NULL,
        UMIDADE_MINIMA_PCT REAL NOT NULL,
        UMIDADE_MAXIMA_PCT REAL NOT NULL,
        PH_IDEAL_MIN REAL NOT NULL,
        PH_IDEAL_MAX REAL NOT NULL
    );
    """)

    # 2. Tabela de Talhões da Fazenda
    cur.execute("""
    CREATE TABLE IF NOT EXISTS FT4_TALHAO (
        CODIGO_TALHAO VARCHAR(20) PRIMARY KEY,
        NOME_TALHAO VARCHAR(100) NOT NULL,
        AREA_HECTARES REAL NOT NULL,
        TIPO_SOLO VARCHAR(50) NOT NULL,
        ID_CULTURA INTEGER NOT NULL,
        STATUS_OPERACIONAL VARCHAR(30) DEFAULT 'EM_PRODUCAO',
        FOREIGN KEY (ID_CULTURA) REFERENCES FT4_CULTURA(ID_CULTURA)
    );
    """)

    # 3. Tabela de Sensores e Estações IoT (AICSS)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS FT4_SENSOR (
        CODIGO_SENSOR VARCHAR(30) PRIMARY KEY,
        CODIGO_TALHAO VARCHAR(20) NOT NULL,
        TIPO_SENSOR VARCHAR(50) NOT NULL,
        MODELO_HARDWARE VARCHAR(50) NOT NULL,
        DATA_INSTALACAO DATE NOT NULL,
        STATUS_ATIVO INTEGER DEFAULT 1,
        FOREIGN KEY (CODIGO_TALHAO) REFERENCES FT4_TALHAO(CODIGO_TALHAO)
    );
    """)

    # 4. Tabela de Leituras Históricas dos Sensores (Migrada e expandida da Fase 3)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS FT4_LEITURA_SENSOR (
        ID_LEITURA INTEGER PRIMARY KEY AUTOINCREMENT,
        DATA_HORA TIMESTAMP NOT NULL,
        CODIGO_TALHAO VARCHAR(20) NOT NULL,
        UMIDADE_SOLO REAL NOT NULL,
        PH_SOLO REAL NOT NULL,
        FOSFORO_OK INTEGER NOT NULL,
        POTASSIO_OK INTEGER NOT NULL,
        NITROGENIO_OK INTEGER NOT NULL,
        ESTADO_BOMBA INTEGER NOT NULL,
        PREVISAO_CHUVA INTEGER NOT NULL,
        ACAO_SISTEMA VARCHAR(30) NOT NULL,
        ORIGEM_DADO VARCHAR(30) DEFAULT 'ESP32_WOKWI',
        FOREIGN KEY (CODIGO_TALHAO) REFERENCES FT4_TALHAO(CODIGO_TALHAO)
    );
    """)

    # 5. Tabela de Histórico de Acionamentos da Bomba de Irrigação
    cur.execute("""
    CREATE TABLE IF NOT EXISTS FT4_ACIONAMENTO_IRRIGACAO (
        ID_ACIONAMENTO INTEGER PRIMARY KEY AUTOINCREMENT,
        DATA_HORA_INICIO TIMESTAMP NOT NULL,
        DATA_HORA_FIM TIMESTAMP,
        CODIGO_TALHAO VARCHAR(20) NOT NULL,
        DURACAO_MINUTOS INTEGER NOT NULL,
        VOLUME_LITROS REAL NOT NULL,
        MOTIVO_ACIONAMENTO VARCHAR(50) NOT NULL,
        FOREIGN KEY (CODIGO_TALHAO) REFERENCES FT4_TALHAO(CODIGO_TALHAO)
    );
    """)

    # 6. Tabela de Ocorrências de Campo (Parte 1: Cadastro de Ocorrências)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS FT4_OCORRENCIA_CAMPO (
        ID_OCORRENCIA INTEGER PRIMARY KEY AUTOINCREMENT,
        DATA_HORA TIMESTAMP NOT NULL,
        CODIGO_TALHAO VARCHAR(20) NOT NULL,
        TIPO_OCORRENCIA VARCHAR(50) NOT NULL,
        GRAVIDADE VARCHAR(20) NOT NULL,
        OBSERVACAO TEXT NOT NULL,
        OPERADOR VARCHAR(50) NOT NULL,
        HASH_INTEGRIDADE VARCHAR(64) NOT NULL,
        STATUS_TRATAMENTO VARCHAR(30) DEFAULT 'ABERTO',
        FOREIGN KEY (CODIGO_TALHAO) REFERENCES FT4_TALHAO(CODIGO_TALHAO)
    );
    """)

    # 7. Tabela de Previsões do Modelo de Inteligência Artificial
    cur.execute("""
    CREATE TABLE IF NOT EXISTS FT4_PREVISAO_MODELO (
        ID_PREVISAO INTEGER PRIMARY KEY AUTOINCREMENT,
        DATA_HORA TIMESTAMP NOT NULL,
        CODIGO_TALHAO VARCHAR(20) NOT NULL,
        UMIDADE_SOLO_ATUAL REAL NOT NULL,
        PH_ATUAL REAL NOT NULL,
        FOSFORO_OK INTEGER NOT NULL,
        POTASSIO_OK INTEGER NOT NULL,
        PREDICAO_IRRIGAR INTEGER NOT NULL,
        PROBABILIDADE_IRRIGAR REAL NOT NULL,
        CONDICAO_SOLO VARCHAR(30) NOT NULL,
        MODELO_VERSAO VARCHAR(50) NOT NULL,
        DECISAO_REGRA_FASE2 INTEGER NOT NULL,
        CONCORDANCIA_REGRA INTEGER NOT NULL,
        FOREIGN KEY (CODIGO_TALHAO) REFERENCES FT4_TALHAO(CODIGO_TALHAO)
    );
    """)

    # 8. Tabela de Logs de Auditoria Cibernética (Parte 2: Segurança)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS FT4_LOG_SEGURANCA (
        ID_LOG INTEGER PRIMARY KEY AUTOINCREMENT,
        DATA_HORA TIMESTAMP NOT NULL,
        EVENTO VARCHAR(50) NOT NULL,
        USUARIO VARCHAR(50) NOT NULL,
        IP_ORIGEM VARCHAR(45) NOT NULL,
        STATUS VARCHAR(20) NOT NULL,
        DETALHES TEXT,
        HASH_LOG VARCHAR(64) NOT NULL
    );
    """)

    conn.commit()
    conn.close()
    print("Banco de dados FT4 inicializado com sucesso.")

def migrar_dados_fase3():
    """
    Carrega as culturas, talhões, leituras e acionamentos da Fase 3 para a Fase 4,
    garantindo continuidade perfeita do ecossistema FarmTech.
    """
    caminho_fase3 = "/home/angelo/FIAP/fase3/agrosaas/1TIAO/FASE3/CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA/data/processed/farmtech_fase3_local.db"
    if not os.path.exists(caminho_fase3):
        print(f"Aviso: Base da Fase 3 nao encontrada em {caminho_fase3}. Inicializando registros padrao.")
        return

    conn_f3 = sqlite3.connect(caminho_fase3)
    conn_f4 = get_connection()
    cur_f4 = conn_f4.cursor()

    # 1. Inserir Culturas
    culturas = [
        ("Milho", "Híbrido K9500 VIP3", 130, 45.0, 75.0, 5.8, 6.8),
        ("Soja", "Intacta RR PRO", 115, 50.0, 80.0, 6.0, 7.0),
        ("Café", "Catuaí Vermelho IAC 144", 365, 55.0, 75.0, 5.5, 6.5)
    ]
    cur_f4.executemany("""
    INSERT OR IGNORE INTO FT4_CULTURA (NOME_CULTURA, VARIEDADE, CICLO_DIAS, UMIDADE_MINIMA_PCT, UMIDADE_MAXIMA_PCT, PH_IDEAL_MIN, PH_IDEAL_MAX)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, culturas)

    # 2. Inserir Talhões
    talhoes = [
        ("TALHAO_01", "Talhão Norte - Pivo 01", 45.0, "Latossolo Vermelho", 1, "EM_PRODUCAO"),
        ("TALHAO_02", "Talhão Leste - Encosta", 38.5, "Argissolo Vermelho-Amarelo", 2, "EM_PRODUCAO"),
        ("TALHAO_03", "Talhão Sul - Várzea", 52.0, "Neossolo Flúvico", 3, "EM_PRODUCAO")
    ]
    cur_f4.executemany("""
    INSERT OR IGNORE INTO FT4_TALHAO (CODIGO_TALHAO, NOME_TALHAO, AREA_HECTARES, TIPO_SOLO, ID_CULTURA, STATUS_OPERACIONAL)
    VALUES (?, ?, ?, ?, ?, ?);
    """, talhoes)

    # 3. Inserir Sensores
    sensores = [
        ("SNS-UMID-01", "TALHAO_01", "UMIDADE_CAPACITIVA", "DHT22/Capacitive v1.2", "2025-08-10", 1),
        ("SNS-NPK-01", "TALHAO_01", "NUTRIENTES_NPK", "LDR Optical Sensor Kit", "2025-08-10", 1),
        ("SNS-UMID-02", "TALHAO_02", "UMIDADE_CAPACITIVA", "DHT22/Capacitive v1.2", "2025-08-12", 1),
        ("SNS-UMID-03", "TALHAO_03", "UMIDADE_CAPACITIVA", "DHT22/Capacitive v1.2", "2025-08-15", 1)
    ]
    cur_f4.executemany("""
    INSERT OR IGNORE INTO FT4_SENSOR (CODIGO_SENSOR, CODIGO_TALHAO, TIPO_SENSOR, MODELO_HARDWARE, DATA_INSTALACAO, STATUS_ATIVO)
    VALUES (?, ?, ?, ?, ?, ?);
    """, sensores)

    # 4. Migrar Leituras da Fase 3
    df_leituras = pd.read_sql_query("SELECT * FROM FT3_LEITURA_SENSOR", conn_f3)
    # Se a tabela da Fase 4 estiver vazia, popula
    count_leituras = cur_f4.execute("SELECT count(*) FROM FT4_LEITURA_SENSOR;").fetchone()[0]
    if count_leituras == 0:
        print(f"Migrando {len(df_leituras)} leituras históricas da Fase 3 para a Fase 4...")
        registros_leituras = []
        for idx, row in df_leituras.iterrows():
            # Distribui entre os 3 talhões para enriquecer a visão do painel
            talhao_alocado = "TALHAO_01" if idx % 3 == 0 else ("TALHAO_02" if idx % 3 == 1 else "TALHAO_03")
            registros_leituras.append((
                row["DATA_HORA"],
                talhao_alocado,
                float(row["UMIDADE_TRATADA"]),
                float(row["PH_TRATADO"]),
                int(row["FOSFORO_OK"]),
                int(row["POTASSIO_OK"]),
                int(row["NITROGENIO_OK"]),
                int(row["ESTADO_BOMBA"]),
                int(row["PREVISAO_CHUVA"]),
                str(row["ACAO_SISTEMA"]),
                str(row.get("ORIGEM_REGISTRO", "FASE3_HISTORICO"))
            ))

        cur_f4.executemany("""
        INSERT INTO FT4_LEITURA_SENSOR (
            DATA_HORA, CODIGO_TALHAO, UMIDADE_SOLO, PH_SOLO, FOSFORO_OK, POTASSIO_OK, NITROGENIO_OK,
            ESTADO_BOMBA, PREVISAO_CHUVA, ACAO_SISTEMA, ORIGEM_DADO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, registros_leituras)

    # 5. Migrar Acionamentos da Bomba
    count_bomba = cur_f4.execute("SELECT count(*) FROM FT4_ACIONAMENTO_IRRIGACAO;").fetchone()[0]
    if count_bomba == 0:
        df_bomba = pd.read_sql_query("SELECT * FROM FT3_ACIONAMENTO_BOMBA", conn_f3)
        registros_bomba = []
        for idx, row in df_bomba.iterrows():
            talhao_alocado = "TALHAO_01" if idx % 2 == 0 else "TALHAO_02"
            dur_min = int(float(row["DURACAO_HORAS"]) * 60)
            vol_l = round(dur_min * 180.0, 1) # vazão média 180 L/min
            registros_bomba.append((
                row["DATA_HORA_INICIO"],
                row["DATA_HORA_FIM"],
                talhao_alocado,
                dur_min,
                vol_l,
                "IRRIGACAO_AUTOMATICA_UMIDADE_BAIXA"
            ))
        cur_f4.executemany("""
        INSERT INTO FT4_ACIONAMENTO_IRRIGACAO (
            DATA_HORA_INICIO, DATA_HORA_FIM, CODIGO_TALHAO, DURACAO_MINUTOS, VOLUME_LITROS, MOTIVO_ACIONAMENTO
        ) VALUES (?, ?, ?, ?, ?, ?);
        """, registros_bomba)

    # 6. Inserir Ocorrências Iniciais de Campo
    count_ocorrencias = cur_f4.execute("SELECT count(*) FROM FT4_OCORRENCIA_CAMPO;").fetchone()[0]
    if count_ocorrencias == 0:
        ocorrencias_iniciais = [
            ("2026-01-15 08:30:00", "TALHAO_01", "PRAGA_LAGARTA_CARTUCHO", "MEDIA", "Identificada infestação leve nas folhas inferiores do milho", "Agrônomo Carlos"),
            ("2026-02-04 14:15:00", "TALHAO_02", "QUEIMADURA_GEADA", "ALTA", "Pontas das folhas com sinais evidentes de queima por geada matinal", "Técnico Lucas"),
            ("2026-02-20 10:00:00", "TALHAO_03", "FUNGOS_FERRUGEM", "CRITICA", "Manchas alaranjadas típicas de ferrugem em 12% da área amostrada", "Eng. Mariana"),
            ("2026-03-02 16:45:00", "TALHAO_01", "EROSAO_SULCO", "BAIXA", "Pequeno sulco de escoamento superficial após chuva intensa", "Operador João")
        ]
        registros_ocorr = []
        for dt, talh, tipo, grav, obs, op in ocorrencias_iniciais:
            h = calcular_hash_ocorrencia(dt, talh, tipo, grav, obs, op)
            registros_ocorr.append((dt, talh, tipo, grav, obs, op, h, "ABERTO"))

        cur_f4.executemany("""
        INSERT INTO FT4_OCORRENCIA_CAMPO (
            DATA_HORA, CODIGO_TALHAO, TIPO_OCORRENCIA, GRAVIDADE, OBSERVACAO, OPERADOR, HASH_INTEGRIDADE, STATUS_TRATAMENTO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, registros_ocorr)

    # 7. Inserir Log Inicial de Segurança
    count_logs = cur_f4.execute("SELECT count(*) FROM FT4_LOG_SEGURANCA;").fetchone()[0]
    if count_logs == 0:
        dt_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        h_log = hashlib.sha256(f"{dt_agora}|SISTEMA_INICIALIZADO|ADMIN|127.0.0.1".encode()).hexdigest()
        cur_f4.execute("""
        INSERT INTO FT4_LOG_SEGURANCA (DATA_HORA, EVENTO, USUARIO, IP_ORIGEM, STATUS, DETALHES, HASH_LOG)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (dt_agora, "SISTEMA_INICIALIZADO", "sistema", "127.0.0.1", "SUCESSO", "Inicializacao do banco FT4 com dados da Fase 3", h_log))

    conn_f4.commit()
    conn_f3.close()
    conn_f4.close()
    print("Migracao e populacao da Fase 4 concluidas com sucesso!")

def registrar_ocorrencia_campo(data_hora, codigo_talhao, tipo_ocorrencia, gravidade, observacao, operador):
    """
    Cadastra uma nova ocorrência com hash criptográfico SHA-256 de integridade.
    """
    hash_reg = calcular_hash_ocorrencia(data_hora, codigo_talhao, tipo_ocorrencia, gravidade, observacao, operador)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO FT4_OCORRENCIA_CAMPO (
        DATA_HORA, CODIGO_TALHAO, TIPO_OCORRENCIA, GRAVIDADE, OBSERVACAO, OPERADOR, HASH_INTEGRIDADE, STATUS_TRATAMENTO
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ABERTO');
    """, (data_hora, codigo_talhao, tipo_ocorrencia, gravidade, observacao, operador, hash_reg))
    novo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return novo_id, hash_reg

def verificar_integridade_ocorrencias():
    """
    Audita todos os registros da tabela de ocorrências recalculando o hash SHA-256.
    Identifica registros que foram adulterados indevidamente.
    """
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM FT4_OCORRENCIA_CAMPO", conn)
    conn.close()

    resultados = []
    for _, row in df.iterrows():
        hash_esperado = calcular_hash_ocorrencia(
            row["DATA_HORA"], row["CODIGO_TALHAO"], row["TIPO_OCORRENCIA"],
            row["GRAVIDADE"], row["OBSERVACAO"], row["OPERADOR"]
        )
        valido = (hash_esperado == row["HASH_INTEGRIDADE"])
        resultados.append({
            "ID_OCORRENCIA": row["ID_OCORRENCIA"],
            "TALHAO": row["CODIGO_TALHAO"],
            "TIPO": row["TIPO_OCORRENCIA"],
            "HASH_BANCO": row["HASH_INTEGRIDADE"][:12] + "...",
            "HASH_CALCULADO": hash_esperado[:12] + "...",
            "INTEGRIDADE_CONFIRMADA": valido
        })
    return pd.DataFrame(resultados)

if __name__ == "__main__":
    inicializar_banco()
    migrar_dados_fase3()

