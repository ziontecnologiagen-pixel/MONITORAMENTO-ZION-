import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard Financeiro ODM", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def limpar_financeiro(valor):
    """Converte 'R$ 510.300,00' ou '90000' em float puro"""
    if not valor or valor == "0": return 0.0
    try:
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO DOS DADOS (BASEADO NA IMAGEM image_0fc5da) ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # Mapeamento exato conforme a imagem enviada:
    # Coluna U (20): E/M (Empurrador)
    # Coluna V (21): PREVISTO
    # Coluna Z (25): ODM / REAL (Gasto real de ODM)
    # Coluna AD (29): CONTÁBIL (Gasto total acumulado)
    
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20]
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(limpar_financeiro)
    df_fin['ODM_REAL'] = df_raw.iloc[:, 25].apply(limpar_financeiro)
    df_fin['CONTABIL'] = df_raw.iloc[:, 29].apply(limpar_financeiro)
    
    # Filtra linhas vazias ou cabeçalhos
    df_fin = df_fin[df_fin['EMPURRADOR'] != "E/M"].reset_index(drop=True)

    # --- DASHBOARD ---
    st.title("📊 Raio X Financeiro - Aquisição ODM")
    
    # 1. MÉTRICAS GERAIS (Cards)
    c1, c2, c3 = st.columns(3)
    total_odm = df_fin['ODM_REAL'].sum()
    c1.metric("Total Gasto ODM (Real)", f"R$ {total_odm:,.2f}")
    c2.metric("Total Contábil Acumulado", f"R$ {df_fin['CONTABIL'].sum():,.2f}")
    c3.metric("Maior Consumo (ODM)", df_fin.loc[df_fin['ODM_REAL'].idxmax(), 'EMPURRADOR'])

    st.divider()

    # 2. GRÁFICO DE BARRAS: ODM REAL POR EMPURRADOR
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig_bar = px.bar(
            df_fin.sort_values('ODM_REAL', ascending=False),
            x='EMPURRADOR',
            y='ODM_REAL',
            title="Gasto Real de ODM por Empurrador (Coluna Z)",
            text_auto='.2s',
            color='ODM_REAL',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        # GRÁFICO DE COMPARAÇÃO: PREVISTO VS REAL
        fig_comp = px.bar(
            df_fin, 
            x='EMPURRADOR', 
            y=['PREVISTO', 'ODM_REAL'],
            title="Comparativo: Previsto (V) vs Real (Z)",
            barmode='group'
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    st.divider()

    # 3. TABELA DE CONFERÊNCIA (ESTILO PLANILHA)
    st.markdown("### 📋 Resumo Financeiro Detalhado")
    st.dataframe(
        df_fin.style.format({
            'PREVISTO': 'R$ {:,.2f}',
            'ODM_REAL': 'R$ {:,.2f}',
            'CONTABIL': 'R$ {:,.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )
