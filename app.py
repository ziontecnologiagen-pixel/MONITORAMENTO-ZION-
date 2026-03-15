import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard Definitivo", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados_completos(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url).fillna(0)

def limpar_valor(v):
    try:
        if isinstance(v, str):
            return float(v.replace('R$', '').replace('.', '').replace(',', '.').strip())
        return float(v)
    except: return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados_completos("ODM MARÇO")

if not df_raw.empty:
    # Dados Empurrador (U, V, W, X, Z)
    df_emp = pd.DataFrame()
    df_emp['NOME'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_emp['ORC_RS'] = df_raw.iloc[:, 21].apply(limpar_valor)
    df_emp['FORE_L'] = df_raw.iloc[:, 22].apply(limpar_valor)
    df_emp['REAL_RS'] = df_raw.iloc[:, 23].apply(limpar_valor)
    df_emp['REAL_L'] = df_raw.iloc[:, 25].apply(limpar_valor)
    
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_emp = df_emp[df_emp['NOME'].isin(frota)].reset_index(drop=True)

    # Dados Ciclo (Tabela Mestre AF2:AJ3)
    df_ciclo = df_raw.iloc[1:3, 31:36].copy() 
    df_ciclo.columns = ['CICLO', 'ORC_RS', 'REAL_RS', 'FORE_L', 'REAL_L']
    for c in ['ORC_RS', 'REAL_RS', 'FORE_L', 'REAL_L']:
        df_ciclo[c] = df_ciclo[c].apply(limpar_valor)

    st.markdown("<h1 style='text-align: center; color: black;'><b>PAINEL CONSOLIDADO ZION</b></h1>", unsafe_allow_html=True)

    # --- PARTE 1: GRÁFICOS DE BARRAS POR EMPURRADOR (OS QUE VOCÊ GOSTOU) ---
    st.markdown("## **1. PERFORMANCE POR EMPURRADOR (FROTA ATIVA)**")
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['ORC_RS'], name='<b>ORÇADO</b>', marker_color='lightblue'))
        fig1.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['REAL_RS'], name='<b>REALIZADO</b>', marker_color='blue'))
        for i, r in df_emp.iterrows():
            diff = r['REAL_RS'] - r['ORC_RS']
            cor = "red" if diff > 0 else "green"
            fig1.add_annotation(x=r['NOME'], y=0, text=f"<b>R$ {abs(diff):,.0f}</b>", showarrow=False, yshift=-60, font=dict(color=cor, size=12))
        fig1.update_layout(title="<b>FINANCEIRO (R$)</b>", barmode='group', font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['FORE_L'], name='<b>ORÇADO</b>', marker_color='lightblue'))
        fig2.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['REAL_L'], name='<b>REALIZADO</b>', marker_color='blue'))
        fig2.update_layout(title="<b>CONSUMO (LITROS)</b>", barmode='group', font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig2, use_container_width=True)

    # --- PARTE 2: GRÁFICOS DE BARRAS POR CICLO (DADOS MESTRE AF:AJ) ---
    st.divider()
    st.markdown("## **2. PERFORMANCE POR CICLO (TABELA MESTRE)**")
    col3, col4 = st.columns(2)

    with col3:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df_ciclo['CICLO'], y=df_ciclo['ORC_RS'], name='<b>ORÇADO</b>', marker_color='lightgray'))
        fig3.add_trace(go.Bar(x=df_ciclo['CICLO'], y=df_ciclo['REAL_RS'], name='<b>REALIZADO</b>', marker_color='darkblue'))
        fig3.update_layout(title="<b>CICLOS: FINANCEIRO (R$)</b>", barmode='group', font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df_ciclo['CICLO'], y=df_ciclo['FORE_L'], name='<b>FORECAST</b>', marker_color='lightgray'))
        fig4.add_trace(go.Bar(x=df_ciclo['CICLO'], y=df_ciclo['REAL_L'], name='<b>REAL</b>', marker_color='darkblue'))
        fig4.update_layout(title="<b>CICLOS: CONSUMO (LITROS)</b>", barmode='group', font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig4, use_container_width=True)

    # --- PARTE 3: GRÁFICOS DE PIZZA (DISTRIBUIÇÃO) ---
    st.divider()
    st.markdown("## **3. DISTRIBUIÇÃO PERCENTUAL POR CICLO**")
    col5, col6 = st.columns(2)

    with col5:
        fig5 = px.pie(df_ciclo, values='REAL_RS', names='CICLO', title='<b>PARTICIPAÇÃO NO GASTO (R$)</b>')
        fig5.update_traces(textinfo='percent+label', marker=dict(line=dict(color='black', width=1)))
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        fig6 = px.pie(df_ciclo, values='REAL_L', names='CICLO', title='<b>PARTICIPAÇÃO NO VOLUME (L)</b>')
        fig6.update_traces(textinfo='percent+label', marker=dict(line=dict(color='black', width=1)))
        st.plotly_chart(fig6, use_container_width=True)
