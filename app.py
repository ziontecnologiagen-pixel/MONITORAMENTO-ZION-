import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zion - Dashboard Blue Metal", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def formatar_moeda(valor):
    if not valor or valor == "0": return 0.0
    try:
        # Limpeza para garantir conversão numérica
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # U=20 (Empurrador), V=21 (Previsto), X=23 (Contabil/Real)
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20]
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(formatar_moeda)
    df_fin['REAL'] = df_raw.iloc[:, 23].apply(formatar_moeda)
    
    # Remove linhas de cabeçalho ou vazias
    df_fin = df_fin[df_fin['EMPURRADOR'] != "E/M"].reset_index(drop=True)

    st.title("🔵 Zion Dashboard - Performance Blue Metal")
    
    # --- GRÁFICO AZUL VAZADO ---
    fig = go.Figure()

    # Barra Previsto (Azul Ártico Vazado)
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['PREVISTO'],
        name='Previsto (V)',
        marker=dict(
            color='rgba(135, 206, 235, 0.4)', # Azul claro vazado
            line=dict(color='rgb(135, 206, 235)', width=2) # Contorno sólido
        ),
        text=df_fin['PREVISTO'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))

    # Barra Real (Azul Cobalto Vazado)
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['REAL'],
        name='Real (X)',
        marker=dict(
            color='rgba(0, 102, 204, 0.4)', # Azul forte vazado
            line=dict(color='rgb(0, 102, 204)', width=2) # Contorno sólido
        ),
        text=df_fin['REAL'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))

    # Estilização Técnica
    fig.update_layout(
        template="plotly_dark",
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white", size=12),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickprefix="R$ "),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(t=80, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- TABELA DE CONFERÊNCIA ---
    st.dataframe(
        df_fin.style.format({'PREVISTO': 'R$ {:,.2f}', 'REAL': 'R$ {:,.2f}'}),
        use_container_width=True,
        hide_index=True
    )
