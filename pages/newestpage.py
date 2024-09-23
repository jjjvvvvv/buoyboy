import streamlit as st
from astropy.io import ascii
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Flexible parsing function to automatically map metrics from the 5day.spec file
def parse_buoy_data(url):
    """
    Ingests the buoy data from the given URL and returns a DataFrame
    with the parsed data, using dynamic column mapping based on the headers.
    """
    # Read the data from the URL using astropy's ascii module
    try:
        data = ascii.read(url)
    except Exception as e:
        st.error(f"Error loading data from {url}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    
    # Inspect the first few rows to understand the structure
    headers = data.colnames
    # Convert the astropy table to pandas for easier manipulation
    df = data.to_pandas()

    # Adjust for timezone and timestamp creation
    df['Time'] = df.apply(lambda row: datetime(row['col1'], row['col2'], row['col3'], row['col4'], row['col5'], tzinfo=pytz.timezone("UTC")), axis=1)
    df['Time'] = df['Time'].apply(lambda x: x.astimezone(pytz.timezone("US/Eastern")))

    # Drop columns that aren't needed
    df.drop(['col1', 'col2', 'col3', 'col4', 'col5'], axis=1, inplace=True)

    return df, headers

# Automatically map the buoy data to the relevant columns
def map_buoy_metrics(df, metric_mapping):
    """
    Maps the relevant columns for the metrics (swell height, wave height, etc.)
    and returns a DataFrame containing only the relevant data.
    """
    mapped_df = pd.DataFrame()
    for metric, column_name in metric_mapping.items():
        if column_name in df.columns:
            mapped_df[metric] = df[column_name]
        else:
            st.warning(f"Column {column_name} not found in the dataset.")
            mapped_df[metric] = None  # Fill with None if column not found

    return mapped_df

# URL for example buoy data (5day.spec file)
url = "https://www.ndbc.noaa.gov/data/5day2/44025_5day.spec"

# Parse the buoy data
df, headers = parse_buoy_data(url)

# Define the metric mapping (dynamic mapping from column names)
metric_column_mapping = {
    "Swell Height": "col6",  # Assuming this is the correct column for Swell Height
    "Wave Height": "col5",   # Assuming this is the correct column for Wave Height
    "Swell Period": "col7",  # Assuming this is the correct column for Swell Period
    "Swell Direction": "col14" # Assuming this is the correct column for Swell Direction
}

# Map the relevant metrics
mapped_df = map_buoy_metrics(df, metric_column_mapping)

# Display the resulting data in Streamlit
if not mapped_df.empty:
    st.dataframe(mapped_df)
else:
    st.warning("No data available for the selected metrics.")