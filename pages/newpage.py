from datetime import datetime, timedelta
import streamlit as st
from astropy.io import ascii
import pandas as pd
import pytz

# URL for buoy data
url = "https://www.ndbc.noaa.gov/data/5day2/44025_5day.spec"

# Function to parse the buoy data
def parse_buoy_data(buoy_id):
    url = f"https://www.ndbc.noaa.gov/data/5day2/{buoy_id}_5day.spec"
    try:
        # Read data from the URL using astropy's ascii module
        data = ascii.read(url, header_start=0, data_start=2)
    except Exception as e:
        st.error(f"Error loading data for buoy {buoy_id}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

    df = data.to_pandas()  # Convert to pandas DataFrame

    # Combine date and time columns to create a 'Time' column
    if {'YY', 'MM', 'DD', 'hh', 'mm'}.issubset(df.columns):
        df['Time'] = pd.to_datetime(df[['YY', 'MM', 'DD', 'hh', 'mm']].rename(columns={'YY': 'year'}))
        df['Time'] = df['Time'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
        df.drop(columns=['YY', 'MM', 'DD', 'hh', 'mm'], inplace=True)
    else:
        st.warning(f"Date/time columns not found for buoy {buoy_id}")

    return df

# Metric mapping
metric_column_mapping = {
    "Swell Height": "SwH",
    "Wave Height": "WVHT",
    "Swell Period": "SwP",
    "Swell Direction": "MWD"
}

# Function to map metrics
def map_buoy_metrics(df, metric):
    if 'Time' in df.columns and metric in metric_column_mapping.values():
        return df[['Time', metric]]
    else:
        st.warning(f"Column '{metric}' not found in data")
        return pd.DataFrame()  # Return empty DataFrame if not found

# Buoy selection and processing
buoy_id = "44025"  # Example buoy ID
df_buoy = parse_buoy_data(buoy_id)

# Map relevant metrics (e.g., Swell Height, Wave Height)
if not df_buoy.empty:
    df_mapped = map_buoy_metrics(df_buoy, 'SwH')  # Example for Swell Height
    if not df_mapped.empty:
        st.line_chart(df_mapped.set_index('Time'))  # Plot the data using Streamlit
    else:
        st.warning("No data available for the selected metric.")
else:
    st.warning("No data available for the selected buoy.")