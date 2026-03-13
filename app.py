import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - ODM Real-Time", layout="wide")

# Link e Nome da Aba (Codificando o Ç para evitar erro)
SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
NOME_ABA = "ODM MARÇO"
NOME_ABA_URL = quote(NOME_ABA) # Transforma "MARÇO" em algo que o link entende

@st.cache_data(ttl=60)
def carregar_dados():
    # URL formatada para ler a aba específica corrigindo o erro de caractere
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    df = pd.read_csv(url)
    # Remove linhas totalmente vazias que o importrange costuma gerar
    df = df.dropna(subset=['EMPURRADOR'])
    return df

st.title("⛽ Gestão de Combustível - Zion")

try:
    df_odm = carregar_dados()

    # --- BLOCO 1: PROGRAMADO (CARGAS A REALIZAR) ---
    st.markdown("### ⏳ 1. CARGAS PROGRAMADAS")
    # Filtra onde o STATUS é 'PROGRAMADO'
    df_prog = df_odm[df_odm['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]
    
    if not df_prog.empty:
        # Colunas específicas para o operacional de programação
        cols_p = ['DATA SOLIC', 'EMPURRADOR', 'LOCAL', 'COMPRA LITROS', 'STATUS']
        st.dataframe(df_prog[cols_p], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma carga programada encontrada no momento.")

    st.markdown("---")

    # --- BLOCO 2: REALIZADO (CONCLUÍDAS) ---
    st.markdown("### ✅ 2. CARGAS REALIZADAS")
    # Filtra onde o STATUS é 'REALIZADO'
    df_real = df_odm[df_odm['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        # Colunas específicas para conferência de entrega
        cols_r = ['DT ENTREGA', 'EMPURRADOR', 'LOCAL', 'VL UNT LTS', 'TOTAL', 'STATUS']
        st.dataframe(df_real[cols_r], use_container_width=True, hide_index=True)
        
        # Cálculo de Valor Realizado (Soma da coluna TOTAL)
        # Limpa o R$ e a vírgula antes de somar
        total_limpo = df_real['TOTAL'].replace(r'[\R\$,]', '', regex=True).astype(float).sum()
        st.metric("Total Investido no Mês", f"R$ {total_limpo:,.2f}")
    else:
        st.warning("Ainda não constam cargas 'REALIZADAS' nesta aba.")

except Exception as e:
    st.error(f"Erro ao processar: {e}")
    st.info("Dica: Verifique se a planilha está como 'Qualquer pessoa com o link'.")
