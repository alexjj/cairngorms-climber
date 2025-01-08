import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
from utils import filter_callsigns, get_remaining_summits

# Load data
file = 'sota_awards_summary.json'
with open(file, 'r') as json_file:
    activations_summary = json.load(json_file)

# Title of the app
st.title("Cairngorm Climbers' Award Summary")

# Text input for filtering callsigns
search_term = st.text_input("Search Callsign:")

# Filter the data based on the search term
filtered_data = filter_callsigns(activations_summary, search_term)

# Display the table
st.subheader("Honour roll")
st.dataframe(filtered_data[['Callsign', 'SummitsActivated', 'Award', 'AwardDate']])

# Select a callsign to view remaining summits
selected_callsign = st.selectbox("Select a Callsign:", filtered_data['Callsign'])

if selected_callsign:
    remaining_summits = get_remaining_summits(activations_summary, selected_callsign)

    # Create a map for remaining summits
    map_center = [55.0, -4.0]  # Center of the map (adjust as necessary)
    summit_map = folium.Map(location=map_center, zoom_start=8)

    for summit in remaining_summits:
        folium.Marker(
            location=[summit['latitude'], summit['longitude']],
            popup=f"{summit['summitCode']} - {summit['points']} points",
        ).add_to(summit_map)

    # Display the map
    st.subheader("Remaining Summits")
    st_folium(summit_map, width=700, height=500)
