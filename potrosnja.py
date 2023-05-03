import pandas as pd
import plotly.io as pio
import datetime
from tabulate import tabulate
from currency_converter import CurrencyConverter
import plotly.graph_objects as go
import os
import sys

native_val = "eur"

# proizvod, cijena, valuta, kolicina, svrha, datum
df = pd.read_csv("potrosnja.csv", delimiter=",", header=0)

if not os.path.exists("Slike"):
    os.mkdir("Slike")


showIm = False
if len(sys.argv) > 1:
    showIm = True


# proizvod, cijena, valuta, kolicina, svrha, datum
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
        ukupno = df["Cijena"][item] * df["Kolicina"][item]
        uk.append(ukupno)
        sum += ukupno
        brojProizvoda += df["Kolicina"][item]
        cum_sum.append(sum)
    return cum_sum, brojProizvoda, uk


# proizvod, cijena, valuta, kolicina, svrha, datum
def newDate(df):
    return pd.to_datetime(df["Datum"], format="%d.%m.%Y", dayfirst=True)


# proizvod, cijena, valuta, kolicina, svrha, datum
def showPlots(df):
    fig = go.Figure()
    imName = (
        "Slike/GrafPotrošnje" + datetime.datetime.today().strftime("%d_%m_%Y") + ".png"
    )
    fig.add_trace(go.Scatter(x=df["Datum"], y=df["Cijena"], name="Potršnja"))
    fig.add_trace(
        go.Line(x=df["Datum"], y=df["Kumulativna suma"], name="Kumulativna potrošnja")
    )
    pio.write_image(fig, imName, width=2000, height=2000)
    if showIm:
        return fig.show()
    else:
        return


# proizvod, cijena, valuta, kolicina, svrha, datum
def showStatistics(df, brProiz):
    return f"Najskuplji predmet: {df['Proizvod'][df['Cijena'].idxmax()]} Cijena: {df['Cijena'].max()} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Srednja vrijednost proizvoda: {df['Cijena'].mean()} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Standardna devijacija: {df['Cijena'].std()} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Medijan: {df['Cijena'].median()} {df['Valuta'][df['Cijena'].idxmax()]}\n\
            Potrošnja bez najskupljeg proizvoda: {df['Kumulativna suma'].iloc[-1] - df['Cijena'].max()}\n\
            Srednja vrijednost: {(df['Kumulativna suma'].iloc[-1] - df['Cijena'].max())/brProiz}"


df["Datum"] = newDate(df)
df["Kumulativna suma"], brProiz, df["Ukupna cijena"] = newPriceCalculation(df)

showPlots(df)
stats = showStatistics(df, brProiz)

df.to_excel("Potrošnja.xlsx")
df = tabulate(df, showindex=False, headers=df.columns)
print(df)

print(stats)
