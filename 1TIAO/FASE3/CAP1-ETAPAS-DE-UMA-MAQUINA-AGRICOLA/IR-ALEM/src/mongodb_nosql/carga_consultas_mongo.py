"""
carga_consultas_mongo.py - Ir Alem 2: Leituras Brutas em Banco NoSQL (MongoDB).

Este script:
  1. Conecta ao MongoDB via PyMongo (usando a variavel de ambiente MONGODB_URI,
     ex.: MongoDB Atlas ou mongodb://localhost:27017; caso nenhum servidor
     esteja ativo na maquina no momento da execucao, utiliza um cliente PyMongo
     em memoria compativel via mongomock para validar todas as operacoes).
  2. Le o arquivo CSV BRUTO (data/raw/leituras_brutas.csv) e converte cada ciclo
     de leitura do ESP32 em um documento JSON/BSON na colecao
     farmtech_solutions.leituras_brutas_esp32, preservando integralmente os
     campos originais do Monitor Serial e adicionando atributos flexiveis de
     diagnostico quando a leitura bruta contem falha ("nan") ou valor fora da
     faixa fisica (schema-flexibility tipica de bancos orientados a documentos).
  3. Executa 5 consultas no estilo MongoDB (find com operadores $lt, $gte, $in
     e pipelines aggregate com $match, $group e $sort), respondendo a perguntas
     de gestao e de auditoria de sensores.
  4. Exporta um exemplo de documento JSON armazenado, uma amostra da colecao e
     o relatorio completo de evidencias das consultas.

Execucao:
    python IR-ALEM/src/mongodb_nosql/carga_consultas_mongo.py
"""

import csv
from datetime import datetime
import json
import os
from pathlib import Path

import mongomock
import pymongo

RAIZ_ATIVIDADE = Path(__file__).resolve().parents[3]
RAIZ_IR_ALEM = Path(__file__).resolve().parents[2]
ARQ_CSV_BRUTO = RAIZ_ATIVIDADE / "data" / "raw" / "leituras_brutas.csv"
ARQ_DOC_EXEMPLO = RAIZ_IR_ALEM / "data" / "exemplo_documento_mongodb.json"
ARQ_AMOSTRA_COLECAO = RAIZ_IR_ALEM / "data" / "amostra_colecao_mongodb.json"
ARQ_EVIDENCIA_MONGO = RAIZ_IR_ALEM / "docs" / "evidencia_consultas_mongodb.txt"

NOME_BANCO = "farmtech_solutions"
NOME_COLECAO = "leituras_brutas_esp32"


def conectar_mongodb():
    """Conecta ao MongoDB (Atlas/local) via PyMongo ou usa mongomock se offline."""
    uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    try:
        cliente = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2500)
        cliente.admin.command("ping")
        return cliente, f"CONECTADO AO MONGODB ({uri})"
    except Exception:
        cliente = mongomock.MongoClient()
        return cliente, "MODO VALIDACAO LOCAL (PyMongo/mongomock - defina MONGODB_URI para Atlas/servidor)"


def converter_linha_em_documento(indice, linha):
    """Transforma uma linha do CSV bruto em documento JSON preservando os campos."""
    umidade_txt = linha["umidade"].strip()
    ph_txt = linha["ph"].strip()

    try:
        umidade_num = None if umidade_txt.lower() == "nan" else float(umidade_txt)
    except ValueError:
        umidade_num = None

    try:
        ph_num = None if ph_txt.lower() == "nan" else float(ph_txt)
    except ValueError:
        ph_num = None

    doc = {
        "_id": f"ciclo_{indice:05d}_{linha['data_hora'].replace(' ', 'T')}",
        "ordem_coleta": indice,
        "data_hora": linha["data_hora"],
        "ano_mes": linha["data_hora"][:7],
        "umidade_raw": umidade_txt,
        "umidade": umidade_num,
        "ph_raw": ph_txt,
        "ph": ph_num,
        "fosforo": int(linha["fosforo"]),
        "potassio": int(linha["potassio"]),
        "nitrogenio": int(linha["nitrogenio"]),
        "bomba": int(linha["bomba"]),
        "chuva": int(linha["chuva"]),
        "acao": linha["acao"],
        "origem": linha["origem"],
        "sensores": {
            "S1_umidade_pct": umidade_num,
            "S2_ph_ldr": ph_num,
            "S3_nutrientes": {
                "P": int(linha["fosforo"]),
                "K": int(linha["potassio"]),
                "N": int(linha["nitrogenio"]),
            },
        },
    }

    # Flexibilidade de esquema (NoSQL): documentos com falha ou anomalia ganham
    # um subdocumento extra de diagnostico sem exigir ALTER TABLE.
    anomalias = []
    if umidade_num is None:
        anomalias.append("DHT22_NAN_TIMEOUT")
    elif not (0.0 <= umidade_num <= 100.0):
        anomalias.append("UMIDADE_FORA_FAIXA_0_100")
    if ph_num is None or not (0.0 <= ph_num <= 14.0):
        anomalias.append("PH_FORA_FAIXA_0_14")
    if anomalias:
        doc["diagnostico_bruto"] = {
            "leitura_integra": False,
            "anomalias_detectadas": anomalias,
        }
    return doc


