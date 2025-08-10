# Coffee Dataset Analysis
**Project Overview**

This project involves analyzing a coffee dataset containing information about various coffee samples, including their origins, ratings, and other attributes. The goal is to clean, explore, and analyze the data to uncover insights about coffee quality, origins, and trends.

**Dataset**

The dataset top-rated-coffee.csv contains the following key columns:
coffee_origin: The country or region where the coffee was grown.
Other columns may include coffee ratings, flavor notes, and related metadata.

**Objective**

Identify and handle missing values in important columns like coffee_origin.
Analyze the distribution of coffee origins.
Explore patterns in coffee ratings and quality.
Provide insights that could help coffee enthusiasts or sellers understand the dataset better.

**Key Code Example**
Checking for missing values in the coffee_origin column:

rf['coffee_origin'].isnull()

This returns a Boolean series indicating which rows have missing origin data, helping in data cleaning steps.

How to Run

Clone the repository.

Install dependencies using:


pip install -r requirements.txt

Open the Google Colab notebook notebooks/coffee_analysis.ipynb to explore the dataset and analysis.

Run the cleaning script in scripts/data_cleaning.py for preprocessing steps.

**Future Work**

Extend analysis to predict coffee ratings based on origin and other features.

Visualize coffee origin distribution on a world map.

Build a recommendation system for coffee enthusiasts.

