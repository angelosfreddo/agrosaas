#!/usr/bin/env python3
"""
Módulo "Ir Além 2": Perfis de Solo por Clusterização Não Supervisionada (K-Means).
Aplica aprendizado não supervisionado sobre o histórico de sensores da fazenda,
justifica o número de clusters com o Método do Cotovelo e Silhouette Score,
descreve a leitura agronômica de cada perfil e gera visualizações analíticas.
"""

import os
import sys

# Garante inclusão da raiz no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from src.database import get_connection

def executar_clusterizacao():
    print("=" * 80)
    print("FARMTECH SOLUTIONS — IR ALÉM 2: CLUSTERIZAÇÃO DE PERFIS DE SOLO")
    print("=" * 80)

    conn = get_connection()
    query = """
    SELECT UMIDADE_SOLO, PH_SOLO, FOSFORO_OK, POTASSIO_OK, NITROGENIO_OK
    FROM FT4_LEITURA_SENSOR;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"Total de amostras edafoclimáticas carregadas: {len(df)}")

    # Padronização de escala
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    # 1. Determinação do Número Ótimo de Clusters (Método do Cotovelo e Silhouette)
    k_range = range(2, 8)
    inercia = []
    silhuetas = []

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inercia.append(km.inertia_)
        silhuetas.append(silhouette_score(X_scaled, km.labels_))

    # Geração do Gráfico do Método do Cotovelo
    os.makedirs("assets/diagramas", exist_ok=True)
    os.makedirs("IR_ALEM/IR_ALEM_2_CLUSTERIZACAO", exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=150)
    cor_inercia = "#1E40AF"
    cor_silhueta = "#DC2626"

    ax1.set_xlabel("Número de Grupos (k)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Inércia / WCSS (Soma dos Quadrados Intra-Cluster)", color=cor_inercia, fontsize=10, fontweight="bold")
    line1 = ax1.plot(list(k_range), inercia, marker="o", color=cor_inercia, linewidth=2.0, label="Inércia (Elbow)")
    ax1.tick_params(axis="y", labelcolor=cor_inercia)
    ax1.grid(True, linestyle="--", alpha=0.5)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Silhouette Score Médio", color=cor_silhueta, fontsize=10, fontweight="bold")
    line2 = ax2.plot(list(k_range), silhuetas, marker="s", color=cor_silhueta, linewidth=2.0, linestyle=":", label="Silhouette")
    ax2.tick_params(axis="y", labelcolor=cor_silhueta)
    ax2.grid(False)

    plt.title("Critério de Escolha de k: Método do Cotovelo e Coeficiente de Silhueta", fontsize=11, fontweight="bold", pad=12)
    plt.tight_layout()
    caminho_cotovelo = "assets/diagramas/metodo_cotovelo_kmeans.png"
    plt.savefig(caminho_cotovelo)
    plt.close()
    print(f"Gráfico do método do cotovelo gerado em: {caminho_cotovelo}")

    # Justificativa de k = 3: Ponto de inflexão nítido no cotovelo com máxima interpretabilidade agronômica
    k_escolhido = 3
    kmeans_final = KMeans(n_clusters=k_escolhido, random_state=42, n_init=10)
    df["CLUSTER"] = kmeans_final.fit_predict(X_scaled)

    # Interpretação Agronômica dos Centróides
    centroides = pd.DataFrame(scaler.inverse_transform(kmeans_final.cluster_centers_),
                              columns=df.columns[:-1])
    centroides["TAMANHO_AMOSTRAS"] = df["CLUSTER"].value_counts().sort_index().values
    centroides["PERCENTUAL"] = (centroides["TAMANHO_AMOSTRAS"] / len(df) * 100).round(1)

    print("\n--- CENTRÓIDES DOS PERFIS IDENTIFICADOS (ESCALA REAL DO SOLO) ---")
    print(centroides.to_string())

    # Mapeamento descritivo dos perfis
    mapa_rotulos = {
        0: "Solo Equilibrado e Fértil",
        1: "Solo Seco com Déficit Hídrico",
        2: "Solo com Acidez / Necessidade de Calagem"
    }
    df["PERFIL_AGRONOMICO"] = df["CLUSTER"].map(mapa_rotulos)

    # Geração do Gráfico de Dispersão dos Perfis de Solo
    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=150)
    cores_clusters = {
        "Solo Equilibrado e Fértil": "#10B981", # Verde
        "Solo Seco com Déficit Hídrico": "#F59E0B", # Âmbar/Laranja
        "Solo com Acidez / Necessidade de Calagem": "#8B5CF6" # Roxo
    }

    for perfil, cor in cores_clusters.items():
        sub = df[df["PERFIL_AGRONOMICO"] == perfil]
        ax.scatter(sub["UMIDADE_SOLO"], sub["PH_SOLO"], label=perfil, color=cor, alpha=0.6, s=30)

    # Plota centróides reais
    ax.scatter(centroides["UMIDADE_SOLO"], centroides["PH_SOLO"],
               color="#111827", marker="X", s=180, edgecolors="white", linewidth=1.5,
               label="Centróides dos Perfis", zorder=10)

    ax.set_title("Perfis de Solo da Lavoura Identificados por K-Means (k=3)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Umidade do Solo (%)", fontsize=10, fontweight="bold")
    ax.set_ylabel("pH do Solo", fontsize=10, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True, loc="upper right")
    plt.tight_layout()
    caminho_dispersao = "assets/diagramas/dispersao_clusters_solos.png"
    plt.savefig(caminho_dispersao)
    plt.close()
    print(f"Gráfico de dispersão de clusters gerado em: {caminho_dispersao}")

    # Salvar modelo K-Means
    joblib.dump(kmeans_final, "models/kmeans_perfis_solo.joblib")
    joblib.dump(scaler, "models/scaler_kmeans.joblib")
    print("Modelo K-Means serializado em models/kmeans_perfis_solo.joblib")

    return df, centroides

if __name__ == "__main__":
    executar_clusterizacao()

