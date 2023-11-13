#!/usr/bin/python3
from datetime import timedelta, datetime
import pandas as pd
import numpy as np
from tabulate import tabulate
from currency_converter import CurrencyConverter
import plotly.graph_objects as go
import plotly.io as pio
import os
import sys

image = sys.argv[1]


def newPriceCalculation(df, brojProizvoda=0):
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
        if df["Svrha"][item] != "plaća":
            brojProizvoda += df["Kolicina"][item]
        cum_sum.append(sum)
    return cum_sum, brojProizvoda, uk


def newDate(df):
    return pd.to_datetime(df["Datum"], format="%d.%m.%Y", dayfirst=True)


def showPlots(df):
    fig = go.Figure()
    # imName = ( "Slike/GrafPotrošnje" + datetime.datetime.today().strftime("%d_%m_%Y") + ".png")
    fig.add_trace(go.Line(x=df["Datum"], y=df["Ukupna cijena"], name="Potrošnja"))
    fig.add_trace(
        go.Line(x=df["Datum"], y=df["Kumulativna suma"], name="Kumulativna potrošnja")
    )
    if image != "0":
        # pio.write_image(fig, "Slike/Spending_Earning_over_time", format="png", scale=8)
        return fig.show()
    else:
        # pio.write_image(fig, "Slike/Spending_Earning_over_time", format="png", scale=8)
        return


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

    # Calculate the sum of the 'price' column for the last 7 days
    total_price_last_30_days = np.sum(last_30_days_df["Cijena"])

    return f"Srednja vrijednost proizvoda: {round(float(np.mean(df['Cijena']>=0)),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Standardna devijacija: {round(float(np.std(df['Cijena']>=0)),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Medijan: {round(float(np.median(df['Cijena']>=0)),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Današnja potrošnja: {round(float(df['Dnevna Potrošnja'].iloc[-1]),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Tjedna potrošnja: {round(float(total_price_last_7_days),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Mjesećna potrošnja: {round(float(total_price_last_30_days),2)} {df['Valuta'][df['Cijena'].idxmax()]}"


def line_fit(x, k, l):
    return k * x + l


native_val = "eur"
# proizvod, cijena, valuta, kolicina, svrha, datum
df = pd.read_csv("potrosnja.csv", delimiter=",", header=0)
df.sort_values("Datum")

if not os.path.exists("Slike"):
    os.mkdir("Slike")

df["Datum"] = newDate(df)
df["Datum"] = df["Datum"].dt.date
length = len(df["Cijena"])
df["Kumulativna suma"], brProiz, df["Ukupna cijena"] = newPriceCalculation(df)
df.sort_values(by="Datum")

datum = np.linspace(0, length, length)
k, l = np.polyfit(datum, df["Kumulativna suma"], 1)
print(f"k = {k}\n\nl = {l}")

df["Dnevna Potrošnja"] = df["Cijena"] * df["Kolicina"]
df["Dnevna Potrošnja"] = df.groupby(df["Datum"])["Dnevna Potrošnja"].transform("sum")
showPlots(df)
stats = showStatistics(df)

df.to_excel("Potrošnja.xlsx")

today = datetime.now().date()
today_df = df[df["Datum"] == today]
df = tabulate(df, showindex=False, headers=df.columns)
today = tabulate(today_df, showindex=False, headers=today_df.columns)
if image != "0":
    print(df)
else:
    print(today)

print(stats)
