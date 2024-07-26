import streamlit as st
import pandas as pd
from astropy.io import ascii
import pytz
from datetime import datetime

# Load data
@st.cache_data
def load_data(buoy_ids, metric, hours):
    try:
        # Create a DataFrame to store the data
        df = pd.DataFrame()
        
        for buoy_id in buoy_ids:
            # Fetch data from NOAA NDBC webpage
            data = ascii.read(f"https://www.ndbc.noaa.gov/data/5day2/{buoy_id}_5day.spec")
            
            # Create a counter variable
            i = 0
            
            while i < hours:
                # Create the date and time objects
                my_datetime = datetime(data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], tzinfo=pytz.timezone("UTC"))
                
                # Convert the datetime to EST
                est_datetime = my_datetime.astimezone(pytz.timezone("US/Eastern"))
                
                # Add datetime column
                if 'Time' not in df.columns:
                    df['Time'] = [est_datetime]
                else:
                    df.loc[i, 'Time'] = est_datetime
                
                # Get metric to display
                if metric == "Swell Height":
                    try:
                        if buoy_id not in df.columns:
                            df[buoy_id] = [float(data[i][6]) * 3.28084]
                        else:
                            df.loc[i, buoy_id] = float(data[i][6]) * 3.28084
                    except ValueError:
                        if buoy_id not in df.columns:
                            df[buoy_id] = [None]
                        else:
                            df.loc[i, buoy_id] = None
                elif metric == "Wave Height":
                    try:
                        if buoy_id not in df.columns:
                            df[buoy_id] = [float(data[i][5]) * 3.28084]
                        else:
                            df.loc[i, buoy_id] = float(data[i][5]) * 3.28084
                    except ValueError:
                        if buoy_id not in df.columns:
                            df[buoy_id] = [None]
                        else:
                            df.loc[i, buoy_id] = None
                elif metric == "Swell Period":
                    try:
                        if buoy_id not in df.columns:
                            df[buoy_id] = [pd.to_numeric(data[i][7], errors="coerce")]
                        else:
                            df.loc[i, buoy_id] = pd.to_numeric(data[i][7], errors="coerce")
                    except ValueError:
                        pass
                elif metric == "Swell Direction":
                    if buoy_id not in df.columns:
                        df[buoy_id] = [data[i][14]]
                    else:
                        df.loc[i, buoy_id] = data[i][14]
                
                # Increment i and get next hour's reading
                i += 1
        
        if df.isna().any().any():
            st.warning("Invalid value(s) found for buoy(s) in this report. These values do not display.")
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Process data
def process_data(buoy_data, metrics, time_frame):
    try:
        # Filter data by time frame
        time_frame_hours = int(time_frame.split(' hours')[0])  # Convert time frame to integer
        buoy_data = buoy_data.tail(time_frame_hours)
        
        # Check if data is available for selected buoys and time frame
        if buoy_data.empty:
            st.error("No data available for selected buoys and time frame")
            return None
        
        # Plot the selected metric
        for metric in metrics:
            ax = buoy_data[metric].plot(figsize=(10, 6))
            st.pyplot(ax.get_figure())

    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None

# Main app
def main():
    # Create a dropdown menu for buoy selection
    buoy_list = pd.read_csv('buoylist.csv')
    buoys = buoy_list['buoy'].unique()
    selected_buoys = st.multiselect('Select buoys', buoys, default=buoys[:2])
    
    # Create a dropdown menu for metric selection
    metrics = ['Swell Height', 'Wave Height', 'Swell Period', 'Swell Direction']
    selected_metrics = st.multiselect('Select metrics', metrics, default=metrics[:2])
    
    # Create radio buttons for time frame selection
    time_frames = ['24 hours', '48 hours', '72 hours', '128 hours']
    time_frame = st.radio('Select a time frame', time_frames)
    
    # Load data