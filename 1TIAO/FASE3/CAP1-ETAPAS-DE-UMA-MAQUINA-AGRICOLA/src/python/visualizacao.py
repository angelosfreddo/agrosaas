"""
visualizacao.py - Parte 1: geracao dos graficos com Matplotlib e Seaborn.

Produz quatro figuras em docs/graficos/:
  1. 01_evolucao_umidade_ph_tempo.png
     Evolucao temporal da umidade do solo e do pH ao longo dos 4 meses,
     comparando as leituras tratadas com a curva suavizada por media movel de
     6 horas e destacando as faixas agronomicas de decisao.
  2. 02_relacao_leituras_acionamento_bomba.png
     Relacao entre as leituras dos sensores e os acionamentos da bomba (zoom em
     uma janela de 15 dias mostrando os ciclos de histerese < 40% ate >= 60%,
     mais boxplot da umidade por tipo de acao do sistema e consumo mensal de agua).
  3. 03_distribuicao_sensores.png
     Distribuicao estatistica das leituras de cada sensor (histogramas com KDE
     e violinplots para umidade e pH; frequencia de disponibilidade para N, P e K).
  4. 04_mapa_calor_correlacao.png
     Mapa de calor (Seaborn heatmap) da matriz de correlacao de Pearson entre
     umidade, pH, nutrientes (P, K, N), previsao de chuva e estado da bomba.

Execucao:
    python src/python/visualizacao.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import config

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
})


def grafico_evolucao_temporal(df):
    """Grafico 1: Evolucao da umidade e do pH no tempo (bruto vs media movel)."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 7.5), sharex=True)

    # Painel superior: Umidade do solo
    ax1.plot(df["data_hora"], df["umidade"], color="#90caf9", alpha=0.45,
             linewidth=0.8, label="Umidade tratada (1h)")
    ax1.plot(df["data_hora"], df["umidade_suavizada"], color="#0d47a1",
             linewidth=1.6, label=f"Media movel ({config.JANELA_MEDIA_MOVEL}h)")
    ax1.axhline(config.UMIDADE_LIGA, color="#d32f2f", linestyle="--", linewidth=1.2,
                label="Limite critico (< 40% liga bomba)")
    ax1.axhline(config.UMIDADE_DESLIGA, color="#2e7d32", linestyle="--", linewidth=1.2,
                label="Capacidade de campo (>= 60% desliga bomba)")
    ax1.fill_between(df["data_hora"], 0, config.UMIDADE_LIGA, color="#ffcdd2", alpha=0.20)
    ax1.fill_between(df["data_hora"], config.UMIDADE_DESLIGA, 100, color="#c8e6c9", alpha=0.20)
    ax1.set_ylim(30, 85)
    ax1.set_ylabel("Umidade do Solo (%)")
    ax1.set_title("Evolucao Temporal da Umidade do Solo e do pH (Jan a Abr/2026 - Milho)")
    ax1.legend(loc="upper right", ncol=2, frameon=True)

    # Painel inferior: pH do solo
    ax2.plot(df["data_hora"], df["ph"], color="#ffcc80", alpha=0.45,
             linewidth=0.8, label="pH tratado (1h)")
    ax2.plot(df["data_hora"], df["ph_suavizado"], color="#e65100",
             linewidth=1.6, label=f"Media movel ({config.JANELA_MEDIA_MOVEL}h)")
    ax2.axhline(config.PH_MIN_IDEAL, color="#6a1b9a", linestyle="--", linewidth=1.2,
                label="Faixa ideal sem alerta (6.0 a 7.0)")
    ax2.axhline(config.PH_MAX_IDEAL, color="#6a1b9a", linestyle="--", linewidth=1.2)
    ax2.axhspan(config.PH_MIN_IDEAL, config.PH_MAX_IDEAL, color="#e1bee7", alpha=0.22)
    ax2.set_ylim(5.5, 6.8)
    ax2.set_ylabel("Nivel de pH (LDR)")
    ax2.set_xlabel("Data da Leitura (Relogio Simulado)")
    ax2.legend(loc="upper right", ncol=2, frameon=True)
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%Y"))
    plt.xticks(rotation=25)

    fig.tight_layout()
    caminho = config.DIR_GRAFICOS / "01_evolucao_umidade_ph_tempo.png"
    fig.savefig(caminho)
    plt.close(fig)
    return caminho


