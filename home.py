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

buoyList = [44025, 44017, 44065, 41002, 41117, 41010]
# 41009, 41008

metric_column_mapping = {
  'Swell Height': 'SwH',
  'Wave Height': 'WvH',
  'Swell Period': 'SwP',
  'Swell Direction': 'MWD'
}

SelectedBuoys = st.multiselect("Which buoys do you want to view?",
                               buoyList,
                               default=None)
MetricSelect = st.radio("What do you want to measure?",
                        list(metric_column_mapping.keys()))


def newBuoyData(selected_buoys, metric):
  df = pd.DataFrame()

  for buoy in selected_buoys:
    # create timezone objects for UTC and EST
    utc_tz = pytz.timezone('UTC')
    est_tz = pytz.timezone('US/Eastern')

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

      # get metric to display
      if MetricSelect == 'Swell Height':
        df.loc[i, buoy] = data[i][6] * int(3.28084)
      # get buoy's wave height
      elif MetricSelect == 'Wave Height':
        df.loc[i, buoy] = data[i][5] * int(3.28084)
      # get buoy's swell period
      elif MetricSelect == 'Swell Period':
        df.loc[i, buoy] = data[i][7]
      # get buoy's median swell direction
      elif MetricSelect == 'Swell Direction':
        df.loc[i, buoy] = data[i][14]

      # add datetime column
      df.loc[i, 'Datetime'] = est_datetime

      # increment i and get next buoy
      i += 1

  return df


if len(SelectedBuoys) == 0:
  st.warning('Please choose one or more buoys')

else:
  metric_column = metric_column_mapping[MetricSelect]
  df = newBuoyData(SelectedBuoys, MetricSelect)

  # Create the line chart using the filtered dataframe
  # Set the y-axis range to start at 0
  df = df.sort_values(by=['Datetime'], ascending=True)

  fig = px.line(df, x='Datetime', y=SelectedBuoys)
  fig.update_layout(yaxis=dict(title=MetricSelect))

  # Display the chart in the app
  st.plotly_chart(fig, use_container_width=True)