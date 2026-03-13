import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da página para ocupar a tela inteira
st.set_page_config(page_title="Zion - Torre de Controle", layout="wide")

# Estilização customizada para parecer com os seus relatórios
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTable { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_index=True)

st.title("🚢 Sistema Integrado Zion: Rancho & ODM")

# --- FILTROS ---
with st.sidebar:
    st.header("Filtros de Visão")
    empurrador_selecionado = st.selectbox("Escolha o Empurrador:", ["TODOS", "BRENO", "IPE", "AROEIRA", "CUMARU"])
    periodo = st.date_input("Período de Análise")

# --- SEÇÃO 1: PROGRAMAÇÃO (FUTURO) ---
st.header("📅 TELA DE PROGRAMAÇÃO (PENDENTES)")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🥪 Rancho")
    # Aqui simulamos os dados que você enviou nas imagens
    df_prog_rancho = pd.DataFrame({
        'E/M': ['BRENO', 'IPE', 'AROEIRA'],
        'Data Prevista': ['12/03/26', '11/03/26', '22/03/26'],
        'Local': ['MIR', 'BEL', 'BEL']
    })
    st.table(df_prog_rancho)

with col2:
    st.subheader("⛽ ODM")
    df_prog_odm = pd.DataFrame({
        'E/M': ['BRENO', 'IPE', 'AROEIRA'],
        'Volume Previsto': ['20.000 L', '25.000 L', '25.000 L'],
        'SLA': ['EM ABERTO', 'EM ABERTO', 'EM ABERTO']
    })
    st.table(df_prog_odm)

st.divider()

# --- SEÇÃO 2: REALIZADOS (HISTÓRICO) ---
st.header("✅ TELA DE REALIZADOS (CONCLUÍDOS)")
col3, col4 = st.columns(2)

with col3:
    st.subheader("🥪 Rancho Realizado")
    df_real_rancho = pd.DataFrame({
        'E/M': ['BRENO', 'CUMARU'],
        'Data Entrega': ['09/03/26', '08/03/26'],
        'Status': ['CONCLUÍDO', 'CONCLUÍDO']
    })
    st.table(df_real_rancho)

with col4:
    st.subheader("⛽ ODM Realizado")
    df_real_odm = pd.DataFrame({
        'E/M': ['BRENO', 'CUMARU'],
        'SLA Final': ['192 Hs', 'EM ABERTO'],
        'Dias': ['8.0 d', '- d']
    })
    st.table(df_real_odm)

st.divider()

# --- SEÇÃO 3: DASHBOARDS DE CONSUMO ---
st.header("📊 DASHBOARD DE CONSUMO POR EMPURRADOR")
tab1, tab2 = st.tabs(["📉 Evolução ODM", "🍲 Evolução Rancho"])

with tab1:
    # Gráfico de linha para ODM (Forecast vs Comprado)
    fig_odm = go.Figure()
    fig_odm.add_trace(go.Scatter(x=['Jan', 'Fev', 'Mar'], y=[35000, 40000, 35000], name='Forecast', line=dict(color='#007bff', width=4)))
    fig_odm.add_trace(go.Scatter(x=['Jan', 'Fev', 'Mar'], y=[15000, 25000, 15000], name='Comprado', line=dict(color='#d9534f', width=4)))
    fig_odm.update_layout(title="Consumo de Combustível (Lts)", template="plotly_white")
    st.plotly_chart(fig_odm, use_container_width=True)

with tab2:
    # Gráfico de linha para Rancho
    fig_rancho = go.Figure()
    fig_rancho.add_trace(go.Scatter(x=['Jan', 'Fev', 'Mar'], y=[5000, 7000, 6500], name='Gasto Rancho', line=dict(color='#28a745', dash='dot')))
    fig_rancho.update_layout(title="Gastos com Rancho (R$)", template="plotly_white")
    st.plotly_chart(fig_rancho, use_container_width=True)

st.info("ZION TECNOLOGIA - Torre de Controle Operacional v1.0")
