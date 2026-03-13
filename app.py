import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Zion - Monitoramento ODM", layout="wide")

# Link da sua planilha
SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
# O GID da aba "ODM MARÇO" (Se não for esse, o código tentará pelo nome)
# Nota: Para link público, o ideal é usar o nome da aba codificado ou o GID 0 se for a primeira.
ABA_NOME = "ODM MARÇO"

@st.cache_data(ttl=60) # Atualiza a cada 1 minuto
def carregar_dados_odm():
    # URL formatada para ler a aba específica pelo nome
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=ODM+MARÇO"
    df = pd.read_csv(url)
    
    # Limpeza básica para evitar erro de linha vazia no importrange
    df = df.dropna(subset=['EMPURRADOR'])
    return df

st.title("⛽ Gestão de Combustível - Zion")
st.subheader(f"📅 Aba: {ABA_NOME}")

try:
    df_odm = carregar_dados_odm()

    # --- BLOCO 1: PROGRAMADO ---
    # Filtra onde a coluna STATUS (ou SITUAÇÃO) contém "PROGRAMADO"
    # No vídeo, vi que você usa a coluna STATUS para definir o fluxo
    df_prog = df_odm[df_odm['STATUS'].str.contains('PROGRAMADO', na=False, case=False)]
    
    st.markdown("### ⏳ 1. CARGAS PROGRAMADAS (A REALIZAR)")
    if not df_prog.empty:
        # Colunas que interessam para quem está esperando a carga
        cols_prog = ['DATA SOLIC', 'EMPURRADOR', 'LOCAL', 'COMPRA LITROS', 'STATUS']
        # Filtra apenas as colunas que realmente existem na sua aba
        cols_finais_p = [c for c in cols_prog if c in df_prog.columns]
        st.dataframe(df_prog[cols_finais_p], use_container_width=True, hide_index=True)
    else:
        st.info("Não há cargas com status 'PROGRAMADO' no momento.")

    st.markdown("---")

    # --- BLOCO 2: REALIZADO ---
    # Filtra onde o status é "REALIZADO"
    df_real = df_odm[df_odm['STATUS'].str.contains('REALIZADO', na=False, case=False)]
    
    st.markdown("### ✅ 2. CARGAS REALIZADAS (HISTÓRICO)")
    if not df_real.empty:
        # Colunas para conferência do que já foi entregue
        cols_real = ['DT ENTREGA', 'EMPURRADOR', 'LOCAL', 'VL UNT LTS', 'TOTAL', 'STATUS']
        cols_finais_r = [c for c in cols_real if c in df_real.columns]
        st.dataframe(df_real[cols_finais_r], use_container_width=True, hide_index=True)
        
        # Cálculo de quanto já foi realizado no mês
        if 'TOTAL' in df_real.columns:
            # Remove R$ e converte para número para somar
            total_valor = df_real['TOTAL'].replace(r'[\R\$,]', '', regex=True).astype(float).sum()
            st.metric("Total Gasto no Mês (Realizado)", f"R$ {total_valor:,.2f}")
    else:
        st.warning("Nenhuma carga com status 'REALIZADO' encontrada.")

except Exception as e:
    st.error(f"Erro ao acessar a aba '{ABA_NOME}': {e}")
    st.info("Verifique se o nome da aba na sua planilha é exatamente 'ODM MARÇO' (com espaço e sem aspas).")

st.caption(f"Sincronizado com a Matriz Zion às {datetime.now().strftime('%H:%M:%S')}")
