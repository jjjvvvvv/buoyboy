"""
THE BUOYBOY
Github Codespaces Test

"""

from datetime import date, time, datetime
import streamlit as st
from astropy.io import ascii
import pandas as pd
import pytz
import plotly.express as px

st.set_page_config(page_title="The BuoyBoy 📡",
                   page_icon="📡",
                   layout="wide",
                   initial_sidebar_state="expanded")

# need a way to update buoy List every now and then...

buoydf = pd.read_csv('buoylist.csv')

# create a dictionary to map buoys to their names

buoy_name_mapping = {}
for index, row in buoydf.iterrows():
    buoy_name_mapping[row['buoy']] = row['name']

metric_column_mapping = {
  'Swell Height': 'SwH',
  'Wave Height': 'WvH',
  'Swell Period': 'SwP',
  'Swell Direction': 'MWD'
}

st.sidebar.subheader("Settings")

# make a list of strings equal to 'buoy' + : + 'name'. Make sure to convert buoys to string
buoy_name_list = [
  name + "(" + str(buoy) + ")" for buoy, name in buoy_name_mapping.items()
]

SelectedBuoys = st.sidebar.multiselect("Which buoys do you want to view?",
                                       buoy_name_list,
                                       default=None)

# create a list of selected buoys based on the user's selection
SelectedBuoys = [buoy.split('(')[1].split(')')[0] for buoy in SelectedBuoys]

MetricSelect = st.sidebar.radio("What do you want to measure?",
                                list(metric_column_mapping.keys()))


def new_buoy_data(selected_buoys, metric):
    """
    Process the selected buoys and metric to retrieve new buoy data.

    Parameters:
        selected_buoys (Any): The selected buoys to process.
        metric (Any): The metric to use for retrieving the data.

    Returns:
        DataFrame: The resulting DataFrame containing the new buoy data.
    """

    df = pd.DataFrame()

    for buoy in selected_buoys:
      # create timezone objects for UTC and EST
        utc_tz = pytz.timezone('UTC')
        est_tz = pytz.timezone('US/Eastern')

        data = ascii.read(f"https://www.ndbc.noaa.gov/data/5day2/{buoy}_5day.spec")

        i = 0

        # Change while loop to adjust how many hours are shown in plots

    while i < 72:

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
          try:
            df.loc[i, buoy] = pd.to_numeric(data[i][7], errors='coerce')
          except ValueError:
            pass
        # get buoy's median swell direction
        elif MetricSelect == 'Swell Direction':
          df.loc[i, buoy] = data[i][14]

        # add datetime column
        df.loc[i, 'Datetime'] = est_datetime

        # increment i and get next buoy
        i += 1

        # error handling incomplete Swell Period Readings
    if df.isna().any().any():
        st.warning("Invalid value(s) found for buoy(s) in this report. These values do not display.")
    return df


if len(SelectedBuoys) == 0:
    st.warning('Please choose one or more buoys')

else:
    metric_column = metric_column_mapping[MetricSelect]
    df = new_buoy_data(SelectedBuoys, MetricSelect)

    # Create the line chart using the filtered dataframe
    # Set the y-axis range to start at 0
    df = df.sort_values(by=['Datetime'], ascending=True)

    fig = px.line(df, x='Datetime', y=SelectedBuoys, markers=True)
    fig.update_layout(yaxis=dict(title=MetricSelect),
                    xaxis_title='Time',
                    xaxis=dict(tickformat='%m/%d/%Y'))

    # Display the chart in the app
    st.plotly_chart(fig, use_container_width=True)