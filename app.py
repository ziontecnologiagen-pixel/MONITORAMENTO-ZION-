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
    if not valor or str(valor).strip() == "0" or str(valor).strip() == "": return 0.0
    try:
        # Limpeza pesada para garantir que o número seja lido
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').replace(' ', '').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # --- 1. GRÁFICOS DA FROTA (OS QUE VOCÊ APROVOU) ---
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
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['PREV_RS'], name='ORÇADO', marker_color='rgba(135, 206, 235, 0.7)', 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in df_emp['PREV_RS']], textposition='outside'))
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['REAL_RS'], name='REALIZADO', marker_color='rgba(0, 102, 204, 0.9)', 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in df_emp['REAL_RS']], textposition='outside'))
        fig1.update_layout(title="<b>COMPARAÇÃO FINANCEIRA (R$)</b>", template="plotly_white", barmode='group', height=500, font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['FORE_L'], name='FORECAST', marker_color='rgba(135, 206, 235, 0.7)', 
                             text=[f"<b>{v:,.0f} L</b>" for v in df_emp['FORE_L']], textposition='outside'))
        fig2.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['REAL_L'], name='REAL (ODM)', marker_color='rgba(0, 102, 204, 0.9)', 
                             text=[f"<b>{v:,.0f} L</b>" for v in df_emp['REAL_L']], textposition='outside'))
        fig2.update_layout(title="<b>COMPARAÇÃO DE CONSUMO (LITROS)</b>", template="plotly_white", barmode='group', height=500, font=dict(color="black", family="Arial Black"))
        st.plotly_chart(fig2, use_container_width=True)

    # --- 2. GRÁFICO DE CICLOS (CORRIGINDO O CAPTURA DE DADOS) ---
    st.divider()
    st.markdown("<h3 style='text-align: center; color: black;'><b>DESEMPENHO POR CICLO (AF:AJ)</b></h3>", unsafe_allow_html=True)
    
    ciclos = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4", "Ciclo 5"]
    cols = range(31, 36) # Colunas AF a AJ
    
    # IMPORTANTE: Se o Forecast está zerado, o índice da linha pode estar errado. 
    # Vou buscar o Realizado na linha 2, Forecast na linha 3 e Diferença na linha 4 da sua planilha.
    v_real = [limpar_valor(df_raw.iloc[1, c]) for c in cols] 
    v_fore = [limpar_valor(df_raw.iloc[2, c]) for c in cols] 
    v_diff = [limpar_valor(df_raw.iloc[3, c]) for c in cols] 

    fig_ciclo = go.Figure()
    
    # Realizado
    fig_ciclo.add_trace(go.Bar(x=ciclos, y=v_real, name='REALIZADO', marker_color='rgba(0, 102, 204, 0.9)', 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in v_real], textposition='outside'))
    # Forecast (Verifique se os valores estão na linha 3 da planilha)
    fig_ciclo.add_trace(go.Bar(x=ciclos, y=v_fore, name='FORECAST', marker_color='rgba(135, 206, 235, 0.7)', 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in v_fore], textposition='outside'))
    # Diferença
    cores_diff = ['red' if v < 0 else 'blue' for v in v_diff]
    fig_ciclo.add_trace(go.Bar(x=ciclos, y=v_diff, name='DIFERENÇA', marker_color=cores_diff, 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in v_diff], textposition='outside'))

    fig_ciclo.update_layout(template="plotly_white", barmode='group', height=600, 
                            font=dict(color="black", family="Arial Black"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
    st.plotly_chart(fig_ciclo, use_container_width=True)
