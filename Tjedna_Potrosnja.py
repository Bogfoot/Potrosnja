# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 15:49:36 2024

@author: adria
"""

import pandas as pd
import os
import sys

# Read the data into a DataFrame

full_path = os.path.dirname(os.path.abspath("__file__"))
file_name = "potrosnja.csv"
moja_potrosnja = os.path.join(full_path, file_name)

if sys.platform == "Linux":
    df = pd.read_csv(moja_potrosnja, delimiter=",", header=0)
else:
    df = pd.read_csv(file_name, delimiter=",", header=0)

# Convert the "Datum" column to datetime format
df['Datum'] = pd.to_datetime(df['Datum'], format='%Y-%m-%d')
# Calculate the total spending including both "Cijena" and "Kolicina"
df['Total'] = df['Cijena'] * df['Kolicina']

# Group by week and calculate the sum of "Cijena" for each week
weekly_spending = df.groupby(pd.Grouper(key='Datum', freq='W-Mon')).agg({'Total': 'sum'}).reset_index()
# Create a new row representing the sum of all weekly spendings
total_spending = pd.DataFrame([['Total', weekly_spending['Total'].sum()]], columns=['Datum', 'Total'])
# Concatenate the total spending row to the weekly spending DataFrame
weekly_spending = pd.concat([weekly_spending, total_spending], ignore_index=True)

# Create a new DataFrame with the weekly spending
print(weekly_spending)
