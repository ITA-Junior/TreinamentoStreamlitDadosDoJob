import streamlit as st
import pandas as pd
import numpy as np
from data.dataFrame import criar_dataframe


# -------------   CONFIG   -------------     
st.set_page_config(
    page_title = "Dashboard de Vendas ",
    layout = "wide"
)

# -------------   TITLE    -------------
st.title("Visão Geral")

# -------------   LOAD DATA   -------------   
df = criar_dataframe("orders")
df["Order Date"] = pd.to_datetime(df["Order Date"])

# -------------   SIDEBAR FILTERS   ------------- 
st.sidebar.header("Filtros")

categorias = st.sidebar.multiselect(
    "Categoria",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

regioes = st.sidebar.multiselect(
    "Região",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.slider(
    "Período",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# ---------------- FILTER LOGIC ----------------
df_filtrado = df[
    (df["Category"].isin(categorias)) &
    (df["Region"].isin(regioes)) &
    (df["Order Date"].dt.date.between(date_range[0], date_range[1]))
]

# ---------------- KPI SECTION ----------------
st.subheader(" Indicadores principais")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de Vendas", f"${df_filtrado['Total Sales'].sum():,.2f}")

with col2:
    st.metric("Lucro Total", f"${df_filtrado['Profit'].sum():,.2f}")

with col3:
    st.metric("Pedidos", len(df_filtrado))


# ---------------- DATA TABLE ----------------
st.subheader(" Dados para analise")

st.dataframe(
    df_filtrado[[
        "Order Date", "Segment", "City", "Region",
        "Category","Sub-Category", "Product Name",
        "Sales","Quantity", "Total Sales", "Profit" ]]
        .sort_values("Order Date").reset_index(drop = True),
    use_container_width=True,
    height = 400
)
