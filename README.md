# Prueba de Concepto - Filtrado de IP Reputation por País

> **English version available:** For the English version of this documentation, see [README.en.md](./EN/README.en.md).

> **AVISO:** Este script se proporciona como una Prueba de Concepto (PoC) con fines educativos y demostrativos únicamente. No es una herramienta oficial de Kaspersky, ni ofrece garantías o soporte de funcionalidad. Úselo bajo su propio riesgo y siempre valide los resultados en su entorno.

Este proyecto permite filtrar registros de un archivo JSON the Threat DataFeeds de Kaspersky Threat Intelligence Portal, que contiene datos de reputación de IPs en base al **código de país** especificado en formato ISO 3166-1 alfa-2. El objetivo principal es procesar grandes conjuntos de datos, identificar registros específicos por país, y generar un archivo filtrado con los resultados.

## 🎯 Características

- **Filtro Personalizable**: Filtra registros de un archivo JSON por país usando un código ISO 3166-1 alfa-2 (por ejemplo, `ES` para España, `US` para Estados Unidos).
- **Manejo de Errores**: Soporte para archivos inexistentes, JSON malformados y estructuras inesperadas.
- **Resultados Enriquecidos**: Incluye el nombre del país en el archivo de salida, junto con un timestamp para mayor trazabilidad.
- **Carpeta de Trabajo `feeds`**: Todos los archivos de entrada y salida se procesan dentro de la carpeta `feeds`.
- **Filtrado Avanzado**: Capacidad para filtrar por:
  - **Ubicación Geográfica**: Basado en el campo `ip_geo`.
  - **Ubicación Administrativa**: Basado en el campo `ip_whois.country`.
  - **Combinado**: Filtro que considera tanto geolocalización como registros administrativos.

## 🔧 Requisitos

- **Python**: 3.8 o superior.
- **Dependencias**:
  - `pycountry`: Para obtener el nombre del país basado en su código ISO.
  - `unittest`: Biblioteca estándar para ejecutar tests.

Puedes instalar las dependencias con el siguiente comando:

```bash
pip install -r requirements.txt
```

Contenido del archivo `requirements.txt`:

```**Dependencias**
coverage==7.6.10
pycountry==22.3.5
```

## 📥 Descarga de Datos

### Datos Requeridos

Este proyecto utiliza los **Threat DataFeeds de Kaspersky** para procesar y filtrar registros por país. Actualmente, la descarga de los datos debe realizarse **manualmente** desde el portal de Kaspersky Threat Intelligence, siempre y cuando tengas las licencias necesarias habilitadas.

**Pasos para la descarga:**

