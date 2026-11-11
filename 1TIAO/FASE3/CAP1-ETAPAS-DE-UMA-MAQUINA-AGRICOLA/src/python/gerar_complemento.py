"""
gerar_complemento.py - Complemento simulado do historico (permitido pela atividade).

A atividade pede pelo menos 3 meses de historico. Se as leituras copiadas do
Wokwi nao cobrirem esse periodo, este script gera as horas restantes em Python
A PARTIR DO PADRAO DAS LEITURAS REAIS e marca cada linha como origem = SIMULADO.

Premissas do complemento (documentadas tambem no README):
  - Relogio: 1 linha por hora, continuando a partir da ultima hora do Wokwi
    ate config.FIM_HISTORICO (sem Wokwi, comeca em config.INICIO_HISTORICO).
  - Logica da bomba: replica EXATA do firmware (sketch.ino): chuva bloqueia;
    umidade < 40 liga; umidade >= 60 desliga; entre 40 e 60 mantem o estado;
    falha do DHT22 nao altera a bomba.
  - Solo: perde umidade por evapotranspiracao (maior entre 10h e 16h e nos
    meses mais quentes), ganha 3,0 pontos percentuais por hora de bomba ligada
    e ganha 8 a 25 pontos em eventos de chuva (mais frequentes em jan-mar).
  - Previsao de chuva: em 80% dos dias de chuva o comando '1' chega 6 horas
    antes (bloqueando a bomba); 3% dos dias tem alarme falso de 4 horas.
  - pH: parte da mediana do pH real (ou 6,3), sofre acidificacao lenta
    (-0,005 por dia) e recebe calagem (+0,6 em 3 dias) quando a media de 7 dias
    fica abaixo de 5,8.
  - Nutrientes P, K e N: alternam entre adequado (1) e baixo (0); a deficiencia
    surge em media a cada 12 dias e e corrigida mais rapido quando ha
    fertirrigacao.
  - Ruido e falhas de campo, para exercitar a limpeza: ruido gaussiano
    (umidade +-1,2; pH +-0,08), 0,6% de falhas do DHT22 ("nan"), 0,3% de picos
    de umidade fora de 0-100%, 0,3% de pH fora de 0-14 (erro de transmissao),
    0,2% de linhas duplicadas e 0,2% de horas perdidas na copia.
  - Semente fixa (42): o arquivo gerado e sempre o mesmo (reprodutivel).

Execucao:
    python src/python/gerar_complemento.py
"""

import csv

import numpy as np
import pandas as pd

import config

SEMENTE = 42

# Probabilidade diaria de chuva por mes (verao chuvoso -> outono mais seco)
PROB_CHUVA_MES = {1: 0.30, 2: 0.28, 3: 0.22, 4: 0.12, 5: 0.08, 6: 0.05,
                  7: 0.04, 8: 0.05, 9: 0.10, 10: 0.18, 11: 0.24, 12: 0.30}
# Fator de evapotranspiracao por mes (1.0 = verao)
FATOR_ET_MES = {1: 1.00, 2: 1.00, 3: 0.95, 4: 0.85, 5: 0.75, 6: 0.70,
                7: 0.70, 8: 0.80, 9: 0.90, 10: 0.95, 11: 1.00, 12: 1.00}


def ler_wokwi():
    """Le o CSV exportado do Wokwi (se existir) e devolve um DataFrame."""
    if not config.ARQ_BRUTO_WOKWI.exists():
        return pd.DataFrame(columns=config.COLUNAS_SERIAL + ["origem"])
    return pd.read_csv(config.ARQ_BRUTO_WOKWI, dtype=str)


def perda_por_evapotranspiracao(hora, mes):
    """Pontos percentuais de umidade perdidos na hora (maior ao meio-dia)."""
    if 10 <= hora <= 16:
        base = 0.90
    elif 7 <= hora <= 9 or 17 <= hora <= 19:
        base = 0.50
    else:
        base = 0.15
    return base * FATOR_ET_MES[mes]


