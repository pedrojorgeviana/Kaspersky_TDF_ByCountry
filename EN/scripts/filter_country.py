# Proof of Concept (PoC) for Filtering by Country Code
# This script demonstrates filtering data from a JSON file containing IP reputation data.
# DISCLAIMER: This script is provided as a Proof of Concept (PoC) for educational and demonstration purposes only.
# It is not an official tool from Kaspersky, nor does it come with any guarantees or warranties of functionality or support.
# Use at your own risk, and always validate the results in your environment.

import json
import datetime
import os
import pycountry

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
country = 'ES'  # Country code in ISO 3166-2 format (ES, PT, BR, etc...)

def get_country_name(iso_code):
    """
    Returns the name of the country given its ISO alpha-2 code using pycountry.
    """
    try:
        country = pycountry.countries.get(alpha_2=iso_code.upper())
        return country.name if country else "Unknown"
    except Exception:
        return "Unknown"

def filter_by_country(input_file, output_file):
    """
    Filters records in a JSON file where the 'ip_whois' field has 'country' equal to the specified country code.
    """
    try:
        # Create the feeds folder if it doesn't exist
        os.makedirs(os.path.dirname(input_file), exist_ok=True)

        # Open and load the JSON file
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("The JSON file must contain a list of records.")

        # Filter the data
        filtered_records = [
            record for record in data
            if record.get("ip_whois", {}).get("country", "").upper() == country.upper()
        ]

        # Report the results
        print(f"Total records processed: {len(data)}")
        print(f"Ignored records: {len(data) - len(filtered_records)}")
        if filtered_records:
            print(f"{len(filtered_records)} records found with country = '{country}' ({get_country_name(country)}).")
        else:
            print(f"No records found with country = '{country}' ({get_country_name(country)}).")

        # Save the filtered records
        with open(output_file, 'w', encoding='utf-8') as output:
            json.dump(filtered_records, output, indent=4, ensure_ascii=False)
        print(f"Filtered records saved to: {output_file}")

    except FileNotFoundError as e:
        print(f"Error: The file '{input_file}' was not found.")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: The file is not a valid JSON. Details: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    # Display disclaimer
    disclaimer = (
        "\n*** DISCLAIMER ***\n"
        "This script is provided as a Proof of Concept (PoC) for educational and demonstration purposes only.\n"
        "It is not an official tool from Kaspersky, nor does it come with any guarantees or warranties of functionality or support.\n"
        "Use at your own risk, and always validate the results in your environment.\n"
    )
    print(disclaimer)

    # Files in the feeds folder
    folder = "./feeds/"
    input_file = os.path.join(folder, "IP_Reputation_Data_Feed.json")
    output_file = os.path.join(folder, f"IP_Reputation_filtered_{country}_{timestamp}.json")

    # Execute the function
    filter_by_country(input_file, output_file)
