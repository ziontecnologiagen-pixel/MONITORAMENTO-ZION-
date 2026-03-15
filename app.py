import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# ... (Configuração e carregar_dados iguais) ...

def renderizar_rancho(df):
    # Ajustando o mapeamento baseado na sua imagem da planilha
    # Se o Pandas leu a linha preta como cabeçalho, os nomes serão "2", "7", "11", etc.
    # Se ele leu a linha de baixo, serão "STATUS", "SC", "EMPURRADOR".
    
    # Vamos criar uma função para encontrar a coluna pelo que está escrito nela
    def encontrar_coluna(df, nomes_possiveis):
        for nome in nomes_possiveis:
            for col in df.columns:
                if str(nome).upper() in str(col).upper():
                    return col
        return None

    col_status = encontrar_coluna(df, ["STATUS", "2"])
    col_sc = encontrar_coluna(df, ["SC", "7"])
    col_emp = encontrar_coluna(df, ["EMPURRADOR", "11"])
    col_entrega = encontrar_coluna(df, ["DATA ENTREGA", "ENTREGA", "18"]) # Verifique se Entrega é 18
    col_local = encontrar_coluna(df, ["LOCAL", "20"])

    # Filtro de Status
    df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()

    # --- LÓGICA DE DATA (MAIS SIMPLES PARA NÃO ERRAR) ---
    # Tentamos converter, o que não for data vira "NaT"
    df_prog['DT_OBJ'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
    
    # Hoje é 14/03/2026. Vamos pegar tudo de HOJE em diante.
    hoje = pd.Timestamp(2026, 3, 14)
    
    # Se a conversão de data funcionar, filtramos. Se falhar, mantemos (para garantir)
    df_prog = df_prog[(df_prog['DT_OBJ'] >= hoje) | (df_prog['DT_OBJ'].isna())]
    
    # Ordenar
    df_prog = df_prog.sort_values(by='DT_OBJ', ascending=True)

    st.markdown("### 📅 RANCHOS PROGRAMADOS")
    
    if not df_prog.empty:
        # Exibimos apenas as colunas que você quer
        st.dataframe(
            df_prog[[col_emp, col_sc, col_local, col_entrega]],
            use_container_width=True, 
            hide_index=True,
            column_config={
                col_emp: "EMPURRADOR",
                col_sc: "SC",
                col_local: "LOCAL",
                col_entrega: "DATA ENTREGA"
            }
        )
    else:
        st.info("Nenhum rancho programado encontrado para data futura.")

    # ... (Restante do Realizado)
