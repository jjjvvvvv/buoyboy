from datetime import datetime, timedelta
import streamlit as st
from astropy.io import ascii
import pandas as pd
import pytz

st.set_page_config(page_title="Buoy Data Page", layout="wide")

# Buoy and metric mappings
df = pd.read_csv("buoylist.csv")

buoy_name_mapping = {}
for index, row in df.iterrows():
    buoy_name_mapping[row["buoy"]] = row["name"]

metric_column_mapping = {
    "Swell Height": "SwH",
    "Wave Height": "WVHT",
    "Swell Period": "SwP",
    "Swell Direction": "MWD",
}

buoy_name_list = [
    name + "(" + str(buoy) + ")" for buoy, name in buoy_name_mapping.items()
]

col1, col2 = st.columns(2)

# Select buoys and metrics
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

# Select the time range (in hours)
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

# Process the selected buoys
SelectedBuoys = [buoy.split("(")[1].split(")")[0] for buoy in SelectedBuoys]


# Function to parse buoy data (adjusted for datetime creation and missing data handling)
def parse_buoy_data(buoy_id):
    """
    Ingests the buoy data from the 5-day spec file for a given buoy and returns a DataFrame
    with the parsed data, ensuring the 'Time' column is properly created.
    """
    url = f"https://www.ndbc.noaa.gov/data/5day2/{buoy_id}_5day.spec"
    
    try:
        # Read the data from the URL using astropy's ascii module
        data = ascii.read(url, header_start=0, data_start=2)  # Use the first row as headers, skip the second row
    except Exception as e:
        st.error(f"Error loading data for buoy {buoy_id}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    
    # Convert the astropy table to pandas for easier manipulation
    df = data.to_pandas()

    # Check if necessary date and time columns exist (adjusting for the prefix in '#YY')
    required_columns = ['YY', 'MM', 'DD', 'hh', 'mm']
    if set(required_columns).issubset(df.columns):
        # Drop rows with missing values in any of the required columns
        df.dropna(subset=required_columns, inplace=True)

        try:
            # Check if 'Time' column already exists to avoid duplicates
            if 'Time' not in df.columns:
                # Combine the year, month, day, hour, and minute columns into a single 'Time' column
                df['Time'] = pd.to_datetime(df[['YY', 'MM', 'DD', 'hh', 'mm']].rename(columns={'YY': 'year'}))
                df['Time'] = df['Time'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')  # Convert to Eastern time
                df.drop(columns=['YY', 'MM', 'DD', 'hh', 'mm'], inplace=True)  # Drop the original columns
        except Exception as e:
            st.error(f"Error creating 'Time' column: {e}")
    else:
        st.warning(f"Date/time columns (YY, MM, DD, hh, mm) not found for buoy {buoy_id}.")
    
    return df


# Function to map buoy metrics
def map_buoy_metrics(df, metric):
    """
    Maps the relevant columns for the selected metric (swell height, wave height, etc.)
    and returns a DataFrame containing only the relevant data for that metric.
    """
    metric_column = metric_column_mapping.get(metric, None)
    
    if 'Time' in df.columns and metric_column in df.columns:
        # Return the DataFrame with the Time and metric column
        return df[['Time', metric_column]].rename(columns={metric_column: metric})
    else:
        # If the column is not found, show a warning and print available columns for debugging
        st.warning(f"Column '{metric_column}' for '{metric}' not found in the data.")
        return pd.DataFrame()  # Return an empty DataFrame if the column is missing


# Fetch and process data for each selected buoy
def new_buoy_data(selected_buoys, metric, hours):
    df_final = pd.DataFrame()

    for buoy in selected_buoys:
        # Fetch the buoy data
        df_buoy = parse_buoy_data(buoy)
        
        if not df_buoy.empty:
            # Only create the 'Time' column if it's not already there (avoiding duplicates)
            if 'Time' not in df_buoy.columns:
                for i in range(hours):
                    try:
                        my_datetime = datetime(
                            df_buoy.iloc[i]['YY'],  # Year
                            df_buoy.iloc[i]['MM'],  # Month
                            df_buoy.iloc[i]['DD'],  # Day
                            df_buoy.iloc[i]['hh'],  # Hour
                            df_buoy.iloc[i]['mm'],  # Minute
                            tzinfo=pytz.UTC  # Assuming data is in UTC
                        )
                        my_datetime += timedelta(minutes=30)  # Add 30 minutes
                        est_datetime = my_datetime.astimezone(pytz.timezone("US/Eastern"))
                        
                        # Explicitly cast 'Time' to datetime64[ns] format
                        df_buoy.loc[i, "Time"] = pd.to_datetime(est_datetime)
                    except Exception as e:
                        st.error(f"Error processing date and time for buoy {buoy}: {e}")
            
            df_buoy = map_buoy_metrics(df_buoy, metric)
            df_buoy = df_buoy.tail(hours)
            df_final = pd.concat([df_final, df_buoy], axis=1)

    if df_final.isna().any().any():
        st.warning("Invalid value(s) found in this report. These values do not display.")
    
    return df_final


# Display the data for selected buoys and metrics
if len(SelectedBuoys) > 0:
    new_df = new_buoy_data(SelectedBuoys, MetricSelect, hours_choice)

    if not new_df.empty:
        new_df = new_df.sort_values(by=["Time"], ascending=True)
        st.line_chart(data=new_df, x="Time", y=SelectedBuoys, use_container_width=True)
    else:
        st.warning("No data available for the selected buoys.")
