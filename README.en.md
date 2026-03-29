# Proof of Concept - Data Filtering by Country Code

> **Versión en español disponible:** See [README.md](README.md).
>
> **WARNING:** This script is provided as a Proof of Concept (PoC) for educational and demonstrative purposes only. It is not an official tool from Kaspersky and does not offer any guarantees or functionality support. Use at your own risk and always validate results in your environment.

This project includes Python and PowerShell scripts to filter records from a JSON file of Threat Data Feeds from the Kaspersky Threat Intelligence Portal, based on an **ISO 3166-1 alpha-2 country code**. These scripts allow identifying relevant records and generating a filtered file with the results.

## 🎯 Features

### Pipeline Scripts (Stage 2 — API Integration)

- **Full end-to-end workflow:** authenticate → download feed → filter by country → save output.
  - **Python:** `kaspersky_tdf.py` (English) and `kaspersky_tdf_es.py` (Spanish).
  - **PowerShell:** `KasperskyTDF.ps1` (English) and `KasperskyTDF_ES.ps1` (Spanish).
  - API token loaded securely from a `.env` file — never from CLI arguments.
  - Supports all three filtering modes: `geo`, `admin`, `combined`.
  - Optional `--save-raw` flag to also save the unfiltered feed.
  - Local file fallback via `--input-file` (no token required).

### Basic Scripts (Stage 1)

- **Simple Country Filtering:**
  - **Python:** `filtrado_pais.py` (Spanish) and `filter_country.py` (English).
  - Filters records where the `ip_whois.country` field matches the specified ISO country code.

### Advanced Scripts (Stage 1)

- **Multiple Filtering Modes:**
  - **Python:** `filtrado_pais_avanzado.py` (Spanish) and `filter_country_advanced.py` (English).
  - Modes: Geographic (`geo`), Administrative (`admin`), or Combined (`combined`).
  - CLI parameter support with `argparse`.

### PowerShell Scripts (Stage 1)

- Scripts available for Windows users:
  - `FiltrarPorPais.ps1` (Spanish).
  - `FilterByCountry.ps1` (English).
  - Include input validation and filtering based on `ip_geo` and `ip_whois.country`.

## 🔧 Requirements

- **Python:** Version 3.8 or higher.
- **Python Dependencies:**

  ```bash
  pip install -r requirements.txt
  ```

  Includes: `pycountry`, `requests`, `python-dotenv`, `coverage`.

- **PowerShell:** Version 5.1 or higher (PowerShell 7+ recommended).

## 📂 Project Structure

```plaintext
.
├── feeds/                              # Folder for input and output data
│   ├── IP_Reputation_Data_Feed.json    # Example input file
│   └── ...                             # Filtered output files (auto-generated)
├── scripts/
│   ├── Python/
│   │   ├── kaspersky_tdf.py            # Pipeline script in English (Stage 2)
│   │   ├── kaspersky_tdf_es.py         # Pipeline script in Spanish (Stage 2)
│   │   ├── filtrado_pais.py            # Basic script in Spanish (Stage 1)
│   │   ├── filtrado_pais_avanzado.py   # Advanced script in Spanish (Stage 1)
│   │   ├── filter_country.py           # Basic script in English (Stage 1)
│   │   ├── filter_country_advanced.py  # Advanced script in English (Stage 1)
│   └── PowerShell/
│       ├── KasperskyTDF.ps1            # Pipeline script in English (Stage 2)
│       ├── KasperskyTDF_ES.ps1         # Pipeline script in Spanish (Stage 2)
│       ├── FiltrarPorPais.ps1          # Script in Spanish (Stage 1)
│       ├── FilterByCountry.ps1         # Script in English (Stage 1)
├── .env.example                        # API token configuration template
├── README.md                           # Documentation in Spanish
├── README.en.md                        # Documentation in English
├── requirements.txt                    # Python dependencies
└── LICENSE                             # License file
```

## 🔑 API Configuration (Stage 2 — Pipeline Scripts)

