# Premier League Match Outcome Analysis

An end-to-end ETL (Extract, Transform, Load) pipeline that pulls live Premier
League match data, stores it in PostgreSQL, and analyzes which factors —
home advantage, recent form, goal difference — correlate with match
outcomes.

## Overview

This project pulls match data from the [football-data.org](https://www.football-data.org/)
API, cleans it with pandas, loads it into a normalized PostgreSQL database,
and engineers features to test a real question: **do recent form and goal
difference actually predict who wins a match, and does home advantage hold
up in the data?**

The pipeline runs in four stages:

1. **Extract** — `fetch_matches.py` pulls raw match data (fixtures, scores,
   status) for the current Premier League season from the football-data.org
   API and saves it as JSON.
2. **Transform** — `clean_matches.py` parses the raw JSON into a clean
   tabular format using pandas, filters to completed matches, and exports
   to CSV.
3. **Load** — `load_to_postgres.py` loads the cleaned data into a
   normalized PostgreSQL schema (`teams` and `matches` tables with foreign
   keys), de-duplicating teams automatically.
4. **Analyze** — `analyze_results.py` queries the database, engineers
   point-in-time features for each match (each team's form over their last
   5 games and cumulative goal difference — calculated only from matches
   *before* the one being predicted, to avoid data leakage), and measures
   their correlation with match outcomes. Results are visualized with
   matplotlib.

## Tech stack

- **Python** — requests, pandas, matplotlib
- **PostgreSQL** — psycopg2 for the Python connection
- **API** — football-data.org (Premier League competition)

## Database schema

```
teams
├── team_id (PK)
└── team_name

matches
├── match_id (PK)
├── match_date
├── matchday
├── home_team_id (FK → teams)
├── away_team_id (FK → teams)
├── home_goals
├── away_goals
└── result
```

## Findings so far

Based on the first 4 matchdays (40 matches) of the 2026/27 Premier League
season:

- **Form difference** and **goal difference** both show a positive
  correlation (~0.34–0.36) with match outcome — teams in better recent form
  or with a better goal difference are somewhat more likely to win, in the
  expected direction.
- **Home advantage has not appeared yet this season**: home win rate
  (32.5%) and away win rate (32.5%) are identical so far, which is unusual
  compared to historical Premier League trends (typically ~45% home win
  rate). This is an early-season sample and may well shift as more matches
  are played — the pipeline is designed to be re-run throughout the season
  to track whether this holds.

This is a snapshot from a small, early-season sample (season is 38
matchdays; only 4 are complete). The pipeline is built to be re-run as the
season progresses to build a larger, more reliable dataset.

## Status

Actively in progress — pipeline is fully functional end-to-end. Planned
next steps: scheduled/automated re-runs as the season progresses, and a
`team_form_snapshot` table to persist historical form calculations instead
of recomputing them on every run.

## Setup

1. Get a free API key from [football-data.org](https://www.football-data.org/client/register)
2. Install dependencies: `pip install requests pandas matplotlib psycopg2-binary`
3. Set up PostgreSQL and create the schema (see above)
4. Run the scripts in order: `fetch_matches.py` → `clean_matches.py` →
   `load_to_postgres.py` → `analyze_results.py`