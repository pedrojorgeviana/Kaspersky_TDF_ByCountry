# Description of the Structure of the IP_Reputation Threat Data Feed (Anonymized Data)

The `IP_Reputation_Data_Feed_*.json` file contains a list of records in JSON format. Each record provides detailed information about the reputation of an IP address, including data on malicious activity, geolocation, popularity, and administrative metadata.

---

## General Structure

The file is structured as a list of JSON objects, where each object includes the following fields:

```json
[
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

---

## Field Descriptions

1. **`id`** (Integer):
   - Unique identifier for the record in the feed.

2. **`ip`** (String):
   - Target IP address (IPv4 or IPv6). In this example, we use a fictitious IP within the documentation-reserved range (`203.0.113.0/24`).

3. **`threat_score`** (Integer):
   - Threat score assigned to the IP. Higher values indicate greater danger.
   - Range: 0 to 100.

4. **`category`** (String):
   - Classification of malicious activity associated with the IP.
   - Examples: `"phishing"`, `"botnet_cnc"`, `"spam"`, `"malware_hosting"`.

5. **`first_seen`** and **`last_seen`** (Strings):
   - Timestamps for the first and last detection of malicious activity, formatted as `"DD.MM.YYYY HH:MM"`.

6. **`popularity`** (Integer):
   - Indicator of the popularity or frequency of the IP.
   - Range: 0 (low) to 5 (high).

7. **`ip_geo`** (String):
   - ISO 3166-1 alpha-2 country code where the IP is physically located. In this example: `us` (United States).

8. **`users_geo`** (String):
   - Comma-separated list of ISO 3166-1 alpha-2 country codes where affected users were detected.

9. **`ip_whois`** (Object):
   - Administrative information about the associated IP range, as per WHOIS records.
     - **`net_range`**: Fictitious IP range.
     - **`net_name`**: Fictitious network name.
     - **`descr`**: Fictitious description of the range.
     - **`created`** and **`updated`**: Fictitious WHOIS record creation and update dates.
     - **`country`**: Fictitious country code.
     - **`contact_owner_name`**: Fictitious owner name.
     - **`contact_owner_code`**: Fictitious owner code.

---

### Example of an Anonymized Record

```json
{
    "id": 9876543210,
    "ip": "198.51.100.25",
    "threat_score": 90,
    "category": "botnet_cnc",
    "first_seen": "01.02.2025 08:15",
    "last_seen": "05.02.2025 14:45",
    "popularity": 4,
    "ip_geo": "gb",
    "users_geo": "us, gb, de, fr, es",
    "ip_whois": {
        "net_range": "198.51.100.0 - 198.51.100.255",
        "net_name": "FictionalNet",
        "descr": "Fictional Network for Demonstration",
        "created": "01.01.2023",
        "updated": "15.12.2024",
        "country": "GB",
        "contact_owner_name": "Demo Hosting Inc.",
        "contact_owner_code": "ORG-DE123-RIPE"
    }
}
```

---

## Important Notes

1. **Fictitious Data:**
   - All IP addresses and record data have been generated using standard conventions for documentation purposes (e.g., using `203.0.113.0/24` and `198.51.100.0/24` as reserved ranges).

2. **Structure Maintained:**
   - Although the data is fictitious, it retains the structure and semantics of the original feed.

3. **References:**
   - More information about the feed can be found in the official documentation: [Kaspersky Threat Intelligence - IP Reputation Feed](https://tip.kaspersky.com/Help/TIDF/en-US/IpReputationFeed.htm).
