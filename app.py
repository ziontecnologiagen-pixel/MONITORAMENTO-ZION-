import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zion - Dashboard Performance", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def limpar_valor(valor):
    if not valor or valor == "0": return 0.0
    try:
        # Limpeza para R$ e Litros
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    df = pd.DataFrame()
    df['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df['PREV_RS'] = df_raw.iloc[:, 21].apply(limpar_valor)
    df['REAL_RS'] = df_raw.iloc[:, 23].apply(limpar_valor)
    df['FORE_L'] = df_raw.iloc[:, 22].apply(limpar_valor)
    df['REAL_L'] = df_raw.iloc[:, 25].apply(limpar_valor)
    
    # Filtro exato da sua frota
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df = df[df['EMPURRADOR'].isin(frota)].reset_index(drop=True)

    # Título corrigido (sem o erro da imagem 0d8e09)
    st.markdown("<h2 style='text-align: center; color: black;'><b>PAINEL DE PERFORMANCE ZION - REALIZADO VS ORÇADO</b></h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # --- GRÁFICO FINANCEIRO (R$) ---
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df['EMPURRADOR'], y=df['PREV_RS'], name='<b>ORÇADO</b>', marker_color='rgba(135, 206, 235, 0.7)', text=df['PREV_RS'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'), textposition='outside'))
        fig1.add_trace(go.Bar(x=df['EMPURRADOR'], y=df['REAL_RS'], name='<b>REALIZADO</b>', marker_color='rgba(0, 102, 204, 0.9)', text=df['REAL_RS'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'), textposition='outside'))
        
        for i, r in df.iterrows():
            diff = r['REAL_RS'] - r['PREV_RS']
            cor, txt = ("red", "ESTOURO") if diff > 0 else ("green", "SALDO")
            fig1.add_annotation(x=r['EMPURRADOR'], y=0, text=f"<b>{txt}:</b><br><b>R$ {abs(diff):,.2f}</b>", showarrow=False, yshift=-80, font=dict(color=cor, size=11))

        fig1.update_layout(title="<b>COMPARAÇÃO FINANCEIRA (R$)</b>", template="plotly_white", barmode='group', height=600, margin=dict(b=180), font=dict(color="black"), xaxis=dict(tickfont=dict(family="Arial Black", size=12)))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # --- GRÁFICO DE CONSUMO (LITROS) ---
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df['EMPURRADOR'], y=df['FORE_L'], name='<b>FORECAST</b>', marker_color='rgba(135, 206, 235, 0.7)', text=df['FORE_L'].apply(lambda x: f'<b>{x:,.0f} L</b>'), textposition='outside'))
        fig2.add_trace(go.Bar(x=df['EMPURRADOR'], y=df['REAL_L'], name='<b>REAL (ODM)</b>', marker_color='rgba(0, 102, 204, 0.9)', text=df['REAL_L'].apply(lambda x: f'<b>{x:,.0f} L</b>'), textposition='outside'))
        
        for i, r in df.iterrows():
            diff_l = r['REAL_L'] - r['FORE_L']
            cor_l, txt_l = ("red", "ESTOURO") if diff_l > 0 else ("green", "SALDO")
            fig2.add_annotation(x=r['EMPURRADOR'], y=0, text=f"<b>{txt_l}:</b><br><b>{abs(diff_l):,.0f} L</b>", showarrow=False, yshift=-80, font=dict(color=cor_l, size=11))

        fig2.update_layout(title="<b>COMPARAÇÃO DE CONSUMO (LITROS)</b>", template="plotly_white", barmode='group', height=600, margin=dict(b=180), font=dict(color="black"), xaxis=dict(tickfont=dict(family="Arial Black", size=12)))
        st.plotly_chart(fig2, use_container_width=True)

    # Tabela de suporte em Negrito/Preto
    st.dataframe(df.style.format({'PREV_RS': 'R$ {:,.2f}', 'REAL_RS': 'R$ {:,.2f}', 'FORE_L': '{:,.0f} L', 'REAL_L': '{:,.0f} L'}).set_properties(**{'font-weight': 'bold', 'color': 'black'}), use_container_width=True, hide_index=True)
