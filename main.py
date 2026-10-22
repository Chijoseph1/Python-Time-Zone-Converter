from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import csv
import json
import os


HISTORY_FILE = "conversion_history.json"
CSV_FILE = "conversion_history.csv"


def get_datetime():
    while True:
        value = input(
            "Enter date and time (YYYY-MM-DD HH:MM, e.g. 2026-05-04 10:00): "
        ).strip()

        try:
            parsed_date = datetime.strptime(value, "%Y-%m-%d %H:%M")

            if parsed_date.strftime("%Y-%m-%d %H:%M") != value:
                raise ValueError

            return parsed_date

        except ValueError:
            print("Invalid date and time. Example: 2026-05-04 10:00.")


def get_timezone(prompt):
    while True:
        name = input(
            f"{prompt} (e.g. Africa/Lagos or Europe/London): "
        ).strip()

        try:
            return ZoneInfo(name)

        except (ZoneInfoNotFoundError, ValueError):
            print("Invalid time zone. Please try again.")


def get_aware_datetime(date_time, zone):
    while True:
        first = date_time.replace(tzinfo=zone, fold=0)
        second = date_time.replace(tzinfo=zone, fold=1)

        first_back = first.astimezone(timezone.utc).astimezone(zone)
        second_back = second.astimezone(timezone.utc).astimezone(zone)

        first_valid = first_back.replace(tzinfo=None) == date_time
        second_valid = second_back.replace(tzinfo=None) == date_time

        if not first_valid and not second_valid:
            print("This local time does not exist because of a clock change.")
            date_time = get_datetime()
            continue

        if (
            first_valid
            and second_valid
            and first.utcoffset() != second.utcoffset()
        ):
            print("This time occurs twice because of a clock change.")
            print("1. First occurrence:", first.strftime("%Y-%m-%d %H:%M %Z"))
            print("2. Second occurrence:", second.strftime("%Y-%m-%d %H:%M %Z"))

            while True:
                choice = input("Choose an occurrence (1 or 2): ").strip()

                if choice == "1":
                    return first

                if choice == "2":
                    return second

                print("Invalid choice. Please choose 1 or 2.")

        if first_valid:
            return first

        return second


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

                if isinstance(data, list) and all(
                    isinstance(item, dict) for item in data
                ):
                    return data

                print("Saved history has an invalid format.")

        except (json.JSONDecodeError, OSError):
            print("Could not read saved history. Starting with empty history.")

    return []


history = load_history()


def save_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

    except OSError:
        print("Could not save conversion history.")


def record_conversion(original, source, converted, target):
    history.append({
        "original_time": original.strftime("%Y-%m-%d %H:%M %Z"),
        "source_zone": source.key,
        "converted_time": converted.strftime("%Y-%m-%d %H:%M %Z"),
        "target_zone": target.key,
        "utc_offset": converted.strftime("%z"),
        "abbreviation": converted.strftime("%Z")
    })

    save_history()


def show_history():
    if not history:
        print("No conversion history available.")
        return

    print("\nCONVERSION HISTORY")

    for number, item in enumerate(history, start=1):
        print(f"\nConversion {number}")

        for key, value in item.items():
            print(f"{key.replace('_', ' ').title()}: {value}")


def export_csv():
    if not history:
        print("No history to export.")
        return

    fields = [
        "original_time",
        "source_zone",
        "converted_time",
        "target_zone",
        "utc_offset",
        "abbreviation"
    ]

    try:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(history)

        print(f"History exported successfully to {CSV_FILE}.")

    except OSError:
        print("Could not export the history file.")


def get_source_datetime():
    date_time = get_datetime()
    source_tz = get_timezone("Enter the source time zone")
    aware_time = get_aware_datetime(date_time, source_tz)

    return aware_time, source_tz


def display_conversion(original, source, converted, target):
    print("\nCONVERSION RESULT")
    print("-" * 40)
    print("Original time:", original.strftime("%Y-%m-%d %H:%M %Z"))
    print("Source time zone:", source.key)
    print("Converted time:", converted.strftime("%Y-%m-%d %H:%M %Z"))
    print("Target time zone:", target.key)
    print("UTC offset:", converted.strftime("%z"))
    print("Time zone abbreviation:", converted.strftime("%Z"))

    record_conversion(original, source, converted, target)


def convert_one():
    date_time, source_tz = get_source_datetime()
    target_tz = get_timezone("Enter the target time zone")

    converted_time = date_time.astimezone(target_tz)

    display_conversion(date_time, source_tz, converted_time, target_tz)


def convert_cities():
    date_time, source_tz = get_source_datetime()

    while True:
        names = input(
            "Enter target time zones separated by commas "
            "(e.g. Europe/London, Asia/Tokyo, America/New_York): "
        ).strip()

        city_names = [name.strip() for name in names.split(",") if name.strip()]

        if not city_names:
            print("Please enter at least one target time zone.")
            continue

        targets = []
        invalid_names = []

        for name in city_names:
            try:
                targets.append(ZoneInfo(name))

            except (ZoneInfoNotFoundError, ValueError):
                invalid_names.append(name)

        if invalid_names:
            print("Invalid time zones:", ", ".join(invalid_names))
            print("Please enter the target time zones again.")
            continue

        break

    print("\nTIME IN DIFFERENT CITIES")
    print("-" * 40)

    for target_tz in targets:
        converted_time = date_time.astimezone(target_tz)

        print(f"\nTime zone: {target_tz.key}")
        print("Converted time:", converted_time.strftime("%Y-%m-%d %H:%M %Z"))
        print("UTC offset:", converted_time.strftime("%z"))
        print("Abbreviation:", converted_time.strftime("%Z"))

        record_conversion(date_time, source_tz, converted_time, target_tz)


def main():
    while True:
        print("\n===== TIME ZONE CONVERTER =====")
        print("1. Convert time")
        print("2. View conversion history")
        print("3. Export history to CSV")
        print("4. Convert to several cities")
        print("5. Exit")

        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            convert_one()

        elif choice == "2":
            show_history()

        elif choice == "3":
            export_csv()

        elif choice == "4":
            convert_cities()

        elif choice == "5":
            print("Thank you for using the Time Zone Converter.")
            break

        else:
            print("Invalid selection. Please choose a number from 1 to 5.")
            continue

        if choice in ("1", "4"):
            while True:
                again = input(
                    "\nWould you like to perform another conversion? (yes/no): "
                ).strip().lower()

                if again in ("yes", "y", "no", "n"):
                    break

                print("Please enter yes or no.")

            if again in ("yes", "y"):
                continue


if __name__ == "__main__":
    main()