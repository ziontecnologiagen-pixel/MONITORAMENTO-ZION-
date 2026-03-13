import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Zion - Dashboard Executivo", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
NOME_ABA = "ODM MARÇO"
NOME_ABA_URL = quote(NOME_ABA)

@st.cache_data(ttl=60)
def carregar_dados():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    # Lemos as colunas necessárias (A até O)
    df = pd.read_csv(url, usecols=range(15))
    df.columns = df.columns.str.strip().str.upper()
    df = df.dropna(subset=['EMPURRADOR'])
    
    # Tratamento de dados para cálculo
    df['LITROS_NUM'] = pd.to_numeric(df['COMPRA LITROS'].astype(str).str.upper().str.replace('L', '', regex=False).str.replace('.', '', regex=False).str.strip(), errors='coerce').fillna(0)
    df['VALOR_NUM'] = pd.to_numeric(df['TOTAL'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(0)
    
    return df

st.title("🚢 Monitoramento Estratégico Zion - ODM")
st.markdown("---")

try:
    df = carregar_dados()

    # --- TABELA 1: RESUMO CONSOLIDADO POR EMPURRADOR ---
    st.subheader("📊 Resumo de Consumo por Empurrador")
    
    # Criando o resumo agrupado
    resumo = df.groupby('EMPURRADOR').apply(lambda x: pd.Series({
        'LTS REALIZADO': x[x['STATUS'].str.contains('REALIZADO', na=False, case=False)]['LITROS_NUM'].sum(),
        'VALOR REALIZADO': x[x['STATUS'].str.contains('REALIZADO', na=False, case=False)]['VALOR_NUM'].sum(),
        'LTS PROGRAMADO': x[x['STATUS'].str.contains('PROGRAMADO', na=False, case=False)]['LITROS_NUM'].sum(),
        'VALOR PROGRAMADO': x[x['STATUS'].str.contains('PROGRAMADO', na=False, case=False)]['VALOR_NUM'].sum()
    })).reset_index()

    # Formatação para exibição amigável
    resumo_view = resumo.copy()
    for col in ['VALOR REALIZADO', 'VALOR PROGRAMADO']:
        resumo_view[col] = resumo_view[col].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    for col in ['LTS REALIZADO', 'LTS PROGRAMADO']:
        resumo_view[col] = resumo_view[col].apply(lambda x: f"{x:,.0f} L".replace(',', '.'))

    st.table(resumo_view) # Usando st.table para ficar mais "limpo" e fixo

    st.markdown("---")

    # --- TABELA 2: APENAS PROGRAMADOS (VISÃO COMPACTA) ---
    st.subheader("⏳ Próximas Cargas Programadas")
    
    df_prog = df[df['STATUS'].str.contains('PROGRAMADO', na=False, case=False)]
    
    if not df_prog.empty:
        # Selecionando colunas B(DATA SOLIC), C(EMPURRADOR), D(LOCAL), F(COMPRA LITROS), L(STATUS)
        # Nota: O índice do Python começa em 0, então B=1, C=2, D=3, F=5, L=11
        colunas_indices = [1, 2, 3, 5, 11]
        colunas_nomes = [df.columns[i] for i in colunas_indices]
        
        df_compacto = df_prog[colunas_nomes]
        
        # Exibição compacta sem barra de rolagem se possível
        st.dataframe(df_compacto, use_container_width=True, hide_index=True)
    else:
        st.info("Não há programações pendentes.")

except Exception as e:
    st.error(f"Erro ao gerar dashboard: {e}")

st.caption("Visualização simplificada para tomada de decisão rápida.")
