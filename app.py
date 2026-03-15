import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Raio X Financeiro", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("")

def limpar_valor(valor):
    """Converte strings de moeda (ex: R$ 1.200,50) em números para o gráfico"""
    if not valor: return 0.0
    try:
        # Remove símbolos e ajusta separadores decimais
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- CARREGAMENTO ---
df_odm_raw = carregar_dados("ODM MARÇO")

# --- PROCESSAMENTO FINANCEIRO ---
st.title("💰 Raio X Financeiro - Combustível (ODM)")

if not df_odm_raw.empty:
    # 1. Identificar colunas: Nome do Empurrador (Índice 1) e Valor Total (Ajustar Índice conforme sua planilha)
    # Supondo que o Valor Total esteja na Coluna G (Índice 6) ou similar no ODM
    df_financeiro = df_odm_raw.copy()
    
    # IMPORTANTE: Altere o número '6' abaixo para o índice da coluna que tem o VALOR em R$ no seu ODM
    df_financeiro['VALOR_NUM'] = df_financeiro.iloc[:, 6].apply(limpar_valor) 
    
    # Agrupa gastos por empurrador
    gastos_por_empurrador = df_financeiro.groupby(df_financeiro.iloc[:, 1])['VALOR_NUM'].sum().reset_index()
    gastos_por_empurrador.columns = ['EMPURRADOR', 'TOTAL_GASTO']
    gastos_por_empurrador = gastos_por_empurrador.sort_values(by='TOTAL_GASTO', ascending=False)

    # --- EXIBIÇÃO DO GRÁFICO FINANCEIRO ---
    fig_custo = px.bar(
        gastos_por_empurrador, 
        x='EMPURRADOR', 
        y='TOTAL_GASTO',
        title="Total Gasto com ODM por Empurrador (R$)",
        text_auto='.2s',
        color='TOTAL_GASTO',
        color_continuous_scale='Reds'
    )
    fig_custo.update_traces(texttemplate='R$ %{y:.2f}', textposition='outside')
    st.plotly_chart(fig_custo, use_container_width=True)

    # --- MÉTRICAS RÁPIDAS (Cards) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Gasto Total Frota", f"R$ {gastos_por_empurrador['TOTAL_GASTO'].sum():,.2f}")
    col2.metric("Maior Consumidor", gastos_por_empurrador.iloc[0]['EMPURRADOR'])
    col3.metric("Média por Empurrador", f"R$ {gastos_por_empurrador['TOTAL_GASTO'].mean():,.2f}")

st.divider()

# --- TABELAS DETALHADAS LOGO ABAIXO ---
st.markdown("### ⛽ Detalhamento de Lançamentos (ODM)")
if not df_odm_raw.empty:
    st.dataframe(df_odm_raw, use_container_width=True, hide_index=True)