def decidir_bomba(umidade_lida, chuva, bomba_atual):
    """Replica da regra do firmware. Devolve (bomba, nome_da_acao_base)."""
    if np.isnan(umidade_lida):
        return bomba_atual, "FALHA_SENSOR"
    if chuva:
        return 0, "BLOQUEIO_CHUVA"
    if umidade_lida < config.UMIDADE_LIGA:
        return 1, "IRRIGACAO"
    if umidade_lida >= config.UMIDADE_DESLIGA:
        return 0, "DESLIGADA"
    return bomba_atual, ("IRRIGACAO_EM_ANDAMENTO" if bomba_atual else "REPOUSO")


def nome_acao(acao_base, precisa_nutriente):
    """Ajusta o nome da acao como o firmware faz quando falta nutriente."""
    if acao_base == "IRRIGACAO" and precisa_nutriente:
        return "FERTIRRIGACAO"
    if acao_base == "DESLIGADA" and precisa_nutriente:
        return "DESLIGADA_NUTRIENTE_BAIXO"
    return acao_base


def estado_inicial(df_wokwi):
    """Extrai do Wokwi o ponto de partida e o padrao das leituras reais."""
    estado = {"inicio": pd.Timestamp(config.INICIO_HISTORICO), "umidade": 55.0,
              "ph_base": 6.3, "bomba": 0, "p": 1, "k": 1, "n": 1}
    if df_wokwi.empty:
        return estado

    tempos = pd.to_datetime(df_wokwi["data_hora"], errors="coerce").dropna()
    umid = pd.to_numeric(df_wokwi["umidade"], errors="coerce")
    ph = pd.to_numeric(df_wokwi["ph"], errors="coerce")
    estado["inicio"] = tempos.max() + pd.Timedelta(hours=1)

    ultima_umid = umid.dropna()
    if not ultima_umid.empty and 0 <= ultima_umid.iloc[-1] <= 100:
        estado["umidade"] = float(np.clip(ultima_umid.iloc[-1], 5, 95))
    mediana_ph = ph[(ph >= 0) & (ph <= 14)].median()
    if pd.notna(mediana_ph) and 4.5 <= mediana_ph <= 8.5:
        estado["ph_base"] = float(mediana_ph)   # segue o padrao do circuito real

    ultima = df_wokwi.iloc[-1]
    for chave, coluna in (("bomba", "bomba"), ("p", "fosforo"),
                          ("k", "potassio"), ("n", "nitrogenio")):
        if str(ultima[coluna]) in ("0", "1"):
            estado[chave] = int(ultima[coluna])
    return estado


