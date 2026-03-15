import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zion - Dashboard Premium", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def formatar_moeda(valor):
    if not valor or valor == "0": return 0.0
    try:
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO DOS DADOS ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # Mapeamento conforme image_0fc5da: U(20), V(21), X(23)
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20]
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(formatar_moeda)
    df_fin['REAL'] = df_raw.iloc[:, 23].apply(formatar_moeda)
    df_fin = df_fin[df_fin['EMPURRADOR'] != "E/M"].reset_index(drop=True)

    st.title("🚢 Zion Premium - Raio X de Performance Financeira")
    st.markdown("### Comparativo de Aquisição ODM (Previsto vs Real)")

    # --- CRIAÇÃO DO GRÁFICO ELEGANTE ---
    fig = go.Figure()

    # Barra Previsto (Efeito Metalizado Cinza/Platina)
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['PREVISTO'],
        name='Orcado (V)',
        marker=dict(
            color='rgba(192, 192, 192, 0.6)', # Prata vazado
            line=dict(color='rgb(192, 192, 192)', width=2) # Contorno sólido
        ),
        text=df_fin['PREVISTO'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))

    # Barra Real (Efeito Metalizado Ouro/Bronze)
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['REAL'],
        name='Gasto Real (X)',
        marker=dict(
            color='rgba(212, 175, 55, 0.6)', # Ouro vazado
            line=dict(color='rgb(212, 175, 55)', width=2) # Contorno sólido
        ),
        text=df_fin['REAL'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))

    # Estilização do Layout
    fig.update_layout(
        template="plotly_dark", # Fundo escuro para destacar o "metal"
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif", size=14, color="white"),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', tickprefix="R$ "),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- TABELA DE APOIO ESTILIZADA ---
    st.divider()
    st.markdown("#### Detalhamento de Custos por Empurrador")
    st.dataframe(
        df_fin.style.format({'PREVISTO': 'R$ {:,.2f}', 'REAL': 'R$ {:,.2f}'}),
        use_container_width=True,
        hide_index=True
    )
