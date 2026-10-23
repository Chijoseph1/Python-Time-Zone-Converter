from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import csv

CSV_FILE = "conversion_history.csv"

# History exists only while the program is running.
history = []

def get_datetime():
    while True:
        date_time = input(
            "Enter date and time (YYYY-MM-DD HH:MM), "
            "e.g. 2026-10-22 14:30: "
        ).strip()

        try:
            return datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        except ValueError:
            print(
                "Invalid date or time. "
                "Please use YYYY-MM-DD HH:MM."
            )

def get_timezone(prompt):
    while True:
        zone_name = input(
            f"{prompt} (e.g. Africa/Lagos or Europe/London): "
        ).strip()

        try:
            return ZoneInfo(zone_name)
        except (ZoneInfoNotFoundError, ValueError):
            print(
                "Invalid time-zone name. "
            )

def get_aware_datetime(date_time, zone):
    while True:
        # Try both possible interpretations of the local time.
        first = date_time.replace(tzinfo=zone, fold=0)
        second = date_time.replace(tzinfo=zone, fold=1)

        # Convert each interpretation to UTC and back.
        first_back = first.astimezone(timezone.utc).astimezone(zone)
        second_back = second.astimezone(timezone.utc).astimezone(zone)

        first_valid = (
            first_back.replace(tzinfo=None) == date_time
        )
        second_valid = (
            second_back.replace(tzinfo=None) == date_time
        )

        if not first_valid and not second_valid:
            print(
                f"{date_time} does not exist in {zone.key} "
                "because of a time-zone clock change."
            )
            date_time = get_datetime()
            continue

        if (
            first_valid
            and second_valid
            and first.utcoffset() != second.utcoffset()
        ):
            print(f"This time occurs twice in {zone.key}.")
            print("1. First occurrence")
            print("2. Second occurrence")

            while True:
                choice = input("Choose 1 or 2: ").strip()

                if choice == "1":
                    return first
                elif choice == "2":
                    return second
                else:
                    print("Please enter 1 or 2.")

        if first_valid:
            return first

        return second


def record_conversion(original, source, converted, target):
    history.append({
        "original_time": original.strftime("%Y-%m-%d %H:%M %Z"),
        "source_zone": source.key,
        "converted_time": converted.strftime("%Y-%m-%d %H:%M %Z"),
        "target_zone": target.key,
        "utc_offset": converted.strftime("%z"),
        "abbreviation": converted.strftime("%Z")
    })

def show_history():
    if not history:
        print("\nNo conversion history available.")
        return

    print("\n========== CONVERSION HISTORY ==========")

    for number, item in enumerate(history, start=1):
        print(f"\nConversion {number}")

        for key, value in item.items():
            label = key.replace("_", " ").title()
            print(f"{label}: {value}")

    print("\n========================================")


def export_csv():
    if not history:
        print("\nNo history to export.")
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
        with open(
            CSV_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(history)

        print(f"\nHistory exported successfully to {CSV_FILE}.")

    except OSError as error:
        print(f"\nCould not export history: {error}")


def convert_one():
    print("\n========== CONVERT TIME ==========")

    date_time = get_datetime()
    source = get_timezone("Enter the source time zone")

    original = get_aware_datetime(date_time, source)

    target = get_timezone("Enter the target time zone")

    converted = original.astimezone(target)

    print("\n========== CONVERSION RESULT ==========")
    print(f"Original time: {original.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"Source zone: {source.key}")
    print(f"Converted time: {converted.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"Target zone: {target.key}")
    print(f"UTC offset: {converted.strftime('%z')}")
    print(f"Time-zone abbreviation: {converted.strftime('%Z')}")

    record_conversion(original, source, converted, target)


def convert_cities():
    print("\n========== CONVERT TO MULTIPLE CITIES ==========")

    date_time = get_datetime()
    source = get_timezone("Enter the source time zone")

    original = get_aware_datetime(date_time, source)

    print(
        "\nEnter the target time zones separated by commas."
    )
    print("Example: Europe/London, Asia/Tokyo, America/New_York")

    while True:
        zone_names = input("Target time zones: ").strip()

        if zone_names:
            names = [
                name.strip()
                for name in zone_names.split(",")
                if name.strip()
            ]

            if names:
                break

        print("Please enter at least one time-zone name.")

    targets = []
    invalid_names = []

    for name in names:
        try:
            target = ZoneInfo(name)

            if target.key not in [item.key for item in targets]:
                targets.append(target)

        except (ZoneInfoNotFoundError, ValueError):
            invalid_names.append(name)

    for name in invalid_names:
        print(f"Invalid time-zone name: {name}")

    if not targets:
        print("No valid target time zones were entered.")
        return

    print("\n========== MULTIPLE CITY RESULTS ==========")

    for target in targets:
        converted = original.astimezone(target)

        print(f"\nTarget zone: {target.key}")
        print(
            "Converted time: "
            f"{converted.strftime('%Y-%m-%d %H:%M %Z')}"
        )
        print(f"UTC offset: {converted.strftime('%z')}")
        print(f"Time-zone abbreviation: {converted.strftime('%Z')}")

        record_conversion(original, source, converted, target)


def main():
    print("====================================")
    print("       TIME ZONE CONVERTER")
    print("====================================")

    while True:
        print("\nMain Menu")
        print("1. Convert time")
        print("2. View conversion history")
        print("3. Export history to CSV")
        print("4. Convert to several cities")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            convert_one()

        elif choice == "2":
            show_history()

        elif choice == "3":
            export_csv()

        elif choice == "4":
            convert_cities()

        elif choice == "5":
            print("\nThank you for using the Time Zone Converter!")
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select an option from 1 to 5.")


if __name__ == "__main__":
    main()