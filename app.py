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
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').replace(' ', '').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # --- 1. DADOS DOS EMPURRADORES (OS GRÁFICOS QUE JÁ ESTAVAM PERFEITOS) ---
    df_emp = pd.DataFrame()
    df_emp['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_emp['PREV_RS'] = df_raw.iloc[:, 21].apply(limpar_valor)
    df_emp['REAL_RS'] = df_raw.iloc[:, 23].apply(limpar_valor)
    df_emp['FORE_L'] = df_raw.iloc[:, 22].apply(limpar_valor)
    df_emp['REAL_L'] = df_raw.iloc[:, 25].apply(limpar_valor)
    
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_emp = df_emp[df_emp['EMPURRADOR'].isin(frota)].reset_index(drop=True)

    # --- 2. DADOS DOS CICLOS (LINHAS DA TABELA AF:AJ) ---
    ciclos = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4", "Ciclo 5"]
    cols = range(31, 36) # Colunas AF até AJ
    v_real = [limpar_valor(df_raw.iloc[1, c]) for c in cols] # Linha Realizado
    v_fore = [limpar_valor(df_raw.iloc[2, c]) for c in cols] # Linha Forecast
    v_diff = [limpar_valor(df_raw.iloc[3, c]) for c in cols] # Linha Diferença

    st.markdown("<h2 style='text-align: center; color: black;'><b>PAINEL DE PERFORMANCE ZION - REALIZADO VS ORÇADO</b></h2>", unsafe_allow_html=True)

    # --- LINHA 1: GRÁFICOS DA FROTA ---
    col1, col2 = st.columns(2)
    with col1:
        # FINANCEIRO (R$)
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['PREV_RS'], name='ORÇADO', marker_color='rgba(135, 206, 235, 0.7)', text=df_emp['PREV_RS'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'), textposition='outside'))
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['REAL_RS'], name='REALIZADO', marker_color='rgba(0, 102, 204, 0.9)', text=df_emp['REAL_RS'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'), textposition='outside'))
        for i, r in df_emp.iterrows():
            diff = r['REAL_RS'] - r['PREV_RS']
            cor, txt = ("red", "ESTOURO") if diff > 0 else ("green", "SALDO")
            fig1.add_annotation(x=r['EMPURRADOR'], y=0, text=f"<b>{txt}:</b><br><b>R$ {abs(diff):,.2f}</b>", showarrow=False, yshift=-80, font=dict(color=cor, size=11))
        fig1.update_layout(title="<b>COMPARAÇÃO FINANCEIRA (R$)</b>", template="plotly_white", barmode='group', height=550, margin=dict(b=150), font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # CONSUMO (LITROS)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['FORE_L'], name='FORECAST', marker_color='rgba(135, 206, 235, 0.7)', text=df_emp['FORE_L'].apply(lambda x: f'<b>{x:,.0f} L</b>'), textposition='outside'))
        fig2.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['REAL_L'], name='REAL (ODM)', marker_color='rgba(0, 102, 204, 0.9)', text=df_emp['REAL_L'].apply(lambda x: f'<b>{x:,.0f} L</b>'), textposition='outside'))
        for i, r in df_emp.iterrows():
            diff_l = r['REAL_L'] - r['FORE_L']
            cor_l, txt_l = ("red", "ESTOURO") if diff_l > 0 else ("green", "SALDO")
            fig2.add_annotation(x=r['EMPURRADOR'], y=0, text=f"<b>{txt_l}:</b><br><b>{abs(diff_l):,.0f} L</b>", showarrow=False, yshift=-80, font=dict(color=cor_l, size=11))
        fig2.update_layout(title="<b>COMPARAÇÃO DE CONSUMO (LITROS)</b>", template="plotly_white", barmode='group', height=550, margin=dict(b=150), font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig2, use_container_width=True)

    # --- LINHA 2: GRÁFICO DE CICLOS (O NOVO AJUSTE) ---
    st.divider()
    st.markdown("<h3 style='text-align: center; color: black;'><b>DESEMPENHO POR CICLO (AF:AJ)</b></h3>", unsafe_allow_html=True)
    
    fig_ciclo = go.Figure()
    # Barra 1: Realizado
    fig_ciclo.add_trace(go.Bar(x=ciclos, y=v_real, name='REALIZADO', marker_color='rgba(0, 102, 204, 0.9)', text=[f"<b>R$ {v:,.0f}</b>" for v in v_real], textposition='outside'))
    # Barra 2: Forecast
    fig_ciclo.add_trace(go.Bar(x=ciclos, y=v_fore, name='FORECAST', marker_color='rgba(135, 206, 235, 0.7)', text=[f"<b>R$ {v:,.0f}</b>" for v in v_fore], textposition='outside'))
    # Barra 3: Diferença com Cor Condicional
    cores_diff = ['red' if v < 0 else 'blue' for v in v_diff]
    fig_ciclo.add_trace(go.Bar(x=ciclos, y=v_diff, name='DIFERENÇA', marker_color=cores_diff, text=[f"<b>R$ {v:,.0f}</b>" for v in v_diff], textposition='outside'))

    fig_ciclo.update_layout(template="plotly_white", barmode='group', height=550, font=dict(color="black", family="Arial Black"), margin=dict(b=100))
    st.plotly_chart(fig_ciclo, use_container_width=True)

    # Tabela de dados brutos da frota embaixo
    st.dataframe(df_emp.style.format({'PREV_RS': 'R$ {:,.2f}', 'REAL_RS': 'R$ {:,.2f}', 'FORE_L': '{:,.0f} L', 'REAL_L': '{:,.0f} L'}).set_properties(**{'font-weight': 'bold', 'color': 'black'}), use_container_width=True, hide_index=True)
