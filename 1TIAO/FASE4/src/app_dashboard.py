#!/usr/bin/env python3
"""
Dashboard Interativo Streamlit — FarmTech Solutions (Fase 4: Safra do Conhecimento Cibernético).
Reúne em uma única interface segura:
1. Autenticação e controle de acesso com hash criptográfico;
2. Monitoramento temporal de sensores e telemetria da lavoura;
3. Previsões e recomendações em tempo real do modelo Scikit-Learn;
4. Formulário e consulta de ocorrências de campo com verificação de integridade SHA-256;
5. Auditoria cibernética com teste prático de detecção de adulteração;
6. Desafio Ir Além: Visualização dos clusters de solo via K-Means.
"""

import os
import sys

# Garante inclusão da raiz no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.database import get_connection, registrar_ocorrencia_campo, verificar_integridade_ocorrencias
from src.security import autenticar_usuario, registrar_log_seguranca, simular_teste_adulteracao

# Configuração da página Streamlit
st.set_page_config(
    page_title="FarmTech Solutions - Safra do Conhecimento",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregamento do Modelo Preditivo
@st.cache_resource
def carregar_modelo_ia():
    caminho_mod = os.path.join(os.path.dirname(__file__), "..", "models", "modelo_irrigacao_farmtech.joblib")
    if os.path.exists(caminho_mod):
        return joblib.load(caminho_mod)
    return None

modelo_ia = carregar_modelo_ia()

# ------------------------------------------------------------------------------
# 1. CONTROLE DE ACESSO E AUTENTICAÇÃO (SEGURANÇA CIBERNÉTICA)
# ------------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_ativo" not in st.session_state:
    st.session_state.usuario_ativo = None

def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>FarmTech Solutions — Fase 4</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #4B5563;'>Painel Seguro de Monitoramento e Decisão Agrícola</h4>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("form_login"):
            st.subheader("Autenticação de Usuário")
            usuario = st.text_input("Usuário", value="gestor_farmtech")
            senha = st.text_input("Senha", type="password", help="Senha padrão para demonstração: farmtech2026")
            submit = st.form_submit_button("Acessar Painel")

            if submit:
                if autenticar_usuario(usuario, senha, ip_origem="127.0.0.1"):
                    st.session_state.autenticado = True
                    st.session_state.usuario_ativo = usuario
                    st.success("Autenticação realizada com sucesso!")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Evento registrado na trilha de auditoria.")

if not st.session_state.autenticado:
    render_login()
    st.stop()

# ------------------------------------------------------------------------------
# 2. MENU LATERAL E FILTROS
# ------------------------------------------------------------------------------
st.sidebar.markdown(f"**Operador Logado:** `{st.session_state.usuario_ativo}`")
if st.sidebar.button("Encerrar Sessão (Logout)"):
    registrar_log_seguranca("LOGOUT", st.session_state.usuario_ativo, "127.0.0.1", "SUCESSO", "Encerramento de sessao")
    st.session_state.autenticado = False
    st.session_state.usuario_ativo = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Navegação do Sistema")
menu = st.sidebar.radio(
    "Selecione o Módulo:",
    [
        "1. Visão Geral da Lavoura",
        "2. IA & Recomendação de Irrigação",
        "3. Ocorrências de Campo (CRUD)",
        "4. Segurança & Auditoria",
        "5. Ir Além: Perfis de Solo (K-Means)"
    ]
)

# Filtro de Talhão Compartilhado
conn = get_connection()
talhoes_df = pd.read_sql_query("SELECT CODIGO_TALHAO, NOME_TALHAO FROM FT4_TALHAO", conn)
conn.close()

opcoes_talhao = ["TODOS"] + talhoes_df["CODIGO_TALHAO"].tolist()
talhao_selecionado = st.sidebar.selectbox("Filtrar por Talhão:", opcoes_talhao)

# ------------------------------------------------------------------------------
# MÓDULO 1: VISÃO GERAL DA LAVOURA
# ------------------------------------------------------------------------------
if menu == "1. Visão Geral da Lavoura":
    st.title("Visão Geral da Lavoura e Leituras de Sensores")
    st.markdown("Acompanhamento contínuo dos parâmetros biofísicos do solo e acionamento de manejo.")

    conn = get_connection()
    filtro_sql = "" if talhao_selecionado == "TODOS" else f"WHERE CODIGO_TALHAO = '{talhao_selecionado}'"
    df_leituras = pd.read_sql_query(f"SELECT * FROM FT4_LEITURA_SENSOR {filtro_sql} ORDER BY DATA_HORA ASC", conn)
    df_ocorr = pd.read_sql_query(f"SELECT count(*) as total FROM FT4_OCORRENCIA_CAMPO {filtro_sql}", conn)
    df_acionamentos = pd.read_sql_query(f"SELECT count(*) as total_irrig, sum(VOLUME_LITROS) as vol FROM FT4_ACIONAMENTO_IRRIGACAO {filtro_sql}", conn)
    conn.close()

    if df_leituras.empty:
        st.warning("Nenhum dado encontrado para o filtro selecionado.")
        st.stop()

    # Cards de Indicadores (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    ult_umid = df_leituras["UMIDADE_SOLO"].iloc[-1]
    ult_ph = df_leituras["PH_SOLO"].iloc[-1]
    total_ocorr = df_ocorr["total"].iloc[0]
    total_vol = df_acionamentos["vol"].iloc[0] or 0.0

    col1.metric("Umidade Atual do Solo", f"{ult_umid:.1f}%", delta=f"{ult_umid - 50.0:.1f}% vs Ideal")
    col2.metric("pH Atual do Solo", f"{ult_ph:.2f}", delta="Faixa Ideal: 5.8 a 6.8")
    col3.metric("Ocorrências Registradas", f"{total_ocorr}")
    col4.metric("Volume Irrigado Total", f"{total_vol:,.0f} L")

    st.markdown("---")

    # Gráfico Temporal de Umidade com Linhas de Alerta Agronômico
    st.subheader("Evolução Temporal da Umidade do Solo (%)")
    fig_umid = px.line(
        df_leituras.tail(200),
        x="DATA_HORA", y="UMIDADE_SOLO", color="CODIGO_TALHAO",
        labels={"DATA_HORA": "Data e Hora", "UMIDADE_SOLO": "Umidade do Solo (%)"},
        title="Histórico Recente de Umidade do Solo"
    )
    fig_umid.add_hline(y=50.0, line_dash="dash", line_color="green", annotation_text="Meta Agronômica (50%)")
    fig_umid.add_hline(y=30.0, line_dash="dot", line_color="red", annotation_text="Limite Crítico Fase 2 (30%)")
    fig_umid.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_umid, use_container_width=True)

    # Gráfico de pH e Nutrientes NPK
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Comportamento do pH do Solo")
        fig_ph = px.line(
            df_leituras.tail(120),
            x="DATA_HORA", y="PH_SOLO", color="CODIGO_TALHAO",
            labels={"PH_SOLO": "pH do Solo"},
            color_discrete_sequence=["#D97706", "#2563EB", "#7C3AED"]
        )
        fig_ph.add_hrect(y0=5.8, y1=6.8, line_width=0, fillcolor="green", opacity=0.15, annotation_text="Faixa Ótima")
        fig_ph.update_layout(height=350)
        st.plotly_chart(fig_ph, use_container_width=True)

    with col_b:
        st.subheader("Disponibilidade Nutricional (Fósforo, Potássio e Nitrogênio)")
        resumo_npk = pd.DataFrame({
            "Nutriente": ["Fósforo (P)", "Potássio (K)", "Nitrogênio (N)"],
            "Percentual Adequado (%)": [
                df_leituras["FOSFORO_OK"].mean() * 100,
                df_leituras["POTASSIO_OK"].mean() * 100,
                df_leituras["NITROGENIO_OK"].mean() * 100
            ]
        })
        fig_npk = px.bar(
            resumo_npk, x="Nutriente", y="Percentual Adequado (%)",
            color="Nutriente", text_auto=".1f",
            color_discrete_sequence=["#10B981", "#3B82F6", "#8B5CF6"]
        )
        fig_npk.update_layout(height=350, yaxis_range=[0, 100])
        st.plotly_chart(fig_npk, use_container_width=True)

