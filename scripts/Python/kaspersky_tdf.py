# Kaspersky TDF ByCountry — Full Pipeline (English)
# Authenticate → Download IP Reputation feed → Filter by country → Save output.
#
# DISCLAIMER: This script is provided as a Proof of Concept (PoC) for educational
# and demonstration purposes only. It is not an official tool from Kaspersky, nor
# does it come with any guarantees or warranties of functionality or support.
# Use at your own risk, and always validate the results in your environment.

import argparse
import json
import os
import sys
from datetime import datetime

import pycountry
import requests
from dotenv import load_dotenv

FEED_NAME = "IP_Reputation"
DEFAULT_BASE_URL = "https://tip.kaspersky.com/api/feeds/"
DEFAULT_FEED_ENDPOINT = "ip_reputation"


# ---------------------------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------------------------

def display_disclaimer():
    print(
        "\n*** DISCLAIMER ***\n"
        "This script is provided as a Proof of Concept (PoC) for educational and "
        "demonstration purposes only.\n"
        "It is not an official tool from Kaspersky, nor does it come with any "
        "guarantees or warranties of functionality or support.\n"
        "Use at your own risk, and always validate the results in your environment.\n"
    )


# ---------------------------------------------------------------------------
# CLI arguments
# ---------------------------------------------------------------------------

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Kaspersky TDF ByCountry — full pipeline: "
            "download IP Reputation feed via API, filter by country, save output."
        )
    )
    parser.add_argument(
        "--country",
        type=str,
        default="",
        help="ISO 3166-1 alpha-2 country code (e.g., ES). Prompted interactively if omitted.",
    )
    parser.add_argument(
        "--filter-mode",
        type=str,
        choices=["geo", "admin", "combined"],
        default="",
        help="Filtering mode: geo, admin, or combined (default: combined).",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Output file path. Auto-generated with timestamp if omitted.",
    )
    parser.add_argument(
        "--save-raw",
        action="store_true",
        help="Also save the unfiltered feed response to feeds/IP_Reputation_raw_TIMESTAMP.json.",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default=None,
        help=(
            "LOCAL MODE: read from this local JSON file instead of calling the API. "
            "When set, no API token is required."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Override KASPERSKY_TIP_LIMIT for this run (0 = no limit).",
    )
    parser.add_argument(
        "--feed-endpoint",
        type=str,
        default=None,
        help="Override KASPERSKY_TIP_FEED_ENDPOINT for this run.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Configuration (secrets from .env only — never from CLI args)
# ---------------------------------------------------------------------------

def load_config():
    load_dotenv()
    token = os.environ.get("KASPERSKY_TIP_TOKEN", "").strip()
    base_url = os.environ.get("KASPERSKY_TIP_BASE_URL", DEFAULT_BASE_URL).strip()
    feed_endpoint = os.environ.get("KASPERSKY_TIP_FEED_ENDPOINT", DEFAULT_FEED_ENDPOINT).strip()
    limit_str = os.environ.get("KASPERSKY_TIP_LIMIT", "0").strip()
    try:
        limit = int(limit_str)
    except ValueError:
        limit = 0
    return {
        "token": token,
        "base_url": base_url,
        "feed_endpoint": feed_endpoint,
        "limit": limit,
    }


def validate_token_present(token):
    if not token:
        print("Error: KASPERSKY_TIP_TOKEN is not set.")
        print("  1. Copy .env.example to .env")
        print("  2. Set KASPERSKY_TIP_TOKEN to your API token")
        print("  3. Obtain a token at: https://tip.kaspersky.com (Account Settings)")
        sys.exit(1)


# ---------------------------------------------------------------------------
# HTTP client (API mode)
# ---------------------------------------------------------------------------

def build_api_session(token):
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    })
    session.verify = True  # SSL certificate verification always enabled
    return session


def build_feed_url(base_url, endpoint, limit):
    if not base_url.startswith("https://"):
        print("Error: KASPERSKY_TIP_BASE_URL must use HTTPS. Check your .env file.")
        sys.exit(1)
    url = f"{base_url.rstrip('/')}/{endpoint}"
    if limit and limit > 0:
        url += f"?limit={limit}"
    return url


