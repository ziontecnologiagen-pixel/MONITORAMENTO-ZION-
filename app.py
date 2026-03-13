import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Zion - Gestão ODM", layout="wide")

# Link e Aba (Tratamento para evitar erro de caractere ASCII)
SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
NOME_ABA = "ODM MARÇO"
NOME_ABA_URL = quote(NOME_ABA)

@st.cache_data(ttl=60)
def carregar_dados():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    df = pd.read_csv(url)
    
    # LIMPEZA DE COLUNAS: Remove espaços extras e deixa tudo em MAIÚSCULO
    df.columns = df.columns.str.strip().str.upper()
    
    # Remove linhas vazias baseadas na coluna EMPURRADOR
    if 'EMPURRADOR' in df.columns:
        df = df.dropna(subset=['EMPURRADOR'])
    
    return df

st.title("⛽ Sistema de Gestão de Combustível - Zion")

try:
    df_odm = carregar_dados()

    # --- BLOCO 1: PROGRAMADO ---
    st.markdown("### ⏳ 1. ABASTECIMENTOS PROGRAMADAS")
    
    # Verifica qual o nome exato da coluna de Status na sua planilha
    # Tenta encontrar 'STATUS' ou 'SITUAÇÃO'
    col_status = next((c for c in df_odm.columns if c in ['STATUS', 'SITUAÇÃO', 'SITUACAO']), None)
    
    if col_status:
        df_prog = df_odm[df_odm[col_status].astype(str).str.contains('PROGRAMADO', na=False, case=False)]
        
        if not df_prog.empty:
            # Exibe as colunas que existirem na aba
            colunas_para_exibir = [c for c in ['DATA SOLIC', 'EMPURRADOR', 'LOCAL', 'COMPRA LITROS', col_status] if c in df_prog.columns]
            st.dataframe(df_prog[colunas_para_exibir], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma carga 'PROGRAMADA' encontrada.")
    else:
        st.error("Coluna de 'STATUS' não encontrada na planilha.")

    st.markdown("---")

    # --- BLOCO 2: REALIZADO ---
    st.markdown("### ✅ 2. CARGAS REALIZADAS")
    
    if col_status:
        df_real = df_odm[df_odm[col_status].astype(str).str.contains('REALIZADO', na=False, case=False)]
        
        if not df_real.empty:
            # Lista flexível de colunas para evitar o erro 'not in index'
            cols_real_desejadas = ['DT ENTREGA', 'EMPURRADOR', 'LOCAL', 'VL UNT LTS', 'TOTAL', col_status]
            cols_real_existentes = [c for c in cols_real_desejadas if c in df_real.columns]
            
            st.dataframe(df_real[cols_real_existentes], use_container_width=True, hide_index=True)
            
            # Tenta somar o total se a coluna existir
            if 'TOTAL' in df_real.columns:
                # Converte para número limpando símbolos
                total_val = pd.to_numeric(df_real['TOTAL'].replace(r'[\R\$,]', '', regex=True), errors='coerce').sum()
                st.metric("Total Realizado (Mês)", f"R$ {total_val:,.2f}")
        else:
            st.warning("Nenhuma carga 'REALIZADA' encontrada.")

except Exception as e:
    st.error(f"Erro crítico: {e}")
    st.info("Dica: Certifique-se que os nomes das colunas na Planilha não foram alterados.")