The pipeline scripts authenticate against the [Kaspersky Threat Intelligence Portal API](https://tip.kaspersky.com/Help/api/?specId=tip-feeds-api) using an API token stored in a `.env` file.

### Step 1 — Obtain your API token

1. Sign in at [https://tip.kaspersky.com](https://tip.kaspersky.com).
2. Go to **Account Settings → API tokens**.
3. Set a validity period (maximum 1 year) and click **Request**.
4. Copy the generated token.

> You must accept the Terms and Conditions on the portal before the API is accessible.

### Step 2 — Create your `.env` file

```bash
cp .env.example .env
```

Then edit `.env` and fill in your real values:

```ini
KASPERSKY_TIP_TOKEN=your_api_token_here
KASPERSKY_TIP_BASE_URL=https://tip.kaspersky.com/api/feeds/
KASPERSKY_TIP_FEED_ENDPOINT=ip_reputation
KASPERSKY_TIP_LIMIT=0
```

| Variable | Description |
| --- | --- |
| `KASPERSKY_TIP_TOKEN` | Your API token (required) |
| `KASPERSKY_TIP_BASE_URL` | API base URL (do not change unless instructed) |
| `KASPERSKY_TIP_FEED_ENDPOINT` | Feed endpoint name (adjust if needed — see note below) |
| `KASPERSKY_TIP_LIMIT` | Max records to download (`0` = full feed) |

> **Note on the endpoint name:** The exact endpoint for the IP Reputation feed may differ depending on your subscription. If you receive a `404` error, check the [OpenAPI specification](https://tip.kaspersky.com/Help/api/?specId=tip-feeds-api) for the correct name and update `KASPERSKY_TIP_FEED_ENDPOINT` in your `.env`.
>
> **Security:** The `.env` file is excluded from version control by `.gitignore`. Never commit it. The API token is never passed as a CLI argument or written to logs.

## 🚀 Using the Scripts

### Pipeline Scripts (Stage 2)

#### Python Pipeline

**Full API pipeline (interactive — prompts for country and mode):**

```bash
python scripts/Python/kaspersky_tdf.py
```

**Full API pipeline (with CLI arguments):**

```bash
python scripts/Python/kaspersky_tdf.py --country ES --filter-mode combined
```

**Also save the raw (unfiltered) feed:**

```bash
python scripts/Python/kaspersky_tdf.py --country ES --save-raw
```

**Local file fallback (no token required):**

```bash
python scripts/Python/kaspersky_tdf.py --input-file feeds/IP_Reputation_Data_Feed.json --country ES
```

**Override endpoint or limit for a single run:**

```bash
python scripts/Python/kaspersky_tdf.py --country ES --feed-endpoint dangerous_ips --limit 10000
```

**Available arguments:**

| Argument | Description | Default |
| --- | --- | --- |
| `--country` | ISO 3166-1 alpha-2 code (e.g., `ES`) | Prompted interactively |
| `--filter-mode` | `geo`, `admin`, or `combined` | Prompted interactively (default: `combined`) |
| `--output-file` | Output file path | Auto-generated with timestamp |
| `--save-raw` | Also save the unfiltered feed | Disabled |
| `--input-file` | Use a local JSON file instead of the API | — |
| `--limit` | Override `KASPERSKY_TIP_LIMIT` for this run | From `.env` |
| `--feed-endpoint` | Override `KASPERSKY_TIP_FEED_ENDPOINT` for this run | From `.env` |

#### PowerShell Pipeline

**Full API pipeline (interactive):**

```powershell
.\scripts\PowerShell\KasperskyTDF.ps1
```

**With parameters:**

```powershell
.\scripts\PowerShell\KasperskyTDF.ps1 -Country ES -FilterMode combined
```

**Also save the raw feed:**

```powershell
.\scripts\PowerShell\KasperskyTDF.ps1 -Country ES -SaveRaw
```

**Local file fallback:**

```powershell
.\scripts\PowerShell\KasperskyTDF.ps1 -InputFile feeds\IP_Reputation_Data_Feed.json -Country ES
```

---

### Basic and Advanced Scripts (Stage 1)

#### Python (Stage 1)

**Basic execution** — filters using the `ip_whois.country` field:

```bash
python scripts/Python/filter_country.py
```

Configure the country by editing the `country` variable in the script (default: `ES`).

**Advanced execution** — multiple filter modes via CLI:

```bash
python scripts/Python/filter_country_advanced.py --country ES --filter-mode combined --input-file feeds/IP_Reputation_Data_Feed.json
```

The resulting file is automatically saved in `feeds/` with a name that includes the country, mode, and a timestamp.

#### PowerShell (Stage 1)

**Interactive execution:**

```powershell
.\scripts\PowerShell\FilterByCountry.ps1
```

Place `IP_Reputation_Data_Feed.json` in the `feeds/` folder, then follow the prompts to select country and filter mode.

## 📥 Data Preparation

### Option A — API Pipeline (Stage 2, recommended)

Configure your `.env` file as described in the [API Configuration](#-api-configuration-stage-2--pipeline-scripts) section and run the pipeline script directly. No manual download required.

### Option B — Manual Download (Stage 1)

1. Sign in at [Kaspersky Threat Intelligence Portal](https://tip.kaspersky.com).
2. Download the required data feed (`IP_Reputation_Data_Feed.json`).
3. Place the downloaded file in the project's `feeds/` folder.
4. Run a Stage 1 script with `--input-file feeds/IP_Reputation_Data_Feed.json`.

## 📝 Usage Examples

### Input JSON

```json
[
    {
        "ip": "1.2.3.4",
        "threat_score": 97,
        "category": "malware-ENGLISH",
        "first_seen": "21.01.2015 00:00",
        "last_seen": "20.05.2016 03:48",
        "popularity": 1,
        "ip_geo": "es",
        "users_geo": "us"
    },
    {
        "ip": "1.2.3.5",
        "threat_score": 97,
        "category": "malware-ENGLISH",
        "first_seen": "21.01.2015 00:00",
        "last_seen": "20.05.2016 03:48",
        "popularity": 1,
        "ip_geo": "es",
        "users_geo": "us",
        "ip_whois": {
            "net_range": "1.2.3.4 - 1.2.3.6",
            "net_name": "TEST_LIMITED",
            "descr": "TEST_LIMITED",
            "country": "NL",
            "asn": "50580"
        }
    },
    {
        "ip": "1.2.3.6",
        "threat_score": 97,
        "category": "malware-ENGLISH",
        "first_seen": "21.01.2015 00:00",
        "last_seen": "20.05.2016 03:48",
        "popularity": 1,
        "ip_geo": "es",
        "users_geo": "us",
        "ip_whois": {
            "net_range": "1.2.3.4 - 1.2.3.6",
            "net_name": "TEST_LIMITED",
            "descr": "TEST_LIMITED",
            "country": "ES",
            "asn": "50580"
        }
    },
    {
        "ip": "1.2.3.7",
        "threat_score": 97,
        "category": "malware-ENGLISH",
        "first_seen": "21.01.2015 00:00",
        "last_seen": "20.05.2016 03:48",
        "popularity": 1,
        "ip_geo": "nl",
        "users_geo": "us",
        "ip_whois": {
            "net_range": "1.2.3.4 - 1.2.3.7",
            "net_name": "TEST_LIMITED",
            "descr": "TEST_LIMITED",
            "country": "ES",
            "asn": "50580"
        }
    }
]
```

### Filtered JSON (country = ES, filter-mode = combined)

```json
[
    {
        "ip": "1.2.3.6",
        "threat_score": 97,
        "category": "malware-ENGLISH",
        "first_seen": "21.01.2015 00:00",
        "last_seen": "20.05.2016 03:48",
        "popularity": 1,
        "ip_geo": "es",
        "users_geo": "us",
        "ip_whois": {
            "net_range": "1.2.3.4 - 1.2.3.6",
            "net_name": "TEST_LIMITED",
            "descr": "TEST_LIMITED",
            "country": "ES",
            "asn": "50580"
        }
    },
    {
        "ip": "1.2.3.7",
        "threat_score": 97,
        "category": "malware-ENGLISH",
        "first_seen": "21.01.2015 00:00",
        "last_seen": "20.05.2016 03:48",
        "popularity": 1,
        "ip_geo": "nl",
        "users_geo": "us",
        "ip_whois": {
            "net_range": "1.2.3.4 - 1.2.3.7",
            "net_name": "TEST_LIMITED",
            "descr": "TEST_LIMITED",
            "country": "ES",
            "asn": "50580"
        }
    }
]
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
