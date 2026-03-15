import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard Financeiro Limpo", layout="wide")

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
    # Mapeamento: U(20)=Empurrador, V(21)=Previsto, X(23)=Contabil/Real
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20]
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(formatar_moeda)
    df_fin['REAL'] = df_raw.iloc[:, 23].apply(formatar_moeda)
    
    # Cálculo Único: Diferença Real vs Previsto
    df_fin['DIFERENCA'] = df_fin['REAL'] - df_fin['PREVISTO']
    
    df_fin = df_fin[df_fin['EMPURRADOR'] != "E/M"].reset_index(drop=True)

    st.title("📊 **RAIO X FINANCEIRO ZION**")

    # --- GRÁFICO DE BARRAS ORGANIZADO ---
    fig = go.Figure()

    # Barra Previsto
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['PREVISTO'],
        name='PREVISTO',
        marker=dict(color='rgba(135, 206, 235, 0.5)', line=dict(color='black', width=1)),
        text=df_fin['PREVISTO'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'),
        textposition='outside',
        textfont=dict(color='black')
    ))

    # Barra Real
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['REAL'],
        name='REAL',
        marker=dict(color='rgba(0, 102, 204, 0.8)', line=dict(color='black', width=1)),
        text=df_fin['REAL'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'),
        textposition='outside',
        textfont=dict(color='black')
    ))

    # CORREÇÃO DA BAGUNÇA: Uma anotação por coluna
    for i, row in df_fin.iterrows():
        if row['EMPURRADOR'] == "0": continue
        
        # Decide se é Estouro (Vermelho) ou Saldo (Verde)
        if row['DIFERENCA'] > 0:
            msg = f"<b>ESTOURO:</b><br><b>R$ {row['DIFERENCA']:,.2f}</b>"
            cor_label = "red"
        else:
            msg = f"<b>SALDO:</b><br><b>R$ {abs(row['DIFERENCA']):,.2f}</b>"
            cor_label = "green"

        fig.add_annotation(
            x=row['EMPURRADOR'],
            y=0,
            text=msg,
            showarrow=False,
            yshift=-60, # Espaço para não encavalar no nome
            font=dict(color=cor_label, size=12)
        )

    # Ajustes finais de visibilidade (Letras Pretas e Negrito)
    fig.update_layout(
        template="plotly_white",
        barmode='group',
        height=700,
        margin=dict(b=180, t=100),
        xaxis=dict(
            tickfont=dict(color='black', size=14, family="Arial Black"), # NOME EM PRETO E NEGRITO
            title=""
        ),
        yaxis=dict(
            tickfont=dict(color='black', size=12),
            tickprefix="<b>R$ </b>",
            gridcolor='lightgrey'
        ),
        legend=dict(font=dict(color='black', size=12, family="Arial Black")),
        font=dict(color="black")
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabela consolidada com letras pretas e negrito
    st.markdown("### **DETALHAMENTO CONSOLIDADO**")
    st.dataframe(
        df_fin[['EMPURRADOR', 'PREVISTO', 'REAL', 'DIFERENCA']].style.format({
            'PREVISTO': 'R$ {:,.2f}',
            'REAL': 'R$ {:,.2f}',
            'DIFERENCA': 'R$ {:,.2f}'
        }).set_properties(**{'font-weight': 'bold', 'color': 'black'}),
        use_container_width=True, hide_index=True
    )
