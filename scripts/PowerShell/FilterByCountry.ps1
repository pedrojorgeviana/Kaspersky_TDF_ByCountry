<#
.SYNOPSIS
    Filters records in a JSON file based on the ISO 3166-1 alpha-2 country code.

.DESCRIPTION
    This script loads a JSON file, validates a country code, and filters records
    based on geographic location (`ip_geo`), administrative location (`ip_whois.country`), 
    or both (`combined`).

.PARAMETER Country
    ISO 3166-1 alpha-2 country code to filter (e.g., "US" for United States).

.PARAMETER FilterMode
    Filter mode:
        - "geo": Filters by geographic location (`ip_geo`).
        - "admin": Filters by administrative location (`ip_whois.country`).
        - "combined": Filters by either one.

.PARAMETER InputFile
    Path to the input JSON file. This file must contain the data to be processed.

.PARAMETER OutputFile
    Path to the output JSON file. If not specified, a name will be generated
    automatically based on the input file, filter mode, country code, and timestamp.

.EXAMPLES
    # Filter records for the country "US" by geographic location
    .\FilterByCountry.ps1

.NOTES
    - This script is provided as a Proof of Concept (PoC) and offers no guarantees.
    - Internet access is required to validate the country code using the RESTCountries API.
    - The records in the JSON file must have a consistent structure.
#>

function Show-Warning {
    Clear-Host
    Write-Host "`n*** WARNING ***" -ForegroundColor Yellow
    Write-Host "This script is provided as a Proof of Concept (PoC) and is intended for demonstration purposes only." -ForegroundColor Yellow
    Write-Host "It comes with no guarantees or warranties, and the user assumes full responsibility for any use of this script." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ensure that you have reviewed and understood its functionality before execution. Use this script at your own risk." -ForegroundColor Yellow
    Write-Host ""
}

function Validate-CountryCode {
    param ([string]$Code)

    if ($Code.Length -ne 2 -or ($Code -cmatch '[^a-zA-Z]')) {
        throw "Invalid country code: $Code. It must be a valid ISO 3166-1 alpha-2 code."
    }

    $Code = $Code.ToUpper()
    $ApiUrl = "https://restcountries.com/v3.1/alpha/$Code"

    try {
        $Response = Invoke-RestMethod -Uri $ApiUrl -Method Get -ErrorAction Stop
        if (-not $Response) {
            throw "The country code '$Code' is not valid according to ISO 3166-1 alpha-2."
        }

        $CountryName = $Response.name.common
        Write-Host "The country code '$Code' - $CountryName - was successfully validated using the API." -ForegroundColor Green
    } catch {
        if ($_ -match "Unable to connect" -or $_ -match "timed out") {
            throw "Unable to connect to the API to validate the country code '$Code'. Please check your internet connection."
        } elseif ($_ -match "404") {
            throw "The country code '$Code' is not valid according to ISO 3166-1 alpha-2."
        } else {
            throw "An unexpected error occurred while validating the country code '$Code'. Error: $_"
        }
    }
}

function Import-JsonFile {
    param ([string]$FilePath)

    if (-not (Test-Path -Path $FilePath)) {
        throw "Input file not found: $FilePath"
    }

    try {
        $Data = Get-Content -Path $FilePath -Raw | ConvertFrom-Json
        if (-not $Data -or $Data.Count -eq 0) {
            throw "The file is empty or contains no records."
        }
        return $Data
    } catch {
        throw "The input file is not a valid or well-formed JSON file: $_"
    }
}

function Verify-OutputDirectory {
    param ([string]$FilePath)

    $OutputDir = [System.IO.Path]::GetDirectoryName($FilePath)
    if (-not (Test-Path $OutputDir)) {
        try {
            New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        } catch {
            throw "Unable to create the output directory: $OutputDir"
        }
    }
}

function Export-JsonFile {
    param (
        [string]$FilePath,
        [Object]$Data
    )

    try {
        $Data | ConvertTo-Json -Depth 10 | Set-Content -Path $FilePath -Encoding UTF8
    } catch {
        throw "Failed to save the output file: $_"
    }
}

function Filter-Data {
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

# *** MAIN SCRIPT ***
Show-Warning

try {
    $Country = Read-Host "Enter the country code (ISO 3166-1 alpha-2)"
    $FilterMode = Read-Host "Enter the filter mode (geo, admin, or combined, default: combined)"
    if (-not $FilterMode) {
        $FilterMode = "combined"
        Write-Host "No filter mode specified. Using the default mode: combined" -ForegroundColor Yellow
    }

    $InputFile = "./feeds/IP_Reputation_Data_Feed.json"
    $OutputFile = ""

    Validate-CountryCode -Code $Country

    # Load data
    $Data = Import-JsonFile -FilePath $InputFile

    # Generate output file name if not specified
    if (-not $OutputFile) {
        $BaseName = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
        $Timestamp = (Get-Date -Format "yyyyMMdd_HHmmss")
        $OutputFile = "./feeds/${BaseName}_${FilterMode}_${Country}_${Timestamp}.json"
    }

    # Verify output directory
    Verify-OutputDirectory -FilePath $OutputFile

    # Filter data
    $FilteredData = Filter-Data -Data $Data -Country $Country -Mode $FilterMode

    if (-not $FilteredData -or $FilteredData.Count -eq 0) {
        Write-Host "No records matching the specified criteria were found." -ForegroundColor Yellow
    } else {
        # Save filtered data
        Export-JsonFile -FilePath $OutputFile -Data $FilteredData

        Write-Host "Total records processed: $($Data.Count)" -ForegroundColor Green
        Write-Host "Records matching the criteria: $($FilteredData.Count)" -ForegroundColor Green
        Write-Host "Filtered data saved to: $OutputFile" -ForegroundColor Green
    }

} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
