#!/usr/bin/python3
import sys
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
from currency_converter import CurrencyConverter


# Function to handle currency conversion and price calculations
def newPriceCalculation(df, native_currency):
    c = CurrencyConverter()
    cum_sum = []
    total = 0
    converted_prices = []

    for idx, row in df.iterrows():
        price = row["Cijena"]
        if row["Valuta"] != native_currency:
            price = c.convert(price, row["Valuta"].upper(), native_currency.upper())

        total_cost = -price * row["Kolicina"]
        total += total_cost
        cum_sum.append(total)
        converted_prices.append(total_cost)

    return cum_sum, converted_prices


# Function to convert date strings to datetime objects
def newDate(df):
    return pd.to_datetime(df["Datum"].str.strip(), format="ISO8601", dayfirst=True)


# Function to plot data
def showPlots(df, save_image=False):
    fig, ax = plt.subplots()

    # Convert DataFrame columns to NumPy arrays for plotting
    dates = df["Datum"].to_numpy()
    total_price = df["Ukupna cijena"].to_numpy()
    kumulativna_suma = df["Kumulativna Suma"].to_numpy()

    ax.plot(dates, total_price, label="Potrošnja")
    ax.plot(
        dates,
        kumulativna_suma,
        label=f"Kumulativna Suma: {round(kumulativna_suma[-1],2)}",
        linestyle="--",
    )
    ax.set_xlabel("Datum")
    ax.set_ylabel("Vrijednost")
    ax.legend()

    if save_image:
        plt.savefig("plot.png")
    plt.show()


# Main function to execute the script
def main():
    # Handle command-line argument for image saving
    save_image = sys.argv[1] == "1" if len(sys.argv) > 1 else False

    # Example: Load data and run functions (update with your actual data source)
    df = pd.read_csv("potrosnja.csv")  # Update with your actual data file
    native_currency = "eur"  # Update with your actual native currency

    # Convert date strings to datetime objects and sort by date
    df["Datum"] = newDate(df)
    df = df.sort_values(by="Datum")

    # Calculate cumulative sum and adjusted prices
    df["Kumulativna Suma"], df["Ukupna cijena"] = newPriceCalculation(
        df, native_currency
    )

    # Filter for today's and yesterday's entries
    today = datetime.today().date()
    yesterday = today - timedelta(days=1)

    today_entries = df[df["Datum"].dt.date == today]
    yesterday_entries = df[df["Datum"].dt.date == yesterday]

    print(f"Jučerašnja potrošnja:\n{yesterday_entries}")
    print(f"Današnja potrošnja:\n{today_entries}")

    # Plot the data
    showPlots(df, save_image)


if __name__ == "__main__":
    main()
