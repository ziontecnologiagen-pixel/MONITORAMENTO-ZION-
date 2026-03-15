import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão Integrada", layout="centered")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    # Carregamos tudo como string para evitar erros de leitura
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def renderizar_rancho(df):
    try:
        # AJUSTE CONFORME O VÍDEO:
        # No vídeo, a coluna ENTREGA é a 14. No Pandas (começando do 0), ela é o índice 13.
        # A coluna STATUS é a B (índice 1).
        # A coluna EMPURRADOR é a K (índice 10).
        col_status = df.columns[1]   
        col_emp = df.columns[10]     
        col_entrega = df.columns[13] # ÍNDICE 13 É A COLUNA 14 (N) DO VÍDEO
        col_local = df.columns[19]   # Coluna T (Local)

        # 1. Filtro de Status "PROGRAMADO"
        df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()

        # 2. Filtro de Data (Somente Futuro)
        # Convertendo a coluna 14 para data
        df_prog['DT_OBJ'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
        
        # Data de hoje conforme o sistema
        hoje = pd.Timestamp(2026, 3, 15)

        # FILTRO CRUCIAL: Só mostra se a data for de hoje em diante (21/03 e 23/03 vão aparecer)
        df_final = df_prog[df_prog['DT_OBJ'] >= hoje].copy()
        
        # Ordenação para a data mais próxima ficar no topo
        df_final = df_final.sort_values(by='DT_OBJ', ascending=True)

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        
        if not df_final.empty:
            st.dataframe(
                df_final[[col_emp, col_entrega, col_local]],
                use_container_width=True, 
                hide_index=True,
                column_config={
                    col_emp: "EMPURRADOR",
                    col_entrega: "DATA ENTREGA",
                    col_local: "LOCAL"
                }
            )
        else:
            st.info("Nenhum rancho programado para datas futuras (21/03, 23/03) encontrado.")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")

# --- INTERFACE ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

if aba == "Rancho":
    df_rancho = carregar_dados("RANCHO")
    renderizar_rancho(df_rancho)
else:
    # Lógica do Combustível (mantida a que funcionava)
    df_odm = carregar_dados("ODM MARÇO")
    df_odm.columns = [str(c).strip().upper() for c in df_odm.columns]
    st.markdown("### ⛽ Combustível: Programado")
    prog_odm = df_odm[df_odm['STATUS'].str.contains('PROGR', na=False)]
    st.dataframe(prog_odm[['EMPURRADOR', 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)
