import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Dashboard Executivo", layout="wide")

# CSS para interface compacta
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    h3 {margin-top: 0rem; margin-bottom: 0.5rem; font-size: 1.1rem;}
    [data-testid="stMetricValue"] {font-size: 1.4rem;}
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
NOME_ABA = "ODM MARÇO"
NOME_ABA_URL = quote(NOME_ABA)

@st.cache_data(ttl=60)
def carregar_dados():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    return df

try:
    df_full = carregar_dados()
    
    # --- MAPEAMENTO FORECAST (EXPANDIDO: COLUNA U ATÉ AA, LINHAS 1 ATÉ 15) ---
    # Pegamos um bloco maior para garantir que nomes como BRENO na linha 9 entrem na lista
    bloco_forecast = df_full.iloc[0:15, 20:27].astype(str)
    
    # Limpeza profunda: Remove espaços, converte para maiúsculas e achata em uma lista única
    lista_forecast = []
    for coluna in bloco_forecast.columns:
        nomes = bloco_forecast[coluna].str.strip().str.upper().unique()
        lista_forecast.extend(nomes)
    
    # Filtro final para remover lixo
    lista_forecast = set([n for n in lista_forecast if n not in ['NAN', '', 'NONE', '0', 'EMPTY']])
    
    # --- MAPEAMENTO OPERACIONAL (B ATÉ O) ---
    df_op = df_full.iloc[0:100, 0:15].copy()
    col_emp = df_op.columns[2] # Coluna C (Empurrador)
    df_op = df_op.dropna(subset=[col_emp])
    
    # Padronização de dados
    df_op['EMP_KEY'] = df_op[col_emp].astype(str).str.strip().str.upper()
    df_op['VALOR_NUM'] = pd.to_numeric(df_op['TOTAL'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(0)
    df_op['LTS_NUM'] = pd.to_numeric(df_op['COMPRA LITROS'].astype(str).str.upper().str.replace('L', '', regex=False).str.replace('.', '', regex=False).str.strip(), errors='coerce').fillna(0)

    st.title("🚢 Monitoramento Zion")

    # --- TABELA 1: RESUMO CONSOLIDADO (ELEGANTE E COMPACTO) ---
    st.markdown("### 📊 Consumo Consolidado por Ativo")
    
    resumo = df_op.groupby('EMP_KEY').apply(lambda x: pd.Series({
        'Realizado (L)': x[x['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]['LTS_NUM'].sum(),
        'Realizado (R$)': x[x['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]['VALOR_NUM'].sum(),
        'Programado (L)': x[x['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]['LTS_NUM'].sum(),
        'Programado (R$)': x[x['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]['VALOR_NUM'].sum()
    })).reset_index().rename(columns={'EMP_KEY': 'EMPURRADOR'})

    st.dataframe(
        resumo.style.format({
            'Realizado (L)': '{:,.0f} L', 'Programado (L)': '{:,.0f} L',
            'Realizado (R$)': 'R$ {:,.2f}', 'Programado (R$)': 'R$ {:,.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )

    # --- ALERTAS DE FORECAST (REVISADOS) ---
    total_gral = resumo['Realizado (R$)'].sum()
    alertas = []
    for _, row in resumo.iterrows():
        # Só alerta se o empurrador NÃO estiver em NENHUMA célula do bloco U:AA
        if row['Realizado (R$)'] > 0 and row['EMPURRADOR'] not in lista_forecast:
            perc = (row['Realizado (R$)'] / total_gral * 100) if total_gral > 0 else 0
            alertas.append(f"⚠️ **{row['EMPURRADOR']}** extraplano. Impacto: **{perc:.2f}%**")

    if alertas:
        st.markdown("### ⚠️ Alertas de Forecast")
        cols = st.columns(len(alertas) if len(alertas) < 4 else 4)
        for i, msg in enumerate(alertas):
            cols[i % 4].warning(msg)
    else:
        st.success("✅ Todos os empurradores realizados constam no Forecast.")

    st.markdown("---")

    # --- TABELA 2: REALIZADOS (DESIGN COMPACTO) ---
    st.markdown("### ✅ Detalhamento de Cargas Realizadas")
    df_real = df_op[df_op['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        df_real_view = df_real[[col_emp, 'COMPRA LITROS', 'SC', 'PEDIDO', 'SLA PC', 'DT ENTREGA']]
        st.dataframe(
            df_real_view,
            use_container_width=True,
            hide_index=True,
            column_config={
                col_emp: st.column_config.TextColumn("Empurrador", width="medium"),
                "COMPRA LITROS": st.column_config.TextColumn("Litros", width="small"),
                "SC": st.column_config.TextColumn("SC", width="small"),
                "PEDIDO": st.column_config.TextColumn("Pedido", width="small"),
                "SLA PC": st.column_config.TextColumn("SLA", width="small"),
                "DT ENTREGA": st.column_config.TextColumn("Entrega", width="medium"),
            }
        )

except Exception as e:
    st.error(f"Erro no processamento: {e}")
