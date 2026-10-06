"""
fetch_matches.py
-----------------
A simple script to fetch football match data from football-data.org API.
This is Step 1 of our ETL pipeline: EXTRACT (getting raw data from an API).
"""

import requests
import json

# STEP 1: Put your API key here
# Get it from https://www.football-data.org/client/register
API_KEY = "9f1f1e3acd7f46b7a94146a8b2ab507e"

# STEP 2: Set up the request
# PL = Premier League. You can change this to PD (La Liga), SA (Serie A), etc.
COMPETITION_CODE = "PL"
URL = f"https://api.football-data.org/v4/competitions/{COMPETITION_CODE}/matches"

# The API requires your key to be sent in the headers, not the URL
headers = {
    "X-Auth-Token": API_KEY
}

# STEP 3: Make the request
print("Fetching data from football-data.org...")
response = requests.get(URL, headers=headers)

# STEP 4: Check if it worked
if response.status_code == 200:
    print("Success! Data received.\n")

    # Convert the response into a Python dictionary
    data = response.json()

    # The actual matches are inside data["matches"] (a list of matches)
    matches = data["matches"]

    print(f"Total matches found: {len(matches)}\n")

    # STEP 5: Print the first 5 matches so we can see what the data looks like
    for match in matches[:5]:
        home_team = match["homeTeam"]["name"]
        away_team = match["awayTeam"]["name"]
        home_score = match["score"]["fullTime"]["home"]
        away_score = match["score"]["fullTime"]["away"]
        match_date = match["utcDate"]
        status = match["status"]

        print(f"{match_date} | {home_team} {home_score} - {away_score} {away_team} | Status: {status}")

    # STEP 6 (optional): Save the raw data to a file so we have a backup copy
    with open("raw_matches.json", "w") as f:
        json.dump(data, f, indent=2)
    print("\nRaw data saved to raw_matches.json")

else:
    print(f"Something went wrong. Status code: {response.status_code}")
    print(response.text)