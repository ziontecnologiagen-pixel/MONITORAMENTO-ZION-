import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão ODM", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
NOME_ABA = "ODM MARÇO"
NOME_ABA_URL = quote(NOME_ABA)

@st.cache_data(ttl=60)
def carregar_dados():
    # URL para ler a aba específica
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    df = pd.read_csv(url)
    
    # Limpeza de nomes de colunas
    df.columns = df.columns.str.strip().str.upper()
    
    # Remove linhas onde o EMPURRADOR está vazio (limpa o final da planilha)
    df = df.dropna(subset=['EMPURRADOR'])
    
    return df

st.title("⛽ Sistema de Gestão de Combustível - Zion")

try:
    df_odm = carregar_dados()

    # --- BLOCO 1: PROGRAMADO ---
    st.markdown("### ⏳ 1. CARGAS PROGRAMADAS")
    
    # Filtro rigoroso para STATUS 'PROGRAMADO'
    df_prog = df_odm[df_odm['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]
    
    if not df_prog.empty:
        # Exibe todas as colunas mapeadas da sua planilha
        st.dataframe(df_prog, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma carga 'PROGRAMADA' encontrada no momento.")

    st.markdown("---")

    # --- BLOCO 2: REALIZADO ---
    st.markdown("### ✅ 2. CARGAS REALIZADAS")
    
    # Filtro rigoroso para STATUS 'REALIZADO'
    df_real = df_odm[df_odm['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        st.dataframe(df_real, use_container_width=True, hide_index=True)
        
        # CÁLCULO FINANCEIRO (Correção do erro \R)
        if 'TOTAL' in df_real.columns:
            # Transformamos em texto, removemos "R$", pontos e trocamos vírgula por ponto
            col_financeira = df_real['TOTAL'].astype(str).str.replace('R$', '', regex=False)
            col_financeira = col_financeira.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            
            total_float = pd.to_numeric(col_financeira, errors='coerce').sum()
            st.metric("Acumulado Realizado (Mês)", f"R$ {total_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    else:
        st.warning("Nenhuma carga 'REALIZADA' encontrada.")

except Exception as e:
    st.error(f"Erro ao processar: {e}")
