import csv
from pathlib import Path
from datetime import datetime


# Define the folder containing this Python script.
script_folder = Path(__file__).parent

# Define the input and output file locations.
input_file = script_folder / "raw_clients.csv"
output_file = script_folder / "cleaned_clients.csv"
rejected_file = script_folder / "rejected_clients.csv"
summary_file = script_folder / "processing_summary.txt"


# Store accepted and rejected records until they are written to CSV files.
cleaned_clients = []
rejected_clients = []

# Track emails already accepted so duplicate records can be rejected.
seen_emails = set()

# Track validation results for the summary report.
valid_count = 0
blank_count = 0
invalid_email_count = 0
duplicate_email_count = 0
malformed_row_count = 0


try:
    with open(input_file, "r", newline="", encoding="utf-8") as file:
        # Capture extra CSV values so malformed rows can be detected.
        reader = csv.DictReader(file, restkey="_extra_fields")

        # Define the CSV header names required by this program.
        required_columns = ["client_name", "email"]

        # Stop processing if a required header is missing.
        if not reader.fieldnames or not all(
            column in reader.fieldnames for column in required_columns
        ):
            print("Error: The input CSV must contain 'client_name' and 'email' columns.")

        else:
            for row_number, row in enumerate(reader, start=2):
                # Reject rows with more values than the CSV header defines.
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

                # Reject blank or whitespace-only client names.
                if client is None or client.strip() == "":
                    print(f"Row {row_number}: skipped blank client.")
                    blank_count += 1

                    rejected_clients.append({
                        "row_number": row_number,
                        "client_name": client,
                        "email": email,
                        "reason": "Blank client name"
                    })

                    continue

                # Reject blank email values.
                if email is None or email.strip() == "":
                    print(f"Row {row_number}: skipped {client.strip()} — blank email.")
                    invalid_email_count += 1

                    rejected_clients.append({
                        "row_number": row_number,
                        "client_name": client,
                        "email": email,
                        "reason": "Blank email"
                    })

                    continue

                # Normalize usable values before later validation.
                clean_client = client.strip().title()
                clean_email = email.strip().lower()

                # Reject basic invalid email formats.
                if "@" not in clean_email:
                    print(f"Row {row_number}: skipped {clean_client} — invalid email.")
                    invalid_email_count += 1

                    rejected_clients.append({
                        "row_number": row_number,
                        "client_name": client,
                        "email": email,
                        "reason": "Invalid email"
                    })

                    continue

                # Reject any accepted email that appears again later in the file.
                if clean_email in seen_emails:
                    print(f"Row {row_number}: skipped duplicate email — {clean_email}")
                    duplicate_email_count += 1

                    rejected_clients.append({
                        "row_number": row_number,
                        "client_name": client,
                        "email": email,
                        "reason": "Duplicate email"
                    })

                    continue

                # Store cleaned data for the valid-client export.
                print(f"Row {row_number}: kept client: {clean_client}")

                cleaned_clients.append({
                    "client_name": clean_client,
                    "email": clean_email
                })

                seen_emails.add(clean_email)
                valid_count += 1

except FileNotFoundError:
    print(f"Error: Input file not found: {input_file.name}")


# Create the clean output file only if the run found valid client records.
if valid_count > 0:
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        fieldnames = ["client_name", "email"]

        # Ensure rows match the cleaned CSV column structure.
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="raise"
        )

        writer.writeheader()
        writer.writerows(cleaned_clients)

    print(f"Saved cleaned clients to {output_file.name}")

else:
    # Remove old output so it cannot be mistaken for this run's output.
    if output_file.exists():
        output_file.unlink()
        print(f"Removed stale output file: {output_file.name}")

    print("No valid clients were found. No output file was created.")


# Create a report only when one or more client records were rejected.
if rejected_clients:
    with open(rejected_file, "w", newline="", encoding="utf-8") as file:
        rejected_fieldnames = [
            "row_number",
            "client_name",
            "email",
            "reason"
        ]

        # Ensure rows match the rejected-record report structure.
        rejected_writer = csv.DictWriter(
            file,
            fieldnames=rejected_fieldnames,
            extrasaction="raise"
        )

        rejected_writer.writeheader()
        rejected_writer.writerows(rejected_clients)

    print(f"Saved rejected clients to {rejected_file.name}")


# Record when the latest run completed.
run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Build a summary that can be reviewed outside the terminal.
summary = (
    f"Run completed: {run_timestamp}\n"
    f"Valid clients processed: {valid_count}\n"
    f"Blank clients skipped: {blank_count}\n"
    f"Invalid emails skipped: {invalid_email_count}\n"
    f"Duplicate emails skipped: {duplicate_email_count}\n"
    f"Malformed rows skipped: {malformed_row_count}\n"
)

# Write the report for the current run.
with open(summary_file, "w", encoding="utf-8") as file:
    file.write(summary)

print(f"Saved processing summary to {summary_file.name}")