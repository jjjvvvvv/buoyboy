import streamlit as st
import pandas as pd

df = pd.read_csv('buoylist.csv')

# make new dataframe only when lat and lon are not null

df = df[df['lat'].notna()]
df = df[df['lon'].notna()]

buoy_name_mapping = {}
for index, row in df.iterrows():
    buoy_name_mapping[row["buoy"]] = row["name"]

buoy_name_list = list(buoy_name_mapping.values())

# Remove extra " at the end of the names in buoy_name_list
# use enumerate to get the index and value of each item in the list

for index, value in enumerate(buoy_name_list):
    buoy_name_list[index] = value[:-1]

SelectedBuoys = st.multiselect(
    "Which buoy(s) do you want to view?", buoy_name_mapping.values(), default=None)
if len(SelectedBuoys) == 0:
    st.warning("Please choose one or more buoys")

# SelectedBuoys is now a list of the selected names in the multiselect.
# I need to convert these names back to the buoy numbers to use in the map.
# Use the buoy_name_mapping dictionary to convert the names back to buoy numbers
# and store the results in a new list called SelectedBuoys

SelectedBuoys = [buoy for buoy in buoy_name_mapping if buoy_name_mapping[buoy] in SelectedBuoys]

buoydf = df[df['buoy'].isin(SelectedBuoys)]

# If the length of Selected buoys changes I need to update the map
# I need to update the map when the user selects a new buoy


st.map(data=buoydf, zoom=None, use_container_width=True)

st.subheader('Currently serving these buoys')
st.write('see status log for updates')