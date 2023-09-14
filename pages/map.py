import streamlit as st
import pandas as pd

csv_df = pd.read_csv('buoylist.csv')

# make new dataframe only when lat and lon are not null

df = csv_df[df['lat'].notna()]
df = csv_df[df['lon'].notna()]

st.map(data=df, zoom=None, use_container_width=True)

st.subheader('Currently serving these buoys')
st.write('see status log for updates')

# Using object notation
# Add a sidebar to the app
