import streamlit as st
import pandas as pd

df = pd.read_csv('buoylist.csv')

st.sidebar.header('Use Ctrl + F to search for a buoy')
st.sidebar.write('*Select inside the table to toggle search*')
st.dataframe(df, width=800, height=1600)