import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard Financeiro", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def formatar_moeda(valor):
    """Converte strings financeiras da planilha para float"""
    if not valor or valor == "0": return 0.0
    try:
        # Remove R$, pontos de milhar e troca vírgula por ponto
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # MAPEAMENTO DIRETO PELAS COLUNAS DA IMAGEM
    # U = Índice 20 (Empurrador)
    # V = Índice 21 (Previsto)
    # X = Índice 23 (Contabil/Real)
    
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20]
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(formatar_moeda)
    df_fin['REAL'] = df_raw.iloc[:, 23].apply(formatar_moeda)
    
    # Limpa cabeçalhos e linhas vazias
    df_fin = df_fin[df_fin['EMPURRADOR'] != "E/M"].reset_index(drop=True)

    # --- TELA DO DASHBOARD ---
    st.title("📊 Comparativo Financeiro: Previsto vs Real")
    st.subheader("Análise de Orçamento de Compra ODM por Empurrador")

    # CRIANDO O GRÁFICO DE BARRAS CRUZADO
    fig = go.Figure()

    # Barra do Previsto (V)
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['PREVISTO'],
        name='Orçado (Previsto)',
        marker_color='#1f77b4',
        text=df_fin['PREVISTO'].apply(lambda x: f'R$ {x:,.2f}'),
        textposition='outside'
    ))

    # Barra do Real (X)
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['REAL'],
        name='Gasto Real (Contábil)',
        marker_color='#d62728',
        text=df_fin['REAL'].apply(lambda x: f'R$ {x:,.2f}'),
        textposition='outside'
    ))

    fig.update_layout(
        barmode='group',
        xaxis_title="Empurrador",
        yaxis_title="Valores em R$",
        legend_title="Legenda",
        height=600,
        yaxis=dict(tickprefix="R$ ")
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- TABELA DE APOIO ---
    st.divider()
    st.markdown("### 📝 Dados Consolidados")
    st.dataframe(
        df_fin.style.format({'PREVISTO': 'R$ {:,.2f}', 'REAL': 'R$ {:,.2f}'}),
        use_container_width=True,
        hide_index=True
    )

else:
    st.error("Não foi possível carregar os dados da aba ODM MARÇO.")
