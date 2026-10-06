"""
analyze_results.py
-------------------
Step 4 of our ETL pipeline: ANALYZE.
Pulls match data from PostgreSQL, builds features (recent form, goal
difference, home advantage), and checks which ones correlate with
match outcomes.
"""

import pandas as pd
import psycopg2
import matplotlib.pyplot as plt

# STEP 1: Database connection settings (same as load_to_postgres.py)
DB_NAME = "football_pipeline"
DB_USER = "postgres"
DB_PASSWORD = "Chandana@1306"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

# STEP 2: Connect and pull all matches, with team names joined in
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

query = """
    SELECT
        m.match_id,
        m.match_date,
        m.matchday,
        t1.team_name AS home_team,
        t2.team_name AS away_team,
        m.home_goals,
        m.away_goals,
        m.result
    FROM matches m
    JOIN teams t1 ON m.home_team_id = t1.team_id
    JOIN teams t2 ON m.away_team_id = t2.team_id
    ORDER BY m.match_date
"""

df = pd.read_sql(query, conn)
conn.close()

print(f"Loaded {len(df)} matches from PostgreSQL.\n")

# STEP 3: Build a points-per-match table so we can calculate form and
# cumulative goal difference for EACH team, not each match.
# We split every match into two rows: one from the home team's
# perspective, one from the away team's perspective.

team_rows = []

for _, row in df.iterrows():
    # Home team's perspective
    if row["result"] == "HOME_WIN":
        home_points, away_points = 3, 0
    elif row["result"] == "AWAY_WIN":
        home_points, away_points = 0, 3
    else:
        home_points, away_points = 1, 1

    team_rows.append({
        "match_id": row["match_id"],
        "match_date": row["match_date"],
        "team": row["home_team"],
        "is_home": 1,
        "goals_for": row["home_goals"],
        "goals_against": row["away_goals"],
        "points": home_points,
        "result": row["result"]
    })

    team_rows.append({
        "match_id": row["match_id"],
        "match_date": row["match_date"],
        "team": row["away_team"],
        "is_home": 0,
        "goals_for": row["away_goals"],
        "goals_against": row["home_goals"],
        "points": away_points,
        "result": row["result"]
    })

team_df = pd.DataFrame(team_rows)
team_df = team_df.sort_values(["team", "match_date"]).reset_index(drop=True)

# STEP 4: For each team, calculate BEFORE each match:
# - form_last5: points won in their last 5 matches
# - goal_diff_cumulative: total goal difference so far this season
# We use .shift(1) so we only look at matches BEFORE the current one
# (otherwise we'd be leaking the answer into the features).

team_df["goal_diff_match"] = team_df["goals_for"] - team_df["goals_against"]

team_df["form_last5"] = (
    team_df.groupby("team")["points"]
    .transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).sum())
)

team_df["goal_diff_cumulative"] = (
    team_df.groupby("team")["goal_diff_match"]
    .transform(lambda x: x.shift(1).cumsum())
)

# Fill in 0 for teams' very first match (no history yet)
team_df["form_last5"] = team_df["form_last5"].fillna(0)
team_df["goal_diff_cumulative"] = team_df["goal_diff_cumulative"].fillna(0)

# STEP 5: Merge these per-team features back onto the original
# match-level table, once for the home team and once for the away team.

home_features = team_df[team_df["is_home"] == 1][
    ["match_id", "form_last5", "goal_diff_cumulative"]
].rename(columns={
    "form_last5": "home_form",
    "goal_diff_cumulative": "home_goal_diff"
})

away_features = team_df[team_df["is_home"] == 0][
    ["match_id", "form_last5", "goal_diff_cumulative"]
].rename(columns={
    "form_last5": "away_form",
    "goal_diff_cumulative": "away_goal_diff"
})

analysis_df = df.merge(home_features, on="match_id").merge(away_features, on="match_id")

# STEP 6: Build the comparison features we actually want to analyze
analysis_df["form_difference"] = analysis_df["home_form"] - analysis_df["away_form"]
analysis_df["goal_diff_difference"] = analysis_df["home_goal_diff"] - analysis_df["away_goal_diff"]

# Turn result into a number so we can correlate it:
# 1 = home win, 0 = draw, -1 = away win
result_map = {"HOME_WIN": 1, "DRAW": 0, "AWAY_WIN": -1}
analysis_df["outcome_numeric"] = analysis_df["result"].map(result_map)

print("Sample of engineered features:")
print(analysis_df[[
    "home_team", "away_team", "result",
    "form_difference", "goal_diff_difference"
]].head(10))

# STEP 7: Correlation analysis
correlations = analysis_df[[
    "outcome_numeric", "form_difference", "goal_diff_difference"
]].corr()["outcome_numeric"].drop("outcome_numeric")

print("\nCorrelation with match outcome (positive = favors home team):")
print(correlations)

# STEP 8: Home advantage check -- simple win rate comparison
home_win_rate = (analysis_df["result"] == "HOME_WIN").mean()
away_win_rate = (analysis_df["result"] == "AWAY_WIN").mean()
draw_rate = (analysis_df["result"] == "DRAW").mean()

print(f"\nHome win rate: {home_win_rate:.1%}")
print(f"Away win rate: {away_win_rate:.1%}")
print(f"Draw rate: {draw_rate:.1%}")

# STEP 9: Visualize
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Chart 1: Outcome distribution
axes[0].bar(["Home Win", "Draw", "Away Win"],
            [home_win_rate, draw_rate, away_win_rate],
            color=["#4C72B0", "#999999", "#C44E52"])
axes[0].set_title("Match Outcome Distribution")
axes[0].set_ylabel("Proportion of matches")

# Chart 2: Form difference vs outcome
axes[1].scatter(analysis_df["form_difference"], analysis_df["outcome_numeric"], alpha=0.6)
axes[1].set_title("Form Difference vs Outcome")
axes[1].set_xlabel("Home form - Away form (points, last 5 games)")
axes[1].set_ylabel("Outcome (1=Home win, 0=Draw, -1=Away win)")

plt.tight_layout()
plt.savefig("analysis_results.png", dpi=150)
print("\nSaved charts to analysis_results.png")

plt.show()