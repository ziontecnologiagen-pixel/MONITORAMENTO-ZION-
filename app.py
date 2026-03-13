import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# 1. CONFIGURAÇÃO (Centralizado e Compacto)
st.set_page_config(page_title="Zion - Monitoramento", layout="centered")

st.markdown("""
    <style>
    .main .block-container { max-width: 850px; padding-top: 1rem; }
    [data-testid="stMetricValue"] {font-size: 1.1rem !important;}
    h3 {font-size: 1rem !important; margin-bottom: 0.2rem; font-weight: bold;}
    [data-testid="stVerticalBlock"] {gap: 0.4rem !important;}
    .stDataFrame {font-size: 12px !important;}
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
NOME_ABA = "ODM MARÇO"
NOME_ABA_URL = quote(NOME_ABA)

@st.cache_data(ttl=30)
def carregar_dados():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    
    # Tratamento de Data para o Robô comparar com "Hoje"
    # Assume formato DD/MM/YYYY ou similar que o pandas reconheça
    df['DATA_DT'] = pd.to_datetime(df['DATA SOLIC'], dayfirst=True, errors='coerce')
    
    return df

try:
    df_full = carregar_dados()
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # --- PROCESSAMENTO OPERACIONAL ---
    df_op = df_full.iloc[0:100, 0:15].copy()
    col_emp = df_op.columns[2] # EMPURRADOR
    
    # Limpeza para cálculos de cabeçalho
    df_op['VALOR_NUM'] = pd.to_numeric(df_op['TOTAL'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(0)
    df_op['LTS_NUM'] = pd.to_numeric(df_op['COMPRA LITROS'].astype(str).str.upper().str.replace('L', '', regex=False).str.replace('.', '', regex=False).str.strip(), errors='coerce').fillna(0)

    st.title("⛽ Gestão de Cargas Zion")

    # --- TABELA 1: PROGRAMADO (DE HOJE PARA FRENTE) ---
    st.markdown("### ⏳ Programado (A partir de Hoje)")
    
    # Filtro: Status Programado + Data >= Hoje
    df_prog = df_op[
        (df_op['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)) & 
        (df_full['DATA_DT'] >= hoje)
    ]
    
    if not df_prog.empty:
        # Cabeçalho de Totais para Programados
        p1, p2 = st.columns(2)
        p1.metric("Total Programado (L)", f"{df_prog['LTS_NUM'].sum():,.0f}L".replace(',', '.'))
        p2.metric("Total Programado (R$)", f"R${df_prog['VALOR_NUM'].sum():,.0f}".replace(',', '.'))
        
        # Colunas: Empurrador | SC | Local | Entrega
        st.dataframe(
            df_prog[[col_emp, 'SC', 'LOCAL', 'DT ENTREGA']],
            use_container_width=True, hide_index=True,
            column_config={
                col_emp: st.column_config.TextColumn("Empurrador", width=150),
                "SC": st.column_config.TextColumn("SC", width=80),
                "LOCAL": st.column_config.TextColumn("Local", width=120),
                "DT ENTREGA": st.column_config.TextColumn("Entrega", width=100)
            }
        )
    else:
        st.info("Nenhuma carga programada para datas futuras.")

    st.markdown("---")

    # --- TABELA 2: REALIZADO (DENTRO DO PERÍODO) ---
    st.markdown("### ✅ Realizado no Período")
    
    df_real = df_op[df_op['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        # Cabeçalho de Totais para Realizados
        r1, r2 = st.columns(2)
        r1.metric("Total Realizado (L)", f"{df_real['LTS_NUM'].sum():,.0f}L".replace(',', '.'))
        r2.metric("Total Realizado (R$)", f"R${df_real['VALOR_NUM'].sum():,.0f}".replace(',', '.'))

        # Colunas: Empurrador | SC | Local | Entrega
        st.dataframe(
            df_real[[col_emp, 'SC', 'LOCAL', 'DT ENTREGA']],
            use_container_width=True, hide_index=True,
            column_config={
                col_emp: st.column_config.TextColumn("Empurrador", width=150),
                "SC": st.column_config.TextColumn("SC", width=80),
                "LOCAL": st.column_config.TextColumn("Local", width=120),
                "DT ENTREGA": st.column_config.TextColumn("Entrega", width=100)
            }
        )
    else:
        st.warning("Nenhuma carga realizada encontrada no período.")

except Exception as e:
    st.error(f"Erro na leitura dos dados: {e}")
