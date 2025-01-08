# Proof of Concept - Data Filtering by Country Code

> **Versión en español disponible:** See [README.md](README.md).

> **WARNING:** This script is provided as a Proof of Concept (PoC) for educational and demonstrative purposes only. It is not an official tool from Kaspersky and does not offer any guarantees or functionality support. Use at your own risk and always validate results in your environment.

This project includes Python and PowerShell scripts to filter records from a JSON file of Threat Data Feeds from the Kaspersky Threat Intelligence Portal, based on an **ISO 3166-1 alpha-2 country code**. These scripts allow identifying relevant records and generating a filtered file with the results.

## 🎯 Features

### Basic Scripts:
- **Simple Country Filtering:**
  - **Python:** `filtrado_pais.py` (Spanish) and `filter_country.py` (English).
  - Filters records where the `ip_whois.country` field matches the specified ISO country code.

### Advanced Scripts:
- **Multiple Filtering Modes:**
  - **Python:** `filtrado_pais_avanzado.py` (Spanish) and `filter_country_advanced.py` (English).
  - Modes: Geographic (`geo`), Administrative (`admin`), or Combined (`combined`).
  - CLI parameter support with `argparse`.

### PowerShell Scripts:
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
- **PowerShell:** Version 5.1 or higher (PowerShell 7+ recommended).

## 📥 Data Preparation

Manually download the data from [Kaspersky Threat Intelligence Portal](https://tip.kaspersky.com):
1. Download the required data feed (`IP_Reputation_Data_Feed.json`).
2. Place the downloaded file in the project’s `feeds/` folder.

## 📂 Project Structure

```plaintext
.
├── feeds/                              # Folder for input and output data
│   ├── IP_Reputation_Data_Feed.json    # Example input file
│   └── ...                             # Other data files
├── scripts/
│   ├── Python/
│   │   ├── filtrado_pais.py            # Basic script in Spanish
│   │   ├── filtrado_pais_avanzado.py   # Advanced script in Spanish
│   │   ├── filter_country.py           # Basic script in English
│   │   ├── filter_country_advanced.py  # Advanced script in English
│   └── PowerShell/
│       ├── FiltrarPorPais.ps1          # Script in Spanish
│       ├── FilterByCountry.ps1         # Script in English
├── README.md                           # Documentation in Spanish
├── README.en.md                        # Documentation in English
├── requirements.txt                    # Python dependencies
└── LICENSE                             # License file
```

## 🚀 Using the Scripts

### Python

#### Basic Execution:
- **Purpose:** Filter data by country using the `ip_whois.country` field.
- **Command:**
  ```bash
  python scripts/Python/filter_country.py
  ```
  - Configure the country in the script by editing the `country` variable (default: `ES`).

#### Advanced Execution:
- **Purpose:** Filter data with advanced modes (`geo`, `admin`, `combined`).
- **Command:**
  ```bash
  python scripts/Python/filter_country_advanced.py --country ES --filter-mode geo
  ```
  - Change `--country` to the desired ISO country code.
  - Modify the input file using `--input-file`.

#### Example:
Suppose you have the file `IP_Reputation_Data_Feed.json` in the `feeds/` folder and want to filter records for Spain (`ES`):
```bash
python scripts/Python/filter_country_advanced.py --country ES --filter-mode combined --input-file feeds/IP_Reputation_Data_Feed.json
```
The resulting file will be automatically saved in `feeds/` with a name that includes the country, mode, and a timestamp.

### PowerShell

#### Interactive Execution:
- **Purpose:** Interactively filter data in Windows.
- **Command:**
  ```powershell
  .\scripts\PowerShell\FilterByCountry.ps1
  ```
  - Follow the instructions to enter the country and choose the filtering mode.

#### Example:
Place the input file `IP_Reputation_Data_Feed.json` in the `feeds/` folder. Then execute:
```powershell
.\scripts\PowerShell\FilterByCountry.ps1
```
Follow the instructions to filter by Spain (`ES`) and combined mode (`combined`).

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

### Filtered JSON (Example for `country = ES`)
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

This project is licensed under the MIT License. See the `LICENSE` file for details.
