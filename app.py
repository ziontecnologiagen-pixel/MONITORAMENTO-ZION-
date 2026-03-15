import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard Full", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_tudo(aba):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
        return pd.read_csv(url).fillna(0)
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

def limpar(v):
    try:
        if isinstance(v, str):
            return float(v.replace('R$', '').replace('.', '').replace(',', '.').strip())
        return float(v)
    except: return 0.0

# --- CARGA DE DADOS ---
df_raw = carregar_tudo("ODM MARÇO")

if not df_raw.empty:
    # 1. DADOS DOS EMPURRADORES (U, V, W, X, Z)
    df_emp = pd.DataFrame()
    df_emp['NOME'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_emp['ORC_RS'] = df_raw.iloc[:, 21].apply(limpar)
    df_emp['REAL_RS'] = df_raw.iloc[:, 23].apply(limpar)
    df_emp['FORE_L'] = df_raw.iloc[:, 22].apply(limpar)
    df_emp['REAL_L'] = df_raw.iloc[:, 25].apply(limpar)
    
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_emp = df_emp[df_emp['NOME'].isin(frota)].reset_index(drop=True)

    # 2. DADOS DOS CICLOS (AF2:AJ3) - Serviço Bruto
    df_ciclo = df_raw.iloc[1:3, 31:36].copy() # AF:AJ linhas 2 e 3
    df_ciclo.columns = ['CICLO', 'ORC_RS', 'REAL_RS', 'FORE_L', 'REAL_L']
    for c in ['ORC_RS', 'REAL_RS', 'FORE_L', 'REAL_L']:
        df_ciclo[c] = df_ciclo[c].apply(limpar)

    st.markdown("<h1 style='text-align: center; color: black;'><b>MONITORAMENTO INTEGRADO ZION</b></h1>", unsafe_allow_html=True)

    # --- SEÇÃO 1: OS GRÁFICOS QUE JÁ ESTAVAM PERFEITOS (POR EMPURRADOR) ---
    st.markdown("### 🚢 **PERFORMANCE POR EMPURRADOR**")
    c1, c2 = st.columns(2)
    
    with c1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['ORC_RS'], name='<b>ORÇADO</b>', marker_color='lightblue'))
        fig1.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['REAL_RS'], name='<b>REALIZADO</b>', marker_color='blue'))
        for i, r in df_emp.iterrows():
            diff = r['REAL_RS'] - r['ORC_RS']
            cor = "red" if diff > 0 else "green"
            fig1.add_annotation(x=r['NOME'], y=0, text=f"<b>R$ {abs(diff):,.0f}</b>", showarrow=False, yshift=-60, font=dict(color=cor))
        fig1.update_layout(title="<b>FINANCEIRO (R$)</b>", barmode='group', template="plotly_white", font=dict(color="black"))
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['FORE_L'], name='<b>FORECAST</b>', marker_color='lightblue'))
        fig2.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['REAL_L'], name='<b>REAL</b>', marker_color='blue'))
        fig2.update_layout(title="<b>CONSUMO (LITROS)</b>", barmode='group', template="plotly_white", font=dict(color="black"))
        st.plotly_chart(fig2, use_container_width=True)

    # --- SEÇÃO 2: VISUALIZAÇÃO DOS CICLOS (BARRAS + PIZZAS) ---
    st.divider()
    st.markdown("### 🔄 **RESUMO DOS CICLOS (AF2:AJ3)**")
    c3, c4 = st.columns(2)

    with c3:
        # Barras de Ciclo
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df_ciclo['CICLO'], y=df_ciclo['ORC_RS'], name='<b>ORÇADO</b>', marker_color='lightgray'))
        fig3.add_trace(go.Bar(x=df_ciclo['CICLO'], y=df_ciclo['REAL_RS'], name='<b>REALIZADO</b>', marker_color='darkblue'))
        fig3.update_layout(title="<b>CICLOS: FINANCEIRO (R$)</b>", barmode='group', template="plotly_white", font=dict(color="black"))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        # Pizza de Ciclo
        fig4 = px.pie(df_ciclo, values='REAL_L', names='CICLO', title='<b>DISTRIBUIÇÃO LITROS POR CICLO</b>')
        fig4.update_traces(textfont_color="black", textinfo='percent+label', marker=dict(line=dict(color='black', width=1)))
        fig4.update_layout(font=dict(color="black"))
        st.plotly_chart(fig4, use_container_width=True)

    # Tabela Final
    st.dataframe(df_emp.style.set_properties(**{'font-weight': 'bold', 'color': 'black'}), use_container_width=True, hide_index=True)
