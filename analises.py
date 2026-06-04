import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

#como instalar elas

def q1(df) -> dict:
    df_office = df[df["Category"] == "Office Supplies"]

    resultado = (
        df_office.groupby("City")["Sales"]
        .sum()
        .sort_values(ascending = False)
    )

    return {
        "cidade": resultado.idxmax(),
        "valor": resultado.max()
    }
   

def q2(df) -> pd.DataFrame:
    df = df.copy()

    df["Order Date"] = pd.to_datetime(df["Order Date"])

    return (
        df.groupby("Order Date")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Order Date")
    )


def q3(df) -> pd.DataFrame:
    return (
        df.groupby("State")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending = False)
        .reset_index(drop = True)
    )


def q4(df):
    return (
        df.groupby("City")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending = False)
        .head(10)
        .reset_index(drop = True)
    )


def q7(df):

    return (df["Sales"] > 1000).sum()


def q8(df):
    
    media_antes = df["Sales"].mean()

    vendas_com_desconto = (
        df["Sales"] * 0.85
    ).where(
        df["Sales"] > 1000,
        df["Sales"] * 0.90
    )

    media_depois = vendas_com_desconto.mean()

    return {
        "media_antes": media_antes,
        "media_depois": media_depois
    }


def q10(df):

    return (
        df.groupby(["Category", "Sub-Category"])["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending = False)
        .head(12)
        .reset_index(drop = True)
    )