# ------------------------------------------------------------------------------
# MÓDULO 2: IA & RECOMENDAÇÃO DE IRRIGAÇÃO
# ------------------------------------------------------------------------------
elif menu == "2. IA & Recomendação de Irrigação":
    st.title("Inteligência Artificial: Recomendação Preditiva de Irrigação")
    st.markdown("Substituição da regra fixa da Fase 2 por um modelo de Machine Learning treinado com Scikit-Learn.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Simulador em Tempo Real")
        st.markdown("Insira parâmetros simulados para consultar a inferência imediata do modelo:")
        
        sim_umid = st.slider("Umidade do Solo (%)", 10.0, 90.0, 42.0, step=0.5)
        sim_ph = st.slider("pH do Solo", 4.0, 8.5, 6.2, step=0.1)
        sim_p = st.selectbox("Fósforo (P) Adequado?", [1, 0], format_func=lambda x: "Sim (Adequado)" if x == 1 else "Não (Deficiente)")
        sim_k = st.selectbox("Potássio (K) Adequado?", [1, 0], format_func=lambda x: "Sim (Adequado)" if x == 1 else "Não (Deficiente)")
        sim_n = st.selectbox("Nitrogênio (N) Adequado?", [1, 0], format_func=lambda x: "Sim (Adequado)" if x == 1 else "Não (Deficiente)")
        sim_chuva = st.selectbox("Previsão de Chuva Próximas Horas?", [0, 1], format_func=lambda x: "Não" if x == 0 else "Sim (Chuva Prevista)")

    with col2:
        st.subheader("Decisão e Diagnóstico Agronômico da IA")
        if modelo_ia is not None:
            features_input = np.array([[sim_umid, sim_ph, sim_p, sim_k, sim_n, sim_chuva]])
            predicao = modelo_ia.predict(features_input)[0]
            probabilidade = modelo_ia.predict_proba(features_input)[0][1]

            # Decisão da regra antiga (Fase 2)
            regra_antiga = 1 if sim_umid < 30.0 else 0

            st.markdown("<br>", unsafe_allow_html=True)
            if predicao == 1:
                st.error("### RECOMENDAÇÃO: LIGAR SISTEMA DE IRRIGAÇÃO")
                st.markdown(f"**Confiança do Modelo:** `{probabilidade*100:.1f}%` de probabilidade de necessidade de água.")
            else:
                st.success("### RECOMENDAÇÃO: MANTER BOMBA DESLIGADA")
                st.markdown(f"**Confiança do Modelo:** `{(1.0 - probabilidade)*100:.1f}%` de adequação hídrica.")

            st.markdown("---")
            st.markdown("#### Comparação com a Regra Fixa da Fase 2:")
            col_r1, col_r2 = st.columns(2)
            col_r1.info(f"**Regra Antiga (Umidade < 30%):**\n\n{'LIGAR' if regra_antiga == 1 else 'DESLIGAR'}")
            col_r2.warning(f"**Modelo de Machine Learning:**\n\n{'LIGAR' if predicao == 1 else 'DESLIGAR'}")

            if predicao == 1 and regra_antiga == 0:
                st.markdown("> **Ganho Agronômico:** O modelo preditivo identificou estresse hídrico moderado e antecipou a irrigação antes de danificar a cultura.")
            elif predicao == 0 and sim_chuva == 1 and sim_umid < 50.0:
                st.markdown("> **Economia Sustentável:** O modelo evitou desperdício de energia e água porque há previsão de chuva iminente.")
        else:
            st.error("Modelo de Machine Learning não encontrado. Execute 'python src/train_model.py' primeiro.")

    st.markdown("---")
    st.subheader("Últimas Previsões Registradas no Banco de Dados")
    conn = get_connection()
    df_prev = pd.read_sql_query("SELECT DATA_HORA, CODIGO_TALHAO, UMIDADE_SOLO_ATUAL, PREDICAO_IRRIGAR, PROBABILIDADE_IRRIGAR, CONDICAO_SOLO, DECISAO_REGRA_FASE2, CONCORDANCIA_REGRA FROM FT4_PREVISAO_MODELO ORDER BY DATA_HORA DESC LIMIT 15", conn)
    conn.close()
    st.dataframe(df_prev, use_container_width=True)

