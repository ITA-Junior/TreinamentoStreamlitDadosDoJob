import os
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


@st.cache_data(ttl=600)
def criar_dataframe(table_name: str) -> pd.DataFrame:
    """
    Conecta ao Supabase e retorna todos os dados da tabela como DataFrame.
    Os dados são cacheados por 10 minutos para melhor performance.
    """
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise EnvironmentError(
            "Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não encontradas. "
            "Verifique o arquivo .env na raiz do projeto."
        )

    supabase: Client = create_client(url, key)

    all_rows = []
    batch_size = 1000
    offset = 0

    while True:
        response = (
            supabase.table(table_name)
            .select("*")
            .range(offset, offset + batch_size - 1)
            .execute()
        )
        rows = response.data
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < batch_size:
            break
        offset += batch_size

    df = pd.DataFrame(all_rows)

    # ---------- Limpeza e tipagem ----------
    date_cols = [c for c in ["Order Date", "Ship Date"] if c in df.columns]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    numeric_cols = ["Sales", "Quantity", "Discount", "Profit", "Total Sales"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Se a coluna "Total Sales" não existir, cria a partir de Sales * Quantity
    if "Total Sales" not in df.columns and "Sales" in df.columns and "Quantity" in df.columns:
        df["Total Sales"] = df["Sales"] * df["Quantity"]

    # Remove linhas com datas inválidas ou vendas negativas/nulas
    if "Order Date" in df.columns:
        df = df.dropna(subset=["Order Date"])
    if "Total Sales" in df.columns:
        df = df[df["Total Sales"] > 0]

    df = df.reset_index(drop=True)
    return df
