# Prueba de Concepto - Filtrado de Datos por Código de País

> **English version available:** See [README.en.md](README.en.md).
>
> **AVISO:** Este script se proporciona como una Prueba de Concepto (PoC) con fines educativos y demostrativos únicamente. No es una herramienta oficial de Kaspersky, ni ofrece garantías o soporte de funcionalidad. Úselo bajo su propio riesgo y siempre valide los resultados en su entorno.

Este proyecto incluye scripts en Python y PowerShell para filtrar registros de un archivo JSON de Threat Data Feeds del Kaspersky Threat Intelligence Portal, basado en un **código de país ISO 3166-1 alfa-2**. Estos scripts permiten identificar registros relevantes, generando un archivo filtrado con los resultados.

## 🎯 Características

### Scripts de Pipeline (Etapa 2 — Integración con API)

- **Flujo completo de extremo a extremo:** autenticar → descargar feed → filtrar por país → guardar resultado.
  - **Python:** `kaspersky_tdf.py` (inglés) y `kaspersky_tdf_es.py` (español).
  - **PowerShell:** `KasperskyTDF.ps1` (inglés) y `KasperskyTDF_ES.ps1` (español).
  - El token de API se carga de forma segura desde un archivo `.env` — nunca desde argumentos CLI.
  - Compatible con los tres modos de filtrado: `geo`, `admin`, `combined`.
  - Opción `--save-raw` para guardar también el feed sin filtrar.
  - Modo local alternativo mediante `--input-file` (no requiere token).

### Scripts Básicos (Etapa 1)

- **Filtrado Simple por País:**
  - **Python:** `filtrado_pais.py` (español) y `filter_country.py` (inglés).
  - Filtrado por registros donde el campo `ip_whois.country` coincide con el código ISO del país especificado.

### Scripts Avanzados (Etapa 1)

- **Modos de Filtrado Múltiples:**
  - **Python:** `filtrado_pais_avanzado.py` (español) y `filter_country_advanced.py` (inglés).
  - Modos: Geográfico (`geo`), Administrativo (`admin`), o Combinado (`combined`).
  - Soporte para parámetros CLI con `argparse`.

### Scripts en PowerShell (Etapa 1)

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

  Incluye: `pycountry`, `requests`, `python-dotenv`, `coverage`.

- **PowerShell:** Versión 5.1 o superior (recomendado PowerShell 7+).

## 📂 Estructura del Proyecto

```plaintext
.
├── feeds/                              # Carpeta para datos de entrada y salida
│   ├── IP_Reputation_Data_Feed.json    # Archivo de entrada de ejemplo
│   └── ...                             # Archivos de salida filtrados (generados automáticamente)
├── scripts/
│   ├── Python/
│   │   ├── kaspersky_tdf.py            # Script de pipeline en inglés (Etapa 2)
│   │   ├── kaspersky_tdf_es.py         # Script de pipeline en español (Etapa 2)
│   │   ├── filtrado_pais.py            # Script básico en español (Etapa 1)
│   │   ├── filtrado_pais_avanzado.py   # Script avanzado en español (Etapa 1)
│   │   ├── filter_country.py           # Script básico en inglés (Etapa 1)
│   │   ├── filter_country_advanced.py  # Script avanzado en inglés (Etapa 1)
│   └── PowerShell/
│       ├── KasperskyTDF.ps1            # Script de pipeline en inglés (Etapa 2)
│       ├── KasperskyTDF_ES.ps1         # Script de pipeline en español (Etapa 2)
│       ├── FiltrarPorPais.ps1          # Script en español (Etapa 1)
│       ├── FilterByCountry.ps1         # Script en inglés (Etapa 1)
├── .env.example                        # Plantilla de configuración del token de API
├── README.md                           # Documentación en español
├── README.en.md                        # Documentación en inglés
├── requirements.txt                    # Dependencias de Python
└── LICENSE                             # Licencia del proyecto
```

## 🔑 Configuración de la API (Etapa 2 — Scripts de Pipeline)