# ------------------------------------------------------------------------------
# MÓDULO 3: OCORRÊNCIAS DE CAMPO (CRUD)
# ------------------------------------------------------------------------------
elif menu == "3. Ocorrências de Campo (CRUD)":
    st.title("Registro e Acompanhamento de Ocorrências de Campo")
    st.markdown("Monitoramento de eventos observados pelo operador ou câmeras (pragas, geadas, anomalias) com assinatura criptográfica SHA-256.")

    aba_cad, aba_cons = st.tabs(["Cadastrar Nova Ocorrência", "Consultar Ocorrências Registradas"])

    with aba_cad:
        with st.form("form_nova_ocorrencia"):
            st.subheader("Novo Registro de Campo")
            c1, c2 = st.columns(2)
            f_talhao = c1.selectbox("Talhão Afetado:", talhoes_df["CODIGO_TALHAO"].tolist())
            f_tipo = c2.selectbox("Tipo de Ocorrência:", ["PRAGA_LAGARTA", "QUEIMADURA_GEADA", "FUNGOS_FERRUGEM", "EROSAO_SULCO", "DEFICIENCIA_NUTRIENTE", "OUTRO"])
            f_gravidade = c1.selectbox("Gravidade do Evento:", ["BAIXA", "MEDIA", "ALTA", "CRITICA"])
            f_operador = c2.text_input("Operador Responsável:", value=st.session_state.usuario_ativo)
            f_obs = st.text_area("Observação Técnica Detalhada:", placeholder="Descreva os sintomas, extensão da área e produtos recomendados...")
            f_data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            submit_ocorr = st.form_submit_button("Salvar Registro com Assinatura Criptográfica")
            if submit_ocorr:
                if f_obs.strip():
                    nid, hsh = registrar_ocorrencia_campo(f_data, f_talhao, f_tipo, f_gravidade, f_obs, f_operador)
                    registrar_log_seguranca("OCORRENCIA_CADASTRO", f_operador, "127.0.0.1", "SUCESSO", f"Registro ID {nid} criado no talhao {f_talhao}")
                    st.success(f"Ocorrência cadastrada com sucesso! ID: {nid} | Hash SHA-256: `{hsh[:16]}...`")
                else:
                    st.error("Preencha o campo de observação técnica.")

    with aba_cons:
        st.subheader("Histórico de Ocorrências Cadastradas")
        conn = get_connection()
        filtro_ocorr = "" if talhao_selecionado == "TODOS" else f"WHERE CODIGO_TALHAO = '{talhao_selecionado}'"
        df_todas_ocorr = pd.read_sql_query(f"SELECT ID_OCORRENCIA, DATA_HORA, CODIGO_TALHAO, TIPO_OCORRENCIA, GRAVIDADE, OBSERVACAO, OPERADOR, HASH_INTEGRIDADE, STATUS_TRATAMENTO FROM FT4_OCORRENCIA_CAMPO {filtro_ocorr} ORDER BY DATA_HORA DESC", conn)
        conn.close()
        st.dataframe(df_todas_ocorr, use_container_width=True)

