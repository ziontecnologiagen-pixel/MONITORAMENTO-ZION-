import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard Mestre", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_resumo_mestre(aba):
    # O segredo aqui é ler apenas o intervalo AF:AJ
    # Usamos query para limitar as colunas de AF(31) até AJ(35)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}&range=AF1:AJ10"
    df = pd.read_csv(url).fillna(0)
    return df

def converter_limpo(valor):
    try:
        if isinstance(valor, str):
            return float(valor.replace('R$', '').replace('.', '').replace(',', '.').strip())
        return float(valor)
    except: return 0.0

# --- PROCESSAMENTO DOS DADOS (AF2:AJ3) ---
df_mestre = carregar_resumo_mestre("ODM MARÇO")

# Mapeando as colunas do seu serviço bruto:
# AF: Ciclo | AG: Orçado R$ | AH: Realizado R$ | AI: Forecast L | AJ: Realizado L
if not df_mestre.empty:
    df_mestre.columns = ['CICLO', 'ORC_RS', 'REAL_RS', 'FORE_L', 'REAL_L']
    
    # Tratamento de valores numéricos
    for col in ['ORC_RS', 'REAL_RS', 'FORE_L', 'REAL_L']:
        df_mestre[col] = df_mestre[col].apply(converter_limpo)

    st.markdown("<h1 style='text-align: center; color: black;'><b>CONSOLIDADO MESTRE ZION (AF2:AJ3)</b></h1>", unsafe_allow_html=True)

    # --- LINHA 1: BARRAS (FINANCEIRO E LITROS) ---
    col1, col2 = st.columns(2)

    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_mestre['CICLO'], y=df_mestre['ORC_RS'], name='<b>ORÇADO (R$)</b>', marker_color='rgba(135, 206, 235, 0.8)', text=df_mestre['ORC_RS'].apply(lambda x: f'R$ {x:,.0f}'), textposition='outside'))
        fig1.add_trace(go.Bar(x=df_mestre['CICLO'], y=df_mestre['REAL_RS'], name='<b>REALIZADO (R$)</b>', marker_color='rgba(0, 102, 204, 1)', text=df_mestre['REAL_RS'].apply(lambda x: f'R$ {x:,.0f}'), textposition='outside'))
        fig1.update_layout(title="<b>PERFORMANCE FINANCEIRA POR CICLO</b>", template="plotly_white", barmode='group', font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_mestre['CICLO'], y=df_mestre['FORE_L'], name='<b>FORECAST (L)</b>', marker_color='rgba(135, 206, 235, 0.8)', text=df_mestre['FORE_L'].apply(lambda x: f'{x:,.0f} L'), textposition='outside'))
        fig2.add_trace(go.Bar(x=df_mestre['CICLO'], y=df_mestre['REAL_L'], name='<b>REAL (L)</b>', marker_color='rgba(0, 102, 204, 1)', text=df_mestre['REAL_L'].apply(lambda x: f'{x:,.0f} L'), textposition='outside'))
        fig2.update_layout(title="<b>PERFORMANCE DE CONSUMO POR CICLO</b>", template="plotly_white", barmode='group', font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig2, use_container_width=True)

    # --- LINHA 2: PIZZAS (DISTRIBUIÇÃO) ---
    col3, col4 = st.columns(2)

    with col3:
        fig3 = px.pie(df_mestre, values='REAL_L', names='CICLO', title='<b>DISTRIBUIÇÃO DE LITROS</b>', hole=.3)
        fig3.update_traces(textinfo='percent+label', marker=dict(line=dict(color='black', width=1)))
        fig3.update_layout(font=dict(family="Arial Black", color="black"))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = px.pie(df_mestre, values='REAL_RS', names='CICLO', title='<b>DISTRIBUIÇÃO CONTÁBIL</b>', hole=.3)
        fig4.update_traces(textinfo='percent+label', marker=dict(line=dict(color='black', width=1)))
        fig4.update_layout(font=dict(family="Arial Black", color="black"))
        st.plotly_chart(fig4, use_container_width=True)

    # --- TABELA DE RESUMO MESTRE ---
    st.markdown("### **RESUMO DA TABELA MESTRE**")
    st.dataframe(df_mestre.style.format({
        'ORC_RS': 'R$ {:,.2f}', 'REAL_RS': 'R$ {:,.2f}', 
        'FORE_L': '{:,.0f} L', 'REAL_L': '{:,.0f} L'
    }).set_properties(**{'font-weight': 'bold', 'color': 'black'}), use_container_width=True, hide_index=True)
