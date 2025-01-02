# Descripción de la estructura del IP_Reputation Threat Data Feed (Datos Anonimizados)

El archivo `IP_Reputation_Data_Feed_*.json` contiene una lista de registros en formato JSON. Cada registro representa información detallada sobre la reputación de una dirección IP, incluyendo datos sobre actividad maliciosa, geolocalización, popularidad, y metadatos administrativos.

---

## Estructura General

El archivo está estructurado como una lista de objetos JSON, donde cada objeto incluye los siguientes campos:

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

## Descripción de los Campos

1. **`id`** (Número Entero):
   - Identificador único del registro en el feed.

2. **`ip`** (Cadena):
   - Dirección IP objetivo (IPv4 o IPv6). En este ejemplo, usamos una IP ficticia dentro del rango reservado para documentación (`203.0.113.0/24`).

3. **`threat_score`** (Número Entero):
   - Puntaje de amenaza asignado a la IP. Valores más altos indican mayor peligrosidad.
   - Rango: 0 a 100.

4. **`category`** (Cadena):
   - Clasificación de la actividad maliciosa asociada con la IP.
   - Ejemplo: `"phishing"`, `"botnet_cnc"`, `"spam"`, `"malware_hosting"`.

5. **`first_seen`** y **`last_seen`** (Cadenas):
   - Tiempos de la primera y última detección de actividad maliciosa, en formato `"DD.MM.YYYY HH:MM"`.

6. **`popularity`** (Número Entero):
   - Indicador del nivel de popularidad o frecuencia de la IP.
   - Rango: 0 (baja) a 5 (alta).

7. **`ip_geo`** (Cadena):
   - Código del país (ISO 3166-1 alfa-2) donde está físicamente localizada la IP. En este ejemplo: `us` (Estados Unidos).

8. **`users_geo`** (Cadena):
   - Lista separada por comas de códigos de países (ISO 3166-1 alfa-2) donde se detectaron usuarios afectados.

9. **`ip_whois`** (Objeto):
   - Información administrativa sobre el rango de IP asociado, según registros WHOIS.
     - **`net_range`**: Rango de direcciones IP ficticio.
     - **`net_name`**: Nombre ficticio de la red.
     - **`descr`**: Descripción ficticia del rango.
     - **`created`** y **`updated`**: Fechas ficticias de creación y actualización del registro WHOIS.
     - **`country`**: Código de país ficticio.
     - **`contact_owner_name`**: Nombre ficticio del propietario.
     - **`contact_owner_code`**: Código ficticio del propietario.

---

### Ejemplo de Registro Anonimizado

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

## Notas Importantes

1. **Datos Ficticios:**
   - Todas las direcciones IP y datos de registros han sido generados siguiendo convenciones estándar para documentación (por ejemplo, el uso de `203.0.113.0/24` y `198.51.100.0/24` como rangos reservados).

2. **Estructura Respetada:**
   - Aunque los datos son ficticios, mantienen la estructura y semántica del feed original.

3. **Referencias:**
   - Más información sobre el feed puede consultarse en la documentación oficial: [Kaspersky Threat Intelligence - IP Reputation Feed](https://tip.kaspersky.com/Help/TIDF/en-US/IpReputationFeed.htm).