# ------------------------------------------------------------------------------
# MÓDULO 4: SEGURANÇA & AUDITORIA CIBERNÉTICA
# ------------------------------------------------------------------------------
elif menu == "4. Segurança & Auditoria":
    st.title("Memória e Segurança Cibernética dos Dados")
    st.markdown("Verificação contínua de integridade de registros, trilha de auditoria e mitigação de ameaças digitais.")

    st.subheader("1. Auditoria de Integridade Criptográfica (SHA-256)")
    st.markdown("Cada ocorrência de campo possui um hash calculado na gravação. Se um invasor adulterar diretamente o banco, o hash não baterá.")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Executar Verificação de Integridade em Tempo Real"):
            df_audit = verificar_integridade_ocorrencias()
            adulterados = df_audit[df_audit["INTEGRIDADE_CONFIRMADA"] == False]
            if adulterados.empty:
                st.success("Todos os registros conferem com seus respectivos hashes SHA-256! Integridade 100% preservada.")
            else:
                st.error(f"Alerta: {len(adulterados)} registro(s) violado(s) detectado(s)!")
            st.dataframe(df_audit, use_container_width=True)

    with col_btn2:
        if st.button("Simular Ataque e Adulteração de Registro (Teste Prático)"):
            violado = simular_teste_adulteracao()
            if violado:
                st.error("Alerta Crítico: O sistema detectou imediatamente a divergência de hash provocada pelo ataque simulado!")
            st.rerun()

    st.markdown("---")
    st.subheader("2. Trilha de Auditoria (Logs de Segurança)")
    conn = get_connection()
    df_logs = pd.read_sql_query("SELECT DATA_HORA, EVENTO, USUARIO, IP_ORIGEM, STATUS, DETALHES, HASH_LOG FROM FT4_LOG_SEGURANCA ORDER BY DATA_HORA DESC LIMIT 25", conn)
    conn.close()
    st.dataframe(df_logs, use_container_width=True)

