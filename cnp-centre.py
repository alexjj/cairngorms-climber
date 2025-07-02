import geopandas as gpd
import pandas as pd
import json

# --- STEP 1. Load the GeoJSON perimeter ---
# This reads a GeoDataFrame
gdf = gpd.read_file("cairngorms.geojson")

# Dissolve geometries to single geometry if multiple features exist
park_geom = gdf.geometry.union_all()

# Compute the centroid
centroid = park_geom.centroid
centre_lat = centroid.y
centre_lon = centroid.x

print(f"Centroid coordinates: {centre_lat}, {centre_lon}")

# --- STEP 2. Load the CSV of summits ---
summits_df = pd.read_csv("cairngorms_summits.csv")

# Prepare list of markers for JavaScript
summit_markers = []
for _, row in summits_df.iterrows():
    marker = {
        "name": row["name"],
        "code": row["summitCode"],
        "lat": row["latitude"],
        "lon": row["longitude"],
        "altM": row["altM"],
        "points": row["points"],
        "region": row["Region"]
    }
    summit_markers.append(marker)

# --- STEP 3. Prepare GeoJSON of perimeter for Leaflet ---
# Convert GeoPandas GeoDataFrame to JSON string
park_geojson_str = gdf.to_json()

# Format centroid coordinates as strings with 5 decimals
centre_lat_str = f"{centre_lat:.5f}"
centre_lon_str = f"{centre_lon:.5f}"

# --- STEP 4. Generate HTML file ---
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Cairngorms National Park Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <style>
      #map {{
        height: 800px;
      }}
    </style>
</head>
<body>
<div id="map"></div>

<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
<script>

// Create map and center on centroid
var map = L.map('map').setView([{centre_lat}, {centre_lon}], 10);

// Add base layer
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
}}).addTo(map);

// --- Add park perimeter polygon ---
var parkGeoJson = {json.dumps(json.loads(park_geojson_str))};

L.geoJSON(parkGeoJson, {{
    style: {{
        color: 'green',
        weight: 2,
        fillOpacity: 0.1
    }}
}}).addTo(map);

// --- Add summit markers ---
var summitData = {json.dumps(summit_markers)};

summitData.forEach(function(summit) {{
    var popup = "<b>" + summit.name + "</b><br>" +
                "Code: " + summit.code + "<br>" +
                "Alt: " + summit.altM + " m<br>" +
                "Points: " + summit.points + "<br>" +
                "Region: " + summit.region;
    L.marker([summit.lat, summit.lon]).addTo(map)
        .bindPopup(popup);
}});

// --- Add centroid marker ---
L.marker([{centre_lat}, {centre_lon}], {{
    icon: L.icon({{
        iconUrl: 'https://maps.gstatic.com/intl/en_us/mapfiles/markers2/measle.png',
        iconSize: [12, 12]
    }})
}}).addTo(map)
  .bindPopup("<b>Park Centre</b><br>Lat: {centre_lat_str}<br>Lon: {centre_lon_str}");

</script>
</body>
</html>
"""

# Write out to file
with open("cairngorms_map.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Map saved as cairngorms_map.html")
