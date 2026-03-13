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
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    # Lemos as colunas principais (A até O)
    df = pd.read_csv(url, usecols=range(15))
    df.columns = df.columns.str.strip().str.upper()
    df = df.dropna(subset=['EMPURRADOR'])
    return df

def limpar_moeda(coluna):
    """Converte coluna de R$ em número somável"""
    return pd.to_numeric(
        coluna.astype(str)
        .str.replace('R$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .str.strip(), 
        errors='coerce'
    ).sum()

def limpar_litros(coluna):
    """Remove o 'L' e os pontos para conseguir somar os litros"""
    return pd.to_numeric(
        coluna.astype(str)
        .str.upper()
        .str.replace('L', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.strip(),
        errors='coerce'
    ).sum()

st.title("⛽ Sistema de Gestão de Combustível - Zion")
st.markdown("---")

try:
    df_odm = carregar_dados()

    # --- BLOCO 1: PROGRAMADO ---
    st.subheader("⏳ 1. CARGAS PROGRAMADAS (A REALIZAR)")
    
    if 'STATUS' in df_odm.columns:
        df_prog = df_odm[df_odm['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]
        
        if not df_prog.empty:
            col1, col2 = st.columns(2)
            with col1:
                # Soma litros limpando o "L" e o ponto
                total_lts_prog = limpar_litros(df_prog['COMPRA LITROS'])
                st.metric("Litros Programados", f"{total_lts_prog:,.0f} L".replace(',', '.'))
            with col2:
                total_val_prog = limpar_moeda(df_prog['TOTAL'])
                st.metric("Custo Previsto", f"R$ {total_val_prog:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            
            st.dataframe(df_prog, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma carga 'PROGRAMADA' encontrada.")
    
    st.markdown("---")

    # --- BLOCO 2: REALIZADO ---
    st.subheader("✅ 2. CARGAS REALIZADAS (CONCLUÍDO)")
    
    if 'STATUS' in df_odm.columns:
        df_real = df_odm[df_odm['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
        
        if not df_real.empty:
            col3, col4 = st.columns(2)
            with col3:
                # Soma litros do que já foi entregue
                total_lts_real = limpar_litros(df_real['COMPRA LITROS'])
                st.metric("Litros Realizados", f"{total_lts_real:,.0f} L".replace(',', '.'))
            with col4:
                total_val_real = limpar_moeda(df_real['TOTAL'])
                st.metric("Total Investido", f"R$ {total_val_real:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            
            st.dataframe(df_real, use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhuma carga 'REALIZADA' encontrada.")

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
