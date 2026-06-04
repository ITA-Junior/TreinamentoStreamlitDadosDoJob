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

#cabecalho do supabase
#carregar as variaveis ambiente
load_dotenv()

#cabecalho do supabase

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key) # type: ignore

def criar_dataframe(tabela):
    try:
        response = supabase.table(tabela).select("*").execute()

        return pd.DataFrame(response.data)
        
    except Exception as e:
        print(f"Erro: {e}")
