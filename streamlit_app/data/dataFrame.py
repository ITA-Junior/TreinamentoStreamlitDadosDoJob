from data.supabase_client import supabase
import pandas as pd

def criar_dataframe(tabela):

    try:
        response = supabase.table(tabela).select("*").execute()

        df = pd.DataFrame(response.data)

        if (tabela == "orders"):
            df["Total Sales"] = df["Sales"] * df["Quantity"]
        
        return df
    
    except Exception as e:
        print(f"Erro: {e}")

