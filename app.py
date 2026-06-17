import streamlit as st
import pandas as pd
import numpy as np
from analises import *
from data import *

st.header("DADOS DO JOOOOBBBBB 🎲🎲🍆🥛")


df_returns = criar_dataframe("Returns")
df_orders = criar_dataframe("orders")
df_people = criar_dataframe("people")


col1, col2 = st.columns(2)

with col1:
    st.header("Q1")
    st.dataframe(pd.DataFrame([q1(df=df_orders)]))
    st.header("Q3")
    st.dataframe(q3(df=df_orders))
    st.header("Q7")
    st.metric(label="Q7", value=q7(df=df_orders))
    st.dataframe(q10(df=df_orders))
with col2: 
    st.header("Q2")
    st.dataframe(q2(df=df_orders))
    st.header("Q4")
    st.dataframe(q4(df=df_orders))
    st.header("Q8")
    st.dataframe(pd.DataFrame([q8(df=df_orders)]))

