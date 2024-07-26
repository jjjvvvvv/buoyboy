"""
THE BUOYBOY
https://buoyboy.streamlit.app
"""

from datetime import datetime, timedelta
import streamlit as st
from astropy.io import ascii
import pandas as pd
import pytz

st.set_page_config(page_title="The BuoyBoy", page_icon="", layout="wide")

df = pd.read_csv("buoylist.csv")

buoy_name_mapping = {}
for index, row in df.iterrows():
    buoy_name_mapping[row["buoy"]] = row["name"]

metric_column_mapping = {
    "Swell Height": "SwH",
    "Wave Height": "WvH",
    "Swell Period": "SwP",
    "Swell Direction": "MWD",
}

buoy_name_list = [
    name + "(" + str(buoy) + ")" for buoy, name in buoy_name_mapping.items()
]

col1, col2 = st.columns(2)

with col1:
    SelectedBuoys = st.multiselect(
        "Which buoy(s) do you want to view?", buoy_name_list, default=None
    )

    if len(SelectedBuoys) == 0:
        st.warning("Please choose one or more buoys")

with col2:
    MetricSelect = st.radio(
        "What do you want to measure?",
        list(metric_column_mapping.keys())
    )

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    st.write("")  # Empty column
with col2:
    if st.button("1 Day"):
        st.session_state.hours_choice = 48
with col3:
    if st.button("2 Days"):
        st.session_state.hours_choice = 96
with col4:
    if st.button("3 Days"):
        st.session_state.hours_choice = 144
with col5:
    if st.button("4 Days"):
        st.session_state.hours_choice = 192
with col6:
    if st.button("5 Days"):
        st.session_state.hours_choice = 238
with col7:
    st.write("")  # Empty column

# Initialize hours_choice if it's not already set
if "hours_choice" not in st.session_state:
    st.session_state.hours_choice = 48

hours_choice = st.session_state.hours_choice

SelectedBuoys = [buoy.split("(")[1].split(")")[0] for buoy in SelectedBuoys]

def new_buoy_data(selected_buoys, metric, hours):
    df = pd.DataFrame()

    for buoy in selected_buoys:
        data = ascii.read(f"https://www.ndbc.noaa.gov/data/5day2/{buoy}_5day.spec")

        i = 0

        while i < hours:
            my_datetime = datetime(data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], tzinfo=pytz.timezone("UTC"))
            my_datetime += timedelta(minutes=30)  # add 30 minutes
            est_datetime = my_datetime.astimezone(pytz.timezone("US/Eastern"))

            df.loc[i, "Time"] = est_datetime

            if metric == "Swell Height":
                try:
                    df.loc[i, buoy] = float(data[i][6]) * 3.28084
                except ValueError:
                    df.loc[i, buoy] = None
            elif metric == "Wave Height":
                try:
                    df.loc[i, buoy] = float(data[i][5]) * 3.28084
                except ValueError:
                    df.loc[i, buoy] = None
            elif metric == "Swell Period":
                try:
                    df.loc[i, buoy] = pd.to_numeric(data[i][7], errors="coerce")
                except ValueError:
                    df.loc[i, buoy] = None
            elif metric == "Swell Direction":
                df.loc[i, buoy] = data[i][14]

            i += 2  # increment by 2 (30-minute intervals)

    if df.isna().any().any():
        st.warning("Invalid value(s) found in this report. These values do not display.")

    return df

if len(SelectedBuoys) > 0:
    metric_column = metric_column_mapping[MetricSelect]
    new_df = new_buoy_data(SelectedBuoys, MetricSelect, hours_choice)

    new_df = new_df.sort_values(by=["Time"], ascending=True)

    st.line_chart(data=new_df, x="Time", y=SelectedBuoys, use_container_width=True)