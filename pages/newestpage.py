import streamlit as st
import pandas as pd

# Set page configuration for mobile-friendly layout
st.set_page_config(page_title="Buoy Swell Data", page_icon="🌊", layout="centered")

# Define the buoy data retrieval function (following home.py structure)
@st.cache_data(ttl=600)
def get_buoy_data(station_id):
    url = f'https://www.ndbc.noaa.gov/data/realtime2/{station_id}.txt'
    
    # Manually define the column headers (same as in home.py)
    headers = ["#YY", "MM", "DD", "hh", "mm", "WDIR", "WSPD", "GST", "WVHT", "DPD", "APD", "MWD", 
               "PRES", "ATMP", "WTMP", "DEWP", "VIS", "TIDE", "SwH", "SwP", "SwD"]
    
    # Read the data and assign the correct headers
    df = pd.read_csv(url, delim_whitespace=True, skiprows=[1], names=headers, na_values=['MM'])
    
    # Ensure the date-time columns are present and correctly parsed
    if {"#YY", "MM", "DD", "hh", "mm"}.issubset(df.columns):
        df['date_time'] = pd.to_datetime(df[['#YY', 'MM', 'DD', 'hh', 'mm']])
        df.set_index('date_time', inplace=True)
        df.drop(columns=['#YY', 'MM', 'DD', 'hh', 'mm'], inplace=True, errors='ignore')
    else:
        st.warning("Date columns are missing or incomplete in the data.")
        return pd.DataFrame()  # Return empty DataFrame if date components are missing
    
    return df

# Main page content
def main():
    st.title("Buoy Swell and Wave Data")

    # Input to get station ID (same as home.py)
    station_id = st.text_input("Enter Buoy Station ID", value="46042", help="e.g., 46042")

    # Fetch data when station ID is entered
    if station_id:
        with st.spinner("Fetching buoy data..."):
            try:
                df = get_buoy_data(station_id)
                if not df.empty:
                    st.success(f"Data retrieved for Station {station_id}")

                    # Filter for desired columns
                    required_columns = ['SwH', 'WVHT', 'SwP', 'SwD']  # Assuming these are the correct column names for your data
                    if all(col in df.columns for col in required_columns):
                        # Subset data
                        df_filtered = df[required_columns]
                        df_filtered.columns = ['Swell Height (m)', 'Wave Height (m)', 'Swell Period (s)', 'Swell Direction (°)']

                        # Display the filtered data
                        st.dataframe(df_filtered)

                        # Optionally display a chart for these fields
                        st.line_chart(df_filtered)
                    else:
                        missing_cols = [col for col in required_columns if col not in df.columns]
                        st.warning(f"Missing columns in data: {', '.join(missing_cols)}")
                else:
                    st.warning("No data available for this station.")
            except Exception as e:
                st.error(f"An error occurred while fetching data: {e}")

if __name__ == "__main__":
    main()