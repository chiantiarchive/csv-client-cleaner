# 1st version tracked with GitHub


import csv
from pathlib import Path

script_folder = Path(__file__).parent
input_file = script_folder / "raw_clients.csv"
output_file = script_folder / "cleaned_clients.csv"

cleaned_clients = []
valid_count = 0
blank_count = 0

invalid_email_count = 0


try:
    with open(input_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)


        if "client_name" not in reader.fieldnames:
            print("Error: The input CSV must contain a 'client_name' column.")
        else:
            for row in reader:
                client = row["client_name"]
                email = row["email"]

                if client is None or client.strip() == "":
                    print("Skipped blank client.")
                    blank_count += 1
                    continue

                if email is None or email.strip() == "":
                    print(f"Skipped {client.strip()}: blank email.")
                    invalid_email_count += 1
                    continue

                clean_client = client.strip().title()
                clean_email = email.strip().lower()


                if "@" not in clean_email:
                    print(f"Skipped {clean_client}: invalid email.")
                    invalid_email_count += 1
                    continue

                print(f"Kept client: {clean_client}!")
                cleaned_clients.append({
                    "client_name": clean_client,
                    "email": clean_email
                })
                valid_count += 1

except FileNotFoundError:
    print(f"Error: Input file not found: {input_file.name}")

if valid_count > 0:
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        fieldnames = ["client_name", "email"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(cleaned_clients)




    print(f"\nValid clients processed: {valid_count}")
    print(f"Blank clients skipped: {blank_count}")
    print(f"Invalid emails skipped: {invalid_email_count}")
    print(f"Saved cleaned clients to {output_file.name}")
else:
    print("\nNo valid clients were found. No output file was created.")

