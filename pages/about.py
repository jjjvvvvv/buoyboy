import streamlit as st

st.markdown(
  'Understand whats going on in the water. BuoyBoy helps you make the best decision on the hunt. Simple visuals inform and enhance the quality of the data relayed from NOAA buoys. Understand what is going on in the water in real time, without the speculation and forecasting. Remember - Everything is a forecast until the buoys pick it up.'
)

st.button("Learn more about Buoy Data")

col1, col2, col3 = st.columns(3)

with col1:
  st.subheader("SwH")
  st.markdown(
    "Swell height is the vertical distance (meters) between any swell crest and the succeeding swell wave trough."
  )

with col2:
  st.subheader("WvH")
  st.markdown(
    "Significant Wave Height is the average height (meters) of the highest one-third of the waves during a 20 minute sampling period."
  )

with col3:
  st.subheader("APD")
  st.markdown(
    "Average Wave Period is the average period (seconds) of the highest one-third of the wave observed during a 20 minute sampling period"
  )

