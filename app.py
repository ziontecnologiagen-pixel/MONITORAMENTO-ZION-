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
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # --- 1. GRÁFICOS DOS EMPURRADORES (O CÓDIGO PERFEITO) ---
    df_emp = pd.DataFrame()
    df_emp['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_emp['PREV_RS'] = df_raw.iloc[:, 21].apply(limpar_valor)
    df_emp['REAL_RS'] = df_raw.iloc[:, 23].apply(limpar_valor)
    df_emp['FORE_L'] = df_raw.iloc[:, 22].apply(limpar_valor)
    df_emp['REAL_L'] = df_raw.iloc[:, 25].apply(limpar_valor)
    
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_emp = df_emp[df_emp['EMPURRADOR'].isin(frota)].reset_index(drop=True)

    st.markdown("<h2 style='text-align: center; color: black;'><b>PAINEL DE PERFORMANCE ZION - REALIZADO VS ORÇADO</b></h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['PREV_RS'], name='ORÇADO', marker_color='rgba(135, 206, 235, 0.7)'))
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['REAL_RS'], name='REALIZADO', marker_color='rgba(0, 102, 204, 0.9)'))
        for i, r in df_emp.iterrows():
            diff = r['REAL_RS'] - r['PREV_RS']
            cor, txt = ("red", "ESTOURO") if diff > 0 else ("green", "SALDO")
            fig1.add_annotation(x=r['EMPURRADOR'], y=0, text=f"<b>{txt}:</b><br><b>R$ {abs(diff):,.2f}</b>", showarrow=False, yshift=-80, font=dict(color=cor, size=11))
        fig1.update_layout(title="<b>COMPARAÇÃO FINANCEIRA (R$)</b>", template="plotly_white", barmode='group', height=550, margin=dict(b=150), font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['FORE_L'], name='FORECAST', marker_color='rgba(135, 206, 235, 0.7)'))
        fig2.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['REAL_L'], name='REAL (ODM)', marker_color='rgba(0, 102, 204, 0.9)'))
        for i, r in df_emp.iterrows():
            diff_l = r['REAL_L'] - r['FORE_L']
            cor_l, txt_l = ("red", "ESTOURO") if diff_l > 0 else ("green", "SALDO")
            fig2.add_annotation(x=r['EMPURRADOR'], y=0, text=f"<b>{txt_l}:</b><br><b>{abs(diff_l):,.0f} L</b>", showarrow=False, yshift=-80, font=dict(color=cor_l, size=11))
        fig2.update_layout(title="<b>COMPARAÇÃO DE CONSUMO (LITROS)</b>", template="plotly_white", barmode='group', height=550, margin=dict(b=150), font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig2, use_container_width=True)

    # --- 2. GRÁFICO DE CICLOS (CORREÇÃO DO VALUERROR) ---
    st.divider()
    st.markdown("<h3 style='text-align: center; color: black;'><b>CRUZAMENTO: GASTO REAL VS DISPARIDADE (CÍRCULO AZUL)</b></h3>", unsafe_allow_html=True)
    
    nomes_ciclo = ["CICLO 1", "CICLO 2", "CICLO 3", "CICLO 4", "CICLO 5"]
    v_real_ciclo = [limpar_valor(df_raw.iloc[1, c]) for c in range(31, 36)] # Gasto Real (Linha 3)
    v_disp_ciclo = [limpar_valor(df_raw.iloc[2, c]) for c in range(31, 36)] # Disparidade (Linha 4)

    fig_ciclo = go.Figure()

    # Adicionando Gasto Real (Eixo Y1)
    fig_ciclo.add_trace(go.Scatter(
        x=nomes_ciclo, y=v_real_ciclo, mode='lines+markers+text', 
        name='<b>GASTO REAL</b>', line=dict(color='darkblue', width=4),
        text=[f"<b>R$ {v:,.0f}</b>" for v in v_real_ciclo], textposition="top center"
    ))

    # Adicionando Disparidade (Eixo Y2) - Aqui é o segredo para não dar erro
    fig_ciclo.add_trace(go.Scatter(
        x=nomes_ciclo, y=v_disp_ciclo, mode='lines+markers+text', 
        name='<b>DISPARIDADE (AZUL)</b>', line=dict(color='red', width=4, dash='dot'),
        text=[f"<b>R$ {v:,.0f}</b>" for v in v_disp_ciclo], textposition="bottom center",
        yaxis="y2"
    ))

    # Layout configurado peça por peça para evitar conflito de legendas e eixos
    fig_ciclo.update_layout(
        template="plotly_white", height=500,
        font=dict(color="black", family="Arial Black"),
        xaxis=dict(title="Ciclos de Operação"),
        yaxis=dict(title="<b>Gasto Real (R$)</b>", titlefont=dict(color="darkblue")),
        yaxis2=dict(title="<b>Disparidade (R$)</b>", titlefont=dict(color="red"), overlaying='y', side='right'),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig_ciclo, use_container_width=True)

    # Tabela final
    st.dataframe(df_emp.style.format({'PREV_RS': 'R$ {:,.2f}', 'REAL_RS': 'R$ {:,.2f}', 'FORE_L': '{:,.0f} L', 'REAL_L': '{:,.0f} L'}).set_properties(**{'font-weight': 'bold', 'color': 'black'}), use_container_width=True, hide_index=True)
