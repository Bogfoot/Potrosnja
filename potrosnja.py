#!/usr/bin/python3
import os
import sys
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import pandas as pd
from currency_converter import CurrencyConverter
from matplotlib.widgets import Button
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
    return pd.to_datetime(df["Datum"].str.strip(), format="ISO8601", dayfirst=True)


def showStatistics(df):
    # Week
    end_date = df["Datum"].max()
    start_date = end_date - timedelta(days=7)

    # Filter the DataFrame to include only the last 7 days
    last_7_days_df = df[
        (df["Datum"] >= start_date)
        & (df["Datum"] <= end_date)
        & ((df["Svrha"].str.strip()).str.lower() != "plaća")
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


class AnnotationToggle:
    def __init__(self, annotations):
        self.annotations = annotations
        self.visible = True

    def toggle(self, event):
        self.visible = not self.visible
        for ann in self.annotations:
            ann.set_visible(self.visible)
        plt.draw()


def showPlots(df, image):
    fig, ax = plt.subplots()

    # Plotting "Potrošnja"
    (potrosnja_line,) = ax.plot(df["Datum"], df["Ukupna cijena"], label="Potrošnja")

    # Plotting "Kumulativna potrošnja" with markers
    (kumulativna_line,) = ax.plot(
        df["Datum"], df["Kumulativna suma"], label="Kumulativna potrošnja", marker="o"
    )

    # Adding hover text as annotations only for items with "svrha" == "plaća"
    annotations = []
    for i, txt in enumerate(df["Proizvod"]):
        if df["Svrha"][i] == "plaća":
            annotations.append(
                ax.annotate(
                    txt, (df["Datum"][i], df["Kumulativna suma"][i]), visible=False
                )
            )

    # Setting title and labels
    ax.set_title("Potrošnja i kumulativna suma")
    ax.set_xlabel("Datum")
    ax.set_ylabel("Potrošnja i kumulativna suma")

    # Showing legend
    ax.legend()

    # Make the plot interactive
    mplcursors.cursor([potrosnja_line, kumulativna_line], hover=True)

    # Create a button to toggle annotations
    toggle_button_ax = plt.axes([0.8, 0.05, 0.1, 0.04])
    toggle_button = Button(toggle_button_ax, "Toggle Annotations")
    annotation_toggle = AnnotationToggle(annotations)
    toggle_button.on_clicked(annotation_toggle.toggle)

    # Displaying the plot if image is not "0"
    if image == "0":
        return 0
    else:
        plt.show()


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
df.sort_values(by="Datum", ascending=False)

length = len(df["Cijena"])
df["Kumulativna suma"], df["Ukupna cijena"] = newPriceCalculation(df)

datum = np.linspace(0, length, length)
k, l = np.polyfit(datum, df["Kumulativna suma"], 1)
print(f"k = {k}\n\nl = {l}")

df["Dnevna Potrošnja"] = df["Cijena"] * df["Kolicina"]
df["Dnevna Potrošnja"] = df.groupby(df["Datum"])["Dnevna Potrošnja"].transform("sum")
showPlots(df, image)
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
