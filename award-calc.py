# Golden Eagle Explorer - all summits
# Osprey Outlander - 50%
# Capercaillie Conqueror - 10
# Ptarmigan Pioneer - 5
# Heather Hopper - 1 summit

# Activations - https://api-db2.sota.org.uk/api/activations/GM/ES-001

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

# Count the number of summits activated by each callsign
activations_summary = activations_df.groupby('UserId')['summitCode'].nunique().reset_index()
activations_summary.columns = ['UserId', 'SummitsActivated']

# Add awards based on activation counts
def assign_awards(row):
    if row['SummitsActivated'] >= 1 and row['SummitsActivated'] < 5:
        return 'Heather Hopper'
    elif row['SummitsActivated'] >= 5 and row['SummitsActivated'] < 10:
        return 'Ptarmigan Pioneer'
    elif row['SummitsActivated'] >= 10 and row['SummitsActivated'] < len(summit_codes) * 0.5:
        return 'Capercaillie Conqueror'
    elif row['SummitsActivated'] >= len(summit_codes) * 0.5 and row['SummitsActivated'] < len(summit_codes):
        return 'Osprey Outlander'
    elif row['SummitsActivated'] == len(summit_codes):
        return 'Golden Eagle Explorer'
    else:
        return None

activations_summary['Award'] = activations_summary.apply(assign_awards, axis=1)

# Determine the date each callsign achieved their award
def get_award_date(user_id, required_summits):
    activations = activations_df[activations_df['UserId'] == user_id]
    activations = activations.sort_values('ActivationDate', ascending=False)
    unique_summits = set()
    for _, row in activations.iterrows():
        unique_summits.add(row['summitCode'])
        if len(unique_summits) >= required_summits:
            return row['ActivationDate']
    return None

activations_summary['AwardDate'] = activations_summary.apply(
    lambda row: get_award_date(row['UserId'], row['SummitsActivated']), axis=1
)

# Replace UserId with the most frequent Callsign
def get_most_frequent_callsign(user_id):
    user_activations = activations_df[activations_df['UserId'] == user_id]
    return user_activations['Callsign'].mode()[0]

activations_summary['Callsign'] = activations_summary['UserId'].apply(get_most_frequent_callsign)

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
        'SummitsActivated': user_data['SummitsActivated'],
        'Award': user_data['Award'],
        'AwardDate': user_data['AwardDate'],
        'RemainingSummits': get_remaining_summits(user_id)
    })

# Save to JSON
with open('sota_awards_summary.json', 'w') as json_file:
    json.dump(output_data, json_file, indent=4, default=str)
