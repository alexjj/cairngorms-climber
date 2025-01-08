def fetch_data():
    # Function to fetch data from the JSON file
    import json
    with open('sota_awards_summary.json', 'r') as json_file:
        return json.load(json_file)

def filter_callsigns(data, search_term):
    # Function to filter callsigns based on the search term
    return [entry for entry in data if search_term.lower() in entry['Callsign'].lower()]

def get_remaining_summits(user_data):
    # Function to retrieve remaining summits for the selected callsign
    return user_data['RemainingSummits'] if 'RemainingSummits' in user_data else []