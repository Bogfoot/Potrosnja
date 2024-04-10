# %%

#!/usr/bin/python3
import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from currency_converter import CurrencyConverter
from tabulate import tabulate

try:
    image = sys.argv[1]
except:
    image = "0"


def newPriceCalculation(df):
    sum = 0
    cum_sum = []
    c = CurrencyConverter()
    uk = []
    for item in range(len(df["Cijena"])):
        if df["Valuta"][item] != native_val:
            df["Cijena"][item] = c.convert(
                df["Cijena"][item],
                str(df["Valuta"][item]).upper(),
                str(native_val).upper(),
            )
        ukupno = -df["Cijena"][item] * df["Kolicina"][item]
        uk.append(ukupno)
        sum += ukupno
        cum_sum.append(sum)
    return cum_sum, uk


def newDate(df):
    # return pd.to_datetime(df["Datum"], format="%d.%m.%Y", dayfirst=True)
    return pd.to_datetime(df["Datum"], format="ISO8601", dayfirst=True)


def showStatistics(df):
    # Week
    end_date = df["Datum"].max()
    start_date = end_date - timedelta(days=7)

    # Filter the DataFrame to include only the last 7 days
    last_7_days_df = df[
        (df["Datum"] >= start_date)
        & (df["Datum"] <= end_date)
        & (df["Svrha"].str.lower() != "plaća")
    ]

    # Calculate the sum of the 'price' column for the last 7 days
    total_price_last_7_days = np.sum(last_7_days_df["Cijena"])

    end_date = df["Datum"].max()
    start_date = end_date - timedelta(days=30)
    # Filter the DataFrame to include only the last 30 days
    last_30_days_df = df[
        (df["Datum"] >= start_date)
        & (df["Datum"] <= end_date)
        & (df["Svrha"].str.lower() != "plaća")
    ]
    todays_spending = df[(df["Datum"] == datetime.today().strftime("%d-%m-%Y"))]
    # Calculate the product of "Cijena" and "Količina" for each row
    todays_spending["Total_Price"] = (
        todays_spending["Cijena"] * todays_spending["Kolicina"]
    )

    # Sum up the total prices
    total_spending_today = todays_spending["Total_Price"].sum()

    # Calculate the sum of the 'price' column for the last 7 days
    total_price_last_30_days = np.sum(last_30_days_df["Cijena"])

    return f"Srednja vrijednost proizvoda: {round(float(np.mean(df['Cijena']>=0)),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Standardna devijacija: {round(float(np.std(df['Cijena']>=0)),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Današnja potrošnja: {total_spending_today} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Tjedna potrošnja: {round(float(total_price_last_7_days),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Mjesećna potrošnja: {round(float(total_price_last_30_days),2)} {df['Valuta'][df['Cijena'].idxmax()]}"


def saveDF(df):
    df["Kolicina"].fillna(1, inplace=True)
    df.to_csv(moja_potrosnja, index=False)
    return df


def showPlots(df):
    fig = go.Figure()
    fig.add_trace(
        go.Line(
            x=df["Datum"],
            y=df["Ukupna cijena"],
            name="Potrošnja",
        )
    )
    fig.add_trace(
        go.Line(
            x=df["Datum"],
            y=df["Kumulativna suma"],
            name="Kumulativna potrošnja",
            mode="lines",
            hovertext=df["Proizvod"],
            marker=dict(size=8),
        )
    )
    fig.update_layout(
        title="Potrošnja i kumulativna suma",
        xaxis_title="Datum",
        yaxis_title="Potrošnja i kumulativna suma",
        hovermode="x unified",
    )
    if image != "0":
        return fig.show()
    else:
        return 0


native_val = "eur"
# proizvod, cijena, valuta, kolicina, svrha, datum
full_path = os.path.dirname(os.path.abspath("__file__"))
file_name = "potrosnja.csv"
moja_potrosnja = os.path.join(full_path, file_name)
if sys.platform == "Linux":
    df = pd.read_csv(moja_potrosnja, delimiter=",", header=0)
else:
    df = pd.read_csv(file_name, delimiter=",", header=0)
df = saveDF(df)

if not os.path.exists("Slike"):
    os.mkdir("Slike")


df["Datum"] = newDate(df)
df["Datum"] = df["Datum"].dt.date
df.sort_values(by="Datum",ascending=False)

length = len(df["Cijena"])
df["Kumulativna suma"], df["Ukupna cijena"] = newPriceCalculation(df)

datum = np.linspace(0, length, length)
k, l = np.polyfit(datum, df["Kumulativna suma"], 1)
print(f"k = {k}\n\nl = {l}")

df["Dnevna Potrošnja"] = df["Cijena"] * df["Kolicina"]
df["Dnevna Potrošnja"] = df.groupby(df["Datum"])["Dnevna Potrošnja"].transform("sum")
showPlots(df)
stats = showStatistics(df)

df.to_excel("Potrošnja.xlsx")

# This is to print out only todays expenses
# otherwise print out everything

today = datetime.now().date()
today_df = df[df["Datum"] == today]
df = tabulate(df, showindex=False, headers=df.columns)
today = tabulate(today_df, showindex=False, headers=today_df.columns)
if image == 1:
    print(df)
else:
    print(today)
print(stats)
