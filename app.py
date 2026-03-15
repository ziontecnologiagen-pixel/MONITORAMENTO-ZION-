import streamlit as st
import pandas as pd
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Raio X Empurrador", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    """Lê os dados brutos como string para garantir que a SC (Índice 6) apareça"""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    return pd.read_csv(url, dtype=str).fillna("")

def processar_programacao_unificada():
    # 1. Carrega as duas frentes de dados
    df_rancho = carregar_dados("RANCHO")
    df_odm = carregar_dados("ODM MARÇO")
    
    hoje = pd.to_datetime("2026-03-15")
    lista_programacao = []

    # --- VARREDURA RANCHO (Programados) ---
    if not df_rancho.empty:
        # Filtro: Status (Índice 1) contém "PROGR"
        # Colunas: Empurrador(10), SC(6), Entrega(13)
        df_p = df_rancho[df_rancho.iloc[:, 1].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
        for _, row in df_p.iterrows():
            lista_programacao.append({
                "EMPURRADOR": row.iloc[10],
                "TIPO": "🍎 RANCHO",
                "SC / DOC": row.iloc[6], # Coluna G
                "DATA PROGRAMADA": row.iloc[13],
                "STATUS": "AGUARDANDO"
            })

    # --- VARREDURA ODM (Programados/Pendentes) ---
    if not df_odm.empty:
        # Supondo que no ODM a coluna de Empurrador e Data existam (ajustado pelos índices do seu vídeo)
        # Se o ODM não tiver status "Programado", pegamos os dados gerais de agendamento
        for _, row in df_odm.iterrows():
            # Exemplo baseado na estrutura padrão de ODM que você usa
            if row.iloc[0] != "": # Verifica se a linha não está vazia
                lista_programacao.append({
                    "EMPURRADOR": row.iloc[1], # Ajuste conforme a coluna de empurrador no seu ODM
                    "TIPO": "⛽ COMBUSTÍVEL",
                    "SC / DOC": "ODM", 
                    "DATA PROGRAMADA": row.iloc[0], # Ajuste conforme a coluna de data
                    "STATUS": "PROGRAMADO"
                })

    return pd.DataFrame(lista_programacao)

# --- INTERFACE ---
st.title("🚢 Raio X do Empurrador - Zion")
st.subheader("1ª Tela: Cronograma Unificado (Rancho + ODM)")

df_final = processar_programacao_unificada()

if not df_final.empty:
    # Filtro por Empurrador para o Raio X
    empurradores = sorted(df_final["EMPURRADOR"].unique())
    selecionado = st.selectbox("Selecione o Empurrador para ver a agenda:", ["TODOS"] + empurradores)

    if selecionado != "TODOS":
        df_exibir = df_final[df_final["EMPURRADOR"] == selecionado]
    else:
        df_exibir = df_final

    # Exibição da Tabela Unificada
    st.dataframe(
        df_exibir.sort_values(by="DATA PROGRAMADA"),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Nenhuma programação futura encontrada nas tabelas.")

st.divider()
st.write("**Próximo passo:** Deseja que eu puxe agora os **gastos totais** (valores) de cada um para fechar o Raio X?")
