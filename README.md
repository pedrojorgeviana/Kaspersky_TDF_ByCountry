# Prueba de Concepto - Filtrado de Datos por Código de País

> **English version available:** See [README.en.md](README.en.md).

> **AVISO:** Este script se proporciona como una Prueba de Concepto (PoC) con fines educativos y demostrativos únicamente. No es una herramienta oficial de Kaspersky, ni ofrece garantías o soporte de funcionalidad. Úselo bajo su propio riesgo y siempre valide los resultados en su entorno.

Este proyecto incluye scripts en Python y PowerShell para filtrar registros de un archivo JSON de Threat Data Feeds del Kaspersky Threat Intelligence Portal, basado en un **código de país ISO 3166-1 alfa-2**. Estos scripts permiten identificar registros relevantes, generando un archivo filtrado con los resultados.

## 🎯 Características

### Scripts Básicos:

- **Filtrado Simple por País:**
  - **Python:** `filtrado_pais.py` (español) y `filter_country.py` (inglés).
  - Filtrado por registros donde el campo `ip_whois.country` coincide con el código ISO del país especificado.

### Scripts Avanzados:

- **Modos de Filtrado Múltiples:**
  - **Python:** `filtrado_pais_avanzado.py` (español) y `filter_country_advanced.py` (inglés).
  - Modos: Geográfico (`geo`), Administrativo (`admin`), o Combinado (`combined`).
  - Soporte para parámetros CLI con `argparse`.

### Scripts en PowerShell:

- Scripts disponibles para usuarios de Windows:
  - `FiltrarPorPais.ps1` (español).
  - `FilterByCountry.ps1` (inglés).
  - Incluyen validación de entrada y filtrado basado en `ip_geo` y `ip_whois.country`.

## 🔧 Requisitos

- **Python:** Versión 3.8 o superior.
- **Dependencias Python:**

  ```bash
  pip install -r requirements.txt
  ```

- **PowerShell:** Versión 5.1 o superior (recomendado PowerShell 7+).

## 📥 Preparación de Datos

Descarga manualmente los datos desde [Kaspersky Threat Intelligence Portal](https://tip.kaspersky.com):

1. Descarga el feed de datos necesario (`IP_Reputation_Data_Feed.json`).
2. Coloca el archivo descargado en la carpeta `feeds/` del proyecto.

## 📂 Estructura del Proyecto

```plaintext
.
├── feeds/                              # Carpeta para datos de entrada y salida
│   ├── IP_Reputation_Data_Feed.json    # Archivo de entrada de ejemplo
│   └── ...                             # Otros archivos de datos
├── scripts/
│   ├── Python/
│   │   ├── filtrado_pais.py            # Script básico en español
│   │   ├── filtrado_pais_avanzado.py   # Script avanzado en español
│   │   ├── filter_country.py           # Script básico en inglés
│   │   ├── filter_country_advanced.py  # Script avanzado en inglés
│   └── PowerShell/
│       ├── FiltrarPorPais.ps1          # Script en español
│       ├── FilterByCountry.ps1         # Script en inglés
├── README.md                           # Documentación en español
├── README.en.md                        # Documentación en inglés
├── requirements.txt                    # Dependencias de Python
└── LICENSE                             # Licencia del proyecto
```

## 🚀 Uso de los Scripts

### Python

#### Ejecución Básica:

- **Propósito:** Filtrar datos por país usando el campo `ip_whois.country`.
- **Comando:**

  ```bash
  python scripts/Python/filtrado_pais.py
  ```

  - Configura el país en el script editando la variable `pais` (por defecto: `ES`).

#### Ejecución Avanzada:

- **Propósito:** Filtrar datos con modos avanzados (`geo`, `admin`, `combined`).
- **Comando:**

  ```bash
  python scripts/Python/filtrado_pais_avanzado.py --country ES --filter-mode geo
  ```

  - Cambia `--country` por el código ISO del país deseado.
  - Modifica el archivo de entrada usando `--input-file`.

#### Ejemplo:

Supongamos que tienes el archivo `IP_Reputation_Data_Feed.json` en la carpeta `feeds/` y quieres filtrar registros para España (`ES`):

```bash
python scripts/Python/filtrado_pais_avanzado.py --country ES --filter-mode combined --input-file feeds/IP_Reputation_Data_Feed.json
```

El archivo resultante se guardará automáticamente en `feeds/` con un nombre que incluye el país, el modo y un timestamp.

### PowerShell

#### Ejecución Interactiva:

- **Propósito:** Filtrar datos de manera interactiva en Windows.
- **Comando:**

  ```powershell
  .\scripts\PowerShell\FiltrarPorPais.ps1
  ```

  - Sigue las instrucciones para ingresar el país y elegir el modo de filtrado.

#### Ejemplo:

Coloca el archivo de entrada `IP_Reputation_Data_Feed.json` en la carpeta `feeds/`. Luego ejecuta:

```powershell
.\scripts\PowerShell\FiltrarPorPais.ps1
```

Sigue las instrucciones para filtrar por España (`ES`) y modo combinado (`combined`).

## 📝 Ejemplos de Uso

### JSON de Entrada

```json
[
    {
        "ip": "1.2.3.4",
        "threat_score": 97,
        "category": "malware-ESPAÑOL",
        "first_seen": "21.01.2015 00:00",
        "last_seen": "20.05.2016 03:48",
        "popularity": 1,
        "ip_geo": "es",
        "users_geo": "us"
    },
    {
        "ip": "1.2.3.5",
        "threat_score": 97,
        "category": "malware-ESPAÑOL",
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
        "category": "malware-ESPAÑOL",
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
        "category": "malware-ESPAÑOL",
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

### JSON Filtrado (Ejemplo para `country = ES` y `filter-mode = combined`)

```json
[
    {
        "ip": "1.2.3.6",
        "threat_score": 97,
        "category": "malware-ESPAÑOL",
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
        "category": "malware-ESPAÑOL",
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

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
