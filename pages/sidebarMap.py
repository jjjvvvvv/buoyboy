"""
THE BUOYBOY
https://buoyboy.streamlit.app

"""

from datetime import datetime
import streamlit as st
from astropy.io import ascii
import pandas as pd
import pytz

st.set_page_config(page_title="The BuoyBoy", page_icon="📡", layout="wide")

# TODO: need a way to update buoy list periodically...

df = pd.read_csv("buoylist.csv")

# TODO: create a dictionary to map buoys to their names

buoy_name_mapping = {}
for index, row in df.iterrows():
    buoy_name_mapping[row["buoy"]] = row["name"]

metric_column_mapping = {
    "Swell Height": "SwH",
    "Wave Height": "WvH",
    "Swell Period": "SwP",
    "Swell Direction": "MWD",
}

# makes a list of strings equal to 'buoy' + : + 'name'
buoy_name_list = [
    name + "(" + str(buoy) + ")" for buoy, name in buoy_name_mapping.items()
]

# LAYOUT 

col1, col2 = st.columns(2)

with col1:
    SelectedBuoys = st.multiselect(
        "Which buoy(s) do you want to view?", buoy_name_list, default=None
    )
    if len(SelectedBuoys) == 0:
        st.warning("Please choose one or more buoys")

# creates a list of selected buoys based on the user's selection
SelectedBuoys = [buoy.split("(")[1].split(")")[0] for buoy in SelectedBuoys]

with col2:
    MetricSelect = st.radio(
        "What do you want to measure?",
        list(metric_column_mapping.keys())
    )


def new_buoy_data(selected_buoys, metric, hours):
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
        utc_tz = pytz.timezone("UTC")
        est_tz = pytz.timezone("US/Eastern")

        data = ascii.read(f"https://www.ndbc.noaa.gov/data/5day2/{buoy}_5day.spec")

        # create a slider to determine how many loops to run

        # create a counter variable

        i = 0

        while i < hours:
            # create the date and time objects
            my_datetime = datetime(data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], tzinfo=utc_tz)

            # set the timezone for the datetime object using the 'tzinfo' attribute
            my_datetime = my_datetime.replace(tzinfo=utc_tz)

            # convert the datetime to EST
            est_datetime = my_datetime.astimezone(est_tz)

            # add datetime column
            df.loc[i, "Time"] = est_datetime

            # get metric to display

            # TODO: need to handle the case where the metric is not in the data
            # Currently 1/4

            if metric == "Swell Height":

                df.loc[i, buoy] = data[i][6] * int(3.28084)
            
            elif metric == "Wave Height":
            
                df.loc[i, buoy] = data[i][5] * int(3.28084)
            
            elif metric == "Swell Period":

                # This solves Swell Period being a string

                try:
                    df.loc[i, buoy] = pd.to_numeric(data[i][7], errors="coerce")
                except ValueError:
                    pass

            elif metric == "Swell Direction":
            
                df.loc[i, buoy] = data[i][14]

            # increment i and get next hour's reading
            i += 1

    if df.isna().any().any():
        st.warning(
            "Invalid value(s) found for buoy(s) in this report. These values do not display."
        )

    return df



if len(SelectedBuoys) == 0:
    st.stop()

else: 
    
    hours_choice = st.radio("How many hours?", [24, 48, 72, 128], horizontal=True)
    
    metric_column = metric_column_mapping[MetricSelect]
    df = new_buoy_data(SelectedBuoys, MetricSelect, hours_choice)

    # Create the line chart using the filtered dataframe
    # Set the y-axis range to start at 0
    df = df.sort_values(by=["Time"], ascending=True)

    st.line_chart(df, x="Time", y=SelectedBuoys, use_container_width=True)

    st.sidebar.subheader('Active buoys')


 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Add a sidebar map that uses the selected buoys to highlight them on the map
    # Use the sidebar to display the dataframe with the selected buoys highlighted
    # Return a map in the sidebar with only the selected buoys highlighted.
    # Use the first column of the dataframe as the key for the map.
    # Every buoy has a unique ID such as 44025, 44065, 44027, etc.

    # Create new df by re-reading the file buoylist.csv
    # Give the new df a name

    df = pd.read_csv("buoylist.csv")

    # edit dataframe to only include buoy name and lat/lon

    df = df[['buoy', 'lat', 'lon']]
    df = df.drop_duplicates()

    # rewrite all buoys in buoy column as strings

    df['buoy'] = df['buoy'].astype(str)


    # filter df to only include the selected buoys

    buoydf = df[df['buoy'].isin(SelectedBuoys)]

    # update sidebar map every time a buoy is added or removed from SelectedBuoys

    st.sidebar.map(data=buoydf, zoom=None, use_container_width=True)