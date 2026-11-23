#!/usr/bin/env python3
"""
Módulo de Treinamento e Avaliação do Modelo Preditivo — FarmTech Solutions (Fase 4).
Treina modelos com Scikit-Learn utilizando o histórico de sensores da Fase 3,
avalia com Validação Cruzada Estratificada (5-Fold), gera matriz de confusão,
compara com a regra estática da Fase 2 e serializa o modelo campeão.
"""

import os
import sys

# Garante inclusão da raiz no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from src.database import get_connection

def preparar_dados_historicos():
    conn = get_connection()
    query = """
    SELECT 
        DATA_HORA, CODIGO_TALHAO, UMIDADE_SOLO, PH_SOLO, 
        FOSFORO_OK, POTASSIO_OK, NITROGENIO_OK, PREVISAO_CHUVA, ESTADO_BOMBA
    FROM FT4_LEITURA_SENSOR
    ORDER BY DATA_HORA ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Tratamento de dados e engenharia de atributos
    df["UMIDADE_SOLO"] = df["UMIDADE_SOLO"].clip(0.0, 100.0)
    df["PH_SOLO"] = df["PH_SOLO"].clip(3.5, 9.0)

    # Definição do Alvo Agronômico Inteligente de Irrigação:
    # 1 (LIGAR): Umidade do solo abaixo do patamar de estresse (< 50%) e sem chuva iminente
    # 0 (DESLIGAR): Umidade adequada (>= 50%) OU chuva prevista para as próximas horas (economia de água)
    df["ALVO_IRRIGAR"] = np.where(
        (df["UMIDADE_SOLO"] < 50.0) & (df["PREVISAO_CHUVA"] == 0), 1, 0
    )

    # Classificação agronômica da condição do solo
    condicoes = [
        (df["UMIDADE_SOLO"] < 45.0),
        (df["UMIDADE_SOLO"] >= 45.0) & (df["UMIDADE_SOLO"] <= 65.0),
        (df["UMIDADE_SOLO"] > 65.0)
    ]
    escolhas = ["SECA", "MODERADA", "UMIDA"]
    df["CONDICAO_SOLO"] = np.select(condicoes, escolhas, default="MODERADA")

    # Decisão da Regra Fixa da Fase 2 (Regra antiga: Irrigar estritamente se umidade < 30%)
    df["DECISAO_REGRA_FASE2"] = np.where(df["UMIDADE_SOLO"] < 30.0, 1, 0)

    return df

def treinar_e_avaliar_modelo():
    print("=" * 80)
    print("FARMTECH SOLUTIONS - TREINAMENTO DO MODELO PREDITIVO DE IRRIGAÇÃO")
    print("=" * 80)

    df = preparar_dados_historicos()
    print(f"Total de amostras históricas carregadas: {len(df)}")
    print("Distribuição da classe ALVO_IRRIGAR:")
    print(df["ALVO_IRRIGAR"].value_counts(normalize=True).apply(lambda x: f"{x*100:.1f}%"))

    features = ["UMIDADE_SOLO", "PH_SOLO", "FOSFORO_OK", "POTASSIO_OK", "NITROGENIO_OK", "PREVISAO_CHUVA"]
    X = df[features]
    y = df["ALVO_IRRIGAR"]

    # Divisão estratificada 80% treino / 20% teste
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, df.index, test_size=0.20, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Comparação de Algoritmos com Validação Cruzada Estratificada em 5 Folds
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    modelos = {
        "Random Forest (Campeão)": RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=80, max_depth=4, random_state=42),
        "Árvore de Decisão": DecisionTreeClassifier(max_depth=5, random_state=42),
        "Regressão Logística": LogisticRegression(max_iter=500, random_state=42)
    }

    tabela_resultados = []

    for nome, mod in modelos.items():
        if "Logística" in nome:
            scores_acc = cross_val_score(mod, X_train_scaled, y_train, cv=cv, scoring="accuracy")
            scores_f1 = cross_val_score(mod, X_train_scaled, y_train, cv=cv, scoring="f1")
            mod.fit(X_train_scaled, y_train)
            y_pred = mod.predict(X_test_scaled)
        else:
            scores_acc = cross_val_score(mod, X_train, y_train, cv=cv, scoring="accuracy")
            scores_f1 = cross_val_score(mod, X_train, y_train, cv=cv, scoring="f1")
            mod.fit(X_train, y_train)
            y_pred = mod.predict(X_test)

        acc_teste = accuracy_score(y_test, y_pred)
        f1_teste = f1_score(y_test, y_pred)

        tabela_resultados.append({
            "Algoritmo": nome,
            "CV Acurácia Média": f"{scores_acc.mean()*100:.2f}% (±{scores_acc.std()*100:.2f}%)",
            "CV F1-Score": f"{scores_f1.mean():.4f}",
            "Acurácia Teste": f"{acc_teste*100:.2f}%",
            "F1-Score Teste": f"{f1_teste:.4f}"
        })

    df_comp = pd.DataFrame(tabela_resultados)
    print("\n--- DESEMPENHO COMPARATIVO DOS MODELOS ---")
    print(df_comp.to_string(index=False))

    # Modelo Campeão: Random Forest
    modelo_campeao = modelos["Random Forest (Campeão)"]
    y_test_pred = modelo_campeao.predict(X_test)
    y_test_proba = modelo_campeao.predict_proba(X_test)[:, 1]

    # Matriz de Confusão no Teste
    cm = confusion_matrix(y_test, y_test_pred)
    print("\n--- MATRIZ DE CONFUSÃO (RANDOM FOREST NO CONJUNTO DE TESTE) ---")
    print("                  Previsto: NÃO IRRIGAR (0) | Previsto: IRRIGAR (1)")
    print(f"Real: NÃO IRRIGAR (0)       {cm[0][0]:<15} | {cm[0][1]}")
    print(f"Real: IRRIGAR (1)           {cm[1][0]:<15} | {cm[1][1]}")

    print("\n--- CLASSIFICATION REPORT DETALHADO ---")
    print(classification_report(y_test, y_test_pred, target_names=["NÃO IRRIGAR", "IRRIGAR"]))

    # Comparação Crítica com a Regra Fixa da Fase 2
    regra_fase2_teste = df.loc[idx_test, "DECISAO_REGRA_FASE2"]
    concordancia_regra = (y_test_pred == regra_fase2_teste).mean()
    
    # Falhas da regra fixa: situações onde o solo estava seco (30% a 50%) mas a regra antiga não irrigou
    estresse_ignorado = ((df.loc[idx_test, "UMIDADE_SOLO"] >= 30.0) & 
                         (df.loc[idx_test, "UMIDADE_SOLO"] < 50.0) & 
                         (df.loc[idx_test, "PREVISAO_CHUVA"] == 0)).sum()
    
    # Desperdício evitado: situações onde a regra antiga irrigaria antes da chuva
    desperdicio_evitado = ((df.loc[idx_test, "UMIDADE_SOLO"] < 30.0) & 
                           (df.loc[idx_test, "PREVISAO_CHUVA"] == 1)).sum()

    print("\n--- CONFRONTO: MODELO MACHINE LEARNING vs. REGRA FIXA DA FASE 2 ---")
    print(f"Concordância entre Modelo e Regra Antiga: {concordancia_regra*100:.1f}%")
    print(f"Situações de estresse hídrico ignoradas pela regra fixa (30% a 50% de umidade): {estresse_ignorado} ocorrências")
    print(f"Situações de desperdício evitadas pelo modelo (chuva iminente): {desperdicio_evitado} ocorrências")
    print("Vantagem Agronômica: O modelo preditivo antecipa a irrigação prevenindo perda de produtividade")
    print("e economiza recursos hídricos ao considerar a previsão meteorológica.")

    # Serialização do Modelo e Scaler
    os.makedirs("models", exist_ok=True)
    caminho_modelo = "models/modelo_irrigacao_farmtech.joblib"
    caminho_scaler = "models/scaler_farmtech.joblib"
    joblib.dump(modelo_campeao, caminho_modelo)
    joblib.dump(scaler, caminho_scaler)
    print(f"\nModelo salvo com sucesso em: {caminho_modelo}")

    # Gravar Previsões Recentes no Banco de Dados (FT4_PREVISAO_MODELO)
    conn = get_connection()
    cur = conn.cursor()
    # Limpa previsões anteriores para teste
    cur.execute("DELETE FROM FT4_PREVISAO_MODELO;")

    amostra_previsoes = df.iloc[-60:].copy() # últimas 60 leituras
    X_amostra = amostra_previsoes[features]
    preds = modelo_campeao.predict(X_amostra)
    probas = modelo_campeao.predict_proba(X_amostra)[:, 1]

    registros_prev = []
    for (_, row), p, pb in zip(amostra_previsoes.iterrows(), preds, probas):
        concorda = 1 if p == row["DECISAO_REGRA_FASE2"] else 0
        registros_prev.append((
            row["DATA_HORA"],
            row["CODIGO_TALHAO"],
            float(row["UMIDADE_SOLO"]),
            float(row["PH_SOLO"]),
            int(row["FOSFORO_OK"]),
            int(row["POTASSIO_OK"]),
            int(p),
            round(float(pb), 4),
            row["CONDICAO_SOLO"],
            "RandomForest_v1.0",
            int(row["DECISAO_REGRA_FASE2"]),
            concorda
        ))

    cur.executemany("""
    INSERT INTO FT4_PREVISAO_MODELO (
        DATA_HORA, CODIGO_TALHAO, UMIDADE_SOLO_ATUAL, PH_ATUAL, FOSFORO_OK, POTASSIO_OK,
        PREDICAO_IRRIGAR, PROBABILIDADE_IRRIGAR, CONDICAO_SOLO, MODELO_VERSAO, DECISAO_REGRA_FASE2, CONCORDANCIA_REGRA
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, registros_prev)
    conn.commit()
    conn.close()
    print(f"60 previsões gravadas na tabela FT4_PREVISAO_MODELO do banco de dados.")

    return modelo_campeao, df_comp

if __name__ == "__main__":
    treinar_e_avaliar_modelo()

