import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

#como instalar elas

def q1(df_orders):

    df_office = df_orders[
        df_orders["Category"] == "Office Supplies"
    ].copy()

    df_office["Valor_Venda"] = (
        df_office["Sales"] * df_office["Quantity"]
    )

    resultado = (
        df_office.groupby("City")["Valor_Venda"]
        .sum()
        .sort_values(ascending=False)
    )

    return {
        "cidade": resultado.idxmax(),
        "valor": resultado.max()
    }
   

def q2(df_orders):
    df = df_orders.copy()

    df["Order Date"] = pd.to_datetime(df["Order Date"])

    df["Valor_Venda"] = (
        df["Sales"] * df["Quantity"]
    )

    return (
        df.groupby("Order Date")["Valor_Venda"]
        .sum()
        .reset_index()
        .sort_values("Order Date")
    )


def q3(df_orders):

    df = df_orders.copy()

    df["Valor_Venda"] = (
        df["Sales"] * df["Quantity"]
    )

    return (
        df.groupby("State")["Valor_Venda"]
        .sum()
        .reset_index()
        .sort_values("Valor_Venda", ascending=False)
        .reset_index(drop=True)
    )


def q4(df_orders):

    df = df_orders.copy()

    df["Valor_Venda"] = (
        df["Sales"] * df["Quantity"]
    )

    return (
        df.groupby("City")["Valor_Venda"]
        .sum()
        .reset_index()
        .sort_values("Valor_Venda", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )


def q7(df_orders):

    valor_venda = (
        df_orders["Sales"] * df_orders["Quantity"]
    )

    return int((valor_venda > 1000).sum())


def q8(df_orders):

    valor_venda = (
        df_orders["Sales"] * df_orders["Quantity"]
    )

    media_antes = valor_venda.mean()

    vendas_com_desconto = (
        valor_venda * 0.85
    ).where(
        valor_venda > 1000,
        valor_venda * 0.90
    )

    media_depois = vendas_com_desconto.mean()

    return {
        "media_antes": media_antes,
        "media_depois": media_depois
    }

def q10(df_orders):

    df = df_orders.copy()

    df["Valor_Venda"] = (
        df["Sales"] * df["Quantity"]
    )

    return (
        df.groupby(["Category", "Sub-Category"])["Valor_Venda"]
        .sum()
        .reset_index()
        .sort_values("Valor_Venda", ascending=False)
        .head(12)
        .reset_index(drop=True)
    )
