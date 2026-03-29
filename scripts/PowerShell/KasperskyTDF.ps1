# Kaspersky TDF ByCountry — Full Pipeline (English)
# Authenticate -> Download IP Reputation feed -> Filter by country -> Save output.
#
# DISCLAIMER: This script is provided as a Proof of Concept (PoC) for educational
# and demonstration purposes only. It is not an official tool from Kaspersky, nor
# does it come with any guarantees or warranties of functionality or support.
# Use at your own risk, and always validate the results in your environment.

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

$FEED_NAME           = "IP_Reputation"
$DEFAULT_BASE_URL    = "https://tip.kaspersky.com/api/feeds/"
$DEFAULT_ENDPOINT    = "ip_reputation"


# ---------------------------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------------------------

function Show-Warning {
    Write-Host "`n*** DISCLAIMER ***" -ForegroundColor Yellow
    Write-Host "This script is provided as a Proof of Concept (PoC) for educational and demonstration purposes only."
    Write-Host "It is not an official tool from Kaspersky, nor does it come with any guarantees or warranties."
    Write-Host "Use at your own risk, and always validate the results in your environment.`n"
}


# ---------------------------------------------------------------------------
# .env loading (PowerShell-native parser)
# ---------------------------------------------------------------------------

function Read-EnvFile {
    param([string]$EnvFilePath = "")

    if (-not $EnvFilePath) {
        $EnvFilePath = Join-Path $PSScriptRoot "..\..\..\.env"
    }

    if (-not (Test-Path $EnvFilePath)) {
        return  # No .env file — environment variables may already be set by the shell
    }

    Get-Content $EnvFilePath | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }

        $idx = $line.IndexOf("=")
        if ($idx -lt 1) { return }

        $key   = $line.Substring(0, $idx).Trim()
        $value = $line.Substring($idx + 1).Trim()

        # Strip surrounding single or double quotes
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}


# ---------------------------------------------------------------------------
# Configuration (token from environment only — never from parameters)
# ---------------------------------------------------------------------------

function Get-ApiConfig {
    $token    = $env:KASPERSKY_TIP_TOKEN
    $baseUrl  = $env:KASPERSKY_TIP_BASE_URL
    $endpoint = $env:KASPERSKY_TIP_FEED_ENDPOINT
    $limitEnv = $env:KASPERSKY_TIP_LIMIT

    if (-not $token -or $token.Trim() -eq "") {
        Write-Host "Error: KASPERSKY_TIP_TOKEN is not set." -ForegroundColor Red
        Write-Host "  1. Copy .env.example to .env"
        Write-Host "  2. Set KASPERSKY_TIP_TOKEN to your API token"
        Write-Host "  3. Obtain a token at: https://tip.kaspersky.com (Account Settings)"
        exit 1
    }

    if (-not $baseUrl -or $baseUrl.Trim() -eq "")    { $baseUrl  = $DEFAULT_BASE_URL }
    if (-not $endpoint -or $endpoint.Trim() -eq "")  { $endpoint = $DEFAULT_ENDPOINT }

    $limitVal = 0
    if ($limitEnv -and [int]::TryParse($limitEnv, [ref]$limitVal)) {
        $limitVal = [int]$limitEnv
    }

    return @{
        Token    = $token.Trim()
        BaseUrl  = $baseUrl.Trim()
        Endpoint = $endpoint.Trim()
        Limit    = $limitVal
    }
}


# ---------------------------------------------------------------------------
# Country validation and interactive prompts
# ---------------------------------------------------------------------------

function Confirm-CountryCode {
    param([string]$Code)

    if ($Code.Length -ne 2 -or $Code -notmatch '^[a-zA-Z]{2}$') {
        throw "Invalid country code: '$Code'. Must be a two-letter ISO 3166-1 alpha-2 code (e.g., ES)."
    }

    # Validate via RESTCountries API (requires internet access)
    try {
        $uri      = "https://restcountries.com/v3.1/alpha/$($Code.ToUpper())"
        $response = Invoke-RestMethod -Uri $uri -Method Get -TimeoutSec 10 -ErrorAction Stop
        return $response[0].name.common
    } catch {
        # If the API is unreachable, accept the code with a warning
        Write-Host "  Warning: Could not validate country code online. Proceeding anyway." -ForegroundColor Yellow
        return $Code.ToUpper()
    }
}


function Get-CountryIfMissing {
    param([string]$Country)

    if ($Country -ne "") { return $Country }

    while ($true) {
        $code = Read-Host "Enter country code (ISO 3166-1 alpha-2, e.g., ES)"
        $code = $code.Trim()
        try {
            Confirm-CountryCode -Code $code | Out-Null
            return $code.ToUpper()
        } catch {
            Write-Host "  $_" -ForegroundColor Red
        }
    }
}