def grafico_relacao_bomba(df, mensal):
    """Grafico 2: Relacao entre as leituras dos sensores e o acionamento da bomba."""
    fig = plt.figure(figsize=(13, 8))
    grade = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.0])

    # Painel A (topo inteiro): recorte de 15 dias mostrando os ciclos de histerese
    ax_topo = fig.add_subplot(grade[0, :])
    recorte = df[(df["data_hora"] >= "2026-01-01") & (df["data_hora"] < "2026-01-16")].copy()
    ax_topo.plot(recorte["data_hora"], recorte["umidade"], color="#1565c0",
                 linewidth=1.4, label="Umidade do Solo (%)")
    ax_topo.axhline(config.UMIDADE_LIGA, color="#c62828", linestyle="--", linewidth=1.0,
                    label="Gatilho Liga (40%)")
    ax_topo.axhline(config.UMIDADE_DESLIGA, color="#2e7d32", linestyle="--", linewidth=1.0,
                    label="Gatilho Desliga (60%)")
    ax_topo.fill_between(
        recorte["data_hora"], 30, 80,
        where=recorte["bomba"] == 1,
        color="#42a5f5", alpha=0.28, label="Bomba Ligada (Irrigacao/Fertirrigacao)"
    )
    ax_topo.fill_between(
        recorte["data_hora"], 30, 80,
        where=recorte["chuva"] == 1,
        color="#ffb300", alpha=0.25, label="Bloqueio por Previsao de Chuva"
    )
    ax_topo.set_ylim(32, 78)
    ax_topo.set_ylabel("Umidade (%)")
    ax_topo.set_title("Ciclos de Acionamento da Bomba por Histerese (Recorte de 01/01 a 15/01/2026)")
    ax_topo.legend(loc="upper right", ncol=3, frameon=True, fontsize=9)
    ax_topo.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))

    # Painel B (inferior esquerdo): Boxplot da umidade por estado da bomba e acao
    ax_esq = fig.add_subplot(grade[1, 0])
    ordem_acoes = [
        "IRRIGACAO", "FERTIRRIGACAO", "IRRIGACAO_EM_ANDAMENTO",
        "REPOUSO", "BLOQUEIO_CHUVA", "DESLIGADA", "DESLIGADA_NUTRIENTE_BAIXO"
    ]
    presentes = [a for a in ordem_acoes if a in df["acao"].unique()]
    sns.boxplot(
        data=df[df["acao"].isin(presentes)],
        x="umidade", y="acao", hue="acao", order=presentes,
        palette="Blues_r", legend=False, ax=ax_esq
    )
    ax_esq.axvline(config.UMIDADE_LIGA, color="#c62828", linestyle="--", linewidth=1.0)
    ax_esq.axvline(config.UMIDADE_DESLIGA, color="#2e7d32", linestyle="--", linewidth=1.0)
    ax_esq.set_xlabel("Umidade do Solo (%)")
    ax_esq.set_ylabel("Acao Decidida pelo Firmware")
    ax_esq.set_title("Faixa de Umidade em Cada Decisao do Sistema")

    # Painel C (inferior direito): Horas de bomba ligada e volume de agua por mes
    ax_dir = fig.add_subplot(grade[1, 1])
    barras = ax_dir.bar(
        mensal["ano_mes"], mensal["volume_agua_m3"],
        color=["#1976d2", "#1e88e5", "#42a5f5", "#64b5f6"], edgecolor="#0d47a1"
    )
    for barra, horas in zip(barras, mensal["horas_bomba_ligada"]):
        altura = barra.get_height()
        ax_dir.text(
            barra.get_x() + barra.get_width() / 2.0, altura + 6,
            f"{altura:.0f} m3\n({int(horas)}h)", ha="center", va="bottom", fontsize=9
        )
    ax_dir.set_ylim(0, mensal["volume_agua_m3"].max() * 1.22)
    ax_dir.set_xlabel("Mes de Referencia")
    ax_dir.set_ylabel("Volume de Agua Aplicado (m3)")
    ax_dir.set_title("Consumo Mensal de Agua e Tempo de Bomba Ligada")

    fig.tight_layout()
    caminho = config.DIR_GRAFICOS / "02_relacao_leituras_acionamento_bomba.png"
    fig.savefig(caminho)
    plt.close(fig)
    return caminho


