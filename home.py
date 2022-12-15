import streamlit as st
from astropy.io import ascii
import pandas as pd
from datetime import date, time, datetime
import pytz
import plotly.express as px

st.set_page_config(page_title="The BuoyBoy",
                   page_icon="📡",
                   layout="centered",
                   initial_sidebar_state="auto")

st.header('The BuoyBoy')

df = pd.DataFrame()

buoyList = [44025, 44017, 44065, 41002, 41117, 41010, 41009, 41008]
# 41009, 41008

SelectedBuoys = st.multiselect("Which buoys do you want to view?",
                               buoyList,
                               default=None)


def newBuoyData(selected_buoys):

  # create timezone objects for UTC and EST
  utc_tz = pytz.timezone('UTC')
  est_tz = pytz.timezone('US/Eastern')

  for buoy in buoyList:
    data = ascii.read(f"https://www.ndbc.noaa.gov/data/5day2/{buoy}_5day.spec")

    i = 0
    while i < 24:
      # create the date and time objects
      my_date = date(data[i][0], data[i][1], data[i][2])
      my_time = time(data[i][3], data[i][4])

      # create a datetime object in UTC using the date and time objects
      my_datetime = datetime.combine(my_date, my_time)

      # set the timezone for the datetime object using the 'tzinfo' attribute
      my_datetime = my_datetime.replace(tzinfo=utc_tz)

      # convert the datetime to EST
      est_datetime = my_datetime.astimezone(est_tz)

      # get first buoy swell height
      swellHeight = data[i][6] * int(3.28084)
      # add buoy number
      df.loc[i, buoy] = swellHeight

      # add date column
      df.loc[i, 'Date'] = est_datetime.strftime('%Y-%m-%d')
      df.loc[i, 'Time'] = est_datetime.strftime('%I:%M:%S %p')
      df.loc[i, 'SwH'] = swellHeight

      # increment i and get next buoy
      i += 1


if len(SelectedBuoys) == 0:
  st.warning('Please choose one or more buoys')

else:
  newBuoyData(SelectedBuoys)

  # Filter the dataframe to only include the selected y columns
  filtered_df = df[['Date'] + ['Time'] + SelectedBuoys]
  # st.dataframe(filtered_df)

  # sort the time column
  filtered_df = filtered_df.sort_index(ascending=False)

  # Create the line chart using the filtered dataframe
  # Set the y-axis range to start at 0
  fig = px.line(filtered_df, x='Time', y=SelectedBuoys)
  fig.update_layout(yaxis=dict(title="Swell Height (ft)"))

  # Display the chart in the app
  st.plotly_chart(fig, use_container_width=True)
  st.dataframe(filtered_df)