import argparse
import csv
from datetime import datetime, timedelta


def write_to_csv(file_path, proizvod, cijena, valuta, kolicina, svrha, datum):
    fieldnames = ["Proizvod", "Cijena", "Valuta", "Kolicina", "Svrha", "Datum"]

    # Handle relative dates
    if datum.startswith("+") or datum.startswith("-"):
        try:
            offset = int(datum)
            datum = (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date offset format. Use +/- followed by a number.")
            return

    data = {
        "Proizvod": proizvod,
        "Cijena": cijena,
        "Valuta": valuta if not valuta.isnumeric() else "eur",
        "Kolicina": kolicina,
        "Svrha": svrha,
        "Datum": datum,
    }

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(data)


def change_date_format(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")


def update_csv_date_format(file_path):
    updated_data = []

    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["Datum"] = change_date_format(row["Datum"])
            updated_data.append(row)

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(updated_data)


def sort_csv_by_date(file_path):
    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        sorted_data = sorted(
            reader, key=lambda row: datetime.strptime(row["Datum"], "%Y-%m-%d")
        )

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=sorted_data[0].keys())
        writer.writeheader()
        writer.writerows(sorted_data)


def main():
    parser = argparse.ArgumentParser(description="Manage CSV data.")
    subparsers = parser.add_subparsers(dest="command")

    write_parser = subparsers.add_parser("write", help="Write data to CSV.")
    write_parser.add_argument("file", help="Path to the CSV file.")
    write_parser.add_argument("proizvod", help="Product name.")
    write_parser.add_argument("cijena", type=float, help="Price.")
    write_parser.add_argument("valuta", help="Currency. Default is eur.")
    write_parser.add_argument("kolicina", type=float, help="Quantity.")
    write_parser.add_argument("svrha", help="Purpose.")
    write_parser.add_argument(
        "datum", help="Date in yyyy-mm-dd format or relative format (+/-days)."
    )

    update_parser = subparsers.add_parser(
        "update_dates", help="Update date format in CSV."
    )
    update_parser.add_argument("file", help="Path to the CSV file.")

    args = parser.parse_args()

    if args.command == "write":
        write_to_csv(
            args.file,
            args.proizvod,
            args.cijena,
            args.valuta,
            args.kolicina,
            args.svrha,
            args.datum,
        )
        sort_csv_by_date(args.file)
    elif args.command == "update_dates":
        update_csv_date_format(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