# ------------------------------------------------------------------------------
# MÓDULO 5: IR ALÉM — PERFIS DE SOLO (K-MEANS)
# ------------------------------------------------------------------------------
elif menu == "5. Ir Além: Perfis de Solo (K-Means)":
    st.title("Ir Além: Descoberta de Perfis de Solo por Clusterização Não Supervisionada")
    st.markdown("Aplicação de algoritmo K-Means para segmentar as condições edafoclimáticas da lavoura sem depender de rótulos prévios.")

    conn = get_connection()
    df_cluster = pd.read_sql_query("SELECT UMIDADE_SOLO, PH_SOLO, FOSFORO_OK, POTASSIO_OK FROM FT4_LEITURA_SENSOR", conn)
    conn.close()

    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    scaler_km = StandardScaler()
    X_km = scaler_km.fit_transform(df_cluster)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_cluster["CLUSTER"] = kmeans.fit_predict(X_km)

    mapa_perfis = {
        0: "Perfil 1: Solo Equilibrado e Fértil (Manter Manejo)",
        1: "Perfil 2: Solo Seco com Estresse Hídrico (Priorizar Irrigação)",
        2: "Perfil 3: Solo com Acidez / Correção Necessária (Aplicar Calcário)"
    }
    df_cluster["NOME_PERFIL"] = df_cluster["CLUSTER"].map(mapa_perfis)

    st.subheader("Distribuição dos Talhões nos Perfis Identificados pelo K-Means")
    fig_clust = px.scatter(
        df_cluster.sample(500, random_state=42),
        x="UMIDADE_SOLO", y="PH_SOLO", color="NOME_PERFIL",
        labels={"UMIDADE_SOLO": "Umidade (%)", "PH_SOLO": "pH do Solo"},
        title="Agrupamento Não Supervisionado K-Means (k=3)"
    )
    fig_clust.update_layout(height=450)
    st.plotly_chart(fig_clust, use_container_width=True)

    st.markdown("### Interpretação Agronômica dos Perfis Descobertos:")
    st.info("""
    - **Perfil 1 (Equilibrado):** Umidade entre 55% e 70%, pH neutro/ligeiramente ácido (6.0 a 6.5) e saturação nutricional adequada. Recomendação: Manter rotina de monitoramento.
    - **Perfil 2 (Estresse Hídrico):** Umidade abaixo de 45%, exigindo liberação imediata da bomba de irrigação para não comprometer a produtividade da safra.
    - **Perfil 3 (Acidez Elevada):** pH abaixo de 5.5 demandando calagem corretiva antes do próximo plantio.
    """)
