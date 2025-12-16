import pandas as pd
import requests
import json
from datetime import datetime

# Load summit data from CSV
summits_df = pd.read_csv('cairngorms_summits.csv')
summit_codes = summits_df['summitCode'].tolist()

# Function to fetch activations from SOTA API
def fetch_activations(summit_code):
    url = f"https://api-db2.sota.org.uk/api/activations/{summit_code}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {summit_code}: {response.status_code}")
        return []

def fetch_callsign(userId):
    url = f"https://sotl.as/api/activators/{userId}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('callsign')
    return None


# Collect activation data
activation_data = []

for summit_code in summit_codes:
    data = fetch_activations(summit_code)
    for entry in data:
        activation_data.append({
            'summitCode': summit_code,
            'UserId': entry['userId'],
            'Callsign': entry['ownCallsign'],
            'ActivationDate': datetime.strptime(entry['activationDate'], '%Y-%m-%dT%H:%M:%SZ'),
        })

# Create DataFrame from activation data
activations_df = pd.DataFrame(activation_data)
activations_df['ActivationDate'] = pd.to_datetime(activations_df['ActivationDate'])

# Aggregate per user
activations_summary = (
    activations_df
    .groupby('UserId')
    .agg(
        SummitsActivated=('summitCode', 'nunique'),
        FirstActivationDate=('ActivationDate', 'min'),
        LastActivationDate=('ActivationDate', 'max')
    )
    .reset_index()
)

activations_summary['ActivationSpanDays'] = (
    activations_summary['LastActivationDate'] -
    activations_summary['FirstActivationDate']
).dt.days
activations_summary['Callsign'] = activations_summary['UserId'].apply(fetch_callsign)

# Determine remaining summits for each userId
def get_remaining_summits(user_id):
    activated_summits = set(activations_df[activations_df['UserId'] == user_id]['summitCode'])
    all_summits = set(summit_codes)
    remaining_summits = all_summits - activated_summits
    return [
        {
            'summitCode': summit_code,
            'summitname': summits_df[summits_df['summitCode'] == summit_code]['name'].values[0],
            'latitude': summits_df[summits_df['summitCode'] == summit_code]['latitude'].values[0],
            'longitude': summits_df[summits_df['summitCode'] == summit_code]['longitude'].values[0],
            'points': summits_df[summits_df['summitCode'] == summit_code]['points'].values[0]
        }
        for summit_code in remaining_summits
    ]

# Create JSON structure
output_data = []
for user_id in activations_summary['UserId']:
    user_data = activations_summary[activations_summary['UserId'] == user_id].iloc[0]
    callsign = user_data['Callsign']
    output_data.append({
        'Callsign': callsign,
        'SummitsActivated': int(user_data['SummitsActivated']),
        'FirstActivationDate': user_data['FirstActivationDate'],
        'LastActivationDate': user_data['LastActivationDate'],
        'ActivationSpanDays': int(user_data['ActivationSpanDays']),
        'RemainingSummits': get_remaining_summits(user_id)
})

# Save to JSON
with open('sota_awards_summary.json', 'w') as json_file:
    json.dump(output_data, json_file, indent=4, default=str)
