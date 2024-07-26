import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Load data
@st.cache
def load_data():
    try:
        # Load buoy data from NOAA NDBC
        buoy_data = pd.read_csv('buoy_data.csv')
        return buoy_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Process data
def process_data(buoy_data):
    try:
        # Handle missing values and outliers
        buoy_data = buoy_data.dropna()
        buoy_data = buoy_data[(np.abs(buoy_data['wind_speed']) < 50) & (np.abs(buoy_data['wave_height']) < 20)]
        return buoy_data
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None

# Create visualizations
def create_visualizations(buoy_data):
    try:
        # Wind speed plot
        wind_speed_fig = px.line(buoy_data, x='timestamp', y='wind_speed', title='Wind Speed')
        wind_speed_fig.update_layout(yaxis_range=[0, 50])

        # Wave height plot
        wave_height_fig = px.line(buoy_data, x='timestamp', y='wave_height', title='Wave Height')
        wave_height_fig.update_layout(yaxis_range=[0, 20])

        return wind_speed_fig, wave_height_fig
    except Exception as e:
        st.error(f"Error creating visualizations: {e}")
        return None, None

# Main app
def main():
    buoy_data = load_data()
    if buoy_data is not None:
        buoy_data = process_data(buoy_data)
        if buoy_data is not None:
            wind_speed_fig, wave_height_fig = create_visualizations(buoy_data)
            if wind_speed_fig and wave_height_fig:
                st.plotly_chart(wind_speed_fig)
                st.plotly_chart(wave_height_fig)
            else:
                st.error("Error creating visualizations")
        else:
            st.error("Error processing data")
    else:
        st.error("Error loading data")

if __name__ == "__main__":
    main()
