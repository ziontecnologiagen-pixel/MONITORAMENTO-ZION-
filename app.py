import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Zion - Gestão ODM", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
NOME_ABA = "ODM MARÇO"
NOME_ABA_URL = quote(NOME_ABA)

@st.cache_data(ttl=60)
def carregar_dados():
    # Carregamos a planilha
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    
    # IMPORTANTE: Lemos apenas até a coluna O (as primeiras 15 colunas) para evitar duplicatas
    df = pd.read_csv(url, usecols=range(15))
    
    # Padronização de nomes
    df.columns = df.columns.str.strip().str.upper()
    
    # Limpa linhas onde o EMPURRADOR está vazio
    df = df.dropna(subset=['EMPURRADOR'])
    
    return df

st.title("⛽ Sistema de Gestão de Combustível - Zion")

try:
    df_odm = carregar_dados()

    # --- BLOCO 1: PROGRAMADO ---
    st.markdown("### ⏳ 1. CARGAS PROGRAMADAS")
    
    # Filtro para STATUS 'PROGRAMADO'
    if 'STATUS' in df_odm.columns:
        df_prog = df_odm[df_odm['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]
        
        if not df_prog.empty:
            st.dataframe(df_prog, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma carga 'PROGRAMADA' encontrada.")
    
    st.markdown("---")

    # --- BLOCO 2: REALIZADO ---
    st.markdown("### ✅ 2. CARGAS REALIZADAS")
    
    # Filtro para STATUS 'REALIZADO'
    if 'STATUS' in df_odm.columns:
        df_real = df_odm[df_odm['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
        
        if not df_real.empty:
            st.dataframe(df_real, use_container_width=True, hide_index=True)
            
            # CÁLCULO DO TOTAL (Tratamento seguro para R$)
            if 'TOTAL' in df_real.columns:
                try:
                    # Limpa R$, pontos e troca vírgula por ponto de forma segura
                    soma_total = df_real['TOTAL'].astype(str).str.replace('R$', '', regex=False)
                    soma_total = soma_total.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                    valor_final = pd.to_numeric(soma_total, errors='coerce').sum()
                    
                    st.metric("Total Acumulado (Realizado)", f"R$ {valor_final:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                except:
                    pass
        else:
            st.warning("Nenhuma carga 'REALIZADA' encontrada.")

except Exception as e:
    st.error(f"Erro ao processar: {e}")
    st.info("Dica: O sistema agora ignora colunas extras para evitar erro de duplicidade.")
