import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard Final", layout="wide")

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

# --- CARGA ---
df_raw = carregar_dados_completos("ODM MARÇO")

if not df_raw.empty:
    # 1. Dados Empurrador (U, V, W, X, Z)
    df_emp = pd.DataFrame()
    df_emp['NOME'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_emp['ORC_RS'] = df_raw.iloc[:, 21].apply(limpar_valor)
    df_emp['FORE_L'] = df_raw.iloc[:, 22].apply(limpar_valor)
    df_emp['REAL_RS'] = df_raw.iloc[:, 23].apply(limpar_valor)
    df_emp['REAL_L'] = df_raw.iloc[:, 25].apply(limpar_valor)
    
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_emp = df_emp[df_emp['NOME'].isin(frota)].reset_index(drop=True)

    # 2. Dados Ciclo (Intervalo AF2:AJ3)
    df_ciclo = df_raw.iloc[1:3, 31:36].copy() 
    df_ciclo.columns = ['CICLO', 'ORC_RS', 'REAL_RS', 'FORE_L', 'REAL_L']
    for c in ['ORC_RS', 'REAL_RS', 'FORE_L', 'REAL_L']:
        df_ciclo[c] = df_ciclo[c].apply(limpar_valor)

    st.markdown("<h1 style='text-align: center; color: black;'><b>PAINEL DE PERFORMANCE ZION</b></h1>", unsafe_allow_html=True)

    # --- SEÇÃO APROVADA: PERFORMANCE POR EMPURRADOR (LADO A LADO) ---
    st.markdown("### **VISUALIZAÇÃO POR EMPURRADOR (R$ E LITROS)**")
    col1, col2 = st.columns(2)
    
    with col1:
        # Financeiro
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['ORC_RS'], name='ORÇADO', marker_color='lightblue'))
        fig1.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['REAL_RS'], name='REALIZADO', marker_color='blue'))
        for i, r in df_emp.iterrows():
            diff = r['REAL_RS'] - r['ORC_RS']
            cor = "red" if diff > 0 else "green"
            lbl = "ESTOURO" if diff > 0 else "SALDO"
            fig1.add_annotation(x=r['NOME'], y=0, text=f"<b>{lbl}:</b><br><b>R$ {abs(diff):,.0f}</b>", showarrow=False, yshift=-75, font=dict(color=cor, size=11))
        fig1.update_layout(title="<b>FINANCEIRO (R$)</b>", barmode='group', font=dict(color="black", family="Arial Black"), margin=dict(b=150))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Consumo
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['FORE_L'], name='ORÇADO', marker_color='lightblue'))
        fig2.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['REAL_L'], name='REALIZADO', marker_color='blue'))
        fig2.update_layout(title="<b>CONSUMO (LITROS)</b>", barmode='group', font=dict(color="black", family="Arial Black"), margin=dict(b=150))
        st.plotly_chart(fig2, use_container_width=True)

    # --- NOVA SEÇÃO: VISUALIZAÇÃO POR CICLO (BARRAS E PIZZA) ---
    st.divider()
    st.markdown("### **RESUMO POR CICLO (TABELA MESTRE AF:AJ)**")
    col3, col4 = st.columns(2)

    with col3:
        # Barras por Ciclo
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df_ciclo['CICLO'], y=df_ciclo['ORC_RS'], name='ORÇADO', marker_color='lightgray'))
        fig3.add_trace(go.Bar(x=df_ciclo['CICLO'], y=df_ciclo['REAL_RS'], name='REALIZADO', marker_color='darkblue'))
        fig3.update_layout(title="<b>CICLOS: COMPARATIVO FINANCEIRO</b>", barmode='group', font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Pizza por Ciclo
        fig4 = px.pie(df_ciclo, values='REAL_L', names='CICLO', title='<b>PARTICIPAÇÃO NO CONSUMO (LITROS)</b>')
        fig4.update_traces(textfont_color="black", textinfo='percent+label', marker=dict(line=dict(color='black', width=1)))
        fig4.update_layout(font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig4, use_container_width=True)
