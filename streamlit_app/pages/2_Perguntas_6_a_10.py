import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.dataFrame import criar_dataframe

st.set_page_config(
    page_title="Perguntas 6–10 · Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
)

# ─────────────────────────  ESTILO  ─────────────────────────
st.markdown(
    """
    <style>
        .insight-box {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-left: 4px solid #FFD700;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 10px 0 20px 0;
            color: #f0f0f0;
        }
        .insight-box strong { color: #FFD700; }
        .block-container { padding-top: 1.2rem; }
        .sim-box {
            background: #0f3460;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
            color: #fff;
            margin: 6px 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────  DADOS  ─────────────────────────
@st.cache_data(ttl=600)
def load_data():
    df = criar_dataframe("orders")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

try:
    df_full = load_data()
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Supabase: {e}")
    st.stop()

# ─────────────────────────  SIDEBAR  ─────────────────────────
st.sidebar.markdown("## 🔎 Filtros")

min_date = df_full["Order Date"].min().date()
max_date = df_full["Order Date"].max().date()
date_range = st.sidebar.slider("📅 Período", min_value=min_date, max_value=max_date, value=(min_date, max_date))

regioes = st.sidebar.multiselect(
    "🌎 Região", options=sorted(df_full["Region"].dropna().unique()),
    default=sorted(df_full["Region"].dropna().unique()),
)
segmentos = st.sidebar.multiselect(
    "👥 Segmento", options=sorted(df_full["Segment"].dropna().unique()),
    default=sorted(df_full["Segment"].dropna().unique()),
)

df = df_full[
    (df_full["Region"].isin(regioes)) &
    (df_full["Segment"].isin(segmentos)) &
    (df_full["Order Date"].dt.date.between(date_range[0], date_range[1]))
].copy()

df["Ano"] = df["Order Date"].dt.year
df["Mes"] = df["Order Date"].dt.month

if df.empty:
    st.warning("⚠️ Nenhum dado para os filtros selecionados.")
    st.stop()

# ─────────────────────────  TÍTULO  ─────────────────────────
st.title("📊 Perguntas de Negócio — 6 a 10")
st.caption("Análises baseadas no dataset Superstore filtrado pela sidebar")
st.divider()


# ══════════════════════════════════════════════════════
#  PERGUNTA 6
# ══════════════════════════════════════════════════════
st.header("📆 Pergunta 6 — Total de Vendas por Segmento e por Ano")

vendas_seg_ano = (
    df.groupby(["Ano", "Segment"])["Total Sales"]
    .sum()
    .reset_index()
    .sort_values(["Ano", "Total Sales"], ascending=[True, False])
)

col1, col2 = st.columns(2)

with col1:
    fig6a = px.bar(
        vendas_seg_ano,
        x="Ano",
        y="Total Sales",
        color="Segment",
        barmode="group",
        title="Vendas por Segmento e Ano (Agrupado)",
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"Total Sales": "Vendas (US$)", "Segment": "Segmento"},
    )
    fig6a.update_layout(height=400)
    st.plotly_chart(fig6a, use_container_width=True)

with col2:
    fig6b = px.line(
        vendas_seg_ano,
        x="Ano",
        y="Total Sales",
        color="Segment",
        markers=True,
        title="Evolução de Vendas por Segmento ao Longo dos Anos",
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"Total Sales": "Vendas (US$)", "Segment": "Segmento"},
    )
    fig6b.update_layout(height=400)
    st.plotly_chart(fig6b, use_container_width=True)

# Tabela pivot
pivot6 = vendas_seg_ano.pivot(index="Segment", columns="Ano", values="Total Sales").fillna(0)
pivot6_display = pivot6.style.format("${:,.2f}")
pivot6_display.index.name = "Segmento"
st.dataframe(pivot6_display, use_container_width=True)

csv6 = vendas_seg_ano.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Baixar dados — Vendas por Segmento/Ano", csv6, "vendas_segmento_ano.csv", "text/csv")

seg_lider = vendas_seg_ano.groupby("Segment")["Total Sales"].sum().idxmax()
st.markdown(
    f"""
    <div class="insight-box">
    💡 <strong>Insight:</strong> Ao cruzar segmento com ano, fica evidente a trajetória de crescimento
    ou estagnação de cada grupo. O segmento <strong>{seg_lider}</strong> acumula o maior volume total
    no período analisado. Variações anuais permitem identificar se determinados segmentos foram
    impactados por sazonalidade, mudanças de mercado ou estratégias específicas.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ══════════════════════════════════════════════════════
#  PERGUNTA 7
# ══════════════════════════════════════════════════════
st.header("🏷️ Pergunta 7 — Simulação de Desconto")

st.markdown(
    "Regra: se **Total Sales > limite** → desconto de **taxa alta**, caso contrário → **taxa baixa**"
)

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    limite = st.number_input("💰 Limite de valor (US$)", min_value=100, max_value=10000, value=1000, step=50, key="p7_lim")
with col_s2:
    taxa_alta  = st.slider("📈 Taxa para vendas acima do limite (%)", 1, 50, 15, key="p7_alta")
with col_s3:
    taxa_baixa = st.slider("📉 Taxa para vendas abaixo/igual (%)", 1, 50, 10, key="p7_baixa")

df7 = df.copy()
df7["Desconto Aplicado (%)"] = df7["Total Sales"].apply(lambda v: taxa_alta if v > limite else taxa_baixa)
df7["Desconto (US$)"]        = df7["Total Sales"] * df7["Desconto Aplicado (%)"] / 100
df7["Valor com Desconto"]    = df7["Total Sales"] - df7["Desconto (US$)"]

n_15 = (df7["Desconto Aplicado (%)"] == taxa_alta).sum()
n_10 = (df7["Desconto Aplicado (%)"] == taxa_baixa).sum()

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric(f"Vendas com {taxa_alta}% de desconto",  f"{n_15:,}", f"{n_15/len(df7)*100:.1f}% do total")
col_b.metric(f"Vendas com {taxa_baixa}% de desconto", f"{n_10:,}", f"{n_10/len(df7)*100:.1f}% do total")
col_c.metric("Total de desconto concedido", f"${df7['Desconto (US$)'].sum():,.2f}")
col_d.metric("Receita após descontos",      f"${df7['Valor com Desconto'].sum():,.2f}")

fig7 = px.pie(
    values=[n_15, n_10],
    names=[f"{taxa_alta}% (acima de US${limite:,})", f"{taxa_baixa}% (até US${limite:,})"],
    title="Distribuição dos Descontos Aplicados",
    hole=0.45,
    color_discrete_sequence=["#E63946", "#457B9D"],
)
fig7.update_traces(textposition="outside", textinfo="percent+label+value")
fig7.update_layout(height=350)
st.plotly_chart(fig7, use_container_width=True)

st.markdown(
    f"""
    <div class="insight-box">
    💡 <strong>Insight:</strong> Com o limite em <strong>US${limite:,}</strong>,
    <strong>{n_15:,} pedidos</strong> ({n_15/len(df7)*100:.1f}%) recebem o desconto mais alto de {taxa_alta}%.
    Isso representa um impacto de <strong>${df7['Desconto (US$)'].sum():,.2f}</strong> na receita bruta.
    Ajustar esse limiar permite controlar o balanço entre volume de vendas e margem de lucro.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ══════════════════════════════════════════════════════
#  PERGUNTA 8
# ══════════════════════════════════════════════════════
st.header("📊 Pergunta 8 — Média de Vendas Antes e Depois do Desconto de 15%")

# Usa os mesmos parâmetros da P7
df8 = df7[df7["Desconto Aplicado (%)"] == taxa_alta].copy()

if df8.empty:
    st.warning("Nenhuma venda acima do limite com o desconto selecionado.")
else:
    media_antes  = df8["Total Sales"].mean()
    media_depois = df8["Valor com Desconto"].mean()
    reducao      = media_antes - media_depois

    col1, col2, col3 = st.columns(3)
    col1.metric("Média ANTES do desconto",  f"${media_antes:,.2f}")
    col2.metric("Média DEPOIS do desconto", f"${media_depois:,.2f}")
    col3.metric(f"Redução ({taxa_alta}%)",  f"${reducao:,.2f}")

    fig8 = go.Figure(
        go.Bar(
            x=["Antes do Desconto", "Depois do Desconto"],
            y=[media_antes, media_depois],
            text=[f"${media_antes:,.2f}", f"${media_depois:,.2f}"],
            textposition="outside",
            marker_color=["#4361EE", "#F72585"],
            width=0.4,
        )
    )
    fig8.update_layout(
        title=f"Média de Vendas (pedidos > US${limite:,}) — Antes vs Após {taxa_alta}% de Desconto",
        yaxis_title="Valor médio (US$)",
        height=380,
        yaxis_range=[0, media_antes * 1.3],
    )
    st.plotly_chart(fig8, use_container_width=True)

    # Histograma de distribuição
    fig8b = px.histogram(
        df8,
        x="Total Sales",
        color_discrete_sequence=["#4361EE"],
        nbins=40,
        title=f"Distribuição dos valores de venda (pedidos com {taxa_alta}% de desconto)",
        labels={"Total Sales": "Valor de Venda (US$)", "count": "Quantidade"},
    )
    fig8b.add_vline(x=media_antes,  line_dash="dash", line_color="#FF6B35", annotation_text="Média antes")
    fig8b.add_vline(x=media_depois, line_dash="dash", line_color="#06D6A0", annotation_text="Média depois")
    fig8b.update_layout(height=300)
    st.plotly_chart(fig8b, use_container_width=True)

    st.markdown(
        f"""
        <div class="insight-box">
        💡 <strong>Insight:</strong> Aplicando {taxa_alta}% de desconto nas vendas acima de US${limite:,},
        a média cai de <strong>${media_antes:,.2f}</strong> para <strong>${media_depois:,.2f}</strong>
        — uma redução de <strong>${reducao:,.2f}</strong> por pedido. A política de desconto deve ser
        avaliada em conjunto com a margem de lucro: descontos elevados em produtos de alta margem
        podem ser saudáveis; em produtos de baixa margem, podem gerar prejuízo.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()


# ══════════════════════════════════════════════════════
#  PERGUNTA 9
# ══════════════════════════════════════════════════════
st.header("📈 Pergunta 9 — Média de Vendas por Segmento, Ano e Mês")

meses_pt = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

media_seg_ano_mes = (
    df.groupby(["Segment", "Ano", "Mes"])["Total Sales"]
    .mean()
    .reset_index()
)
media_seg_ano_mes["Mes_Nome"] = media_seg_ano_mes["Mes"].map(meses_pt)
media_seg_ano_mes["Periodo"]  = (
    media_seg_ano_mes["Ano"].astype(str) + "-" + media_seg_ano_mes["Mes"].astype(str).str.zfill(2)
)

anos_disponiveis = sorted(media_seg_ano_mes["Ano"].unique())
anos_sel = st.multiselect("Filtrar anos", anos_disponiveis, default=anos_disponiveis, key="p9_anos")
segs_sel = st.multiselect(
    "Filtrar segmentos",
    sorted(media_seg_ano_mes["Segment"].unique()),
    default=sorted(media_seg_ano_mes["Segment"].unique()),
    key="p9_segs",
)

df9 = media_seg_ano_mes[
    (media_seg_ano_mes["Ano"].isin(anos_sel)) &
    (media_seg_ano_mes["Segment"].isin(segs_sel))
]

fig9 = px.line(
    df9,
    x="Periodo",
    y="Total Sales",
    color="Segment",
    markers=True,
    title="Média de Vendas por Segmento, Ano e Mês",
    color_discrete_sequence=px.colors.qualitative.Bold,
    labels={"Total Sales": "Média de Vendas (US$)", "Segment": "Segmento", "Periodo": "Período"},
)
fig9.update_layout(height=460, xaxis_tickangle=-45, legend=dict(orientation="h", y=1.12))
st.plotly_chart(fig9, use_container_width=True)

# Heatmap: segmento x mês
for seg in segs_sel:
    df_heat = (
        df[df["Segment"] == seg]
        .groupby(["Ano", "Mes"])["Total Sales"]
        .mean()
        .reset_index()
        .pivot(index="Mes", columns="Ano", values="Total Sales")
    )
    df_heat.index = df_heat.index.map(meses_pt)
    fig_heat = px.imshow(
        df_heat,
        title=f"Heatmap de Média de Vendas — {seg}",
        color_continuous_scale="Blues",
        labels={"x": "Ano", "y": "Mês", "color": "Média US$"},
        aspect="auto",
    )
    fig_heat.update_layout(height=300)
    st.plotly_chart(fig_heat, use_container_width=True)

seg_maior_media = (
    df.groupby("Segment")["Total Sales"].mean().idxmax()
)
st.markdown(
    f"""
    <div class="insight-box">
    💡 <strong>Insight:</strong> A análise mês a mês permite identificar padrões sazonais dentro de cada segmento.
    O segmento <strong>{seg_maior_media}</strong> apresenta a maior média de vendas por pedido.
    Meses com médias mais altas podem indicar períodos de alta demanda (datas comemorativas, fim de ano fiscal),
    orientando melhor o timing de campanhas e gestão de equipes comerciais.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ══════════════════════════════════════════════════════
#  PERGUNTA 10
# ══════════════════════════════════════════════════════
st.header("🏷️ Pergunta 10 — Total de Vendas por Categoria e Subcategoria (Top 12)")

top_n = st.slider("Número de subcategorias", min_value=5, max_value=20, value=12, key="p10_topn")

vendas_cat_sub = (
    df.groupby(["Category", "Sub-Category"])["Total Sales"]
    .sum()
    .reset_index()
    .sort_values("Total Sales", ascending=False)
)

top_subs = vendas_cat_sub.head(top_n)

# Gráfico principal: barras agrupadas por categoria
fig10a = px.bar(
    top_subs,
    x="Sub-Category",
    y="Total Sales",
    color="Category",
    title=f"Top {top_n} Subcategorias — Total de Vendas por Categoria",
    text_auto=".2s",
    color_discrete_sequence=px.colors.qualitative.Bold,
    labels={"Total Sales": "Vendas (US$)", "Sub-Category": "Subcategoria", "Category": "Categoria"},
)
fig10a.update_layout(height=460, xaxis_tickangle=-35)
st.plotly_chart(fig10a, use_container_width=True)

# Treemap
fig10b = px.treemap(
    top_subs,
    path=["Category", "Sub-Category"],
    values="Total Sales",
    title=f"Treemap — Top {top_n} Subcategorias por Categoria",
    color="Total Sales",
    color_continuous_scale="RdYlGn",
    labels={"Total Sales": "Vendas (US$)"},
)
fig10b.update_layout(height=460)
st.plotly_chart(fig10b, use_container_width=True)

# Sunburst
fig10c = px.sunburst(
    top_subs,
    path=["Category", "Sub-Category"],
    values="Total Sales",
    title=f"Sunburst — Participação das Top {top_n} Subcategorias",
    color="Total Sales",
    color_continuous_scale="Blues",
)
fig10c.update_layout(height=440)
st.plotly_chart(fig10c, use_container_width=True)

st.markdown("**Tabela completa — Top subcategorias**")
top_subs_display = top_subs.copy()
top_subs_display["Total Sales"] = top_subs_display["Total Sales"].map("${:,.2f}".format)
top_subs_display["Participação"] = (
    vendas_cat_sub.head(top_n)["Total Sales"] / df["Total Sales"].sum() * 100
).map("{:.1f}%".format).values
top_subs_display.columns = ["Categoria", "Subcategoria", "Vendas (US$)", "Participação"]
st.dataframe(top_subs_display.reset_index(drop=True), hide_index=True, use_container_width=True)

csv10 = top_subs.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Baixar dados — Top Subcategorias", csv10, "top_subcategorias.csv", "text/csv")

top_sub = top_subs.iloc[0]
st.markdown(
    f"""
    <div class="insight-box">
    💡 <strong>Insight:</strong> As top {top_n} subcategorias concentram a maior parte da receita.
    <strong>{top_sub['Sub-Category']}</strong> (categoria: {top_sub['Category']}) lidera com
    <strong>${top_sub['Total Sales']:,.2f}</strong>. O Treemap e o Sunburst facilitam a comparação visual
    da participação relativa — subcategorias com alto volume e baixa margem podem ser candidatas a
    revisão de mix ou estratégias de upsell.
    </div>
    """,
    unsafe_allow_html=True,
)
