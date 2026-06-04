import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

#como instalar elas

#pip install supabase
#pip install python dotenv
#pip install pandas
#pip install streamlit

#carregar as variaveis ambiente
load_dotenv()

#cabecalho do supabase

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

def criar_dataframe(tabela):
    try:
        response = supabase.table(tabela).select("*").execute()

        return pd.DataFrame(response.data)
        
    except Exception as e:
        print(f"Erro: {e}")


#df_returns = criar_dataframe("Returns")
df_orders = criar_dataframe("orders")
#df_people = criar_dataframe("people")



def q1(df_orders):
    df_office = df_orders[df_orders["Category"] == "Office Supplies"]

    resultado = (df_office.groupby("City")["Sales"]
    .sum()
    .sort_values(ascending = False))

    return{
        "cidade": resultado.idxmax(),
        "valor": resultado.max()
    }
   

def q2(df_orders):
    df = df_orders.copy()

    df["Order Date"] = pd.to_datetime(df["Order Date"])

    return(

        df.groupby("Order Date")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Order Date")
    )


def q3(df_orders):
    return(
        df_orders.groupby("State")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending = False)
        .reset_index(drop = True)
    )


def q4(df_orders):

    return(
        df_orders.groupby("City")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending = False)
        .head(10)
        .reset_index(drop = True)
    )


def q7(df_orders):

    return (df_orders["Sales"] > 1000).sum()


def q8(df_orders):
    
    #considerando que esta sendo requisitado apenas a media dos valores com desconto de 15%
    vendas_15 = (df_orders["Sales"] > 1000)

    media_antes = vendas_15.mean()
    media_depois = (vendas_15*0.85).mean()

    return{
        "media_antes": media_antes,
        "media_depois": media_depois
    }


def q10(df_orders):

    return(
        df_orders.groupby(["Category", "Sub-Category"])["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending = False)
        .head(12)
        .reset_index(drop = True)
    )
