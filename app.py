import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zion - Dashboard Integrado", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def formatar_valor(valor):
    if not valor or valor == "0": return 0.0
    try:
        return float(str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip())
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # Preparação de Dados
    df = pd.DataFrame()
    df['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df['PREVISTO_RS'] = df_raw.iloc[:, 21].apply(formatar_valor)
    df['REAL_RS'] = df_raw.iloc[:, 23].apply(formatar_valor)
    df['FORECAST_L'] = df_raw.iloc[:, 22].apply(formatar_valor)
    df['REAL_L'] = df_raw.iloc[:, 25].apply(formatar_valor)
    
    # Filtro da Frota Ativa
    validos = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df = df[df['EMPURRADOR'].isin(validos)].reset_index(drop=True)

    st.markdown("<h1 style='text-align: center; color: black;'><b>PAINEL DE PERFORMANCE ZION</b></h1>", unsafe_allow_headers=True)

    # --- CRIAÇÃO DAS COLUNAS (LADO A LADO) ---
    col1, col2 = st.columns(2)

    with col1:
        # GRAFICO 1: FINANCEIRO
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df['EMPURRADOR'], y=df['PREVISTO_RS'], name='<b>ORÇADO</b>', marker_color='rgba(135, 206, 235, 0.6)', text=df['PREVISTO_RS'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'), textposition='outside'))
        fig1.add_trace(go.Bar(x=df['EMPURRADOR'], y=df['REAL_RS'], name='<b>REALIZADO</b>', marker_color='rgba(0, 102, 204, 0.9)', text=df['REAL_RS'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'), textposition='outside'))
        
        for i, r in df.iterrows():
            diff = r['REAL_RS'] - r['PREVISTO_RS']
            cor = "red" if diff > 0 else "green"
            lab = "ESTOURO" if diff > 0 else "SALDO"
            fig1.add_annotation(x=r['EMPURRADOR'], y=0, text=f"<b>{lab}:</b><br><b>R$ {abs(diff):,.2f}</b>", showarrow=False, yshift=-70, font=dict(color=cor, size=11))

        fig1.update_layout(title="<b>REALIZADO VS ORÇADO (R$)</b>", template="plotly_white", barmode='group', height=600, margin=dict(b=150), font=dict(color="black"), xaxis=dict(tickfont=dict(family="Arial Black", size=12)))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # GRAFICO 2: LITROS
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df['EMPURRADOR'], y=df['FORECAST_L'], name='<b>ORÇADO (L)</b>', marker_color='rgba(135, 206, 235, 0.6)', text=df['FORECAST_L'].apply(lambda x: f'<b>{x:,.0f} L</b>'), textposition='outside'))
        fig2.add_trace(go.Bar(x=df['EMPURRADOR'], y=df['REAL_L'], name='<b>REALIZADO (L)</b>', marker_color='rgba(0, 102, 204, 0.9)', text=df['REAL_L'].apply(lambda x: f'<b>{x:,.0f} L</b>'), textposition='outside'))
        
        for i, r in df.iterrows():
            diff = r['REAL_L'] - r['FORECAST_L']
            cor = "red" if diff > 0 else "green"
            lab = "ESTOURO" if diff > 0 else "SALDO"
            fig2.add_annotation(x=r['EMPURRADOR'], y=0, text=f"<b>{lab}:</b><br><b>{abs(diff):,.0f} L</b>", showarrow=False, yshift=-70, font=dict(color=cor, size=11))

        fig2.update_layout(title="<b>REALIZADO VS ORÇADO (LITROS)</b>", template="plotly_white", barmode='group', height=600, margin=dict(b=150), font=dict(color="black"), xaxis=dict(tickfont=dict(family="Arial Black", size=12)))
        st.plotly_chart(fig2, use_container_width=True)

    # Tabela consolidada abaixo
    st.markdown("### **DETALHAMENTO TÉCNICO E FINANCEIRO**")
    st.dataframe(df.style.set_properties(**{'font-weight': 'bold', 'color': 'black'}), use_container_width=True, hide_index=True)
