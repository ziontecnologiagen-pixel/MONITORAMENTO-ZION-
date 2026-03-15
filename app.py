import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard Completo", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def formatar_moeda(valor):
    if not valor or valor == "0": return 0.0
    try:
        # Conversão baseada na planilha original
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO DOS DADOS ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # Mapeamento conforme image_0f58fd: U(20)=E/M, V(21)=PREVISTO, X(23)=CONTABIL/REAL
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(formatar_moeda)
    df_fin['REAL'] = df_raw.iloc[:, 23].apply(formatar_moeda)
    df_fin['DIFERENCA'] = df_fin['REAL'] - df_fin['PREVISTO']
    
    # --- FILTRO CORRIGIDO: Incluindo Luiz Felipe e Breno ---
    lista_validos = [
        'CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 
        'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO'
    ]
    df_fin = df_fin[df_fin['EMPURRADOR'].isin(lista_validos)].reset_index(drop=True)

    # --- GRÁFICO REALIZADO VS ORÇADO ---
    fig = go.Figure()

    # Barra Orçado (Letras em negrito e preto)
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['PREVISTO'],
        name='<b>ORÇADO</b>',
        marker=dict(color='rgba(135, 206, 235, 0.6)', line=dict(color='black', width=2)),
        text=df_fin['PREVISTO'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'),
        textposition='outside',
        textfont=dict(color='black', size=11)
    ))

    # Barra Realizado (Letras em negrito e preto)
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['REAL'],
        name='<b>REALIZADO</b>',
        marker=dict(color='rgba(0, 102, 204, 0.9)', line=dict(color='black', width=2)),
        text=df_fin['REAL'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'),
        textposition='outside',
        textfont=dict(color='black', size=11)
    ))

    # Anotações de Saldo/Estouro (Abaixo do Eixo X)
    for i, row in df_fin.iterrows():
        cor_label = "red" if row['DIFERENCA'] > 0 else "green"
        txt_label = "ESTOURO" if row['DIFERENCA'] > 0 else "SALDO"
        
        fig.add_annotation(
            x=row['EMPURRADOR'], y=0,
            text=f"<b>{txt_label}:</b><br><b>R$ {abs(row['DIFERENCA']):,.2f}</b>",
            showarrow=False, yshift=-75,
            font=dict(color=cor_label, size=12)
        )

    fig.update_layout(
        title={'text': "<b>REALIZADO VS ORÇADO</b>", 'y':0.95, 'x':0.5, 'xanchor':'center', 'yanchor':'top', 'font':{'size': 24, 'color':'black'}},
        template="plotly_white",
        barmode='group',
        height=700,
        margin=dict(b=200, t=120),
        xaxis=dict(tickfont=dict(color='black', size=13, family="Arial Black"), title=""),
        yaxis=dict(tickfont=dict(color='black'), tickprefix="<b>R$ </b>", gridcolor='lightgrey'),
        legend=dict(font=dict(color='black', size=13, family="Arial Black"), orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Conferência (Preta e Negrito)
    st.markdown("### **TABELA DE DADOS COMPLETA**")
    st.dataframe(
        df_fin[['EMPURRADOR', 'PREVISTO', 'REAL', 'DIFERENCA']].style.format({
            'PREVISTO': 'R$ {:,.2f}', 'REAL': 'R$ {:,.2f}', 'DIFERENCA': 'R$ {:,.2f}'
        }).set_properties(**{'font-weight': 'bold', 'color': 'black'}),
        use_container_width=True, hide_index=True
    )
