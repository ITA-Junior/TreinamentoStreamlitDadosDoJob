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
try:
    supabase: Client = create_client(url, key)
    
    #exemplo de uso para retornar valores da tabela
    #vai em "tabela_para_analise"  e retorna todos os valores("*")

    response = supabase.table("tabela_para_analise").select("*").execute()

    #transforma os dados da tabela para um dataframe

    df = pd.DataFrame(response.data)
except:
    print('f')

