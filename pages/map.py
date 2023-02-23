import streamlit as st
import pandas as pd

df = pd.read_csv('buoylist.csv')

st.map(data=df, zoom=None, use_container_width=True)

st.subheader('Currently serving these buoys')
st.write('see status log for updates')

st.dataframe(df)

# Using object notation
# Add a sidebar to the app
