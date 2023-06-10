#!/usr/bin/python3
import pandas as pd
import numpy as np
import datetime
from tabulate import tabulate
from currency_converter import CurrencyConverter
import plotly.graph_objects as go
import os
import sys


showIm = False
if len(sys.argv) > 1:
    showIm = True


def newPriceCalculation(df, brojProizvoda=0):
    sum = 0
    cum_sum = []
    c = CurrencyConverter()
    df["Stara cijena"] = df["Cijena"]
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
        brojProizvoda += df["Kolicina"][item]
        cum_sum.append(sum)
    return cum_sum, brojProizvoda, uk


def newDate(df):
    return pd.to_datetime(df["Datum"], format="%d.%m.%Y", dayfirst=True)


def showPlots(df):
    fig = go.Figure()
    imName = (
        "Slike/GrafPotrošnje" + datetime.datetime.today().strftime("%d_%m_%Y") + ".png"
    )
    fig.add_trace(go.Line(x=df["Datum"], y=df["Cijena"], name="Potršnja"))
    fig.add_trace(
        go.Line(x=df["Datum"], y=df["Kumulativna suma"], name="Kumulativna potrošnja")
    )

    # fig.add_trace(
    #     go.Line(
    #         x=df["Datum"],
    #         y=line_fit(np.linspace(0, len(df["Datum"]), len(df["Datum"])), k, l),
    #         name="Linear fit",
    #         mode="markers",
    #     )
    # )
    # pio.write_image(fig, imName, width=2000, height=2000)
    return fig.show()


def showStatistics(df, brProiz):
    return f"Najskuplji predmet: {df['Proizvod'][df['Cijena'].idxmax()]} Cijena: {round(float(df['Cijena'].max()),2)}  {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Srednja vrijednost proizvoda: {round(float(df['Cijena'].mean()),2)} {df['Valuta'][df['Cijena'].idxmax()]} \n\
            Standardna devijacija: {round(float(df['Cijena'].std()),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Medijan: {round(float(df['Cijena'].median()),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Potrošnja bez najskupljeg proizvoda: {round(float(df['Kumulativna suma'].iloc[-1] - df['Cijena'].max()),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Srednja vrijednost: {round(float((df['Kumulativna suma'].iloc[-1])/brProiz),2)} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Današnja potrošnja: {round(float(df['Dnevna Potrošnja'].iloc[-1]),2)} {df['Valuta'][df['Cijena'].idxmax()]}"

    # Srednja vrijednost: {(df['Kumulativna suma'].iloc[-1] - df['Cijena'].max())/brProiz}\n\


def line_fit(x, k, l):
    return k * x + l


native_val = "eur"
# proizvod, cijena, valuta, kolicina, svrha, datum
df = pd.read_csv("potrosnja.csv", delimiter=",", header=0)
df.sort_values("Datum")

if not os.path.exists("Slike"):
    os.mkdir("Slike")

df["Datum"] = newDate(df)
df["Datum"] = df['Datum'].dt.date
length = len(df["Cijena"])
# td = pd.Series([pd.Timedelta(milliseconds=i) for i in range(length)])
# df["Datum"] += td
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
