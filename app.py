import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Zion - Torre de Controle", layout="wide")

# 2. ESTILIZAÇÃO CSS (CORRIGIDO)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTable { background: white; border-radius: 8px; }
    div[data-testid="stExpander"] { background: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO PRINCIPAL ---
st.title("🚢 Sistema Integrado Zion: Rancho & ODM")
st.markdown("---")

# 3. BARRA LATERAL (FILTROS)
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/product/2x/sheets_2020q4_48dp.png", width=50)
    st.header("Painel de Controle")
    empurrador_selecionado = st.selectbox(
        "Filtrar por Empurrador:",
        ["TODOS", "BRENO", "IPE", "AROEIRA", "CUMARU", "JATOBA"]
    )
    st.info("O Dashboard atualiza automaticamente conforme a planilha.")

# 4. TELA DE PROGRAMAÇÃO (FUTURO)
st.subheader("📅 1. TELA DE PROGRAMAÇÃO (PENDENTES)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🥪 Rancho")
    # Exemplo de dados para visualização
    df_prog_rancho = pd.DataFrame({
        'Empurrador': ['BRENO', 'IPE', 'AROEIRA'],
        'Data Prevista': ['12/03/26', '14/03/26', '15/03/26'],
        'Local': ['MIR', 'BEL', 'SAN']
    })
    st.table(df_prog_rancho)

with col2:
    st.markdown("#### ⛽ ODM")
    df_prog_odm = pd.DataFrame({
        'Empurrador': ['BRENO', 'IPE', 'AROEIRA'],
        'Volume (Lts)': ['20.000 L', '25.000 L', '15.000 L'],
        'Data Prevista': ['15/03/26', '16/03/26', '16/03/26']
    })
    st.table(df_prog_odm)

st.markdown("---")

# 5. TELA DE REALIZADOS (HISTÓRICO)
st.subheader("✅ 2. TELA DE REALIZADOS (CONCLUÍDOS)")
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 🥪 Rancho Realizado")
    df_real_rancho = pd.DataFrame({
        'Empurrador': ['BRENO', 'CUMARU', 'JATOBA'],
        'Data Entrega': ['09/03/26', '08/03/26', '07/03/26'],
        'Status': ['CONCLUÍDO', 'CONCLUÍDO', 'CONCLUÍDO']
    })
    st.table(df_real_rancho)

with col4:
    st.markdown("#### ⛽ ODM Realizado")
    df_real_odm = pd.DataFrame({
        'Empurrador': ['BRENO', 'CUMARU', 'JATOBA'],
        'Data Realizada': ['05/03/26', '06/03/26', '05/03/26'],
        'SLA Final': ['192 Hs', '120 Hs', '72 Hs']
    })
    st.table(df_real_odm)

st.markdown("---")

# 6. DASHBOARDS DE CONSUMO (GRÁFICOS DE LINHA)
st.subheader(f"📊 3. DASHBOARD DE CONSUMO - {empurrador_selecionado}")
tab1, tab2 = st.tabs(["📉 Consumo ODM (Combustível)", "🍲 Gasto Rancho (Suprimentos)"])

with tab1:
    # Gráfico de linha para ODM (Comparativo Forecast vs Realizado)
    meses = ['Janeiro', 'Fevereiro', 'Março']
    forecast_odm = [35000, 42000, 38000]
    realizado_odm = [32000, 45000, 20000] # Onde 20k é o parcial de março

    fig_odm = go.Figure()
    fig_odm.add_trace(go.Scatter(x=meses, y=forecast_odm, name='Forecast (Lts)', line=dict(color='#007bff', width=3)))
    fig_odm.add_trace(go.Scatter(x=meses, y=realizado_odm, name='Realizado (Lts)', line=dict(color='#d9534f', width=3)))
    
    fig_odm.update_layout(
        title="Evolução de Consumo ODM",
        xaxis_title="Mês",
        yaxis_title="Litros",
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig_odm, use_container_width=True)

with tab2:
    # Gráfico de linha para Rancho
    forecast_rancho = [15000, 15000, 15000]
    realizado_rancho = [14200, 16800, 9500]

    fig_rancho = go.Figure()
    fig_rancho.add_trace(go.Scatter(x=meses, y=forecast_rancho, name='Previsto (R$)', line=dict(color='#28a745', width=3, dash='dot')))
    fig_rancho.add_trace(go.Scatter(x=meses, y=realizado_rancho, name='Gasto Real (R$)', line=dict(color='#ff8c00', width=3)))
    
    fig_rancho.update_layout(
        title="Evolução de Custos com Rancho",
        xaxis_title="Mês",
        yaxis_title="Valor em R$",
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig_rancho, use_container_width=True)

# RODAPÉ
st.markdown("---")
st.caption("Desenvolvido por ZION TECNOLOGIA | Monitoramento Operacional 2026")