def grafico_distribuicao_sensores(df):
    """Grafico 3: Distribuicao das leituras de cada sensor (S1, S2 e S3)."""
    fig, eixos = plt.subplots(2, 2, figsize=(13, 8))

    # 1. Histograma + KDE da Umidade (S1)
    sns.histplot(df["umidade"], bins=30, kde=True, color="#1e88e5", ax=eixos[0, 0])
    eixos[0, 0].axvline(config.UMIDADE_LIGA, color="#c62828", linestyle="--", label="Critico 40%")
    eixos[0, 0].axvline(config.UMIDADE_DESLIGA, color="#2e7d32", linestyle="--", label="Ideal 60%")
    eixos[0, 0].set_title("Distribuicao do Sensor S1 - Umidade do Solo (%)")
    eixos[0, 0].set_xlabel("Umidade (%)")
    eixos[0, 0].set_ylabel("Frequencia (horas)")
    eixos[0, 0].legend()

    # 2. Histograma + KDE do pH (S2)
    sns.histplot(df["ph"], bins=30, kde=True, color="#fb8c00", ax=eixos[0, 1])
    eixos[0, 1].axvline(config.PH_MIN_IDEAL, color="#6a1b9a", linestyle="--", label="Limite 6.0")
    eixos[0, 1].axvline(config.PH_MAX_IDEAL, color="#6a1b9a", linestyle="--", label="Limite 7.0")
    eixos[0, 1].set_title("Distribuicao do Sensor S2 - pH do Solo (LDR)")
    eixos[0, 1].set_xlabel("pH")
    eixos[0, 1].set_ylabel("Frequencia (horas)")
    eixos[0, 1].legend()

    # 3. Violinplot da Umidade e do pH por mes
    df_mes = df.copy()
    df_mes["Mes"] = df_mes["data_hora"].dt.strftime("%Y-%m")
    sns.violinplot(
        data=df_mes, x="Mes", y="umidade", hue="Mes",
        palette="Blues", inner="quartile", legend=False, ax=eixos[1, 0]
    )
    eixos[1, 0].set_title("Distribuicao Mensal da Umidade (Violinplot)")
    eixos[1, 0].set_xlabel("Mes")
    eixos[1, 0].set_ylabel("Umidade (%)")

    # 4. Disponibilidade dos nutrientes S3 (P, K, N) e estado da bomba (% das horas)
    percentuais = pd.DataFrame({
        "Variavel": ["Fosforo (P)", "Potassio (K)", "Nitrogenio (N)", "Bomba Ligada"],
        "Adequado / Ativo (%)": [
            df["fosforo"].mean() * 100,
            df["potassio"].mean() * 100,
            df["nitrogenio"].mean() * 100,
            df["bomba"].mean() * 100,
        ],
    })
    percentuais["Deficit / Desligada (%)"] = 100.0 - percentuais["Adequado / Ativo (%)"]
    x = np.arange(len(percentuais))
    b1 = eixos[1, 1].bar(x, percentuais["Adequado / Ativo (%)"], width=0.55,
                         color="#43a047", label="Adequado / Bomba Ligada")
    eixos[1, 1].bar(x, percentuais["Deficit / Desligada (%)"], width=0.55,
                    bottom=percentuais["Adequado / Ativo (%)"],
                    color="#e53935", alpha=0.75, label="Baixo / Bomba Desligada")
    for barra in b1:
        v = barra.get_height()
        eixos[1, 1].text(barra.get_x() + barra.get_width() / 2, v / 2,
                         f"{v:.1f}%", ha="center", va="center", color="white", fontweight="bold")
    eixos[1, 1].set_xticks(x)
    eixos[1, 1].set_xticklabels(percentuais["Variavel"])
    eixos[1, 1].set_ylim(0, 100)
    eixos[1, 1].set_ylabel("Proporcao das Leituras (%)")
    eixos[1, 1].set_title("Disponibilidade dos Sensores S3 (NPK) e Taxa de Uso da Bomba")
    eixos[1, 1].legend(loc="upper right")

    fig.tight_layout()
    caminho = config.DIR_GRAFICOS / "03_distribuicao_sensores.png"
    fig.savefig(caminho)
    plt.close(fig)
    return caminho


def grafico_mapa_calor_correlacao(corr):
    """Grafico 4: Mapa de calor (Seaborn heatmap) da matriz de correlacao."""
    fig, ax = plt.subplots(figsize=(8.5, 6.8))
    mascara = np.zeros_like(corr, dtype=bool)
    sns.heatmap(
        corr, mask=mascara, annot=True, fmt=".3f",
        cmap="coolwarm", vmin=-1.0, vmax=1.0, center=0.0,
        square=True, linewidths=0.8, cbar_kws={"shrink": 0.82, "label": "Correlacao de Pearson (r)"},
        ax=ax
    )
    ax.set_title("Mapa de Calor da Correlacao entre Sensores, Clima e Acionamento da Bomba")
    plt.xticks(rotation=25, ha="right")
    plt.yticks(rotation=0)
    fig.tight_layout()
    caminho = config.DIR_GRAFICOS / "04_mapa_calor_correlacao.png"
    fig.savefig(caminho)
    plt.close(fig)
    return caminho


def main():
    config.DIR_GRAFICOS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(config.ARQ_TRATADO)
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    mensal = pd.read_csv(config.ARQ_IND_MENSAL)
    corr = pd.read_csv(config.ARQ_CORRELACAO, index_col=0)

    caminhos = [
        grafico_evolucao_temporal(df),
        grafico_relacao_bomba(df, mensal),
        grafico_distribuicao_sensores(df),
        grafico_mapa_calor_correlacao(corr),
    ]
    print("Graficos gerados com sucesso:")
    for c in caminhos:
        print(f"  - {c}")


if __name__ == "__main__":
    main()

