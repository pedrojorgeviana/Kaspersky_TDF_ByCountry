<#
.SINOPSIS
    Filtra registros en un archivo JSON basado en el código de país ISO 3166-1 alfa-2.

.DESCRIPCIÓN
    Este script carga un archivo JSON, valida un código de país y filtra los registros
    basados en la ubicación geográfica (`ip_geo`), la ubicación administrativa 
    (`ip_whois.country`) o ambos (`combined`).

.PARAMETER Country
    Código ISO 3166-1 alfa-2 del país que se desea filtrar (por ejemplo, "ES" para España).

.PARAMETER FilterMode
    Modo de filtrado:
        - "geo": Filtra por ubicación geográfica (`ip_geo`).
        - "admin": Filtra por ubicación administrativa (`ip_whois.country`).
        - "combined": Filtra por cualquiera de las dos opciones.

.PARAMETER InputFile
    Ruta al archivo JSON de entrada. Este archivo debe contener los datos a procesar.

.PARAMETER OutputFile
    Ruta al archivo JSON de salida. Si no se especifica, se generará automáticamente
    un nombre basado en el archivo de entrada, el modo de filtrado, el código de país y la marca de tiempo.

.EJEMPLOS
    # Filtrar registros para el país "ES" por ubicación geográfica
    .\FiltrarPorPais.ps1

.NOTAS
    - Este script se proporciona como una Prueba de Concepto (PoC) y no ofrece garantías.
    - Requiere acceso a internet para validar el código de país mediante la API de RESTCountries.
    - Los registros del archivo JSON deben tener una estructura esperada.
#>

function Mostrar-Aviso {
    Clear-Host
    Write-Host "`n*** AVISO ***" -ForegroundColor Yellow
    Write-Host "Este script se proporciona como una Prueba de Concepto (PoC) y está diseñado únicamente con fines de demostración." -ForegroundColor Yellow
    Write-Host "No ofrece garantías ni responsabilidades, y el usuario asume toda la responsabilidad por su uso." -ForegroundColor Yellow
    Write-Host "" 
    Write-Host "Asegúrese de revisar y comprender su funcionalidad antes de ejecutarlo. Use este script bajo su propio riesgo." -ForegroundColor Yellow
    Write-Host ""
}

function Validar-CodigoPais {
    param ([string]$Code)

    if ($Code.Length -ne 2 -or ($Code -cmatch '[^a-zA-Z]')) {
        throw "Código de país inválido: $Code. Debe ser un código ISO 3166-1 alfa-2 válido."
    }

    $Code = $Code.ToUpper()
    $ApiUrl = "https://restcountries.com/v3.1/alpha/$Code"

    try {
        $Response = Invoke-RestMethod -Uri $ApiUrl -Method Get -ErrorAction Stop
        if (-not $Response) {
            throw "El código de país '$Code' no es válido según ISO 3166-1 alfa-2."
        }

        $CountryName = $Response.name.common
        Write-Host "El código de país '$Code' - $CountryName - ha sido validado correctamente mediante la API." -ForegroundColor Green
    } catch {
        if ($_ -match "Unable to connect" -or $_ -match "timed out") {
            throw "No se pudo conectar a la API para validar el código de país '$Code'. Por favor, revise su conexión a internet."
        } elseif ($_ -match "404") {
            throw "El código de país '$Code' no es válido según ISO 3166-1 alfa-2."
        } else {
            throw "Ocurrió un error inesperado durante la validación del código de país '$Code'. Error: $_"
        }
    }
}

function Importar-ArchivoJson {
    param ([string]$FilePath)

    if (-not (Test-Path -Path $FilePath)) {
        throw "Archivo de entrada no encontrado: $FilePath"
    }

    try {
        $Data = Get-Content -Path $FilePath -Raw | ConvertFrom-Json
        if (-not $Data -or $Data.Count -eq 0) {
            throw "El archivo está vacío o no contiene registros."
        }
        return $Data
    } catch {
        throw "El archivo de entrada no es un JSON válido o está malformado: $_"
    }
}

function Verificar-DirectorioSalida {
    param ([string]$FilePath)

    $OutputDir = [System.IO.Path]::GetDirectoryName($FilePath)
    if (-not (Test-Path $OutputDir)) {
        try {
            New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        } catch {
            throw "No se pudo crear el directorio de salida: $OutputDir"
        }
    }
}

function Exportar-ArchivoJson {
    param (
        [string]$FilePath,
        [Object]$Data
    )

    try {
        $Data | ConvertTo-Json -Depth 10 | Set-Content -Path $FilePath -Encoding UTF8
    } catch {
        throw "No se pudo guardar el archivo de salida: $_"
    }
}

function Filtrar-Datos {
    param (
        [Object[]]$Data,
        [string]$Country,
        [string]$Mode
    )

    $GeoCountry = $Country.ToLower()
    $AdminCountry = $Country.ToUpper()

    switch ($Mode) {
        "geo" {
            return $Data | Where-Object { $_.ip_geo -eq $GeoCountry }
        }
        "admin" {
            return $Data | Where-Object { $_.ip_whois.country -eq $AdminCountry }
        }
        "combined" {
            return $Data | Where-Object {
                $_.ip_geo -eq $GeoCountry -or $_.ip_whois.country -eq $AdminCountry
            }
        }
    }
}

# *** FLUJO PRINCIPAL ***
Mostrar-Aviso

try {
    $Country = Read-Host "Ingrese el código del país (ISO 3166-1 alfa-2)"
    $FilterMode = Read-Host "Ingrese el modo de filtrado (geo, admin o combined, por defecto: combined)"
    if (-not $FilterMode) {
        $FilterMode = "combined"
        Write-Host "Modo de filtrado no especificado. Usando el modo predeterminado: combined" -ForegroundColor Yellow
    }

    $InputFile = "./feeds/IP_Reputation_Data_Feed.json"
    $OutputFile = ""

    Validar-CodigoPais -Code $Country

    # Cargar datos
    $Data = Importar-ArchivoJson -FilePath $InputFile

    # Generar nombre de archivo de salida si no se especifica
    if (-not $OutputFile) {
        $BaseName = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
        $Timestamp = (Get-Date -Format "yyyyMMdd_HHmmss")
        $OutputFile = "./feeds/${BaseName}_${FilterMode}_${Country}_${Timestamp}.json"
    }

    # Verificar directorio de salida
    Verificar-DirectorioSalida -FilePath $OutputFile

    # Filtrar datos
    $FilteredData = Filtrar-Datos -Data $Data -Country $Country -Mode $FilterMode

    if (-not $FilteredData -or $FilteredData.Count -eq 0) {
        Write-Host "No se encontraron registros que coincidan con los criterios especificados." -ForegroundColor Yellow
    } else {
        # Guardar archivo filtrado
        Exportar-ArchivoJson -FilePath $OutputFile -Data $FilteredData

        Write-Host "Total de registros procesados: $($Data.Count)" -ForegroundColor Green
        Write-Host "Registros que cumplen los criterios: $($FilteredData.Count)" -ForegroundColor Green
        Write-Host "Datos filtrados guardados en: $OutputFile" -ForegroundColor Green
    }

} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
