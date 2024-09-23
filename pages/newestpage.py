import streamlit as st
from astropy.io import ascii
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Function to parse the buoy data and handle two-row headers
def parse_buoy_data(url):
    """
    Ingests the buoy data from the given URL and returns a DataFrame
    with the parsed data, using the first row as headers and skipping the second row.
    """
    try:
        # Read the data from the URL using astropy's ascii module
        data = ascii.read(url, header_start=0, data_start=2)  # Use the first row as headers, skip the second row
        st.write("Column Names:", data.colnames)  # Debugging: display column names in the app
        
    except Exception as e:
        st.error(f"Error loading data from {url}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    
    # Convert the astropy table to pandas for easier manipulation
    df = data.to_pandas()

    # Inspect the first few rows to ensure proper ingestion
    st.write("Sample Data:", df.head())  # Display the first few rows for inspection

    # Adjust for timezone and timestamp creation
    if {'#YY', 'MM', 'DD', 'hh', 'mm'}.issubset(df.columns):
        df['Time'] = df.apply(lambda row: datetime(row['#YY'], row['MM'], row['DD'], row['hh'], row['mm'], tzinfo=pytz.timezone("UTC")), axis=1)
        df['Time'] = df['Time'].apply(lambda x: x.astimezone(pytz.timezone("US/Eastern")))
        df.drop(['#YY', 'MM', 'DD', 'hh', 'mm'], axis=1, inplace=True)
    else:
        st.warning("Date/time columns (YY, MM, DD, hh, mm) not found in data.")

    return df

# URL for example buoy data (5day.spec file)
url = "https://www.ndbc.noaa.gov/data/5day2/44025_5day.spec"

# Parse the buoy data
df = parse_buoy_data(url)

# Define the metric mapping based on correct headers
metric_column_mapping = {
    "Swell Height": "SwH",
    "Wave Height": "WVHT",
    "Swell Period": "SwP",
    "Swell Direction": "MWD"
}

# Function to map buoy metrics to the correct columns
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

# Map the relevant metrics
mapped_df = map_buoy_metrics(df, metric_column_mapping)

# Display the resulting data in Streamlit
if not mapped_df.empty:
    st.dataframe(mapped_df)
else:
    st.warning("No data available for the selected metrics.")