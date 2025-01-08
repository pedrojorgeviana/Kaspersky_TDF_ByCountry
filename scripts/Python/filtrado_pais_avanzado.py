# Prueba de Concepto (PoC) para Filtrado Avanzado por Código de País
# Este script demuestra la viabilidad de filtrar datos de un archivo JSON predescargado basado en datos de reputación de IP.
# AVISO: Este script se proporciona como una Prueba de Concepto (PoC) con fines educativos y demostrativos únicamente.
# No es una herramienta oficial de Kaspersky, ni ofrece garantías o soporte de funcionalidad.
# Úselo bajo su propio riesgo y siempre valide los resultados en su entorno.

import argparse
import json
import os
from datetime import datetime
import pycountry

def mostrar_aviso():
    """
    Muestra un mensaje de aviso cada vez que se ejecuta el script.
    """
    aviso = (
        "\n*** AVISO ***\n"
        "Este script se proporciona como una Prueba de Concepto (PoC) con fines educativos y demostrativos únicamente.\n"
        "No es una herramienta oficial de Kaspersky, ni ofrece garantías o soporte de funcionalidad.\n"
        "Úselo bajo su propio riesgo y siempre valide los resultados en su entorno.\n"
    )
    print(aviso)

def parsear_argumentos():
    """
    Analiza los argumentos de la línea de comandos para el script.
    """
    parser = argparse.ArgumentParser(description="Filtrado avanzado basado en país para datos de reputación de IP.")
    parser.add_argument(
        "--country",
        type=str,
        required=True,
        help="Código de país ISO 3166-1 alfa-2 para filtrar (por ejemplo, ES para España).",
    )
    parser.add_argument(
        "--filter-mode",
        type=str,
        choices=["geo", "admin", "combined"],
        default="combined",
        help="Modo de filtrado: 'geo', 'admin' o 'combined' (por defecto: combined).",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default="./feeds/IP_Reputation_Data_Feed.json",
        help="Ruta al archivo JSON de entrada (por defecto: ./feeds/IP_Reputation_Data_Feed.json).",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Ruta al archivo JSON de salida. Si no se especifica, se generará un nombre automáticamente.",
    )
    return parser.parse_args()

def validar_codigo_pais(codigo_pais):
    """
    Valida el código de país.
    """
    if len(codigo_pais) != 2 or not codigo_pais.isalpha():
        raise ValueError(f"Código de país inválido: {codigo_pais}. Debe ser un código ISO 3166-1 alfa-2 de dos letras.")

    if not pycountry.countries.get(alpha_2=codigo_pais.upper()):
        raise ValueError(f"El código de país '{codigo_pais}' no es válido según ISO 3166-1 alfa-2.")

def normalizar_codigo_pais(codigo_pais):
    """
    Normaliza el código de país a mayúsculas.
    """
    return codigo_pais.upper()

def cargar_archivo_entrada(archivo_entrada):
    """
    Carga los datos JSON desde el archivo de entrada.
    """
    if not os.path.exists(archivo_entrada):
        raise FileNotFoundError(f"Archivo de entrada no encontrado: {archivo_entrada}")

    try:
        with open(archivo_entrada, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Formato JSON inválido en el archivo de entrada: {e}")
    except PermissionError as e:
        raise PermissionError(f"Permiso denegado al acceder al archivo: {archivo_entrada}. Detalles: {e}")

    if not datos:
        raise ValueError("El archivo de entrada está vacío o no contiene registros.")

    return datos

def asegurar_directorio_salida(archivo_salida):
    """
    Asegura que el directorio de salida exista, lo crea si es necesario.
    """
    directorio_salida = os.path.dirname(archivo_salida)
    if directorio_salida and not os.path.exists(directorio_salida):
        try:
            os.makedirs(directorio_salida)
        except PermissionError as e:
            raise PermissionError(f"Permiso denegado al crear el directorio de salida: {directorio_salida}. Detalles: {e}")

def generar_nombre_archivo_salida(archivo_entrada, modo):
    """
    Genera un nombre de archivo de salida basado en el archivo de entrada, el modo de filtrado y la marca de tiempo.
    """
    nombre_base = os.path.splitext(os.path.basename(archivo_entrada))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"feeds/{nombre_base}_{modo}_{timestamp}.json"

def filtrar_geo(datos, pais):
    """
    Filtra datos por ubicación geográfica (ip_geo).
    """
    pais_normalizado = pais.lower()
    return [entrada for entrada in datos if entrada.get("ip_geo", "").lower() == pais_normalizado]

def filtrar_admin(datos, pais):
    """
    Filtra datos por ubicación administrativa (ip_whois.country).
    """
    pais_normalizado = pais.upper()
    return [entrada for entrada in datos if entrada.get("ip_whois", {}).get("country", "").upper() == pais_normalizado]

def filtrar_combinado(datos, pais):
    """
    Filtra datos por ubicación geográfica o administrativa.
    """
    geo_normalizado = pais.lower()
    admin_normalizado = pais.upper()
    return [
        entrada
        for entrada in datos
        if entrada.get("ip_geo", "").lower() == geo_normalizado or entrada.get("ip_whois", {}).get("country", "").upper() == admin_normalizado
    ]

def guardar_archivo_salida(archivo_salida, datos_filtrados):
    """
    Guarda los datos filtrados en el archivo de salida.
    """
    try:
        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(datos_filtrados, f, indent=4, ensure_ascii=False)
    except PermissionError as e:
        raise PermissionError(f"Permiso denegado al escribir en el archivo: {archivo_salida}. Detalles: {e}")

def main():
    mostrar_aviso()

    args = parsear_argumentos()

    try:
        validar_codigo_pais(args.country)
        pais = normalizar_codigo_pais(args.country)

        datos = cargar_archivo_entrada(args.input_file)

        archivo_salida = args.output_file or generar_nombre_archivo_salida(args.input_file, args.filter_mode)

        asegurar_directorio_salida(archivo_salida)

        if args.filter_mode == "geo":
            datos_filtrados = filtrar_geo(datos, pais)
        elif args.filter_mode == "admin":
            datos_filtrados = filtrar_admin(datos, pais)
        else:  # combinado
            datos_filtrados = filtrar_combinado(datos, pais)

        guardar_archivo_salida(archivo_salida, datos_filtrados)

        print(f"Total de registros procesados: {len(datos)}")
        print(f"Registros que cumplen los criterios: {len(datos_filtrados)}")
        print(f"Datos filtrados guardados en: {archivo_salida}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Se produjo un error inesperado: {e}")

if __name__ == "__main__":
    main()