def carregar_csv_bruto(colecao):
    """Carrega todas as linhas do CSV bruto no MongoDB sem duplicar (_id unico)."""
    colecao.drop()
    documentos = []
    with open(ARQ_CSV_BRUTO, encoding="utf-8") as arq:
        leitor = csv.DictReader(arq)
        for idx, linha in enumerate(leitor, start=1):
            documentos.append(converter_linha_em_documento(idx, linha))

    if documentos:
        colecao.insert_many(documentos, ordered=False)
    colecao.create_index([("data_hora", pymongo.ASCENDING)])
    colecao.create_index([("bomba", pymongo.ASCENDING), ("acao", pymongo.ASCENDING)])
    colecao.create_index([("umidade", pymongo.ASCENDING)])
    return documentos


def executar_consultas(colecao):
    """Executa 5 consultas NoSQL sobre a colecao de leituras brutas."""
    resultados = {}

    # Consulta 1: Filtrar leituras por faixa critica de umidade (< 40%) e bomba ligada
    filtro_1 = {"umidade": {"$gte": 0.0, "$lt": 40.0}, "bomba": 1}
    projecao_1 = {"_id": 0, "data_hora": 1, "umidade": 1, "ph": 1, "fosforo": 1, "potassio": 1, "acao": 1}
    resultados["q1_total"] = colecao.count_documents(filtro_1)
    resultados["q1_amostra"] = list(colecao.find(filtro_1, projecao_1).sort("umidade", 1).limit(8))

    # Consulta 2: Filtrar leituras por estado da bomba ligada em modo FERTIRRIGACAO
    filtro_2 = {"bomba": 1, "acao": "FERTIRRIGACAO"}
    resultados["q2_total"] = colecao.count_documents(filtro_2)
    resultados["q2_amostra"] = list(
        colecao.find(
            filtro_2,
            {"_id": 0, "data_hora": 1, "umidade": 1, "ph": 1, "sensores.S3_nutrientes": 1, "acao": 1},
        ).limit(8)
    )

    # Consulta 3: Filtrar documentos brutos com subdocumento diagnostico_bruto (anomalias/nan)
    filtro_3 = {"diagnostico_bruto.leitura_integra": False}
    resultados["q3_total"] = colecao.count_documents(filtro_3)
    resultados["q3_amostra"] = list(
        colecao.find(
            filtro_3,
            {"_id": 0, "data_hora": 1, "umidade_raw": 1, "ph_raw": 1, "acao": 1, "diagnostico_bruto": 1},
        ).limit(8)
    )

    # Consulta 4: Pipeline de agregacao por acao do sistema (contagem e umidade media)
    pipeline_4 = [
        {"$match": {"umidade": {"$gte": 0.0, "$lte": 100.0}}},
        {
            "$group": {
                "_id": "$acao",
                "total_ciclos": {"$sum": 1},
                "horas_bomba_ligada": {"$sum": "$bomba"},
                "umidade_media": {"$avg": "$umidade"},
                "ph_medio": {"$avg": "$ph"},
            }
        },
        {"$sort": {"total_ciclos": -1}},
    ]
    resultados["q4_agregacao_acao"] = list(colecao.aggregate(pipeline_4))

    # Consulta 5: Pipeline de agregacao mensal (horas de bomba ligada e deficit de P/K)
    pipeline_5 = [
        {
            "$group": {
                "_id": "$ano_mes",
                "leituras_brutas": {"$sum": 1},
                "horas_bomba_ligada": {"$sum": "$bomba"},
                "horas_chuva": {"$sum": "$chuva"},
                "ciclos_p_baixo": {"$sum": {"$cond": [{"$eq": ["$fosforo", 0]}, 1, 0]}},
                "ciclos_k_baixo": {"$sum": {"$cond": [{"$eq": ["$potassio", 0]}, 1, 0]}},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    resultados["q5_agregacao_mensal"] = list(colecao.aggregate(pipeline_5))

    return resultados


def main():
    ARQ_DOC_EXEMPLO.parent.mkdir(parents=True, exist_ok=True)
    ARQ_EVIDENCIA_MONGO.parent.mkdir(parents=True, exist_ok=True)

    cliente, status_conexao = conectar_mongodb()
    db = cliente[NOME_BANCO]
    colecao = db[NOME_COLECAO]

    documentos = carregar_csv_bruto(colecao)
    resultados = executar_consultas(colecao)

    # Salva um documento tipico e um documento com anomalia para demonstrar o schema flexivel
    doc_normal = next(d for d in documentos if d["acao"] == "FERTIRRIGACAO")
    doc_anomalo = next(d for d in documentos if "diagnostico_bruto" in d)
    ARQ_DOC_EXEMPLO.write_text(
        json.dumps({"documento_padrao_fertirrigacao": doc_normal, "documento_com_anomalia_bruta": doc_anomalo}, indent=2),
        encoding="utf-8",
    )
    ARQ_AMOSTRA_COLECAO.write_text(
        json.dumps(documentos[:25], indent=2),
        encoding="utf-8",
    )

    linhas = [
        "==============================================================================",
        "IR ALEM 2 - EVIDENCIA DE CARGA E CONSULTAS NO MONGODB (FARMTECH SOLUTIONS)",
        "==============================================================================",
        f"Data/Hora da execucao : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Banco / Colecao       : {NOME_BANCO}.{NOME_COLECAO}",
        f"Status da conexao     : {status_conexao}",
        f"Total de documentos   : {colecao.count_documents({})}",
        "",
        "------------------------------------------------------------------------------",
        f"CONSULTA 1 - Leituras com umidade critica (< 40%) e bomba ligada (Total: {resultados['q1_total']})",
        "Filtro PyMongo: {'umidade': {'$gte': 0.0, '$lt': 40.0}, 'bomba': 1}",
        "------------------------------------------------------------------------------",
        json.dumps(resultados["q1_amostra"], indent=2),
        "",
        "------------------------------------------------------------------------------",
        f"CONSULTA 2 - Leituras por estado de bomba em FERTIRRIGACAO (Total: {resultados['q2_total']})",
        "Filtro PyMongo: {'bomba': 1, 'acao': 'FERTIRRIGACAO'}",
        "------------------------------------------------------------------------------",
        json.dumps(resultados["q2_amostra"], indent=2),
        "",
        "------------------------------------------------------------------------------",
        f"CONSULTA 3 - Leituras brutas incompletas/anomalas com subdocumento (Total: {resultados['q3_total']})",
        "Filtro PyMongo: {'diagnostico_bruto.leitura_integra': False}",
        "------------------------------------------------------------------------------",
        json.dumps(resultados["q3_amostra"], indent=2),
        "",
        "------------------------------------------------------------------------------",
        "CONSULTA 4 - Agregacao NoSQL ($group) por acao decidida pelo firmware",
        "------------------------------------------------------------------------------",
        json.dumps(resultados["q4_agregacao_acao"], indent=2),
        "",
        "------------------------------------------------------------------------------",
        "CONSULTA 5 - Agregacao NoSQL ($group) mensal de uso da bomba e deficit P/K",
        "------------------------------------------------------------------------------",
        json.dumps(resultados["q5_agregacao_mensal"], indent=2),
        "",
    ]
    texto = "\n".join(linhas)
    ARQ_EVIDENCIA_MONGO.write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()

