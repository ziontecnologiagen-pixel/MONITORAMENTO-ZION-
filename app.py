import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados_full(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url).fillna(0)

def limpar(v):
    try:
        if isinstance(v, str):
            return float(v.replace('R$', '').replace('.', '').replace(',', '.').strip())
        return float(v)
    except: return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados_full("ODM MARÇO")

if not df_raw.empty:
    # Dados Empurrador (U, V, W, X, Z)
    df_emp = pd.DataFrame()
    df_emp['NOME'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_emp['ORC_RS'] = df_raw.iloc[:, 21].apply(limpar)
    df_emp['FORE_L'] = df_raw.iloc[:, 22].apply(limpar)
    df_emp['REAL_RS'] = df_raw.iloc[:, 23].apply(limpar)
    df_emp['REAL_L'] = df_raw.iloc[:, 25].apply(limpar)
    
    # Filtro aprovado (Cumaru ao Breno)
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_emp = df_emp[df_emp['NOME'].isin(frota)].reset_index(drop=True)

    # Dados Ciclo (Tabela AF2:AJ3)
    df_ciclo = df_raw.iloc[1:3, 31:36].copy() 
    df_ciclo.columns = ['CICLO', 'ORC_RS', 'REAL_RS', 'FORE_L', 'REAL_L']
    for c in ['ORC_RS', 'REAL_RS', 'FORE_L', 'REAL_L']:
        df_ciclo[c] = df_ciclo[c].apply(limpar)

    st.markdown("<h1 style='text-align: center; color: black;'><b>PAINEL DE PERFORMANCE ZION</b></h1>", unsafe_allow_html=True)

    # --- RETORNANDO OS GRÁFICOS ORIGINAIS (LADO A LADO) ---
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico Financeiro Aprovado
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['ORC_RS'], name='ORÇADO', marker_color='rgba(135, 206, 235, 0.7)'))
        fig1.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['REAL_RS'], name='REALIZADO', marker_color='rgba(0, 102, 204, 1)'))
        
        for i, r in df_emp.iterrows():
            diff = r['REAL_RS'] - r['ORC_RS']
            cor, txt = ("red", "ESTOURO") if diff > 0 else ("green", "SALDO")
            fig1.add_annotation(x=r['NOME'], y=0, text=f"<b>{txt}:</b><br><b>R$ {abs(diff):,.2f}</b>", showarrow=False, yshift=-75, font=dict(color=cor, size=11))
        
        fig1.update_layout(title="<b>COMPARAÇÃO FINANCEIRA (R$)</b>", barmode='group', template="plotly_white", font=dict(color="black", family="Arial Black"), margin=dict(b=150))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Gráfico de Consumo Aprovado
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['FORE_L'], name='ORÇADO', marker_color='rgba(135, 206, 235, 0.7)'))
        fig2.add_trace(go.Bar(x=df_emp['NOME'], y=df_emp['REAL_L'], name='REALIZADO', marker_color='rgba(0, 102, 204, 1)'))
        
        fig2.update_layout(title="<b>COMPARAÇÃO DE CONSUMO (LITROS)</b>", barmode='group', template="plotly_white", font=dict(color="black", family="Arial Black"), margin=dict(b=150))
        st.plotly_chart(fig2, use_container_width=True)

    # --- ANÁLISE POR CICLO (SÓ PIZZAS, CONFORME ÚLTIMA SOLICITAÇÃO) ---
    st.divider()
    st.markdown("<h3 style='text-align: center; color: black;'><b>DISTRIBUIÇÃO POR CICLO (AF2:AJ3)</b></h3>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        fig3 = px.pie(df_ciclo, values='REAL_RS', names='CICLO', title='<b>PARTICIPAÇÃO NO GASTO (R$)</b>')
        fig3.update_traces(textfont_color="black", textinfo='percent+label', marker=dict(line=dict(color='black', width=1)))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = px.pie(df_ciclo, values='REAL_L', names='CICLO', title='<b>PARTICIPAÇÃO NO VOLUME (L)</b>')
        fig4.update_traces(textfont_color="black", textinfo='percent+label', marker=dict(line=dict(color='black', width=1)))
        st.plotly_chart(fig4, use_container_width=True)
