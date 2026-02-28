# Kaspersky TDF ByCountry — Pipeline Completo (Español)
# Autenticar -> Descargar feed de Reputación de IP -> Filtrar por país -> Guardar resultado.
#
# AVISO LEGAL: Este script se proporciona como Prueba de Concepto (PoC) únicamente con
# fines educativos y de demostración. No es una herramienta oficial de Kaspersky, ni
# conlleva garantías de funcionalidad o soporte.
# Úselo bajo su propia responsabilidad y valide siempre los resultados en su entorno.

param(
    [string]$Country      = "",
    [string]$FilterMode   = "",
    [string]$OutputFile   = "",
    [switch]$SaveRaw,
    [string]$InputFile    = "",
    [int]$Limit           = -1,
    [string]$FeedEndpoint = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$NOMBRE_FEED      = "IP_Reputation"
$URL_BASE_DEFECTO = "https://tip.kaspersky.com/api/feeds/"
$ENDPOINT_DEFECTO = "ip_reputation"


# ---------------------------------------------------------------------------
# Aviso legal
# ---------------------------------------------------------------------------

function Mostrar-Aviso {
    Write-Host "`n*** AVISO LEGAL ***" -ForegroundColor Yellow
    Write-Host "Este script se proporciona como Prueba de Concepto (PoC) únicamente con fines educativos y de demostración."
    Write-Host "No es una herramienta oficial de Kaspersky, ni conlleva garantías de funcionalidad o soporte."
    Write-Host "Úselo bajo su propia responsabilidad y valide siempre los resultados en su entorno.`n"
}


# ---------------------------------------------------------------------------
# Carga del archivo .env (parser nativo de PowerShell)
# ---------------------------------------------------------------------------

function Leer-ArchivoEnv {
    param([string]$RutaEnv = "")

    if (-not $RutaEnv) {
        $RutaEnv = Join-Path $PSScriptRoot "..\..\..\.env"
    }

    if (-not (Test-Path $RutaEnv)) {
        return  # Sin archivo .env — las variables de entorno pueden estar ya configuradas
    }

    Get-Content $RutaEnv | ForEach-Object {
        $linea = $_.Trim()
        if ($linea -eq "" -or $linea.StartsWith("#")) { return }

        $idx = $linea.IndexOf("=")
        if ($idx -lt 1) { return }

        $clave = $linea.Substring(0, $idx).Trim()
        $valor = $linea.Substring($idx + 1).Trim()

        # Eliminar comillas simples o dobles que envuelvan el valor
        if (($valor.StartsWith('"') -and $valor.EndsWith('"')) -or
            ($valor.StartsWith("'") -and $valor.EndsWith("'"))) {
            $valor = $valor.Substring(1, $valor.Length - 2)
        }

        [System.Environment]::SetEnvironmentVariable($clave, $valor, "Process")
    }
}


# ---------------------------------------------------------------------------
# Configuración (el token viene solo del entorno — nunca de parámetros)
# ---------------------------------------------------------------------------

function Obtener-Configuracion {
    $token    = $env:KASPERSKY_TIP_TOKEN
    $urlBase  = $env:KASPERSKY_TIP_BASE_URL
    $endpoint = $env:KASPERSKY_TIP_FEED_ENDPOINT
    $limiteEnv = $env:KASPERSKY_TIP_LIMIT

    if (-not $token -or $token.Trim() -eq "") {
        Write-Host "Error: KASPERSKY_TIP_TOKEN no está configurado." -ForegroundColor Red
        Write-Host "  1. Copie .env.example a .env"
        Write-Host "  2. Establezca KASPERSKY_TIP_TOKEN con su token de API"
        Write-Host "  3. Obtenga un token en: https://tip.kaspersky.com (Configuración de cuenta)"
        exit 1
    }

    if (-not $urlBase -or $urlBase.Trim() -eq "")    { $urlBase  = $URL_BASE_DEFECTO }
    if (-not $endpoint -or $endpoint.Trim() -eq "")  { $endpoint = $ENDPOINT_DEFECTO }

    $limiteVal = 0
    if ($limiteEnv -and [int]::TryParse($limiteEnv, [ref]$limiteVal)) {
        $limiteVal = [int]$limiteEnv
    }

    return @{
        Token    = $token.Trim()
        UrlBase  = $urlBase.Trim()
        Endpoint = $endpoint.Trim()
        Limite   = $limiteVal
    }
}


# ---------------------------------------------------------------------------
# Validación del código de país y prompts interactivos
# ---------------------------------------------------------------------------

function Confirmar-CodigoPais {
    param([string]$Codigo)

    if ($Codigo.Length -ne 2 -or $Codigo -notmatch '^[a-zA-Z]{2}$') {
        throw "Código de país inválido: '$Codigo'. Debe ser un código de dos letras ISO 3166-1 alpha-2 (ej. ES)."
    }

    # Validar mediante la API RESTCountries (requiere acceso a internet)
    try {
        $uri      = "https://restcountries.com/v3.1/alpha/$($Codigo.ToUpper())"
        $respuesta = Invoke-RestMethod -Uri $uri -Method Get -TimeoutSec 10 -ErrorAction Stop
        return $respuesta[0].name.common
    } catch {
        Write-Host "  Aviso: No se pudo validar el código de país en línea. Se continúa de todas formas." -ForegroundColor Yellow
        return $Codigo.ToUpper()
    }
}


function Obtener-PaisSiFalta {
    param([string]$Pais)

    if ($Pais -ne "") { return $Pais }

    while ($true) {
        $codigo = Read-Host "Introduzca el código de país (ISO 3166-1 alpha-2, ej. ES)"
        $codigo = $codigo.Trim()
        try {
            Confirmar-CodigoPais -Codigo $codigo | Out-Null
            return $codigo.ToUpper()
        } catch {
            Write-Host "  $_" -ForegroundColor Red
        }
    }
}


function Obtener-ModoSiFalta {
    param([string]$Modo)

    if ($Modo -ne "") { return $Modo }

    while ($true) {
        $valor = Read-Host "Seleccione el modo de filtrado [geo / admin / combined] (pulse Intro para combined)"
        $valor = $valor.Trim().ToLower()
        if ($valor -eq "") { return "combined" }
        if ($valor -in @("geo", "admin", "combined")) { return $valor }
        Write-Host "  Modo no válido. Elija entre: geo, admin, combined." -ForegroundColor Red
    }
}


# ---------------------------------------------------------------------------
# Cliente HTTP (modo API)
# ---------------------------------------------------------------------------

function Construir-UrlFeed {
    param(
        [string]$UrlBase,
        [string]$Endpoint,
        [int]$Limite
    )

    if (-not $UrlBase.StartsWith("https://")) {
        Write-Host "Error: KASPERSKY_TIP_BASE_URL debe usar HTTPS. Revise su archivo .env." -ForegroundColor Red
        exit 1
    }

    $url = "$($UrlBase.TrimEnd('/'))/$Endpoint"
    if ($Limite -gt 0) { $url += "?limit=$Limite" }
    return $url
}


function Resolver-ErrorApi {
    param([System.Net.HttpStatusCode]$CodigoEstado)

    $mensajes = @{
        [System.Net.HttpStatusCode]::Unauthorized           = "Autenticación fallida. Verifique KASPERSKY_TIP_TOKEN en su .env. Los tokens expiran tras 1 año."
        [System.Net.HttpStatusCode]::Forbidden              = "Acceso denegado. Es posible que su token no tenga permisos para este feed. Compruebe su suscripción."
        [System.Net.HttpStatusCode]::NotFound               = "Endpoint del feed no encontrado. Verifique KASPERSKY_TIP_FEED_ENDPOINT en .env. Consulte https://tip.kaspersky.com/Help/api/?specId=tip-feeds-api"
        [System.Net.HttpStatusCode]::TooManyRequests        = "Límite de peticiones superado. Espere antes de volver a intentarlo."
        [System.Net.HttpStatusCode]::InternalServerError    = "Error interno del servidor de Kaspersky TIP API. Inténtelo más tarde."
        [System.Net.HttpStatusCode]::BadGateway             = "Kaspersky TIP API temporalmente no disponible (502). Inténtelo en unos minutos."
        [System.Net.HttpStatusCode]::ServiceUnavailable     = "Kaspersky TIP API temporalmente no disponible (503). Inténtelo en unos minutos."
        [System.Net.HttpStatusCode]::GatewayTimeout         = "Tiempo de espera en la puerta de enlace de Kaspersky TIP API (504). Inténtelo en unos minutos."
    }

    if ($mensajes.ContainsKey($CodigoEstado)) {
        return $mensajes[$CodigoEstado]
    }
    return "Error HTTP inesperado $([int]$CodigoEstado) desde Kaspersky TIP API."
}


function Invocar-RedireccionDescarga {
    param(
        [hashtable]$Cabeceras,
        [string]$UrlDescarga
    )

    try {
        $respuesta = Invoke-RestMethod -Uri $UrlDescarga -Headers $Cabeceras `
                     -Method Get -TimeoutSec 300 -ErrorAction Stop
        return $respuesta
    } catch [System.Net.WebException] {
        $codigoEstado = $_.Exception.Response.StatusCode
        $msg = Resolver-ErrorApi -CodigoEstado $codigoEstado
        Write-Host "Error: $msg" -ForegroundColor Red
        exit 1
    } catch {
        Write-Host "Error durante la descarga: $_" -ForegroundColor Red
        exit 1
    }
}


function Invocar-FeedApi {
    param(
        [hashtable]$Cabeceras,
        [string]$Url
    )

    try {
        $respuesta = Invoke-RestMethod -Uri $Url -Headers $Cabeceras `
                     -Method Get -TimeoutSec 60 -ErrorAction Stop
    } catch [System.Net.WebException] {
        $codigoEstado = $_.Exception.Response.StatusCode
        $msg = Resolver-ErrorApi -CodigoEstado $codigoEstado
        Write-Host "Error: $msg" -ForegroundColor Red
        exit 1
    } catch {
        Write-Host "Error: No se pudo conectar a Kaspersky TIP API: $_" -ForegroundColor Red
        exit 1
    }

    # Opción A: la API devolvió un array directamente
    if ($respuesta -is [System.Array]) {
        return $respuesta
    }

    # Opción B: la API devolvió un objeto con URL de descarga
    $urlRedireccion = $null
    foreach ($clave in @("download_url", "url", "link", "data_url")) {
        if ($respuesta.PSObject.Properties.Name -contains $clave) {
            $urlRedireccion = $respuesta.$clave
            break
        }
    }

    if ($urlRedireccion) {
        Write-Host "  Resolviendo enlace de descarga desde la respuesta de la API..."
        return Invocar-RedireccionDescarga -Cabeceras $Cabeceras -UrlDescarga $urlRedireccion
    }

    Write-Host "Error: Formato de respuesta inesperado. No se pudo localizar el feed." -ForegroundColor Red
    exit 1
}


# ---------------------------------------------------------------------------
# Carga de archivo local (modo alternativo / compatibilidad hacia atrás)
# ---------------------------------------------------------------------------

function Importar-ArchivoJson {
    param([string]$RutaArchivo)

    if (-not (Test-Path $RutaArchivo)) {
        throw "Archivo de entrada no encontrado: $RutaArchivo"
    }

    try {
        $contenido = Get-Content $RutaArchivo -Raw -Encoding UTF8
        $datos     = $contenido | ConvertFrom-Json
    } catch {
        throw "Error al parsear el archivo JSON '$RutaArchivo': $_"
    }

    if (-not $datos -or $datos.Count -eq 0) {
        throw "El archivo de entrada está vacío o no contiene registros."
    }

    return $datos
}


# ---------------------------------------------------------------------------
# Filtrado
# ---------------------------------------------------------------------------

function Seleccionar-DatosFiltrados {
    param(
        [array]$Datos,
        [string]$Pais,
        [string]$Modo
    )

    $codigoGeo  = $Pais.ToLower()
    $codigoAdm  = $Pais.ToUpper()

    switch ($Modo) {
        "geo" {
            return $Datos | Where-Object { $_.ip_geo -and $_.ip_geo.ToLower() -eq $codigoGeo }
        }
        "admin" {
            return $Datos | Where-Object { $_.ip_whois -and $_.ip_whois.country -and $_.ip_whois.country.ToUpper() -eq $codigoAdm }
        }
        "combined" {
            return $Datos | Where-Object {
                ($_.ip_geo -and $_.ip_geo.ToLower() -eq $codigoGeo) -or
                ($_.ip_whois -and $_.ip_whois.country -and $_.ip_whois.country.ToUpper() -eq $codigoAdm)
            }
        }
        default {
            throw "Modo de filtrado desconocido: '$Modo'. Use geo, admin o combined."
        }
    }
}


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------

function Nuevo-NombreArchivoSalida {
    param([string]$Pais, [string]$Modo)
    $marcaTiempo = Get-Date -Format "yyyyMMdd_HHmmss"
    return "feeds\${NOMBRE_FEED}_${Pais}_${Modo}_${marcaTiempo}.json"
}


function Nuevo-NombreArchivoRaw {
    $marcaTiempo = Get-Date -Format "yyyyMMdd_HHmmss"
    return "feeds\${NOMBRE_FEED}_raw_${marcaTiempo}.json"
}


function Exportar-ArchivoSalida {
    param([string]$RutaArchivo, [array]$Datos)

    $directorio = Split-Path $RutaArchivo -Parent
    if ($directorio -and -not (Test-Path $directorio)) {
        New-Item -ItemType Directory -Path $directorio -Force | Out-Null
    }

    $Datos | ConvertTo-Json -Depth 10 | Set-Content $RutaArchivo -Encoding UTF8
}


function Mostrar-Resumen {
    param(
        [string]$Origen,
        [string]$Pais,
        [string]$Modo,
        [int]$Total,
        [int]$Coincidencias,
        [string]$ArchivoSalida,
        [string]$ArchivoRaw = ""
    )

    Write-Host "`n--- Resumen ---" -ForegroundColor Cyan
    Write-Host "  Origen           : $Origen"
    Write-Host "  País             : $Pais"
    Write-Host "  Modo de filtrado : $Modo"
    Write-Host "  Registros totales: $Total"
    Write-Host "  Coincidencias    : $Coincidencias"
    Write-Host "  Filtrados        : $($Total - $Coincidencias)"
    Write-Host "  Resultado en     : $ArchivoSalida"
    if ($ArchivoRaw -ne "") {
        Write-Host "  Feed sin filtrar : $ArchivoRaw"
    }
    if ($Coincidencias -eq 0) {
        Write-Host "`n  [!] Ningún registro coincide. Pruebe con otro país o modo de filtrado." -ForegroundColor Yellow
    }
    Write-Host ""
}


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

Mostrar-Aviso

try {
    $modoLocal = ($InputFile -ne "")

    # Modo API: cargar configuración y validar token antes de cualquier otra acción
    if (-not $modoLocal) {
        Leer-ArchivoEnv
        $config = Obtener-Configuracion

        # Aplicar sobreescrituras de la línea de comandos (solo endpoint y límite)
        if ($FeedEndpoint -ne "") { $config.Endpoint = $FeedEndpoint }
        if ($Limit -ge 0)         { $config.Limite   = $Limit }
    }

    # Resolver país y modo de filtrado (parámetros o prompts interactivos)
    $Country    = Obtener-PaisSiFalta -Pais $Country
    $Country    = $Country.ToUpper()
    Confirmar-CodigoPais -Codigo $Country | Out-Null
    $FilterMode = Obtener-ModoSiFalta -Modo $FilterMode

    # Obtener o cargar datos
    $archivoRaw = ""
    if ($modoLocal) {
        Write-Host "Cargando archivo local: $InputFile"
        $datos  = Importar-ArchivoJson -RutaArchivo $InputFile
        $origen = "Archivo local: $InputFile"
    } else {
        # Cabeceras con token en línea — nunca almacenado en una variable con nombre
        $cabeceras = @{
            "Authorization" = "Bearer $($env:KASPERSKY_TIP_TOKEN)"
            "Accept"        = "application/json"
        }
        $url    = Construir-UrlFeed -UrlBase $config.UrlBase -Endpoint $config.Endpoint -Limite $config.Limite
        Write-Host "Descargando feed desde Kaspersky TIP API..."
        $datos  = Invocar-FeedApi -Cabeceras $cabeceras -Url $url
        $origen = "Endpoint API: $($config.Endpoint)"
        Write-Host "  Descargados $($datos.Count) registros."

        if ($SaveRaw) {
            $archivoRaw = Nuevo-NombreArchivoRaw
            Exportar-ArchivoSalida -RutaArchivo $archivoRaw -Datos $datos
            Write-Host "  Feed sin filtrar guardado en: $archivoRaw"
        }

        # Limpiar el hashtable de cabeceras tras su uso
        $cabeceras.Clear()
    }

    # Filtrar
    Write-Host "Filtrando por país '$Country' con modo '$FilterMode'..."
    $filtrados = @(Seleccionar-DatosFiltrados -Datos $datos -Pais $Country -Modo $FilterMode)

    # Guardar resultado
    if ($OutputFile -eq "") { $OutputFile = Nuevo-NombreArchivoSalida -Pais $Country -Modo $FilterMode }
    Exportar-ArchivoSalida -RutaArchivo $OutputFile -Datos $filtrados

    Mostrar-Resumen `
        -Origen        $origen `
        -Pais          $Country `
        -Modo          $FilterMode `
        -Total         $datos.Count `
        -Coincidencias $filtrados.Count `
        -ArchivoSalida $OutputFile `
        -ArchivoRaw    $archivoRaw

} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
