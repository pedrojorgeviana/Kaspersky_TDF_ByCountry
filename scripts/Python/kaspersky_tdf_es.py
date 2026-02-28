# Kaspersky TDF ByCountry — Pipeline Completo (Español)
# Autenticar → Descargar feed de Reputación de IP → Filtrar por país → Guardar resultado.
#
# AVISO LEGAL: Este script se proporciona como Prueba de Concepto (PoC) únicamente con
# fines educativos y de demostración. No es una herramienta oficial de Kaspersky, ni
# conlleva garantías de funcionalidad o soporte.
# Úselo bajo su propia responsabilidad y valide siempre los resultados en su entorno.

import argparse
import json
import os
import sys
from datetime import datetime

import pycountry
import requests
from dotenv import load_dotenv

NOMBRE_FEED = "IP_Reputation"
URL_BASE_DEFECTO = "https://tip.kaspersky.com/api/feeds/"
ENDPOINT_DEFECTO = "ip_reputation"


# ---------------------------------------------------------------------------
# Aviso legal
# ---------------------------------------------------------------------------

def mostrar_aviso():
    print(
        "\n*** AVISO LEGAL ***\n"
        "Este script se proporciona como Prueba de Concepto (PoC) únicamente con fines "
        "educativos y de demostración.\n"
        "No es una herramienta oficial de Kaspersky, ni conlleva garantías de "
        "funcionalidad o soporte.\n"
        "Úselo bajo su propia responsabilidad y valide siempre los resultados en su entorno.\n"
    )


# ---------------------------------------------------------------------------
# Argumentos de línea de comandos
# ---------------------------------------------------------------------------

def parsear_argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "Kaspersky TDF ByCountry — pipeline completo: "
            "descarga el feed de Reputación de IP, filtra por país y guarda el resultado."
        )
    )
    parser.add_argument(
        "--country",
        type=str,
        default="",
        help="Código de país ISO 3166-1 alpha-2 (ej. ES). Se solicita de forma interactiva si se omite.",
    )
    parser.add_argument(
        "--filter-mode",
        type=str,
        choices=["geo", "admin", "combined"],
        default="",
        help="Modo de filtrado: geo, admin o combined (por defecto: combined).",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Ruta del archivo de salida. Se genera automáticamente con marca de tiempo si se omite.",
    )
    parser.add_argument(
        "--save-raw",
        action="store_true",
        help="Guarda también el feed sin filtrar en feeds/IP_Reputation_raw_TIMESTAMP.json.",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default=None,
        help=(
            "MODO LOCAL: lee desde este archivo JSON local en lugar de llamar a la API. "
            "Cuando se especifica, no se requiere token de API."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Sobreescribe KASPERSKY_TIP_LIMIT para esta ejecución (0 = sin límite).",
    )
    parser.add_argument(
        "--feed-endpoint",
        type=str,
        default=None,
        help="Sobreescribe KASPERSKY_TIP_FEED_ENDPOINT para esta ejecución.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Configuración (secretos desde .env únicamente — nunca desde argumentos CLI)
# ---------------------------------------------------------------------------

def cargar_configuracion():
    load_dotenv()
    token = os.environ.get("KASPERSKY_TIP_TOKEN", "").strip()
    url_base = os.environ.get("KASPERSKY_TIP_BASE_URL", URL_BASE_DEFECTO).strip()
    endpoint = os.environ.get("KASPERSKY_TIP_FEED_ENDPOINT", ENDPOINT_DEFECTO).strip()
    limite_str = os.environ.get("KASPERSKY_TIP_LIMIT", "0").strip()
    try:
        limite = int(limite_str)
    except ValueError:
        limite = 0
    return {
        "token": token,
        "url_base": url_base,
        "endpoint": endpoint,
        "limite": limite,
    }


def validar_token_presente(token):
    if not token:
        print("Error: KASPERSKY_TIP_TOKEN no está configurado.")
        print("  1. Copie .env.example a .env")
        print("  2. Establezca KASPERSKY_TIP_TOKEN con su token de API")
        print("  3. Obtenga un token en: https://tip.kaspersky.com (Configuración de cuenta)")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Cliente HTTP (modo API)
# ---------------------------------------------------------------------------

def crear_sesion_api(token):
    sesion = requests.Session()
    sesion.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    })
    sesion.verify = True  # Verificación de certificado SSL siempre activada
    return sesion


def construir_url_feed(url_base, endpoint, limite):
    if not url_base.startswith("https://"):
        print("Error: KASPERSKY_TIP_BASE_URL debe usar HTTPS. Revise su archivo .env.")
        sys.exit(1)
    url = f"{url_base.rstrip('/')}/{endpoint}"
    if limite and limite > 0:
        url += f"?limit={limite}"
    return url


