import streamlit as st

from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlopen

df = pd.DataFrame()

buoyList = [44025, 44017, 44065, 41010, 41009, 41002, 41117]


def getLatLong(buoyList):
  for buoy in buoyList:
    url = f'https://www.ndbc.noaa.gov/data/latest_obs/{buoy}.txt'
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    # get second line of text
    text = soup.get_text().splitlines()[1]
    # define lat as the beginning of the second line of text up and including the first letter
    lat = text[:text.find('N') + 1]
    # define lon as the text after the first letter of the second line of text
    lon = text[text.find('N') + 1:]

    # extract numbers from lat to make into a latitude float skipping the degree symbol
    lat_str = lat

    # Split the input string into its individual parts
    parts = lat_str.split("°")

    # Convert the degree value into a floating-point number
    degree = float(parts[0])

    # Convert the minute value into a floating-point number
    minute = float(parts[1].split("'")[0]) / 60.0

    # Add the degree and minute values to obtain the final value
    lat = degree + minute

    # If the direction letter is "S", the final value is negative
    if parts[1].split("'")[1].strip() in ["S", "s"]:
      lat = -lat

    # extract numbers from lon to make into a longitude float skipping the degree symbol
    lon_str = lon

    # Split the input string into its individual parts
    parts = lon_str.split("°")

    # Convert the degree value into a floating-point number
    degree = float(parts[0])

    # Convert the minute value into a floating-point number
    minute = float(parts[1].split("'")[0]) / 60.0

    # Add the degree and minute values to obtain the final value
    lon = degree + minute

    # If the direction letter is "W", the final value is negative
    if parts[1].split("'")[1].strip() in ["W", "w"]:
      lon = -lon

    # add lat and lon to the dataframe
    df.loc[buoy, 'lat'] = lat
    df.loc[buoy, 'lon'] = lon

getLatLong(buoyList)

st.header('Currently serving these buoys')
st.write('see status log for updates')

st.map(data=df, zoom=None, use_container_width=True)

# Using object notation
# Add a sidebar to the app
with st.form("my_form"):
   #st.write("Inside the form")
   slider_val = st.slider("Form slider")
   checkbox_val = st.checkbox("Form checkbox")

   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
       st.write("slider", slider_val, "checkbox", checkbox_val)

#st.write("Outside the form")

with st.form("home_form"):
  SelectedBuoys = st.multiselect("Which buoys do you want to view?",
                               buoyList,
                               default=44025)
  