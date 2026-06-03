import streamlit as st
import pandas as pd
import numpy as np
import analises
import data

st.header("DADOS DO JOOOOBBBBB 🎲🎲🍆🥛")

st.write("Tabela de Returns")
st.dataframe(data.Returns)
st.write("Tabela de orders")
st.dataframe(data.orders)
st.write("Tabela de people")
st.dataframe(data.people)
