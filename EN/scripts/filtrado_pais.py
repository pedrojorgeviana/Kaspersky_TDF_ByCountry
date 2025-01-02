import json
import datetime
import os
import pycountry

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
pais = 'ES'  # Código del país en formato ISO 3166-2 (ES, PT, BR, etc...)

def obtener_nombre_pais(codigo_iso):
    """
    Devuelve el nombre del país dado su código ISO alfa-2 utilizando pycountry.
    """
    try:
        pais = pycountry.countries.get(alpha_2=codigo_iso.upper())
        return pais.name if pais else "Desconocido"
    except Exception:
        return "Desconocido"

def filtrar_por_pais(fichero_entrada, fichero_salida):
    """
    Filtra registros en un archivo JSON donde el campo 'ip_whois' tiene 'country' igual al valor indicado en la variable pais.
    """
    try:
        # Crear la carpeta feeds si no existe
        os.makedirs(os.path.dirname(fichero_entrada), exist_ok=True)

        # Abrir y cargar el archivo JSON
        with open(fichero_entrada, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            if not isinstance(datos, list):
                raise ValueError("El archivo JSON debe contener una lista de registros.")

        # Filtrar los datos
        registros_filtrados = [
            registro for registro in datos
#            if registro.get("ip_geo").upper() == pais.upper() // TBD
            if registro.get("ip_whois", {}).get("country", "").upper() == pais.upper()
        ]

        # Informar sobre los resultados
        print(f"Total registros procesados: {len(datos)}")
        print(f"Registros ignorados: {len(datos) - len(registros_filtrados)}")
        if registros_filtrados:
            print(f"Se encontraron {len(registros_filtrados)} registros con country = '{pais}' ({obtener_nombre_pais(pais)}).")
        else:
            print(f"No se encontraron registros con country = '{pais}' ({obtener_nombre_pais(pais)}).")

        # Guardar los registros filtrados
        with open(fichero_salida, 'w', encoding='utf-8') as archivo_salida:
            json.dump(registros_filtrados, archivo_salida, indent=4, ensure_ascii=False)
        print(f"Registros filtrados guardados en: {fichero_salida}")

    except FileNotFoundError as e:
        print(f"Error: El archivo '{fichero_entrada}' no se encuentra.")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: El archivo no es un JSON válido. Detalle: {e}")
        raise
    except Exception as e:
        print(f"Error inesperado: {e}")
        raise

if __name__ == "__main__":
    # Archivos en la carpeta feeds
    carpeta = "./feeds/"
    fichero_entrada = os.path.join(carpeta, "IP_Reputation_Data_Feed_200516_1445.json")
    fichero_salida = os.path.join(carpeta, f"IP_Reputation_filtrado_{pais}_{timestamp}.json")
    
    # Ejecutar la función
    filtrar_por_pais(fichero_entrada, fichero_salida)
