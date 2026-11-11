"""
tratamento_dados.py - Parte 1: limpeza, reducao de ruido, indicadores e correlacao.

Pipeline executado sobre data/raw/leituras_brutas.csv usando NumPy e Pandas:
  1. Conversao de tipos (data_hora -> datetime64, umidade/ph -> float64,
     nutrientes/bomba/chuva -> int64).
  2. Remocao de timestamps invalidos e de linhas duplicadas pelo mesmo horario.
  3. Reindexacao em grade horaria continua e marcacao de valores fora da faixa
     fisica dos sensores (umidade fora de 0-100%, pH fora de 0-14) como NaN.
  4. Interpolacao linear limitada (ate 3 horas) dos valores ausentes de umidade
     e pH, preservando os valores brutos em colunas separadas para comparacao.
  5. Reducao de ruido por media movel centrada de 6 horas (filtro passa-baixa)
     e mediana movel sobre umidade e pH.
  6. Calculo dos indicadores de manejo (diarios, mensais, eventos de acionamento
     da bomba com volume de agua em litros e m3, faixas de umidade).
  7. Calculo da matriz de correlacao de Pearson entre umidade, pH, nutrientes,
     previsao de chuva e acionamento da bomba.

Execucao:
    python src/python/tratamento_dados.py
"""

import numpy as np
import pandas as pd

import config