def handle_api_error(response):
    status = response.status_code
    messages = {
        401: (
            "Authentication failed. Verify KASPERSKY_TIP_TOKEN in your .env file. "
            "Tokens expire after 1 year — request a new one at https://tip.kaspersky.com."
        ),
        403: (
            "Access denied. Your token may not have permission for this feed. "
            "Check your Kaspersky TIP subscription."
        ),
        404: (
            "Feed endpoint not found. Verify KASPERSKY_TIP_FEED_ENDPOINT in your .env file. "
            "Consult the OpenAPI spec at https://tip.kaspersky.com/Help/api/?specId=tip-feeds-api"
        ),
        429: "Rate limit exceeded. Wait before retrying.",
        500: "Kaspersky TIP API internal server error. Try again later.",
        502: "Kaspersky TIP API is temporarily unavailable (502). Try again in a few minutes.",
        503: "Kaspersky TIP API is temporarily unavailable (503). Try again in a few minutes.",
        504: "Kaspersky TIP API gateway timeout (504). Try again in a few minutes.",
    }
    msg = messages.get(status, f"Unexpected HTTP {status} from Kaspersky TIP API.")
    print(f"Error: {msg}")
    sys.exit(1)


def resolve_download_redirect(session, download_url):
    try:
        response = session.get(download_url, timeout=(10, 300))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        handle_api_error(response)
    except requests.exceptions.SSLError as e:
        print(f"Error: SSL certificate verification failed during download: {e}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Download timed out. The feed file may be very large. Try again.")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Could not connect to the download URL: {e}")
        sys.exit(1)


def fetch_feed(session, url):
    try:
        response = session.get(url, timeout=(10, 60))
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        handle_api_error(response)
    except requests.exceptions.SSLError as e:
        print(f"Error: SSL certificate verification failed: {e}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Check your network connection and try again.")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Could not reach Kaspersky TIP API: {e}")
        sys.exit(1)

    data = response.json()

    if isinstance(data, list):
        return data  # Option A: API returned records directly

    if isinstance(data, dict):
        # Option B: API returned a redirect object with a download URL
        for key in ("download_url", "url", "link", "data_url"):
            if key in data:
                print("  Resolving download link from API response...")
                return resolve_download_redirect(session, data[key])
        raise ValueError(
            f"Unexpected API response format. Keys in response: {list(data.keys())}"
        )

    raise ValueError(
        f"Unexpected API response type: {type(data).__name__}. Expected a JSON array."
    )


# ---------------------------------------------------------------------------
# Country validation and interactive prompts
# ---------------------------------------------------------------------------

def validate_country_code(country_code):
    if len(country_code) != 2 or not country_code.isalpha():
        raise ValueError(
            f"Invalid country code: '{country_code}'. "
            "Must be a two-letter ISO 3166-1 alpha-2 code (e.g., ES, US, DE)."
        )
    if not pycountry.countries.get(alpha_2=country_code.upper()):
        raise ValueError(
            f"Country code '{country_code}' is not a valid ISO 3166-1 alpha-2 code."
        )


def normalize_country_code(country_code):
    return country_code.upper()


def prompt_country_if_missing(country):
    if country:
        return country
    while True:
        code = input("Enter country code (ISO 3166-1 alpha-2, e.g., ES): ").strip()
        try:
            validate_country_code(code)
            return code
        except ValueError as e:
            print(f"  {e}")


def prompt_filter_mode_if_missing(mode):
    if mode:
        return mode
    while True:
        value = input(
            "Select filter mode [geo / admin / combined] (press Enter for combined): "
        ).strip().lower()
        if not value:
            return "combined"
        if value in ("geo", "admin", "combined"):
            return value
        print("  Invalid mode. Choose from: geo, admin, combined.")


# ---------------------------------------------------------------------------
# Local file loading (fallback / backward-compatible mode)
# ---------------------------------------------------------------------------

def load_input_file(input_file):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in input file: {e}")
    except PermissionError as e:
        raise PermissionError(f"Permission denied reading: {input_file}. Details: {e}")
    if not data:
        raise ValueError("Input file is empty or contains no records.")
    return data