def manejar_error_api(respuesta):
    estado = respuesta.status_code
    mensajes = {
        401: (
            "Autenticación fallida. Verifique KASPERSKY_TIP_TOKEN en su archivo .env. "
            "Los tokens expiran tras 1 año — solicite uno nuevo en https://tip.kaspersky.com."
        ),
        403: (
            "Acceso denegado. Es posible que su token no tenga permisos para este feed. "
            "Compruebe su suscripción en el portal Kaspersky TIP."
        ),
        404: (
            "Endpoint del feed no encontrado. Verifique KASPERSKY_TIP_FEED_ENDPOINT en su .env. "
            "Consulte la especificación OpenAPI en https://tip.kaspersky.com/Help/api/?specId=tip-feeds-api"
        ),
        429: "Límite de peticiones superado. Espere antes de volver a intentarlo.",
        500: "Error interno del servidor de Kaspersky TIP API. Inténtelo más tarde.",
        502: "Kaspersky TIP API temporalmente no disponible (502). Inténtelo en unos minutos.",
        503: "Kaspersky TIP API temporalmente no disponible (503). Inténtelo en unos minutos.",
        504: "Tiempo de espera en la puerta de enlace de Kaspersky TIP API (504). Inténtelo en unos minutos.",
    }
    msg = mensajes.get(estado, f"Error HTTP inesperado {estado} desde Kaspersky TIP API.")
    print(f"Error: {msg}")
    sys.exit(1)


def resolver_redireccion_descarga(sesion, url_descarga):
    try:
        respuesta = sesion.get(url_descarga, timeout=(10, 300))
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.HTTPError:
        manejar_error_api(respuesta)
    except requests.exceptions.SSLError as e:
        print(f"Error: Verificación de certificado SSL fallida durante la descarga: {e}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Tiempo de espera agotado en la descarga. El archivo puede ser muy grande. Inténtelo de nuevo.")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"Error: No se pudo conectar a la URL de descarga: {e}")
        sys.exit(1)


def obtener_feed(sesion, url):
    try:
        respuesta = sesion.get(url, timeout=(10, 60))
        respuesta.raise_for_status()
    except requests.exceptions.HTTPError:
        manejar_error_api(respuesta)
    except requests.exceptions.SSLError as e:
        print(f"Error: Verificación de certificado SSL fallida: {e}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Tiempo de espera agotado. Compruebe su conexión de red e inténtelo de nuevo.")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"Error: No se pudo conectar a Kaspersky TIP API: {e}")
        sys.exit(1)

    datos = respuesta.json()

    if isinstance(datos, list):
        return datos  # Opción A: la API devolvió los registros directamente

    if isinstance(datos, dict):
        # Opción B: la API devolvió un objeto con URL de descarga
        for clave in ("download_url", "url", "link", "data_url"):
            if clave in datos:
                print("  Resolviendo enlace de descarga desde la respuesta de la API...")
                return resolver_redireccion_descarga(sesion, datos[clave])
        raise ValueError(
            f"Formato de respuesta inesperado. Claves en la respuesta: {list(datos.keys())}"
        )

    raise ValueError(
        f"Tipo de respuesta inesperado: {type(datos).__name__}. Se esperaba un array JSON."
    )


# ---------------------------------------------------------------------------
# Validación del código de país y prompts interactivos
# ---------------------------------------------------------------------------

def validar_codigo_pais(codigo_pais):
    if len(codigo_pais) != 2 or not codigo_pais.isalpha():
        raise ValueError(
            f"Código de país inválido: '{codigo_pais}'. "
            "Debe ser un código de dos letras ISO 3166-1 alpha-2 (ej. ES, US, DE)."
        )
    if not pycountry.countries.get(alpha_2=codigo_pais.upper()):
        raise ValueError(
            f"El código '{codigo_pais}' no es un código ISO 3166-1 alpha-2 válido."
        )


def normalizar_codigo_pais(codigo_pais):
    return codigo_pais.upper()


def solicitar_pais_si_falta(pais):
    if pais:
        return pais
    while True:
        codigo = input("Introduzca el código de país (ISO 3166-1 alpha-2, ej. ES): ").strip()
        try:
            validar_codigo_pais(codigo)
            return codigo
        except ValueError as e:
            print(f"  {e}")


def solicitar_modo_si_falta(modo):
    if modo:
        return modo
    while True:
        valor = input(
            "Seleccione el modo de filtrado [geo / admin / combined] (pulse Intro para combined): "
        ).strip().lower()
        if not valor:
            return "combined"
        if valor in ("geo", "admin", "combined"):
            return valor
        print("  Modo no válido. Elija entre: geo, admin, combined.")


# ---------------------------------------------------------------------------
# Carga de archivo local (modo alternativo / compatibilidad hacia atrás)
# ---------------------------------------------------------------------------

