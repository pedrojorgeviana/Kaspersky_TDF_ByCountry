# IP Reputation Filtering by Country

This project allows filtering records from a JSON file containing Threat Data Feeds from the **Kaspersky Threat Intelligence Portal**, which includes IP reputation data based on the **ISO 3166-1 alpha-2 country code**. The primary goal is to process large datasets, identify specific records by country, and generate a filtered file with the results.

## 🎯 Features

- **Customizable Filter**: Filter records from a JSON file by country using an ISO 3166-1 alpha-2 code (e.g., `ES` for Spain, `US` for the United States).
- **Error Handling**: Support for missing files, malformed JSON, and unexpected structures.
- **Enriched Results**: Includes the country's name in the output file, along with a timestamp for traceability.
- **`feeds` Work Folder**: All input and output files are processed within the `feeds` folder.

## 🔧 Requirements

- **Python**: Version 3.8 or later.
- **Dependencies**:
  - `pycountry`: To fetch the country's name based on its ISO code.
  - `unittest`: Standard library for running tests.

Install the dependencies using the following command:

```bash
pip install -r requirements.txt
```

Contents of the `requirements.txt` file:

```**Dependencies**
coverage==7.6.10
pycountry==22.3.5
```

## 📥 Data Download

### Required data

This project uses **Threat DataFeeds de Kaspersky** to process and filter records by country. Currently, the data must be **manually downloaded** rom the Kaspersky Threat Intelligence Portal, provided you have the necessary licenses enabled.

**Steps to Download:**

1. Access [Kaspersky Threat Intelligence Portal](https://tip.kaspersky.com).
2. Log in with your credentials.
3. Download the corresponding data feed (e.g., `IP_Reputation_Data_Feed.json`).
4. Place the downloaded file into the `feeds` folder of the project.
5. Modify the `fichero_entrada` variable in the `filtrado_pais.py` file to match the name of the downloaded data feed.

## 📁 Project Structure

```plaintext
.
├── feeds/
│   ├── IP_Reputation_Data_Feed_****.json   # Sample input file
│   └── ...                                 # Other test files
├── filtrado_pais.py                        # Main script
├── test_filtrado_pais.py                   # Automated tests
└── README.md                               # Project documentation
```

## Usage

### 1.  Prepare the `feeds` Folder

Create a folder named `feeds` n the root directory and place the JSON input file inside it. For example:

```plaintext
feeds/
└── IP_Reputation_Data_Feed_****.json
```

### 2. Run the Main Script

Run the main script to filter records by a specific country code:

```bash
python filtrado_pais.py
```

The output file will be saved in the `feeds` folder with a name that includes the country code and a timestamp, for example:

```plaintext
feeds/IP_Reputation_filtered_ES_*****.json
```

### 3. Modify the Country Code

You can change the country code by modifying the `pais` variable inside `filtrado_pais.py`. For example:

```python
pais = 'ES'  # Change to Spain or any other country
```

## Tests

This project includes a suite of automated tests to validate its functionality. The tests are located in the `test_filtrado_pais.py` file and cover scenarios such as:

- Files with valid records.
- Files with no matching records.
- Empty or malformed JSON files.
- Nonexistent files.

### Run the Tests

To run the tests, use the following command:

```bash
python -m unittest test_filtrado_pais.py
```

Expected output if everything works correctly:

```plaintext
Total records processed: 4
Records ignored: 2
2 records found with country = 'ES' (Spain).
Filtered records saved in: feeds/test_filtered_feed.json
...
Ran 5 tests in 0.018s

OK
```

## Example of Input JSON

The file `IP_Reputation_Data_Feed_171224_0757.json` should have a structure similar to the following:

```json
[
    ...
    {
        "id": 1234567890,
        "ip": "203.0.113.42",
        "threat_score": 85,
        "category": "phishing",
        "first_seen": "01.01.2025 12:00",
        "last_seen": "02.01.2025 18:30",
        "popularity": 3,
        "ip_geo": "us",
        "users_geo": "es, fr, de, it, nl",
        "ip_whois": {
            "net_range": "203.0.113.0 - 203.0.113.255",
            "net_name": "ExampleNet",
            "descr": "Example Description for Network Range",
            "created": "15.06.2022",
            "updated": "10.11.2024",
            "country": "US",
            "contact_owner_name": "Example Hosting",
            "contact_owner_code": "ORG-EX123-RIPE"
        }
    },
    ...
]
```

## Example of Filtered JSON

A filtered file for `country = 'ES'` would have the following structure:

```json
[
  ...
    {"ip_whois": {"country": "ES", "org": "ISP España"}},
    {"ip_whois": {"country": "ES", "org": "ISP España 2"}},
  ...
]
```

## Error Handling

The script handles the following error cases:

1. **File not found**:
   - Mensage: `Error: El archivo 'archivo_inexistente.json' no se encuentra.`
2. **Malformed JSON**:
   - Mensage: `Error: El archivo no es un JSON válido.`
3. **Invalid Structure**:
   - Mensage: `Advertencia: Se encontró un registro con formato incorrecto y se omitió.`

## 🚀 Next Steps

Here are some ideas to improve and extend this project: (in progress...)

### 1. Geographical vs Administrative Coverage

- Implement the ability to use  **`ip_geo`** or **`ip_whois.country`** as separate or combined filters  (`OR` or `AND`).
- Add detailed classifications to the results, such as:
  - **Geographical**: IPs related to Spain by geolocation (`ip_geo`).
  - **Administrative**: IPs related to Spain by WHOIS registration (`ip_whois.country`).
  - **Both**: IPs meeting both criteria.

### 2. Support for More Input and Output Formats

- **Input**:
  - Add support for other formats such as CSV, Excel, or databases.
  - Allow importing data from APIs from Kaspersky Threat Intelligence Portal.
- **Output**:
  - Generate reports in formats such as CSV or Excel.
  - Export filtered data to a relational database (e.g., PostgreSQL or MySQL).

### 3. Filter Optimization

- **Filter Improvements**:
  - Implement additional filters, such as by IP range (`192.168.x.x`), organization, or connection type.
  - Add support for complex rules using regular expressions.
- **Speed**:
  - Use parallel processing techniques to handle large datasets.

### 4. User Interface

- **Command Line**:
  - Integrate  `argparse` to allow users to specify the country code, input file, and output file directly from the terminal.
- **Graphical Interface**:
  - Create a basic graphical interface using libraries such as `tkinter` or `PyQt`.

### 5. Anomaly Detection

- Identify and flag IPs with discrepancies between geolocation (`ip_geo`) and WHOIS registration (`ip_whois.country`).
- Generate alerts for malicious or suspicious IPs based on public blacklists.

### 6. Visual Analysis

- Create charts and statistics using libraries such as `matplotlib` or `Plotly` to show:
  - Geographic distribution of IPs.
  - Organizations or providers with the most records.

### 7.  Documentation and Automation

- **Improve Documentation**:
  - Create a guide for contributing to the project.
  - Add more advanced usage examples.
- **Automation**:
  - Create an installation or configuration script to facilitate deployment in new environments.

---

### ¿Have More Ideas?

If you have other ideas or suggestions, feel free to contribute or open an issue in the repository! 😊

## Autor

Developed by @pedrojorgeviana. If you have questions or suggestions, feel free to contact me.

## Note on AI Usage

This project was developed with the assistance of artificial intelligence (AI) tools like ChatGPT. All generated content has been supervised, adapted, and validated by the author to ensure quality and functionality.

## Licencia

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