# ---------------------------------------------------------------------------
# Filtering (logic identical to filter_country_advanced.py)
# ---------------------------------------------------------------------------

def filter_geo(data, country):
    normalized = country.lower()
    return [entry for entry in data if entry.get("ip_geo", "").lower() == normalized]


def filter_admin(data, country):
    normalized = country.upper()
    return [
        entry for entry in data
        if entry.get("ip_whois", {}).get("country", "").upper() == normalized
    ]


def filter_combined(data, country):
    geo = country.lower()
    adm = country.upper()
    return [
        entry for entry in data
        if entry.get("ip_geo", "").lower() == geo
        or entry.get("ip_whois", {}).get("country", "").upper() == adm
    ]


def apply_filter(data, country, mode):
    if mode == "geo":
        return filter_geo(data, country)
    elif mode == "admin":
        return filter_admin(data, country)
    elif mode == "combined":
        return filter_combined(data, country)
    raise ValueError(f"Unknown filter mode: '{mode}'. Use geo, admin, or combined.")


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def ensure_output_directory(output_file):
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied creating directory: {output_dir}. Details: {e}"
            )


def generate_output_filename(country, mode):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"feeds/{FEED_NAME}_{country}_{mode}_{timestamp}.json"


def generate_raw_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"feeds/{FEED_NAME}_raw_{timestamp}.json"


def save_output_file(output_file, data):
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except PermissionError as e:
        raise PermissionError(f"Permission denied writing to: {output_file}. Details: {e}")


def display_summary(source, country, mode, total, matched, output_file, raw_file=None):
    country_obj = pycountry.countries.get(alpha_2=country)
    country_name = country_obj.name if country_obj else country
    print("\n--- Summary ---")
    print(f"  Source        : {source}")
    print(f"  Country       : {country} ({country_name})")
    print(f"  Filter mode   : {mode}")
    print(f"  Total records : {total}")
    print(f"  Matched       : {matched}")
    print(f"  Filtered out  : {total - matched}")
    print(f"  Output saved  : {output_file}")
    if raw_file:
        print(f"  Raw feed      : {raw_file}")
    if matched == 0:
        print("\n  [!] No records matched. Try a different country or filter mode.")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    display_disclaimer()
    args = parse_arguments()

    try:
        local_mode = bool(args.input_file)

        # API mode: load config and validate token before doing anything else
        if not local_mode:
            config = load_config()
            validate_token_present(config["token"])
            # Apply per-run CLI overrides (endpoint and limit only — token stays in env)
            if args.feed_endpoint:
                config["feed_endpoint"] = args.feed_endpoint
            if args.limit is not None:
                config["limit"] = args.limit

        # Resolve country and filter mode (from CLI args or interactive prompts)
        country_input = prompt_country_if_missing(args.country)
        validate_country_code(country_input)
        country = normalize_country_code(country_input)
        mode = prompt_filter_mode_if_missing(args.filter_mode)

        # Fetch or load data
        raw_file = None
        if local_mode:
            print(f"Loading local file: {args.input_file}")
            data = load_input_file(args.input_file)
            source = f"Local file: {args.input_file}"
        else:
            url = build_feed_url(config["base_url"], config["feed_endpoint"], config["limit"])
            print(f"Downloading feed from Kaspersky TIP API...")
            session = build_api_session(config["token"])
            data = fetch_feed(session, url)
            source = f"API endpoint: {config['feed_endpoint']}"
            print(f"  Downloaded {len(data)} records.")

            if args.save_raw:
                raw_file = generate_raw_filename()
                ensure_output_directory(raw_file)
                save_output_file(raw_file, data)
                print(f"  Raw feed saved to: {raw_file}")

        # Filter
        print(f"Filtering by country '{country}' using mode '{mode}'...")
        filtered = apply_filter(data, country, mode)

        # Save output
        output_file = args.output_file or generate_output_filename(country, mode)
        ensure_output_directory(output_file)
        save_output_file(output_file, filtered)

        display_summary(source, country, mode, len(data), len(filtered), output_file, raw_file)

    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
