# Proof of Concept (PoC) for Advanced Filtering by Country Code
# This script demonstrates the feasibility of filtering data from a pre-downloaded JSON file based on IP reputation data.
# DISCLAIMER: This script is provided as a Proof of Concept (PoC) for educational and demonstration purposes only.
# It is not an official tool from Kaspersky, nor does it come with any guarantees or warranties of functionality or support.
# Use at your own risk, and always validate the results in your environment.

import argparse
import json
import os
from datetime import datetime
import pycountry

def display_disclaimer():
    """
    Display a disclaimer message each time the script is executed.
    """
    disclaimer = (
        "\n*** DISCLAIMER ***\n"
        "This script is provided as a Proof of Concept (PoC) for educational and demonstration purposes only.\n"
        "It is not an official tool from Kaspersky, nor does it come with any guarantees or warranties of functionality or support.\n"
        "Use at your own risk, and always validate the results in your environment.\n"
    )
    print(disclaimer)

def parse_arguments():
    """
    Parse command-line arguments for the script.
    """
    parser = argparse.ArgumentParser(description="Advanced country-based filtering for IP reputation data.")
    parser.add_argument(
        "--country",
        type=str,
        required=True,
        help="ISO 3166-1 alpha-2 country code to filter by (e.g., ES for Spain).",
    )
    parser.add_argument(
        "--filter-mode",
        type=str,
        choices=["geo", "admin", "combined"],
        default="combined",
        help="Filtering mode: 'geo', 'admin', or 'combined' (default: combined).",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default="./feeds/IP_Reputation_Data_Feed.json",
        help="Path to the input JSON file (default: ./feeds/IP_Reputation_Data_Feed.json).",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Path to the output JSON file. If not specified, a file name will be generated automatically.",
    )
    return parser.parse_args()

def validate_country_code(country_code):
    """
    Validate the country code.
    """
    if len(country_code) != 2 or not country_code.isalpha():
        raise ValueError(f"Invalid country code: {country_code}. It must be a two-letter ISO 3166-1 alpha-2 code.")

    # Check if the country code exists in pycountry
    if not pycountry.countries.get(alpha_2=country_code.upper()):
        raise ValueError(f"Country code '{country_code}' is not a valid ISO 3166-1 alpha-2 code.")

def normalize_country_code(country_code):
    """
    Normalize the country code to uppercase.
    """
    return country_code.upper()

def load_input_file(input_file):
    """
    Load the JSON data from the input file.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in the input file: {e}")
    except PermissionError as e:
        raise PermissionError(f"Permission denied when accessing the file: {input_file}. Details: {e}")

    if not data:
        raise ValueError("The input file is empty or contains no records.")

    return data

def ensure_output_directory(output_file):
    """
    Ensure the output directory exists, create it if necessary.
    """
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except PermissionError as e:
            raise PermissionError(f"Permission denied when creating the output directory: {output_dir}. Details: {e}")

def generate_output_filename(input_file, mode):
    """
    Generate an output file name based on the input file name, filtering mode, and timestamp.
    """
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"feeds/{base_name}_{mode}_{timestamp}.json"

def filter_geo(data, country):
    """
    Filter data by geographical location (ip_geo).
    """
    normalized_country = country.lower()
    return [entry for entry in data if entry.get("ip_geo", "").lower() == normalized_country]

def filter_admin(data, country):
    """
    Filter data by administrative location (ip_whois.country).
    """
    normalized_country = country.upper()
    return [entry for entry in data if entry.get("ip_whois", {}).get("country", "").upper() == normalized_country]

def filter_combined(data, country):
    """
    Filter data by either geographical or administrative location.
    """
    normalized_geo_country = country.lower()
    normalized_admin_country = country.upper()
    return [
        entry
        for entry in data
        if entry.get("ip_geo", "").lower() == normalized_geo_country or entry.get("ip_whois", {}).get("country", "").upper() == normalized_admin_country
    ]

def save_output_file(output_file, filtered_data):
    """
    Save the filtered data to the output file.
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(filtered_data, f, indent=4, ensure_ascii=False)
    except PermissionError as e:
        raise PermissionError(f"Permission denied when writing to the file: {output_file}. Details: {e}")

def main():
    display_disclaimer()

    args = parse_arguments()

    try:
        # Validate and normalize country code
        validate_country_code(args.country)
        country = normalize_country_code(args.country)

        # Load input data
        data = load_input_file(args.input_file)

        # Determine output file name if not specified
        output_file = args.output_file or generate_output_filename(args.input_file, args.filter_mode)

        # Ensure output directory exists
        ensure_output_directory(output_file)

        # Apply filtering logic
        if args.filter_mode == "geo":
            filtered_data = filter_geo(data, country)
        elif args.filter_mode == "admin":
            filtered_data = filter_admin(data, country)
        else:  # combined
            filtered_data = filter_combined(data, country)

        # Save the filtered data
        save_output_file(output_file, filtered_data)

        # Print summary
        print(f"Total records processed: {len(data)}")
        print(f"Records matching criteria: {len(filtered_data)}")
        print(f"Filtered data saved to: {output_file}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
