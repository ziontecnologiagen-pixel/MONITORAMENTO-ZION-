import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zion - Dashboard de Estouro High-Contrast", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def formatar_moeda(valor):
    if not valor or valor == "0": return 0.0
    try:
        # Limpeza para conversão baseada na planilha
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO DOS DADOS ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # Mapeamento conforme image_0f58fd: U(20), V(21), X(23)
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20]
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(formatar_moeda)
    df_fin['REAL'] = df_raw.iloc[:, 23].apply(formatar_moeda)
    df_fin['ESTOURO'] = df_fin['REAL'] - df_fin['PREVISTO']
    
    df_fin = df_fin[df_fin['EMPURRADOR'] != "E/M"].reset_index(drop=True)

    st.title("📊 **RAIO X FINANCEIRO: ORÇADO VS REAL**")
    
    # --- GRÁFICO DE BARRAS COM LETRAS EM NEGRITO ---
    fig = go.Figure()

    # Barra do Orçado (V) - Azul Claro Vazado
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['PREVISTO'],
        name='**ORÇADO (PREVISTO)**',
        marker=dict(color='rgba(135, 206, 235, 0.3)', line=dict(color='rgb(135, 206, 235)', width=2)),
        text=df_fin['PREVISTO'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'),
        textposition='inside',
        textfont=dict(size=12, color="white")
    ))

    # Barra do Gasto Real (X) - Azul Sólido
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['REAL'],
        name='**GASTO REAL (CONTÁBIL)**',
        marker=dict(color='rgba(0, 102, 204, 0.7)', line=dict(color='rgb(0, 102, 204)', width=2)),
        text=df_fin['REAL'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'),
        textposition='outside',
        textfont=dict(size=13, color="white")
    ))

    # Anotações de Estouro/Saldo em Negrito abaixo do eixo X
    for i, row in df_fin.iterrows():
        cor_texto = "red" if row['ESTOURO'] > 0 else "#00FF00"
        prefixo = "ESTOURO" if row['ESTOURO'] > 0 else "SALDO"
        
        fig.add_annotation(
            x=row['EMPURRADOR'],
            y=0,
            text=f"<b>{prefixo}:</b><br><b>R$ {abs(row['ESTOURO']):,.2f}</b>",
            showarrow=False,
            yshift=-60,
            font=dict(color=cor_texto, size=11),
            bgcolor="rgba(0,0,0,0.5)"
        )

    fig.update_layout(
        template="plotly_dark",
        barmode='group',
        height=750,
        margin=dict(b=180, t=100),
        xaxis=dict(tickfont=dict(size=14, family="Arial Black")), # Nomes dos empurradores em destaque
        yaxis=dict(tickfont=dict(size=12), tickprefix="<b>R$ </b>"),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=14))
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- TABELA COM TEXTO EM NEGRITO ---
    st.divider()
    st.markdown("### 📝 **DETALHAMENTO CONSOLIDADO (R$)**")
    
    # Estilizando a tabela para negrito
    st.dataframe(
        df_fin.style.format({
            'PREVISTO': 'R$ {:,.2f}', 
            'REAL': 'R$ {:,.2f}', 
            'ESTOURO': 'R$ {:,.2f}'
        }).set_properties(**{'font-weight': 'bold'}),
        use_container_width=True, 
        hide_index=True
    )
