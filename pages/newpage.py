import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Buoy Data Viewer",
    page_icon="🌊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

def get_buoy_data(station_id, data_type='txt'):
    url = f'https://www.ndbc.noaa.gov/data/realtime2/{station_id}.{data_type}'
    df = pd.read_csv(url, delim_whitespace=True, skiprows=[1], na_values=['MM'])
    # Process date and time columns
    date_cols = ['YY', 'MM', 'DD', 'hh', 'mm']
    for col in date_cols:
        if col not in df.columns and f'#{col}' in df.columns:
            df.rename(columns={f'#{col}': col}, inplace=True)

    df['date_time'] = pd.to_datetime(df[['YY', 'MM', 'DD', 'hh', 'mm']])
    df.set_index('date_time', inplace=True)
    df.drop(columns=['YY', 'MM', 'DD', 'hh', 'mm'], inplace=True, errors='ignore')
    return df

def get_station_info(station_id):
    url = 'https://www.ndbc.noaa.gov/data/stations/station_table.txt'
    stations_df = pd.read_csv(url, sep='|', header=None, names=['ID', 'Latitude', 'Longitude', 'Name'])
    station_info = stations_df[stations_df['ID'].str.strip() == station_id]
    return station_info

def main():
    st.header('Buoy Data Viewer')

    # Inputs in the main area for better mobile visibility
    station_id = st.text_input('Enter Buoy Station ID', '46042', help='e.g., 46042')
    data_type_options = {
        'Real-time': 'txt',
        'Standard Meteorological': 'stdmet',
        'Oceanographic': 'ocean',
        'Spectral Wave Density': 'swden'
    }
    data_type_name = st.selectbox('Select Data Type', list(data_type_options.keys()))
    data_type = data_type_options[data_type_name]

    @st.cache_data(ttl=600)
    def load_data(station_id, data_type):
        return get_buoy_data(station_id, data_type)

    if station_id:
        with st.spinner('Fetching data...'):
            try:
                df = load_data(station_id, data_type)
                if not df.empty:
                    st.success(f"Data for Station {station_id}")

                    # Fetch and display station info
                    station_info = get_station_info(station_id)
                    if not station_info.empty:
                        st.write(f"**Station Name:** {station_info.iloc[0]['Name'].strip()}")
                        st.write(f"**Location:** {station_info.iloc[0]['Latitude']}, {station_info.iloc[0]['Longitude']}")

                        # Map visualization
                        location_df = pd.DataFrame({
                            'lat': [station_info.iloc[0]['Latitude']],
                            'lon': [station_info.iloc[0]['Longitude']]
                        })
                        st.map(location_df)

                    # Display data
                    st.dataframe(df)

                    # Identify numeric columns for plotting
                    numeric_cols = df.select_dtypes(include=['float', 'int']).columns.tolist()

                    if numeric_cols:
                        variables = st.multiselect('Select variables to plot', numeric_cols, default=numeric_cols[:2])
                        if variables:
                            st.line_chart(df[variables])
                        else:
                            st.warning('Please select at least one variable to plot.')
                    else:
                        st.warning('No numeric data available to plot.')
                else:
                    st.warning('No data available for this station and data type.')
            except pd.errors.ParserError:
                st.error('Data format has changed. Please try again later.')
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()