import csv
from pathlib import Path
from datetime import datetime


script_folder = Path(__file__).parent
input_file = script_folder / "raw_clients.csv"
output_file = script_folder / "cleaned_clients.csv"
rejected_file = script_folder / "rejected_clients.csv"
summary_file = script_folder / "processing_summary.txt"



cleaned_clients = []
rejected_clients = []

seen_emails = set()


valid_count = 0
blank_count = 0
invalid_email_count = 0
duplicate_email_count = 0
malformed_row_count = 0

try:
    with open(input_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, restkey="_extra_fields")
        required_columns = ["client_name", "email"]


        if not reader.fieldnames or not all(
            column in reader.fieldnames for column in required_columns
        ):
            print("Error: The input CSV must contain 'client_name' and 'email' columns.")
        else:
            for row_number, row in enumerate(reader, start=2):
                if row.get("_extra_fields") is not None:
                    print(f"Row {row_number}: skipped malformed row.")
                    malformed_row_count += 1

                    rejected_clients.append({
                        "row_number": row_number,
                        "client_name": row.get("client_name"),
                        "email": row.get("email"),
                        "reason": "Extra CSV fields"
                    })

                    continue

                client = row["client_name"]
                email = row["email"]

                if client is None or client.strip() == "":
                    print(f"Row {row_number}: skipped blank client.")

                    rejected_clients.append({
                        "row_number": row_number,
                        "client_name": client,
                        "email": email,
                        "reason": "Blank client name"
                    })

                    blank_count += 1
                    continue

                if email is None or email.strip() == "":
                    print(f"Row {row_number}: skipped {client.strip()} — blank email.")
                    
                    rejected_clients.append({
                        "row_number": row_number,
                        "client_name": client,
                        "email": email,
                        "reason": "Blank email"
                    })

                    invalid_email_count += 1
                    continue

                clean_client = client.strip().title()
                clean_email = email.strip().lower()


                if "@" not in clean_email:
                    print(f"Row {row_number}: skipped {clean_client} — invalid email.")

                    rejected_clients.append({
                        "row_number": row_number,
                        "client_name": client,
                        "email": email,
                        "reason": "Invalid email"
                    })

                    invalid_email_count += 1
                    continue

                if clean_email in seen_emails:
                    print(f"Row {row_number}: skipped duplicate email — {clean_email}")

                    rejected_clients.append({
                        "row_number": row_number,
                        "client_name": client,
                        "email": email,
                        "reason": "Duplicate email"
                    })

                    duplicate_email_count += 1
                    continue

                print(f"Row {row_number}: kept client: {clean_client}")
                cleaned_clients.append({
                    "client_name": clean_client,
                    "email": clean_email
                })
                seen_emails.add(clean_email)
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
    print(f"Duplicate emails skipped: {duplicate_email_count}")
    print(f"Malformed rows skipped: {malformed_row_count}")
    print(f"Saved cleaned clients to {output_file.name}")
else:
    if output_file.exists():
        output_file.unlink()
        print(f"Removed stale output file: {output_file.name}")

    print("\nNo valid clients were found. No output file was created.")


if rejected_clients:
    with open(rejected_file, "w", newline="", encoding="utf-8") as file:
        rejected_fieldnames = ["row_number", "client_name", "email", "reason"]
        rejected_writer = csv.DictWriter(file, fieldnames=rejected_fieldnames)

        rejected_writer.writeheader()
        rejected_writer.writerows(rejected_clients)

    print(f"Saved rejected clients to {rejected_file.name}")


run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

summary = (
    f"Run completed: {run_timestamp}\n"
    f"Valid clients processed: {valid_count}\n"
    f"Blank clients skipped: {blank_count}\n"
    f"Invalid emails skipped: {invalid_email_count}\n"
    f"Duplicate emails skipped: {duplicate_email_count}\n"
    f"Malformed rows skipped: {malformed_row_count}\n"
)

with open(summary_file, "w", encoding="utf-8") as file:
    file.write(summary)

print(f"Saved processing summary to {summary_file.name}")