1. Accede a [Kaspersky Threat Intelligence Portal](https://tip.kaspersky.com).
2. Inicia sesión con tus credenciales.
3. Descarga el feed de datos correspondiente (por ejemplo, `IP_Reputation_Data_Feed.json`).
4. Coloca el archivo descargado en la carpeta `feeds` del proyecto.
5. Modifica la variable `fichero_entrada` en el fichero `filtrado_pais.py` o utiliza la opción `--input-file` en el script avanzado.

## 🗋 Estructura del Proyecto

```plaintext
.
├── EN/
│   ├── scripts/
│   │   ├── feeds/
│   │   │   ├── IP_Reputation_Data_Feed_****.json   # Archivo de entrada de ejemplo
│   │   │   └── ...                                 # Otros archivos de prueba
│   │   ├── filter_by_country.py                   # Script principal en inglés
│   │   └── test_filter_by_country.py              # Tests automáticos en inglés
│   ├── README.en.md                                # Documentación en inglés
├── ES/
│   ├── scripts/
│   │   ├── feeds/
│   │   │   ├── IP_Reputation_Data_Feed_****.json   # Archivo de entrada de ejemplo
│   │   │   └── ...                                 # Otros archivos de prueba
│   │   ├── filtrado_pais.py                       # Script principal en español
│   │   ├── filtrado_pais_avanzado.py              # Script avanzado en español
│   │   └── test_filtrado_pais.py                  # Tests automáticos en español
│   ├── README.md                                   # Documentación en español
├── .gitignore
├── LICENSE
└── requirements.txt
```

## Uso

### 1. Preparar la Carpeta `feeds`

Crea una carpeta llamada `feeds` en el directorio correspondiente (`EN/scripts/feeds` o `ES/scripts/feeds`) y coloca el archivo de entrada JSON dentro de esta. Por ejemplo:

```plaintext
EN/scripts/feeds/
└── IP_Reputation_Data_Feed_****.json
```

```plaintext
ES/scripts/feeds/
└── IP_Reputation_Data_Feed_****.json
```

### 2. Ejecutar el Script Principal

Ejecuta el script principal para filtrar los registros por un código de país específico:

```bash
python EN/scripts/filter_by_country.py
```

O, para la versión en español:

```bash
python ES/scripts/filtrado_pais.py
```

Para usar el script avanzado que incluye modos de filtrado (`geo`, `admin` o `combined`):

```bash
python ES/scripts/filtrado_pais_avanzado.py --country ES --filter-mode geo --input-file ./ES/scripts/feeds/IP_Reputation_Data_Feed.json
```

El archivo de salida se guardará en la carpeta `feeds` con un nombre que incluye el país, el modo de filtrado y un timestamp, por ejemplo:

```plaintext
feeds/IP_Reputation_filtrado_ES_geo_*****.json
```

### 3. Modificar el Código de País

Puedes cambiar el código de país utilizando el argumento `--country`. Por ejemplo:

```bash
python ES/scripts/filtrado_pais_avanzado.py --country US --filter-mode combined --input-file ./ES/scripts/feeds/IP_Reputation_Data_Feed.json
```

## Tests

Este proyecto incluye una suite de tests automáticos para validar su funcionamiento. Los tests están ubicados en los archivos `test_filtrado_pais.py` (español) y `test_filter_by_country.py` (inglés) y cubren casos como:

- Archivos con registros válidos.
- Archivos sin coincidencias.
- Archivos JSON vacíos o malformados.
- Archivos inexistentes.

### Ejecutar los Tests

Para ejecutar los tests, usa el siguiente comando:

```bash
python -m unittest EN/scripts/test_filter_by_country.py
```

O para la versión en español:

```bash
python -m unittest ES/scripts/test_filtrado_pais.py
```

Salida esperada si todo funciona correctamente:

```plaintext
Total registros procesados: 4
Registros ignorados: 2
Se encontraron 2 registros con country = 'ES' (Spain).
Registros filtrados guardados en: feeds/test_filtered_feed.json
...
Ran 5 tests in 0.018s

OK
```

## Ejemplo de JSON de Entrada

El archivo `IP_Reputation_Data_Feed.json` debe tener una estructura similar a la siguiente:

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

## Ejemplo de JSON Filtrado

Un archivo filtrado para `country = 'ES'` tendría la siguiente estructura:

```json
[
  ...
    {"ip_whois": {"country": "ES", "org": "ISP España"}},
    {"ip_whois": {"country": "ES", "org": "ISP España 2"}},
  ...
]
```

## Manejo de Errores

El script maneja los siguientes casos de error:

1. **Archivo Inexistente**:
   - Mensaje: `Error: El archivo 'archivo_inexistente.json' no se encuentra.`
2. **JSON Malformado**:
   - Mensaje: `Error: El archivo no es un JSON válido.`
3. **Estructura Inválida**:
   - Mensaje: `Advertencia: Se encontró un registro con formato incorrecto y se omitió.`

## 🚀 Próximos Pasos

A continuación, algunas ideas para mejorar y extender este proyecto: (en proceso...)

### 1. Cobertura Geográfica vs. Administrativa

- Implementar la posibilidad de usar **`ip_geo`** o **`ip_whois.country`** como filtros separados o combinados (`OR` o `AND`).
- Añadir una clasificación detallada en los resultados, como:
  - **Geográfica**: IPs relacionadas con España por geolocalización (`ip_geo`).
  - **Administrativa**: IPs relacionadas con España por registros administrativos (`ip_whois.country`).
  - **Ambos**: IPs que cumplen ambos criterios.

### 2. Soporte para Más Formatos de Entrada y Salida

- **Entrada**:
  - Agregar soporte para otros formatos como CSV, Excel o bases de datos.
  - Permitir importar datos desde APIs o servicios web.
- **Salida**:
  - Generar reportes en formatos como CSV o Excel.
  - Exportar datos filtrados a una base de datos relacional (como PostgreSQL o MySQL).

### 3. Optimización del Filtro

- **Mejoras en el Filtro**:
  - Implementar filtros adicionales, como por rango de IPs (`192.168.x.x`), organización, o tipo de conexión.
  - Añadir soporte para reglas complejas usando expresiones regulares.
- **Velocidad**:
  - Usar técnicas de procesamiento en paralelo para manejar grandes volúmenes de datos.

### 4. Interfaz de Usuario

- **Línea de Comandos**:
  - Integrar `argparse` para que el usuario pueda especificar el código de país, archivo de entrada y archivo de salida directamente desde la terminal.
- **Interfaz Gráfica**:
  - Crear una interfaz gráfica básica usando bibliotecas como `tkinter` o `PyQt`.

### 5. Detección de Anomalías

- Identificar y marcar IPs con discrepancias entre geolocalización (`ip_geo`) y registro administrativo (`ip_whois.country`).
- Generar alertas para IPs maliciosas o sospechosas basadas en listas negras (blacklists) públicas.

### 6. Análisis Visual

- Crear gráficos y estadísticas con bibliotecas como `matplotlib` o `Plotly` para mostrar:
  - Distribución geográfica de las IPs.
  - Organización o proveedor con más registros.
- Generar dashboards interactivos con **Streamlit** para analizar los datos.

### 7. Documentación y Automatización

- **Mejorar la Documentación**:
  - Crear una guía para contribuir al proyecto.
  - Agregar ejemplos de uso más avanzados.
- **Automatización**:
  - Crear un script de instalación o configuración para facilitar el despliegue en nuevos entornos.

---

### ¿Más Ideas?

Si tienes otras ideas o sugerencias, ¡no dudes en contribuir o abrir un issue en el repositorio! 😊

## Autor

Desarrollado por @pedrojorgeviana, si tienes preguntas o sugerencias, no dudes en contactarme.

## Nota sobre el uso de IA

Este proyecto fue desarrollado con la ayuda de herramientas de inteligencia artificial (IA) como ChatGPT. Todo el contenido generado ha sido supervisado, adaptado y validado por el autor para garantizar su calidad y funcionalidad.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
