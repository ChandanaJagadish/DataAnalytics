"""
clean_matches.py
-----------------
Step 2 of our ETL pipeline: TRANSFORM.
Takes the raw JSON from football-data.org and turns it into a clean,
simple pandas DataFrame with only the columns we actually need.
"""

import json
import pandas as pd

# STEP 1: Load the raw JSON file we saved earlier
with open("raw_matches.json", "r") as f:
    data = json.load(f)

matches = data["matches"]

# STEP 2: Pull out only the fields we care about from each match
cleaned_matches = []

for match in matches:
    cleaned_matches.append({
        "matchday": match["matchday"],
        "date": match["utcDate"],
        "home_team": match["homeTeam"]["name"],
        "away_team": match["awayTeam"]["name"],
        "home_goals": match["score"]["fullTime"]["home"],
        "away_goals": match["score"]["fullTime"]["away"],
        "winner": match["score"]["winner"],  # HOME_TEAM, AWAY_TEAM, DRAW, or None
        "status": match["status"]            # FINISHED, TIMED, etc.
    })

# STEP 3: Convert the list of dicts into a DataFrame
df = pd.DataFrame(cleaned_matches)

# STEP 4: Convert the date column to an actual datetime type
# (right now it's just text, this lets us sort/filter by date properly)
df["date"] = pd.to_datetime(df["date"])

# STEP 5: Filter to only matches that have actually been played
# (status == "TIMED" means it's a future match with no score yet)
finished_df = df[df["status"] == "FINISHED"].copy()

# STEP 6: Sort by date so matches are in chronological order
finished_df = finished_df.sort_values("date").reset_index(drop=True)

# STEP 7: Quick sanity checks
print(f"Total matches in file: {len(df)}")
print(f"Finished matches: {len(finished_df)}")
print(f"Still upcoming: {len(df) - len(finished_df)}")
print("\nFirst few finished matches:")
print(finished_df.head())

# STEP 8: Save the cleaned data to a CSV so we can load it into PostgreSQL next
finished_df.to_csv("cleaned_matches.csv", index=False)
print("\nSaved cleaned data to cleaned_matches.csv")