def gerar(df_wokwi):
    """Gera as linhas simuladas (lista de listas de texto, como no Serial)."""
    rng = np.random.default_rng(SEMENTE)
    est = estado_inicial(df_wokwi)
    fim = pd.Timestamp(config.FIM_HISTORICO)
    if est["inicio"] > fim:
        return []

    horas = pd.date_range(est["inicio"], fim, freq="h")
    umidade_real = est["umidade"]
    ph_real = est["ph_base"]
    bomba, p_ok, k_ok, n_ok = est["bomba"], est["p"], est["k"], est["n"]
    chuva_restante = 0          # horas restantes de chuva caindo
    intensidade_chuva = 0.0
    previsao_ate = None         # janela (inicio, fim) de bloqueio por previsao de chuva
    chuva_dia = None            # (inicio, duracao, intensidade) da chuva do dia
    calagem_restante = 0
    historico_ph = []
    linhas = []

    for t in horas:
        # --- 1. Eventos do dia (sorteados a meia-noite) ---
        if t.hour == 0:
            if rng.random() < PROB_CHUVA_MES[t.month]:
                inicio_chuva = t + pd.Timedelta(hours=int(rng.integers(13, 20)))
                duracao = int(rng.integers(2, 4))
                chuva_dia = (inicio_chuva, duracao, rng.uniform(8, 25) / duracao)
                if rng.random() < 0.80:   # previsao acertou e chegou 6 h antes
                    previsao_ate = (inicio_chuva - pd.Timedelta(hours=6),
                                    inicio_chuva + pd.Timedelta(hours=duracao))
            else:
                chuva_dia = None
                if rng.random() < 0.03:   # alarme falso de 4 horas
                    ini = t + pd.Timedelta(hours=int(rng.integers(8, 18)))
                    previsao_ate = (ini, ini + pd.Timedelta(hours=4))
        if chuva_dia is not None and t == chuva_dia[0]:
            chuva_restante, intensidade_chuva = chuva_dia[1], chuva_dia[2]

        chuva_flag = int(previsao_ate is not None and previsao_ate[0] <= t < previsao_ate[1])

        # --- 2. Dinamica fisica do solo na hora ---
        umidade_real -= perda_por_evapotranspiracao(t.hour, t.month)
        if bomba:
            umidade_real += 3.0
        if chuva_restante > 0:
            umidade_real += intensidade_chuva
            chuva_restante -= 1
        umidade_real = float(np.clip(umidade_real, 5, 95))

        # --- 3. pH: acidificacao lenta e calagem quando a media cai ---
        ph_real -= 0.005 / 24
        historico_ph.append(ph_real)
        if calagem_restante == 0 and len(historico_ph) >= 168 and np.mean(historico_ph[-168:]) < 5.8:
            calagem_restante = 72
        if calagem_restante > 0:
            ph_real += 0.6 / 72
            calagem_restante -= 1

        # --- 4. Nutrientes (cadeia de Markov simples por hora) ---
        def transicao(ok):
            if ok:
                return 0 if rng.random() < 1 / (24 * 12) else 1
            taxa = 0.35 if (bomba and linhas and linhas[-1][8] == "FERTIRRIGACAO") else 1 / (24 * 6)
            return 1 if rng.random() < taxa else 0
        p_ok, k_ok, n_ok = transicao(p_ok), transicao(k_ok), transicao(n_ok)

        # --- 5. Leitura dos sensores (com ruido e falhas de campo) ---
        umidade_lida = umidade_real + rng.normal(0, 1.2)
        sorteio = rng.random()
        if sorteio < 0.006:
            umidade_lida = np.nan                                  # falha do DHT22
        elif sorteio < 0.009:
            umidade_lida = float(rng.choice([rng.uniform(101, 140), rng.uniform(-20, -1)]))
        ph_lido = ph_real + rng.normal(0, 0.08)
        if rng.random() < 0.003:
            ph_lido = float(rng.choice([rng.uniform(14.1, 18.0), rng.uniform(-3.0, -0.1)]))

        # --- 6. Decisao identica ao firmware ---
        bomba, acao_base = decidir_bomba(umidade_lida, chuva_flag, bomba)
        precisa_nutriente = not (p_ok and k_ok and n_ok)
        acao = nome_acao(acao_base, precisa_nutriente)

        # --- 7. Linha no formato do Monitor Serial ---
        linha = [t.strftime("%Y-%m-%d %H:%M"),
                 "nan" if np.isnan(umidade_lida) else f"{umidade_lida:.1f}",
                 f"{ph_lido:.2f}", str(p_ok), str(k_ok), str(n_ok),
                 str(bomba), str(chuva_flag), acao, "SIMULADO"]

        sorteio_copia = rng.random()
        if sorteio_copia < 0.002:
            continue                          # hora perdida na copia do log
        linhas.append(linha)
        if sorteio_copia > 0.998:
            linhas.append(list(linha))        # linha duplicada na copia
    return linhas


def main():
    df_wokwi = ler_wokwi()
    simuladas = gerar(df_wokwi)

    config.ARQ_BRUTO.parent.mkdir(parents=True, exist_ok=True)
    with open(config.ARQ_BRUTO, "w", newline="", encoding="utf-8") as arq:
        escritor = csv.writer(arq)
        escritor.writerow(config.COLUNAS_SERIAL + ["origem"])
        for registro in df_wokwi.itertuples(index=False):
            escritor.writerow(list(registro))
        escritor.writerows(simuladas)

    print("CSV bruto completo gerado")
    print(f"  Linhas reais do Wokwi ......: {len(df_wokwi)}")
    print(f"  Linhas simuladas (complemento): {len(simuladas)}")
    print(f"  Arquivo ....................: {config.ARQ_BRUTO}")


if __name__ == "__main__":
    main()
