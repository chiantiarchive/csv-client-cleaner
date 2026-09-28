# 1st version tracked with GitHub


import csv
from pathlib import Path

script_folder = Path(__file__).parent
input_file = script_folder / "raw_clients.csv"
output_file = script_folder / "cleaned_clients.csv"

cleaned_clients = []
valid_count = 0
blank_count = 0

try:
    with open(input_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        print(reader.fieldnames)

        for row in reader:
            print(row)
            
            client = row["client_name"]
            email = row["email"]

            print(f"Raw email: {email}")

        if "client_name" not in reader.fieldnames:
            print("Error: The input CSV must contain a 'client_name' column.")
        else:
            for row in reader:
                client = row["client_name"]
                email = row["email"]

                print(f"Raw email: {email}")

                clean_client = client.strip().title()

                if client is None or client.strip() == "":
                    print("Skipped blank client.")
                    blank_count += 1
                    continue

                clean_client = client.strip().title()
                print(f"Good morning {clean_client}!")
                cleaned_clients.append(clean_client)
                valid_count += 1

except FileNotFoundError:
    print(f"Error: Input file not found: {input_file.name}")

if valid_count > 0:
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["client_name"])

        for clean_client in cleaned_clients:
            writer.writerow([clean_client])

    print(f"\nValid clients processed: {valid_count}")
    print(f"Blank clients skipped: {blank_count}")
    print(f"Saved cleaned clients to {output_file.name}")
else:
    print("\nNo valid clients were found. No output file was created.")