Los scripts de pipeline se autentican contra la [API del Kaspersky Threat Intelligence Portal](https://tip.kaspersky.com/Help/api/?specId=tip-feeds-api) mediante un token de API almacenado en un archivo `.env`.

### Paso 1 — Obtener el token de API

1. Inicia sesión en [https://tip.kaspersky.com](https://tip.kaspersky.com).
2. Ve a **Configuración de cuenta → Tokens de API**.
3. Selecciona un período de validez (máximo 1 año) y haz clic en **Solicitar**.
4. Copia el token generado.

> Debes aceptar los Términos y Condiciones del portal antes de poder acceder a la API.

### Paso 2 — Crear el archivo `.env`

```bash
cp .env.example .env
```

Edita `.env` e introduce tus valores reales:

```ini
KASPERSKY_TIP_TOKEN=tu_token_de_api_aqui
KASPERSKY_TIP_BASE_URL=https://tip.kaspersky.com/api/feeds/
KASPERSKY_TIP_FEED_ENDPOINT=ip_reputation
KASPERSKY_TIP_LIMIT=0
```

| Variable | Descripción |
| --- | --- |
| `KASPERSKY_TIP_TOKEN` | Tu token de API (requerido) |
| `KASPERSKY_TIP_BASE_URL` | URL base de la API (no modificar salvo indicación) |
| `KASPERSKY_TIP_FEED_ENDPOINT` | Nombre del endpoint del feed (ajustar si es necesario — ver nota) |
| `KASPERSKY_TIP_LIMIT` | Máximo de registros a descargar (`0` = feed completo) |

> **Nota sobre el nombre del endpoint:** El endpoint exacto para el feed de Reputación de IP puede variar según la suscripción. Si recibes un error `404`, consulta la [especificación OpenAPI](https://tip.kaspersky.com/Help/api/?specId=tip-feeds-api) para obtener el nombre correcto y actualiza `KASPERSKY_TIP_FEED_ENDPOINT` en tu `.env`.
>
> **Seguridad:** El archivo `.env` está excluido del control de versiones mediante `.gitignore`. Nunca lo confirmes en el repositorio. El token de API nunca se pasa como argumento CLI ni se escribe en los registros.

## 🚀 Uso de los Scripts

### Scripts de Pipeline (Etapa 2)

#### Pipeline Python

**Pipeline completo con API (interactivo — solicita país y modo):**

```bash
python scripts/Python/kaspersky_tdf_es.py
```

**Pipeline completo con argumentos CLI:**

```bash
python scripts/Python/kaspersky_tdf_es.py --country ES --filter-mode combined
```

**Guardar también el feed sin filtrar:**

```bash
python scripts/Python/kaspersky_tdf_es.py --country ES --save-raw
```

**Modo local alternativo (no requiere token):**

```bash
python scripts/Python/kaspersky_tdf_es.py --input-file feeds/IP_Reputation_Data_Feed.json --country ES
```

**Sobreescribir endpoint o límite para una sola ejecución:**

```bash
python scripts/Python/kaspersky_tdf_es.py --country ES --feed-endpoint dangerous_ips --limit 10000
```

**Argumentos disponibles:**

| Argumento | Descripción | Por defecto |
| --- | --- | --- |
| `--country` | Código ISO 3166-1 alpha-2 (ej. `ES`) | Se solicita de forma interactiva |
| `--filter-mode` | `geo`, `admin` o `combined` | Se solicita interactivamente (por defecto: `combined`) |
| `--output-file` | Ruta del archivo de salida | Generado automáticamente con marca de tiempo |
| `--save-raw` | Guarda también el feed sin filtrar | Desactivado |
| `--input-file` | Usa un archivo JSON local en lugar de la API | — |
| `--limit` | Sobreescribe `KASPERSKY_TIP_LIMIT` para esta ejecución | Desde `.env` |
| `--feed-endpoint` | Sobreescribe `KASPERSKY_TIP_FEED_ENDPOINT` para esta ejecución | Desde `.env` |

#### Pipeline PowerShell

**Pipeline completo con API (interactivo):**

```powershell
.\scripts\PowerShell\KasperskyTDF_ES.ps1
```

**Con parámetros:**

```powershell
.\scripts\PowerShell\KasperskyTDF_ES.ps1 -Country ES -FilterMode combined
```

**Guardar también el feed sin filtrar:**

```powershell
.\scripts\PowerShell\KasperskyTDF_ES.ps1 -Country ES -SaveRaw
```

**Modo local alternativo:**

```powershell
.\scripts\PowerShell\KasperskyTDF_ES.ps1 -InputFile feeds\IP_Reputation_Data_Feed.json -Country ES
```

---

### Scripts Básicos y Avanzados (Etapa 1)

#### Python (Etapa 1)

**Ejecución básica** — filtra usando el campo `ip_whois.country`:

```bash
python scripts/Python/filtrado_pais.py
```

Configura el país editando la variable `pais` en el script (por defecto: `ES`).

**Ejecución avanzada** — múltiples modos de filtrado por CLI:

```bash
python scripts/Python/filtrado_pais_avanzado.py --country ES --filter-mode combined --input-file feeds/IP_Reputation_Data_Feed.json
```

El archivo resultante se guarda automáticamente en `feeds/` con un nombre que incluye el país, el modo y una marca de tiempo.

#### PowerShell (Etapa 1)

**Ejecución interactiva:**

```powershell
.\scripts\PowerShell\FiltrarPorPais.ps1
```

Coloca `IP_Reputation_Data_Feed.json` en la carpeta `feeds/` y sigue las instrucciones para seleccionar el país y el modo de filtrado.

## 📥 Preparación de Datos

### Opción A — Pipeline con API (Etapa 2, recomendado)

Configura el archivo `.env` según la sección [Configuración de la API](#-configuración-de-la-api-etapa-2--scripts-de-pipeline) y ejecuta el script de pipeline directamente. No se requiere descarga manual.

### Opción B — Descarga Manual (Etapa 1)

1. Inicia sesión en [Kaspersky Threat Intelligence Portal](https://tip.kaspersky.com).
2. Descarga el feed de datos necesario (`IP_Reputation_Data_Feed.json`).
3. Coloca el archivo descargado en la carpeta `feeds/` del proyecto.
4. Ejecuta un script de Etapa 1 con `--input-file feeds/IP_Reputation_Data_Feed.json`.

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

### JSON Filtrado (country = ES, filter-mode = combined)

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
