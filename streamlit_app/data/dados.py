import pandas as pd
from data.dataFrame import criar_dataframe


df_orders = criar_dataframe("orders")


def q1(df_orders):
    df_office = df_orders[df_orders["Category"] == "Office Supplies"]

    resultado = (df_office.groupby("City")["Total Sales"]
    .sum()
    .sort_values(ascending = False))

    return{
        "cidade": resultado.idxmax(),
        "valor": resultado.max()
    }

print(q1(df_orders))

def q2(df_orders):

    df = df_orders.copy()

    df["Order Date"] = pd.to_datetime(df["Order Date"])

    return(

        df.groupby("Order Date")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values("Order Date")
    )
   

def q3(df_orders):

    return(
        df_orders.groupby("State")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values("Total Sales", ascending = False)
        .reset_index(drop = True)
    )


def q4(df_orders):

    return(
        df_orders.groupby("City")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values("Total Sales", ascending = False)
        .head(10)
        .reset_index(drop = True)
    )


def q5(df_orders):

    return(
        df_orders.groupby("Segment")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values("Total Sales", ascending = False)
    )


def q6(df_orders):

    df_copia = df_orders.copy()

    df_copia["Order Date"] = pd.to_datetime(df_copia["Order Date"])
    df_copia["Year"] = df_copia["Order Date"].dt.year

    return(
        df_copia.groupby(["Segment", "Year" ])["Total Sales"]
        .sum()
        .reset_index()
        .sort_values(["Year", "Segment"])
    )


def q7(df_orders):

    return{ 
        
        "Qtd com 15% de desconto": (df_orders["Total Sales"] > 1000).sum(),
        "Qtd com 10% de desconto": (df_orders["Total Sales"] <= 1000).sum()
    }


def q8(df_orders):
    
    media_antes = df_orders["Total Sales"].mean()

    # X = A.where(condicao, B)
    # se a condicao for cumprida, X = A, se nao, X = B

    vendas_com_desconto = (
        df_orders["Total Sales"] * 0.85
    ).where(
        df_orders["Total Sales"] > 1000,
        df_orders["Total Sales"] * 0.90
    )

    media_depois = vendas_com_desconto.mean()

    return {
        "media_antes": media_antes,
        "media_depois": media_depois

}


def q9(df_orders):

    df_copia = df_orders.copy()
    df_copia["Order Date"] = pd.to_datetime(df_copia["Order Date"])

    df_copia["Year"] = df_copia["Order Date"].dt.year
    df_copia["Month"] = df_copia["Order Date"].dt.month

    return(
        df_copia.groupby(["Segment", "Year", "Month"])["Total Sales"]
        .mean()
        .reset_index()
        .sort_values(["Year", "Month", "Segment"])
        .reset_index(drop = True)
    )


def q10(df_orders):

    return(
        df_orders.groupby(["Category", "Sub-Category"])["Total Sales"]
        .sum()
        .reset_index()
        .sort_values("Total Sales", ascending = False)
        .head(12)
        .reset_index(drop = True)
    )

