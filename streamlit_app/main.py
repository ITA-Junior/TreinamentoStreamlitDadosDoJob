import streamlit as st
import pandas as pd
import plotly.express as px
from data.dataFrame import criar_dataframe

# ─────────────────────────  CONFIG  ─────────────────────────
st.set_page_config(
    page_title="Dashboard de Vendas · ITA Jr.",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────  ESTILO  ─────────────────────────
st.markdown(
    """
    <style>
        [data-testid="stMetricValue"] { font-size: 1.8rem; }
        .block-container { padding-top: 1.5rem; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 20px;
            border-radius: 6px 6px 0 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────  TÍTULO  ─────────────────────────
st.title("📊 Dashboard de Vendas")
st.caption("Curso de Python 2026 · ITA Júnior — Superstore Dataset")

# ─────────────────────────  DADOS  ─────────────────────────
@st.cache_data(ttl=600)
def load_data():
    df = criar_dataframe("orders")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Supabase: {e}")
    st.info("Verifique se o arquivo `.env` está configurado corretamente com `SUPABASE_URL` e `SUPABASE_KEY`.")
    st.stop()

# ─────────────────────────  SIDEBAR  ─────────────────────────
st.sidebar.image(
    "https://via.placeholder.com/200x60/1a1a2e/FFD700?text=ITA+Jr.",
    use_container_width=True,
)
st.sidebar.markdown("## 🔎 Filtros Globais")
st.sidebar.markdown("_Aplicados em todas as páginas_")

# Período
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()
date_range = st.sidebar.slider(
    "📅 Período",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
)

# Região
regioes = st.sidebar.multiselect(
    "🌎 Região",
    options=sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique()),
)

# Segmento
segmentos = st.sidebar.multiselect(
    "👥 Segmento",
    options=sorted(df["Segment"].dropna().unique()),
    default=sorted(df["Segment"].dropna().unique()),
)

# Categoria
categorias = st.sidebar.multiselect(
    "🏷️ Categoria",
    options=sorted(df["Category"].dropna().unique()),
    default=sorted(df["Category"].dropna().unique()),
)

st.sidebar.divider()
st.sidebar.info("📌 Navegue pelas páginas no menu lateral para ver as análises completas.")

# ─────────────────────────  FILTRO  ─────────────────────────
df_filtrado = df[
    (df["Region"].isin(regioes)) &
    (df["Segment"].isin(segmentos)) &
    (df["Category"].isin(categorias)) &
    (df["Order Date"].dt.date.between(date_range[0], date_range[1]))
].copy()

if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# ─────────────────────────  KPIs  ─────────────────────────
st.subheader("📈 Indicadores Principais")

col1, col2, col3, col4 = st.columns(4)

total_vendas = df_filtrado["Total Sales"].sum()
lucro_total  = df_filtrado["Profit"].sum()
total_pedidos = len(df_filtrado)
ticket_medio = total_vendas / total_pedidos if total_pedidos else 0

margem = (lucro_total / total_vendas * 100) if total_vendas else 0

# Deltas em relação ao dataset completo
delta_vendas  = total_vendas  - df["Total Sales"].sum()
delta_lucro   = lucro_total   - df["Profit"].sum()
delta_pedidos = total_pedidos - len(df)

col1.metric("💰 Total de Vendas",  f"${total_vendas:,.0f}",  f"${delta_vendas:,.0f}" if delta_vendas else None)
col2.metric("📦 Pedidos",          f"{total_pedidos:,}",     f"{delta_pedidos:,}"    if delta_pedidos else None)
col3.metric("🏆 Lucro Total",      f"${lucro_total:,.0f}",   f"${delta_lucro:,.0f}"  if delta_lucro else None)
col4.metric("📊 Margem de Lucro",  f"{margem:.1f}%")

st.divider()

# ─────────────────────────  GRÁFICOS RESUMO  ─────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Vendas por Categoria")
    cat_sales = (
        df_filtrado.groupby("Category")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values("Total Sales", ascending=False)
    )
    fig = px.bar(
        cat_sales,
        x="Category",
        y="Total Sales",
        color="Category",
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_layout(showlegend=False, height=320,
                      yaxis_title="Vendas (US$)", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("#### Vendas por Região")
    reg_sales = (
        df_filtrado.groupby("Region")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values("Total Sales", ascending=False)
    )
    fig2 = px.pie(
        reg_sales,
        names="Region",
        values="Total Sales",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig2.update_layout(height=320)
    st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────  EVOLUÇÃO MENSAL  ─────────────────────────
st.markdown("#### 📅 Evolução Mensal de Vendas e Lucro")
df_filtrado["Mês"] = df_filtrado["Order Date"].dt.to_period("M").astype(str)
mensal = (
    df_filtrado.groupby("Mês")[["Total Sales", "Profit"]]
    .sum()
    .reset_index()
    .sort_values("Mês")
)
fig3 = px.line(
    mensal,
    x="Mês",
    y=["Total Sales", "Profit"],
    markers=True,
    color_discrete_map={"Total Sales": "#4361EE", "Profit": "#06D6A0"},
    labels={"value": "US$", "variable": "Métrica"},
)
fig3.update_layout(height=340, xaxis_tickangle=-45)
st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────  TABELA  ─────────────────────────
st.divider()
st.subheader("🗃️ Dados Detalhados")

colunas_exibir = [
    c for c in [
        "Order Date", "Segment", "City", "State", "Region",
        "Category", "Sub-Category", "Product Name",
        "Sales", "Quantity", "Discount", "Total Sales", "Profit"
    ] if c in df_filtrado.columns
]

st.dataframe(
    df_filtrado[colunas_exibir].sort_values("Order Date").reset_index(drop=True),
    use_container_width=True,
    height=400,
)

csv = df_filtrado[colunas_exibir].to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Baixar dados filtrados (CSV)",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv",
)