def cargar_archivo_entrada(archivo_entrada):
    if not os.path.exists(archivo_entrada):
        raise FileNotFoundError(f"Archivo de entrada no encontrado: {archivo_entrada}")
    try:
        with open(archivo_entrada, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Formato JSON inválido en el archivo de entrada: {e}")
    except PermissionError as e:
        raise PermissionError(f"Permiso denegado al leer: {archivo_entrada}. Detalles: {e}")
    if not datos:
        raise ValueError("El archivo de entrada está vacío o no contiene registros.")
    return datos


# ---------------------------------------------------------------------------
# Filtrado (lógica idéntica a filtrado_pais_avanzado.py)
# ---------------------------------------------------------------------------

def filtrar_geo(datos, pais):
    normalizado = pais.lower()
    return [entrada for entrada in datos if entrada.get("ip_geo", "").lower() == normalizado]


def filtrar_admin(datos, pais):
    normalizado = pais.upper()
    return [
        entrada for entrada in datos
        if entrada.get("ip_whois", {}).get("country", "").upper() == normalizado
    ]


def filtrar_combinado(datos, pais):
    geo = pais.lower()
    adm = pais.upper()
    return [
        entrada for entrada in datos
        if entrada.get("ip_geo", "").lower() == geo
        or entrada.get("ip_whois", {}).get("country", "").upper() == adm
    ]


def aplicar_filtro(datos, pais, modo):
    if modo == "geo":
        return filtrar_geo(datos, pais)
    elif modo == "admin":
        return filtrar_admin(datos, pais)
    elif modo == "combined":
        return filtrar_combinado(datos, pais)
    raise ValueError(f"Modo de filtrado desconocido: '{modo}'. Use geo, admin o combined.")


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------

def asegurar_directorio_salida(archivo_salida):
    directorio = os.path.dirname(archivo_salida)
    if directorio and not os.path.exists(directorio):
        try:
            os.makedirs(directorio)
        except PermissionError as e:
            raise PermissionError(
                f"Permiso denegado al crear el directorio: {directorio}. Detalles: {e}"
            )


def generar_nombre_archivo_salida(pais, modo):
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"feeds/{NOMBRE_FEED}_{pais}_{modo}_{marca_tiempo}.json"


def generar_nombre_archivo_raw():
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"feeds/{NOMBRE_FEED}_raw_{marca_tiempo}.json"


def guardar_archivo_salida(archivo_salida, datos):
    try:
        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except PermissionError as e:
        raise PermissionError(f"Permiso denegado al escribir en: {archivo_salida}. Detalles: {e}")


def mostrar_resumen(origen, pais, modo, total, coincidencias, archivo_salida, archivo_raw=None):
    objeto_pais = pycountry.countries.get(alpha_2=pais)
    nombre_pais = objeto_pais.name if objeto_pais else pais
    print("\n--- Resumen ---")
    print(f"  Origen          : {origen}")
    print(f"  País            : {pais} ({nombre_pais})")
    print(f"  Modo de filtrado: {modo}")
    print(f"  Registros totales: {total}")
    print(f"  Coincidencias   : {coincidencias}")
    print(f"  Filtrados       : {total - coincidencias}")
    print(f"  Resultado en    : {archivo_salida}")
    if archivo_raw:
        print(f"  Feed sin filtrar: {archivo_raw}")
    if coincidencias == 0:
        print("\n  [!] Ningún registro coincide. Pruebe con otro país o modo de filtrado.")
    print()


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main():
    mostrar_aviso()
    args = parsear_argumentos()

    try:
        modo_local = bool(args.input_file)

        # Modo API: cargar configuración y validar token antes de cualquier otra acción
        if not modo_local:
            config = cargar_configuracion()
            validar_token_presente(config["token"])
            # Aplicar sobreescrituras de la línea de comandos (solo endpoint y límite)
            if args.feed_endpoint:
                config["endpoint"] = args.feed_endpoint
            if args.limit is not None:
                config["limite"] = args.limit

        # Resolver país y modo de filtrado (desde argumentos CLI o prompts interactivos)
        entrada_pais = solicitar_pais_si_falta(args.country)
        validar_codigo_pais(entrada_pais)
        pais = normalizar_codigo_pais(entrada_pais)
        modo = solicitar_modo_si_falta(args.filter_mode)

        # Obtener o cargar datos
        archivo_raw = None
        if modo_local:
            print(f"Cargando archivo local: {args.input_file}")
            datos = cargar_archivo_entrada(args.input_file)
            origen = f"Archivo local: {args.input_file}"
        else:
            url = construir_url_feed(config["url_base"], config["endpoint"], config["limite"])
            print("Descargando feed desde Kaspersky TIP API...")
            sesion = crear_sesion_api(config["token"])
            datos = obtener_feed(sesion, url)
            origen = f"Endpoint API: {config['endpoint']}"
            print(f"  Descargados {len(datos)} registros.")

            if args.save_raw:
                archivo_raw = generar_nombre_archivo_raw()
                asegurar_directorio_salida(archivo_raw)
                guardar_archivo_salida(archivo_raw, datos)
                print(f"  Feed sin filtrar guardado en: {archivo_raw}")

        # Filtrar
        print(f"Filtrando por país '{pais}' con modo '{modo}'...")
        filtrados = aplicar_filtro(datos, pais, modo)

        # Guardar resultado
        archivo_salida = args.output_file or generar_nombre_archivo_salida(pais, modo)
        asegurar_directorio_salida(archivo_salida)
        guardar_archivo_salida(archivo_salida, filtrados)

        mostrar_resumen(origen, pais, modo, len(datos), len(filtrados), archivo_salida, archivo_raw)

    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Se produjo un error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