function Get-FilterModeIfMissing {
    param([string]$Mode)

    if ($Mode -ne "") { return $Mode }

    while ($true) {
        $value = Read-Host "Select filter mode [geo / admin / combined] (press Enter for combined)"
        $value = $value.Trim().ToLower()
        if ($value -eq "") { return "combined" }
        if ($value -in @("geo", "admin", "combined")) { return $value }
        Write-Host "  Invalid mode. Choose from: geo, admin, combined." -ForegroundColor Red
    }
}


# ---------------------------------------------------------------------------
# HTTP client (API mode)
# ---------------------------------------------------------------------------

function Get-FeedUrl {
    param(
        [string]$BaseUrl,
        [string]$Endpoint,
        [int]$Limit
    )

    if (-not $BaseUrl.StartsWith("https://")) {
        Write-Host "Error: KASPERSKY_TIP_BASE_URL must use HTTPS. Check your .env file." -ForegroundColor Red
        exit 1
    }

    $url = "$($BaseUrl.TrimEnd('/'))/$Endpoint"
    if ($Limit -gt 0) { $url += "?limit=$Limit" }
    return $url
}


function Resolve-ApiError {
    param([System.Net.HttpStatusCode]$StatusCode)

    $messages = @{
        [System.Net.HttpStatusCode]::Unauthorized           = "Authentication failed. Verify KASPERSKY_TIP_TOKEN in your .env file. Tokens expire after 1 year."
        [System.Net.HttpStatusCode]::Forbidden              = "Access denied. Your token may not have permission for this feed. Check your Kaspersky TIP subscription."
        [System.Net.HttpStatusCode]::NotFound               = "Feed endpoint not found. Verify KASPERSKY_TIP_FEED_ENDPOINT in .env. Consult the OpenAPI spec at https://tip.kaspersky.com/Help/api/?specId=tip-feeds-api"
        [System.Net.HttpStatusCode]::TooManyRequests        = "Rate limit exceeded. Wait before retrying."
        [System.Net.HttpStatusCode]::InternalServerError    = "Kaspersky TIP API internal server error. Try again later."
        [System.Net.HttpStatusCode]::BadGateway             = "Kaspersky TIP API temporarily unavailable (502). Try again in a few minutes."
        [System.Net.HttpStatusCode]::ServiceUnavailable     = "Kaspersky TIP API temporarily unavailable (503). Try again in a few minutes."
        [System.Net.HttpStatusCode]::GatewayTimeout         = "Kaspersky TIP API gateway timeout (504). Try again in a few minutes."
    }

    if ($messages.ContainsKey($StatusCode)) {
        return $messages[$StatusCode]
    }
    return "Unexpected HTTP $([int]$StatusCode) from Kaspersky TIP API."
}


function Invoke-DownloadRedirect {
    param(
        [hashtable]$Headers,
        [string]$DownloadUrl
    )

    try {
        $response = Invoke-RestMethod -Uri $DownloadUrl -Headers $Headers `
                    -Method Get -TimeoutSec 300 -ErrorAction Stop
        return $response
    } catch [System.Net.WebException] {
        $statusCode = $_.Exception.Response.StatusCode
        $msg = Resolve-ApiError -StatusCode $statusCode
        Write-Host "Error: $msg" -ForegroundColor Red
        exit 1
    } catch {
        Write-Host "Error during download: $_" -ForegroundColor Red
        exit 1
    }
}


function Invoke-FeedApi {
    param(
        [hashtable]$Headers,
        [string]$Url
    )

    try {
        $response = Invoke-RestMethod -Uri $Url -Headers $Headers `
                    -Method Get -TimeoutSec 60 -ErrorAction Stop
    } catch [System.Net.WebException] {
        $statusCode = $_.Exception.Response.StatusCode
        $msg = Resolve-ApiError -StatusCode $statusCode
        Write-Host "Error: $msg" -ForegroundColor Red
        exit 1
    } catch {
        Write-Host "Error: Could not reach Kaspersky TIP API: $_" -ForegroundColor Red
        exit 1
    }

    # Option A: API returned an array directly
    if ($response -is [System.Array]) {
        return $response
    }

    # Option B: API returned an object with a download URL
    $redirectUrl = $null
    foreach ($key in @("download_url", "url", "link", "data_url")) {
        if ($response.PSObject.Properties.Name -contains $key) {
            $redirectUrl = $response.$key
            break
        }
    }

    if ($redirectUrl) {
        Write-Host "  Resolving download link from API response..."
        return Invoke-DownloadRedirect -Headers $Headers -DownloadUrl $redirectUrl
    }

    Write-Host "Error: Unexpected API response format. Cannot locate feed data." -ForegroundColor Red
    exit 1
}


# ---------------------------------------------------------------------------
# Local file loading (fallback / backward-compatible mode)
# ---------------------------------------------------------------------------

function Import-JsonFile {
    param([string]$FilePath)

    if (-not (Test-Path $FilePath)) {
        throw "Input file not found: $FilePath"
    }

    try {
        $content = Get-Content $FilePath -Raw -Encoding UTF8
        $data    = $content | ConvertFrom-Json
    } catch {
        throw "Failed to parse JSON file '$FilePath': $_"
    }

    if (-not $data -or $data.Count -eq 0) {
        throw "Input file is empty or contains no records."
    }

    return $data
}


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

