#!/usr/bin/python3
from datetime import timedelta
import pandas as pd
import numpy as np
from tabulate import tabulate
from currency_converter import CurrencyConverter
import plotly.graph_objects as go
import os
import sys


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
    return fig.show()


def showStatistics(df, brProiz):
    # Week
    end_date = df["Datum"].max()
    start_date = end_date - timedelta(days=6)

    # Filter the DataFrame to include only the last 7 days
    last_7_days_df = df[
        (df["Datum"] >= start_date)
        & (df["Datum"] <= end_date)
        & (df["Svrha"] != "plaća")
    ]

    # Calculate the sum of the 'price' column for the last 7 days
    total_price_last_7_days = last_7_days_df["Cijena"].sum()
    end_date = df["Datum"].max()
    start_date = end_date - timedelta(days=30)

    # Filter the DataFrame to include only the last 7 days
    last_30_days_df = df[
        (df["Datum"] >= start_date)
        & (df["Datum"] <= end_date)
        & (df["Svrha"] != "plaća")
    ]

    # Calculate the sum of the 'price' column for the last 7 days
    total_price_last_30_days = last_30_days_df["Cijena"].sum()

    # Month

    return f"Srednja vrijednost proizvoda: {round(float(df['Cijena'].mean()),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Standardna devijacija: {round(float(df['Cijena'].std()),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Medijan: {round(float(df['Cijena'].median()),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Srednja vrijednost: {round(float((df['Kumulativna suma'].iloc[-1])/brProiz),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
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
stats = showStatistics(df, brProiz)

df.to_excel("Potrošnja.xlsx")

df = tabulate(df, showindex=False, headers=df.columns)
print(df)
print(stats)
