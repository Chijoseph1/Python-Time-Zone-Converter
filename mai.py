from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import csv 
import json
import os

def get_datetime():
    while True:
        date_time = input("Enter date and time (YYYY-MM-DD HH:MM): ")

        try:
            parsed_date = datetime.strptime(date_time, "%Y-%m-%d %H:%M")

            if parsed_date.strftime("%Y-%m-%d %H:%M") != date_time:
                raise ValueError

            return parsed_date

        except ValueError:
                print("Invalid input. Use YYYY-MM-DD HH:MM, e.g. 2026-05-04 10:00.")


def get_timezone(prompt):
    while True:
        timezone_name = input(prompt)

        try:
            return ZoneInfo(timezone_name)
        except (ZoneInfoNotFoundError, ValueError):
                print("Invalid time zone. Please try again (e.g. Africa/Lagos).")


history_file = "conversion_history.json"


def load_history():
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            return json.load(file)
    return []


history = load_history()


def save_history():
    with open(history_file, "w") as file:
        json.dump(history, file, indent=4)


def show_history():
    if not history:
        print("No conversion history yet.")
        return

    for item in history:
        print(item)


def export_csv():
    if not history:
        print("No history to export.")
        return

    with open("conversion_history.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)

    print("History exported to conversion_history.csv")

def main():
    date_time = get_datetime()

    source_tz = get_timezone(
        "Enter source time zone (e.g. Africa/Lagos): "
    )

    target_tz = get_timezone(
        "Enter target time zone (e.g. Europe/London): "
    )

    date_time = date_time.replace(tzinfo=source_tz)

    converted_time = date_time.astimezone(target_tz)

    print(f"Converted time: {converted_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"Target time zone: {target_tz.key}")
    print(f"UTC offset: {converted_time.strftime('%z')}")
    print(f"Abbreviation: {converted_time.strftime('%Z')}")


if __name__ == "__main__":
    main()