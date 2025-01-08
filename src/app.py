import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium

# Load JSON data
def load_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Process data into DataFrame
def process_data(data):
    rows = []
    for entry in data:
        rows.append({
            "Operator": entry["Callsign"],
            "Total Summits Activated": int(entry["SummitsActivated"]),
            "Highest Award Achieved": entry["Award"],
            "Date of Award": entry["AwardDate"],
            "RemainingSummits": entry["RemainingSummits"]
        })
    return pd.DataFrame(rows)

# Create Streamlit app
st.set_page_config(page_title="Cairngorms Climbers' Award", page_icon=":sports_medal:", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("🏔️Cairngorms Climbers' Award🏆")

st.markdown('''The GM/ES SOTA Society wish to recognise those radio amateurs who venture into the remote lands of the Cairngorms, and have created awards for summits activated within the Cairngorms National Park.

There are 82 SOTA summits in the Cairngorms National Park, including several of the highest peaks in the UK. The SOTA summits are split across the regions with 44 in ES, 36 in CS, and 2 in WS.''')

st.subheader("Cairngorm Summits")

# Cairngorms summit map

summits_df = pd.read_csv('cairngorms_summits.csv')
cairngorms_geojson = load_data("cairngorms.geojson")
map_center = [57.07, -3.7]
my_map = folium.Map(location=map_center, zoom_start=8)

folium.GeoJson(
    cairngorms_geojson,
    name="Cairngorms"
).add_to(my_map)

# Iterate through the summits in combined_df
for index, row in summits_df.iterrows():
    latitude = row['latitude']
    longitude = row['longitude']

    popup = f"""<b>{row['name']}</b><br><a href="https://sotl.as/summits/{row['summitCode']}" target="_blank">{row['summitCode']}</a><br>Points: {row['points']}"""

    tooltip = row['name']

    tooltip = f"<b>{row['name']}</b><br>Points: {row['points']}"
    folium.Marker(
        location=[latitude, longitude],
        popup=popup,
        tooltip=tooltip,
        icon=folium.Icon(color="lightgreen" if row["points"] == 1 else "green" if row["points"] ==2 else "darkgreen" if row["points"] == 4 else "orange" if row["points"] == 6 else "darkred" if row["points"] == 8 else "red")
    ).add_to(my_map)

st_folium(my_map, width=700, height=500)

st.subheader("Award Definitions")
st.markdown('''

|         Award          | Number of Summits Activated |
|:----------------------:|:---------------------------:|
|     Heather Hopper     |              1              |
|   Ptarmigan Pioneer    |              5              |
| Capercaillie Conqueror |             10              |
|    Osprey Outlander    |             41              |
| Golden Eagle Explorer  |             82              |
''')

st.markdown("Calculated daily, the awards are presented below. You can select your callsign from the dropdown to see which summits you still need to activate to achieve the Golden Eagle Explorer 🦅🥇")

# Load and display table
data = load_data("sota_awards_summary.json")
df = process_data(data)
df_display = df.drop(columns=["RemainingSummits"]).sort_values(by="Total Summits Activated", ascending=False)
df_sorted = df.sort_values(by="Operator").reset_index(drop=True)

# Configure column formats
column_config = {
    "Operator": st.column_config.TextColumn("Operator"),
    "Total Summits Activated": st.column_config.NumberColumn("Total Summits Activated"),
    "Highest Award Achieved": st.column_config.TextColumn("Highest Award Achieved"),
    "Date of Award": st.column_config.DatetimeColumn(
        "Date of Award", format="Do MMM YYYY"
    )
}

# Display sortable and searchable table
st.subheader("Honour Roll")
selected_row = st.dataframe(
    df_display.style.set_properties(**{'text-align': 'left'}),
    use_container_width=True,
    hide_index=True,
    column_config=column_config,
    selection_mode="single-row"
)
st.caption("The date is wrong...investigating...")

# Create dropdown sorted alphabetically by Operator
selected_index = st.selectbox(
    "Select an operator to view remaining summits:",
    options=range(len(df_sorted)),
    index=None,
    format_func=lambda x: df_sorted.iloc[x]["Operator"]
)

# Plot remaining summits on a map
if selected_index is not None:
    remaining_summits = df_sorted.iloc[selected_index]["RemainingSummits"]

    # Create Folium map
    m = folium.Map(location=[57.07, -3.7], zoom_start=8.5)  # Centered around Scotland
    folium.GeoJson(cairngorms_geojson,name="Cairngorms").add_to(m)

    for summit in remaining_summits:

        latitude = summit['latitude']

        longitude = summit['longitude']

        popup = f"""<b>{summit['summitname']}</b><br><a href="https://sotl.as/summits/{summit['summitCode']}" target="_blank">{summit['summitCode']}</a><br>Points: {summit['points']}"""

        tooltip = summit['summitname']

        folium.Marker(
            location=[latitude, longitude],
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color="lightgreen" if summit["points"] == '1' else "green" if summit["points"] =='2' else "darkgreen" if summit["points"] == '4' else "orange" if summit["points"] == '6' else "darkred" if summit["points"] == '8' else "red")
        ).add_to(m)

    st.subheader(f"Remaining Summits for {df_sorted.iloc[selected_index]['Operator']}")
    st_folium(m, width=700, height=500)

    # Display remaining summits in a table
    remaining_summits_table = pd.DataFrame([
        {
            "Summit Name": summit["summitname"],
            "Summit Code": summit["summitCode"],
            "Points": summit["points"]
        }
        for summit in remaining_summits
    ])
    st.subheader(f"List of the {len(remaining_summits)} remaining summits:")
    st.dataframe(remaining_summits_table, hide_index=True)