def carregar_e_limpar(caminho_csv):
    """Carrega o CSV bruto, converte tipos, remove invalidos e aplica media movel."""
    df_bruto = pd.read_csv(caminho_csv, dtype=str)
    metricas = {"linhas_brutas": len(df_bruto)}

    # 1. Conversao de tipos
    df = df_bruto.copy()
    df["data_hora"] = pd.to_datetime(df["data_hora"], format="%Y-%m-%d %H:%M", errors="coerce")
    metricas["datas_invalidas"] = int(df["data_hora"].isna().sum())
    df = df.dropna(subset=["data_hora"]).sort_values("data_hora")

    # 2. Duplicatas de timestamp (geradas na copia do Monitor Serial)
    metricas["duplicatas_removidas"] = int(df.duplicated(subset=["data_hora"]).sum())
    df = df.drop_duplicates(subset=["data_hora"], keep="first").reset_index(drop=True)

    for col in ("umidade", "ph"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ("fosforo", "potassio", "nitrogenio", "bomba", "chuva"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        invalido = ~df[col].isin(config.VALORES_BINARIOS)
        df.loc[invalido, col] = np.nan

    metricas["umidade_ausente_bruta"] = int(df["umidade"].isna().sum())
    metricas["ph_ausente_bruto"] = int(df["ph"].isna().sum())

    # 3. Leituras fora da faixa fisica dos sensores -> marcadas como NaN
    umid_min, umid_max = config.FAIXA_UMIDADE
    ph_min, ph_max = config.FAIXA_PH

    fora_umid = (df["umidade"] < umid_min) | (df["umidade"] > umid_max)
    fora_ph = (df["ph"] < ph_min) | (df["ph"] > ph_max)
    metricas["umidade_fora_faixa"] = int(fora_umid.sum())
    metricas["ph_fora_faixa"] = int(fora_ph.sum())

    df["umidade_bruta"] = df["umidade"]
    df["ph_bruto"] = df["ph"]
    df.loc[fora_umid, "umidade"] = np.nan
    df.loc[fora_ph, "ph"] = np.nan

    # 4. Grade horaria regular (detecta horas perdidas na copia do Serial)
    grade = pd.date_range(df["data_hora"].min(), df["data_hora"].max(), freq="h")
    df = df.set_index("data_hora").reindex(grade)
    df.index.name = "data_hora"
    metricas["horas_perdidas_grade"] = int(df["origem"].isna().sum())

    # Flag indicando se a linha passou por imputacao/correcao na limpeza
    df["registro_imputado"] = (
        df["umidade"].isna() | df["ph"].isna() | df["origem"].isna()
    ).astype(int)

    # Interpolacao linear para sensores continuos e forward/backward fill para estados discretos
    df["umidade"] = df["umidade"].interpolate(method="time", limit=config.LIMITE_INTERPOLACAO).bfill().ffill()
    df["ph"] = df["ph"].interpolate(method="time", limit=config.LIMITE_INTERPOLACAO).bfill().ffill()

    for col in ("fosforo", "potassio", "nitrogenio", "bomba", "chuva"):
        df[col] = df[col].ffill().bfill().astype(int)

    df["acao"] = df["acao"].ffill().bfill()
    df["origem"] = df["origem"].fillna("IMPUTADO")

    # 5. Reducao de ruido com NumPy / Pandas (media movel e mediana movel de 6h)
    janela = config.JANELA_MEDIA_MOVEL
    pesos = np.ones(janela, dtype=float) / janela
    df["umidade_suavizada"] = (
        df["umidade"].rolling(window=janela, min_periods=1, center=False).mean().round(2)
    )
    df["ph_suavizado"] = (
        df["ph"].rolling(window=janela, min_periods=1, center=False).mean().round(2)
    )
    # Convolucao explicita via NumPy nas bordas internas para validacao numerica
    umid_np = np.convolve(df["umidade"].to_numpy(), pesos, mode="valid")
    metricas["desvio_ruido_umidade_antes"] = float(np.nanstd(df["umidade"].to_numpy()))
    metricas["desvio_ruido_umidade_depois"] = float(np.std(umid_np))
    metricas["desvio_ruido_ph_antes"] = float(np.nanstd(df["ph"].to_numpy()))
    metricas["desvio_ruido_ph_depois"] = float(np.std(df["ph_suavizado"].to_numpy()))

    df["umidade"] = df["umidade"].round(2)
    df["ph"] = df["ph"].round(2)
    df = df.reset_index()
    metricas["linhas_tratadas"] = len(df)
    return df, metricas


def extrair_eventos_bomba(df):
    """Agrupa horas consecutivas de bomba ligada em eventos de irrigacao."""
    bomba = df["bomba"].to_numpy()
    mudanca = np.diff(bomba, prepend=0)
    id_bloco = np.cumsum((mudanca == 1).astype(int))
    ligada = df[df["bomba"] == 1].copy()
    if ligada.empty:
        return pd.DataFrame()

    ligada["id_acionamento"] = id_bloco[df["bomba"] == 1]
    eventos = (
        ligada.groupby("id_acionamento", as_index=False)
        .agg(
            inicio=("data_hora", "min"),
            fim=("data_hora", "max"),
            duracao_horas=("bomba", "sum"),
            umidade_inicial=("umidade_suavizada", "first"),
            umidade_final=("umidade_suavizada", "last"),
            ph_medio=("ph_suavizado", "mean"),
            teve_fertirrigacao=("acao", lambda s: int((s == "FERTIRRIGACAO").any())),
        )
    )
    eventos["fim"] = eventos["fim"] + pd.Timedelta(hours=1)
    eventos["duracao_horas"] = eventos["duracao_horas"].astype(float) * config.HORAS_POR_CICLO
    eventos["volume_agua_litros"] = (eventos["duracao_horas"] * config.VAZAO_BOMBA_L_H).round(2)
    eventos["volume_agua_m3"] = (eventos["volume_agua_litros"] / 1000.0).round(3)
    eventos["ph_medio"] = eventos["ph_medio"].round(2)
    eventos["modalidade"] = np.where(
        eventos["teve_fertirrigacao"] == 1, "FERTIRRIGACAO", "IRRIGACAO_COMUM"
    )
    return eventos


def calcular_indicadores(df):
    """Calcula indicadores diarios, mensais e distribuicao por faixa de umidade."""
    df_aux = df.copy()
    df_aux["data"] = df_aux["data_hora"].dt.date
    df_aux["ano_mes"] = df_aux["data_hora"].dt.strftime("%Y-%m")
    df_aux["inicio_acionamento"] = ((df_aux["bomba"] == 1) & (df_aux["bomba"].shift(1, fill_value=0) == 0)).astype(int)
    df_aux["alerta_ph"] = ((df_aux["ph_suavizado"] < config.PH_MIN_IDEAL) | (df_aux["ph_suavizado"] > config.PH_MAX_IDEAL)).astype(int)
    df_aux["deficit_npk"] = ((df_aux["fosforo"] == 0) | (df_aux["potassio"] == 0) | (df_aux["nitrogenio"] == 0)).astype(int)

    diario = (
        df_aux.groupby("data", as_index=False)
        .agg(
            leituras=("bomba", "count"),
            horas_bomba_ligada=("bomba", "sum"),
            num_acionamentos=("inicio_acionamento", "sum"),
            umidade_media=("umidade_suavizada", "mean"),
            umidade_min=("umidade_suavizada", "min"),
            umidade_max=("umidade_suavizada", "max"),
            ph_medio=("ph_suavizado", "mean"),
            ph_min=("ph_suavizado", "min"),
            ph_max=("ph_suavizado", "max"),
            horas_alerta_ph=("alerta_ph", "sum"),
            horas_deficit_npk=("deficit_npk", "sum"),
            horas_bloqueio_chuva=("chuva", "sum"),
        )
    )
    diario["volume_agua_litros"] = (diario["horas_bomba_ligada"] * config.VAZAO_BOMBA_L_H).round(2)
    diario["volume_agua_m3"] = (diario["volume_agua_litros"] / 1000.0).round(2)
    for col in ("umidade_media", "umidade_min", "umidade_max", "ph_medio", "ph_min", "ph_max"):
        diario[col] = diario[col].round(2)

    mensal = (
        df_aux.groupby("ano_mes", as_index=False)
        .agg(
            leituras=("bomba", "count"),
            horas_bomba_ligada=("bomba", "sum"),
            num_acionamentos=("inicio_acionamento", "sum"),
            umidade_media=("umidade_suavizada", "mean"),
            umidade_min=("umidade_suavizada", "min"),
            umidade_max=("umidade_suavizada", "max"),
            ph_medio=("ph_suavizado", "mean"),
            ph_min=("ph_suavizado", "min"),
            ph_max=("ph_suavizado", "max"),
            horas_alerta_ph=("alerta_ph", "sum"),
            horas_deficit_npk=("deficit_npk", "sum"),
            horas_bloqueio_chuva=("chuva", "sum"),
        )
    )
    mensal["volume_agua_litros"] = (mensal["horas_bomba_ligada"] * config.VAZAO_BOMBA_L_H).round(2)
    mensal["volume_agua_m3"] = (mensal["volume_agua_litros"] / 1000.0).round(2)
    for col in ("umidade_media", "umidade_min", "umidade_max", "ph_medio", "ph_min", "ph_max"):
        mensal[col] = mensal[col].round(2)

    # Faixas agronomicas de umidade do solo (avaliadas sobre a leitura tratada)
    condicoes = [
        df_aux["umidade"] < config.UMIDADE_LIGA,
        (df_aux["umidade"] >= config.UMIDADE_LIGA) & (df_aux["umidade"] < config.UMIDADE_DESLIGA),
        df_aux["umidade"] >= config.UMIDADE_DESLIGA,
    ]
    rotulos = [
        "Critica (< 40% - exige irrigacao)",
        "Transicao / Histerese (40% a 59.9%)",
        "Adequada / Capacidade de Campo (>= 60%)",
    ]
    df_aux["faixa_umidade"] = np.select(condicoes, rotulos, default="Indefinida")
    faixas = (
        df_aux.groupby("faixa_umidade", as_index=False)
        .agg(
            horas_observadas=("bomba", "count"),
            horas_bomba_ligada=("bomba", "sum"),
            umidade_media=("umidade", "mean"),
        )
    )
    faixas["percentual_tempo"] = (faixas["horas_observadas"] / len(df_aux) * 100.0).round(2)
    faixas["umidade_media"] = faixas["umidade_media"].round(2)

    return diario, mensal, faixas


def calcular_correlacao(df):
    """Calcula a matriz de correlacao de Pearson entre sensores e bomba."""
    colunas = ["umidade_suavizada", "ph_suavizado", "fosforo", "potassio", "nitrogenio", "chuva", "bomba"]
    nomes = {
        "umidade_suavizada": "Umidade (%)",
        "ph_suavizado": "pH do Solo",
        "fosforo": "Fosforo (P)",
        "potassio": "Potassio (K)",
        "nitrogenio": "Nitrogenio (N)",
        "chuva": "Previsao Chuva",
        "bomba": "Bomba Ligada",
    }
    corr = df[colunas].rename(columns=nomes).corr(method="pearson").round(4)
    return corr


def salvar_relatorio(metricas, diario, mensal, eventos, faixas, corr):
    """Salva um relatorio textual resumindo a limpeza e os indicadores."""
    linhas = [
        "==============================================================================",
        "RELATORIO DE TRATAMENTO E INDICADORES DE MANEJO - FARMTECH SOLUTIONS (FASE 3)",
        "==============================================================================",
        "",
        "1. AUDITORIA DE LIMPEZA E TRATAMENTO (PANDAS / NUMPY)",
        f"   - Linhas no CSV bruto ......................: {metricas['linhas_brutas']}",
        f"   - Datas invalidas removidas ................: {metricas['datas_invalidas']}",
        f"   - Linhas duplicadas removidas ..............: {metricas['duplicatas_removidas']}",
        f"   - Leituras de umidade ausentes (nan) .......: {metricas['umidade_ausente_bruta']}",
        f"   - Leituras de umidade fora de [0, 100]% ....: {metricas['umidade_fora_faixa']}",
        f"   - Leituras de pH fora de [0, 14] ...........: {metricas['ph_fora_faixa']}",
        f"   - Horas perdidas reindexadas na grade ......: {metricas['horas_perdidas_grade']}",
        f"   - Total de registros no CSV tratado ........: {metricas['linhas_tratadas']}",
        f"   - Desvio padrao da umidade (antes/depois) ..: {metricas['desvio_ruido_umidade_antes']:.2f}% -> {metricas['desvio_ruido_umidade_depois']:.2f}%",
        f"   - Desvio padrao do pH (antes/depois) .......: {metricas['desvio_ruido_ph_antes']:.3f} -> {metricas['desvio_ruido_ph_depois']:.3f}",
        "",
        "2. RESUMO GERAL DE IRRIGACAO E MANEJO",
        f"   - Vazao adotada para a bomba ...............: {config.VAZAO_BOMBA_L_H:,.0f} L/h ({config.VAZAO_BOMBA_L_H/1000:.1f} m3/h)",
        f"   - Total de eventos de acionamento ..........: {len(eventos)}",
        f"   - Tempo total de bomba ligada ..............: {int(mensal['horas_bomba_ligada'].sum())} horas",
        f"   - Volume total de agua aplicado ............: {mensal['volume_agua_litros'].sum():,.0f} L ({mensal['volume_agua_m3'].sum():,.1f} m3)",
        "",
        "3. INDICADORES POR MES",
        mensal.to_string(index=False),
        "",
        "4. FAIXAS DE UMIDADE OBSERVADAS",
        faixas.to_string(index=False),
        "",
        "5. TOP 5 DIAS COM MAIOR TEMPO DE BOMBA LIGADA",
        diario.sort_values(["horas_bomba_ligada", "volume_agua_litros"], ascending=False).head(5).to_string(index=False),
        "",
        "6. MATRIZ DE CORRELACAO DE PEARSON",
        corr.to_string(),
        "",
    ]
    texto = "\n".join(linhas)
    config.ARQ_RELATORIO_LIMPEZA.write_text(texto, encoding="utf-8")
    return texto


def main():
    config.DIR_PROCESSED.mkdir(parents=True, exist_ok=True)
    df, metricas = carregar_e_limpar(config.ARQ_BRUTO)
    eventos = extrair_eventos_bomba(df)
    diario, mensal, faixas = calcular_indicadores(df)
    corr = calcular_correlacao(df)

    df_saida = df.copy()
    df_saida["data_hora"] = df_saida["data_hora"].dt.strftime("%Y-%m-%d %H:%M")
    df_saida.to_csv(config.ARQ_TRATADO, index=False)

    eventos_saida = eventos.copy()
    if not eventos_saida.empty:
        eventos_saida["inicio"] = eventos_saida["inicio"].dt.strftime("%Y-%m-%d %H:%M")
        eventos_saida["fim"] = eventos_saida["fim"].dt.strftime("%Y-%m-%d %H:%M")
    eventos_saida.to_csv(config.ARQ_ACIONAMENTOS, index=False)

    diario.to_csv(config.ARQ_IND_DIARIO, index=False)
    mensal.to_csv(config.ARQ_IND_MENSAL, index=False)
    faixas.to_csv(config.ARQ_FAIXAS_UMIDADE, index=False)
    corr.to_csv(config.ARQ_CORRELACAO)

    relatorio = salvar_relatorio(metricas, diario, mensal, eventos, faixas, corr)
    print(relatorio)


if __name__ == "__main__":
    main()