function Select-FilteredData {
    param(
        [array]$Data,
        [string]$Country,
        [string]$Mode
    )

    $geoCode  = $Country.ToLower()
    $admCode  = $Country.ToUpper()

    switch ($Mode) {
        "geo" {
            return $Data | Where-Object { $_.ip_geo -and $_.ip_geo.ToLower() -eq $geoCode }
        }
        "admin" {
            return $Data | Where-Object { $_.ip_whois -and $_.ip_whois.country -and $_.ip_whois.country.ToUpper() -eq $admCode }
        }
        "combined" {
            return $Data | Where-Object {
                ($_.ip_geo -and $_.ip_geo.ToLower() -eq $geoCode) -or
                ($_.ip_whois -and $_.ip_whois.country -and $_.ip_whois.country.ToUpper() -eq $admCode)
            }
        }
        default {
            throw "Unknown filter mode: '$Mode'. Use geo, admin, or combined."
        }
    }
}


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

function New-OutputFilename {
    param([string]$Country, [string]$Mode)
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    return "feeds\${FEED_NAME}_${Country}_${Mode}_${timestamp}.json"
}


function New-RawFilename {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    return "feeds\${FEED_NAME}_raw_${timestamp}.json"
}


function Export-OutputFile {
    param([string]$FilePath, [array]$Data)

    $dir = Split-Path $FilePath -Parent
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $Data | ConvertTo-Json -Depth 10 | Set-Content $FilePath -Encoding UTF8
}


function Show-Summary {
    param(
        [string]$Source,
        [string]$Country,
        [string]$Mode,
        [int]$Total,
        [int]$Matched,
        [string]$OutputFile,
        [string]$RawFile = ""
    )

    Write-Host "`n--- Summary ---" -ForegroundColor Cyan
    Write-Host "  Source        : $Source"
    Write-Host "  Country       : $Country"
    Write-Host "  Filter mode   : $Mode"
    Write-Host "  Total records : $Total"
    Write-Host "  Matched       : $Matched"
    Write-Host "  Filtered out  : $($Total - $Matched)"
    Write-Host "  Output saved  : $OutputFile"
    if ($RawFile -ne "") {
        Write-Host "  Raw feed      : $RawFile"
    }
    if ($Matched -eq 0) {
        Write-Host "`n  [!] No records matched. Try a different country or filter mode." -ForegroundColor Yellow
    }
    Write-Host ""
}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

Show-Warning

try {
    $localMode = ($InputFile -ne "")

    # API mode: load config and validate token before anything else
    if (-not $localMode) {
        Read-EnvFile
        $config = Get-ApiConfig

        # Apply per-run CLI overrides (endpoint and limit only — token stays in env)
        if ($FeedEndpoint -ne "") { $config.Endpoint = $FeedEndpoint }
        if ($Limit -ge 0)         { $config.Limit    = $Limit }
    }

    # Resolve country and filter mode (parameters or interactive prompts)
    $Country    = Get-CountryIfMissing -Country $Country
    $Country    = $Country.ToUpper()
    Confirm-CountryCode -Code $Country | Out-Null
    $FilterMode = Get-FilterModeIfMissing -Mode $FilterMode

    # Fetch or load data
    $rawFile = ""
    if ($localMode) {
        Write-Host "Loading local file: $InputFile"
        $data   = Import-JsonFile -FilePath $InputFile
        $source = "Local file: $InputFile"
    } else {
        # Build headers inline — token is never stored in a named variable
        $headers = @{
            "Authorization" = "Bearer $($env:KASPERSKY_TIP_TOKEN)"
            "Accept"        = "application/json"
        }
        $url = Get-FeedUrl -BaseUrl $config.BaseUrl -Endpoint $config.Endpoint -Limit $config.Limit
        Write-Host "Downloading feed from Kaspersky TIP API..."
        $data   = Invoke-FeedApi -Headers $headers -Url $url
        $source = "API endpoint: $($config.Endpoint)"
        Write-Host "  Downloaded $($data.Count) records."

        if ($SaveRaw) {
            $rawFile = New-RawFilename
            Export-OutputFile -FilePath $rawFile -Data $data
            Write-Host "  Raw feed saved to: $rawFile"
        }

        # Clear header hashtable after use
        $headers.Clear()
    }

    # Filter
    Write-Host "Filtering by country '$Country' using mode '$FilterMode'..."
    $filtered = @(Select-FilteredData -Data $data -Country $Country -Mode $FilterMode)

    # Save output
    if ($OutputFile -eq "") { $OutputFile = New-OutputFilename -Country $Country -Mode $FilterMode }
    Export-OutputFile -FilePath $OutputFile -Data $filtered

    Show-Summary `
        -Source     $source `
        -Country    $Country `
        -Mode       $FilterMode `
        -Total      $data.Count `
        -Matched    $filtered.Count `
        -OutputFile $OutputFile `
        -RawFile    $rawFile

} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
