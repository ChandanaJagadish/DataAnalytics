"""
load_to_postgres.py
--------------------
Step 3 of our ETL pipeline: LOAD.
Takes the cleaned CSV and inserts it into the PostgreSQL database
(football_pipeline), filling the 'teams' and 'matches' tables.
"""

import pandas as pd
import psycopg2

# STEP 1: Database connection settings
# Fill in YOUR password below (the one you just set with ALTER USER).
DB_NAME = "football_pipeline"
DB_USER = "postgres"
DB_PASSWORD = "Chandana@1306"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

# STEP 2: Load the cleaned CSV we created earlier
df = pd.read_csv("cleaned_matches.csv")
print(f"Loaded {len(df)} rows from cleaned_matches.csv")

# STEP 3: Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()
print("Connected to PostgreSQL.")

# STEP 4: Insert all unique team names into the teams table
# We collect home_team and away_team names, combine them, and remove duplicates.
all_teams = pd.concat([df["home_team"], df["away_team"]]).unique()

for team_name in all_teams:
    cur.execute(
        """
        INSERT INTO teams (team_name)
        VALUES (%s)
        ON CONFLICT (team_name) DO NOTHING
        """,
        (team_name,)
    )

conn.commit()
print(f"Inserted {len(all_teams)} unique teams (duplicates skipped automatically).")

# STEP 5: Build a lookup dictionary: team_name -> team_id
# We need this because the matches table stores team IDs, not names.
cur.execute("SELECT team_id, team_name FROM teams")
team_lookup = {name: team_id for team_id, name in cur.fetchall()}

# STEP 6: Insert each match into the matches table
inserted_count = 0

for _, row in df.iterrows():
    home_id = team_lookup[row["home_team"]]
    away_id = team_lookup[row["away_team"]]

    # Figure out the result from the winner column
    if row["winner"] == "HOME_TEAM":
        result = "HOME_WIN"
    elif row["winner"] == "AWAY_TEAM":
        result = "AWAY_WIN"
    else:
        result = "DRAW"

    cur.execute(
        """
        INSERT INTO matches
            (match_date, matchday, home_team_id, away_team_id, home_goals, away_goals, result)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            row["date"],
            int(row["matchday"]),
            home_id,
            away_id,
            int(row["home_goals"]),
            int(row["away_goals"]),
            result
        )
    )
    inserted_count += 1

conn.commit()
print(f"Inserted {inserted_count} matches into the matches table.")

# STEP 7: Clean up
cur.close()
conn.close()
print("\nDone! Data loaded into PostgreSQL.")