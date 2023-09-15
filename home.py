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
        data = ascii.read(f"https://www.ndbc.noaa.gov/data/5day2/{buoy}_5day.spec")

        # create a counter variable

        i = 0

        while i < hours:
            # create the date and time objects
            my_datetime = datetime(data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], tzinfo=pytz.timezone("UTC"))

            # convert the datetime to EST according to the streamlit docs

            est_datetime = my_datetime.astimezone(pytz.timezone("US/Eastern"))

            # add datetime column
            df.loc[i, "Time"] = est_datetime

            # get metric to display
            if metric == "Swell Height":
                df.loc[i, buoy] = data[i][6] * int(3.28084)
            elif metric == "Wave Height":
                df.loc[i, buoy] = data[i][5] * int(3.28084)
            elif metric == "Swell Period":
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
    new_df = new_buoy_data(SelectedBuoys, MetricSelect, hours_choice)
    
    # Create the line chart using the filtered dataframe
    # Set the y-axis range to start at 0
    new_df = new_df.sort_values(by=["Time"], ascending=True)

    st.line_chart(data=new_df, x="Time", y=SelectedBuoys, use_container_width=True)