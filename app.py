import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

st.set_page_config(page_title="Zion - Dashboard", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def limpar_valor(valor):
    if not valor or str(valor).strip() in ["0", "", "R$ 0,00"]: return 0.0
    try:
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').replace(' ', '').replace('(', '').replace(')', '').strip()
        multiplicador = -1 if '-' in str(valor) or '(' in str(valor) else 1
        return float(s) * multiplicador
    except:
        return 0.0

df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # --- GRÁFICOS DA FROTA (TOP) ---
    df_emp = pd.DataFrame()
    df_emp['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_emp['PREV_RS'] = df_raw.iloc[:, 21].apply(limpar_valor)
    df_emp['REAL_RS'] = df_raw.iloc[:, 23].apply(limpar_valor)
    df_emp['FORE_L'] = df_raw.iloc[:, 22].apply(limpar_valor)
    df_emp['REAL_L'] = df_raw.iloc[:, 25].apply(limpar_valor)
    
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_emp = df_emp[df_emp['EMPURRADOR'].isin(frota)].reset_index(drop=True)

    st.markdown("<h2 style='text-align: center;'>PAINEL DE PERFORMANCE ZION</h2>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['PREV_RS'], name='ORÇADO', marker_color='lightblue', text=[f"R$ {v:,.0f}" for v in df_emp['PREV_RS']], textposition='outside'))
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['REAL_RS'], name='REALIZADO', marker_color='darkblue', text=[f"R$ {v:,.0f}" for v in df_emp['REAL_RS']], textposition='outside'))
        fig1.update_layout(title="FINANCEIRO (R$)", barmode='group', font=dict(family="Arial Black"))
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['FORE_L'], name='FORECAST', marker_color='lightblue', text=[f"{v:,.0f} L" for v in df_emp['FORE_L']], textposition='outside'))
        fig2.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['REAL_L'], name='REAL', marker_color='darkblue', text=[f"{v:,.0f} L" for v in df_emp['REAL_L']], textposition='outside'))
        fig2.update_layout(title="CONSUMO (LITROS)", barmode='group', font=dict(family="Arial Black"))
        st.plotly_chart(fig2, use_container_width=True)

    # --- GRÁFICO DE CICLOS (AF:AJ) ---
    st.divider()
    st.markdown("<h3 style='text-align: center;'>DESEMPENHO POR CICLO</h3>", unsafe_allow_html=True)
    
    ciclos = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4", "Ciclo 5"]
    cols = range(31, 36) 
    
    # Captura exata baseada nas suas marcações coloridas
    v_real = [limpar_valor(df_raw.iloc[1, c]) for c in cols] # Azul
    v_fore = [limpar_valor(df_raw.iloc[2, c]) for c in cols] # Laranja
    v_diff = [limpar_valor(df_raw.iloc[3, c]) for c in cols] # Amarelo

    fig_ciclo = go.Figure()
    fig_ciclo.add_trace(go.Bar(x=ciclos, y=v_real, name='REALIZADO', marker_color='#1E90FF', text=[f"R$ {v:,.0f}" for v in v_real], textposition='outside'))
    fig_ciclo.add_trace(go.Bar(x=ciclos, y=v_fore, name='FORECAST', marker_color='#FF8C00', text=[f"R$ {v:,.0f}" for v in v_fore], textposition='outside'))
    
    # Diferença: Vermelho se negativo, Verde se positivo (Saldo)
    cores_diff = ['red' if v < 0 else 'green' for v in v_diff]
    fig_ciclo.add_trace(go.Bar(x=ciclos, y=v_diff, name='DIFERENÇA', marker_color=cores_diff, text=[f"R$ {v:,.0f}" for v in v_diff], textposition='outside'))

    fig_ciclo.update_layout(template="plotly_white", barmode='group', height=600, font=dict(family="Arial Black", color="black"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
    st.plotly_chart(fig_ciclo, use_container_width=True)
