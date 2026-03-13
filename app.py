import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO DE TELA (Removido o 'wide' para centralizar naturalmente)
st.set_page_config(page_title="Zion - Dashboard", layout="centered")

# CSS para forçar a compactação e centralização
st.markdown("""
    <style>
    /* Limita a largura da página para não espalhar no monitor */
    .main .block-container {
        max-width: 900px;
        padding-top: 1rem;
    }
    
    /* Reduz drasticamente o tamanho das fontes e células */
    [data-testid="stMetricValue"] {font-size: 1.1rem !important;}
    [data-testid="stMetricLabel"] {font-size: 0.7rem !important;}
    h3 {font-size: 1rem !important; margin-bottom: 0.2rem;}
    
    /* Remove espaços entre tabelas e elementos */
    [data-testid="stVerticalBlock"] {gap: 0.4rem !important;}
    
    /* Estilo para as tabelas ficarem mais densas */
    .stDataFrame {font-size: 12px !important;}
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
NOME_ABA = "ODM MARÇO"
NOME_ABA_URL = quote(NOME_ABA)

@st.cache_data(ttl=30)
def carregar_dados():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    return df

try:
    df_full = carregar_dados()
    
    # --- FORECAST ---
    bloco_forecast = df_full.iloc[0:20, 20:27].astype(str).apply(lambda x: x.str.strip().str.upper())
    lista_forecast = set(pd.unique(bloco_forecast.values.ravel()))
    
    # --- OPERACIONAL ---
    df_op = df_full.iloc[0:80, 0:15].copy()
    col_emp = df_op.columns[2]
    df_op = df_op.dropna(subset=[col_emp])
    
    df_op['VALOR_NUM'] = pd.to_numeric(df_op['TOTAL'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(0)
    df_op['LTS_NUM'] = pd.to_numeric(df_op['COMPRA LITROS'].astype(str).str.upper().str.replace('L', '', regex=False).str.replace('.', '', regex=False).str.strip(), errors='coerce').fillna(0)
    df_op['EMP_KEY'] = df_op[col_emp].astype(str).str.strip().str.upper()

    st.title("🚢 Monitoramento Zion")

    # --- TABELA 1 ---
    resumo = df_op.groupby('EMP_KEY').apply(lambda x: pd.Series({
        'REAL (L)': x[x['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]['LTS_NUM'].sum(),
        'REAL (R$)': x[x['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]['VALOR_NUM'].sum(),
        'PROG (L)': x[x['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]['LTS_NUM'].sum(),
        'PROG (R$)': x[x['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]['VALOR_NUM'].sum()
    })).reset_index().rename(columns={'EMP_KEY': 'ATIVO'})

    st.markdown("### 📊 Consumo Consolidado")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Realizado L", f"{resumo['REAL (L)'].sum():,.0f}L".replace(',', '.'))
    c2.metric("Realizado R$", f"R${resumo['REAL (R$)'].sum():,.0f}".replace(',', '.'))
    c3.metric("Prog. L", f"{resumo['PROG (L)'].sum():,.0f}L".replace(',', '.'))
    c4.metric("Prog. R$", f"R${resumo['PROG (R$)'].sum():,.0f}".replace(',', '.'))

    st.dataframe(
        resumo,
        use_container_width=True, hide_index=True,
        column_config={
            "ATIVO": st.column_config.TextColumn("Ativo", width=120),
            "REAL (L)": st.column_config.NumberColumn("Real L", width=80, format="%d"),
            "REAL (R$)": st.column_config.NumberColumn("Real R$", width=100, format="R$ %d"),
            "PROG (L)": st.column_config.NumberColumn("Prog L", width=80, format="%d"),
            "PROG (R$)": st.column_config.NumberColumn("Prog R$", width=100, format="R$ %d")
        }
    )

    # --- ALERTAS ---
    alertas = [f"⚠️ **{r['ATIVO']}** fora" for _, r in resumo.iterrows() if r['REAL (R$)'] > 0 and r['ATIVO'] not in lista_forecast]
    if alertas:
        cols = st.columns(len(alertas))
        for i, a in enumerate(alertas): cols[i].warning(a)

    # --- TABELA 2 ---
    st.markdown("---")
    st.markdown("### ✅ Detalhes Realizados")
    df_real = df_op[df_op['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        st.dataframe(
            df_real[[col_emp, 'COMPRA LITROS', 'SC', 'PEDIDO', 'SLA PC', 'DT ENTREGA']],
            use_container_width=True, hide_index=True,
            column_config={
                col_emp: st.column_config.TextColumn("Ativo", width=120),
                "COMPRA LITROS": st.column_config.TextColumn("Lts", width=70),
                "SC": st.column_config.TextColumn("SC", width=70),
                "PEDIDO": st.column_config.TextColumn("Pedido", width=80),
                "SLA PC": st.column_config.TextColumn("SLA", width=60),
                "DT ENTREGA": st.column_config.TextColumn("Entrega", width=100)
            }
        )

except Exception as e:
    st.error(f"Erro: {e}")
