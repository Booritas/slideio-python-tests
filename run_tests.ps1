<#
.SYNOPSIS
  This script installs and tests SlideIO wheel files for multiple Python versions in conda environments.

.DESCRIPTION
  Given a directory containing wheel files and a range of Python versions,
  this script will:
    1. Create a conda environment per Python version
    2. Install the appropriate wheel (matching "cpXX" portion)
    3. Install any additional Python dependencies (via requirements.txt)
    4. Run pytest
    5. Deactivate and remove each environment

.NOTES
  Requires:
    - conda
    - pytest
    - PowerShell 5.0+ (or PowerShell Core)
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Dists
)

# --- Basic Checks --------------------------------------------------

# Check if the directory exists
if (!(Test-Path -Path $Dists -PathType Container)) {
    Write-Host "Error: Directory '$Dists' does not exist."
    exit 1
}

# Default min/max version.  Must cover the Python versions the wheels are built
# for; a version with no matching wheel is reported at the end rather than
# passing silently.
$minVersion = 9
$maxVersion = 14


# --- Helper Functions ----------------------------------------------

function Generate-PythonVersions {
    param(
        [int]$MinVersion,
        [int]$MaxVersion
    )
    $versions = @()
    for ($v = $MinVersion; $v -le $MaxVersion; $v++) {
        $versions += "3.$v"
    }
    return $versions
}

function Create-And-ActivateCondaEnv {
    param(
        [string]$Version
    )
    Write-Host "`n=== Creating conda environment for Python $Version ==="
    conda create -y -n "env_python_$Version" python=$Version

    Write-Host "=== Activating conda environment for Python $Version ==="
    # If conda is not recognized, ensure you've run: conda init powershell
    conda activate "env_python_$Version"
}

function Deactivate-And-RemoveCondaEnv {
    param(
        [string]$Version
    )
    Write-Host "=== Deactivating conda environment for Python $Version ==="
    conda deactivate

    Write-Host "=== Removing conda environment for Python $Version ==="
    conda remove -y -n "env_python_$Version" --all

    Write-Host "-----end of processing python version $Version-----`n"
}

# --- Main Script Logic ---------------------------------------------

$pythonVersions = Generate-PythonVersions $minVersion $maxVersion

# Remove the local dist folder if present
if (Test-Path "./dist") {
    Remove-Item -Recurse -Force "./dist"
}

Write-Host "`n--- Processing wheel files in '$Dists' ---`n"

# Outcome per Python version, so a failure in one version cannot be hidden by a
# later success.  The script's exit code is derived from this at the end.
$results = [ordered]@{}

foreach ($version in $pythonVersions) {
    Write-Host "`n----- Processing Python version: $version -----"

    # 1. Create & activate environment
    Create-And-ActivateCondaEnv -Version $version

    # 2. Find the wheel file for this Python version
    #    We look for files like *cp38*, *cp39*, etc.
    $wheelPattern = "*cp$($version.Replace('.', ''))*.whl"
    $wheelFile = Get-ChildItem -Path $Dists -Filter $wheelPattern -Recurse | Select-Object -First 1

    if (-not $wheelFile) {
        Write-Host "Error: No .whl file found for Python $version in directory '$Dists'"
        $results[$version] = "NO WHEEL"
        Deactivate-And-RemoveCondaEnv -Version $version
        continue
    }

    # 3. Install the found wheel
    Write-Host "=== Installing $($wheelFile.FullName)"
    python -m pip install $wheelFile.FullName

    # 4. Install dependencies & run tests
    Write-Host "=== Installing dependencies from requirements.txt"
    python -m pip install -r "./requirements.txt"

    Write-Host "=== Running tests via pytest ==="
    pytest .
    $pytestExit = $LASTEXITCODE
    if ($pytestExit -eq 0) {
        $results[$version] = "PASSED"
    } else {
        $results[$version] = "FAILED (pytest exit $pytestExit)"
    }

    # 5. Deactivate & remove environment
    Deactivate-And-RemoveCondaEnv -Version $version
}

# --- Summary -------------------------------------------------------------

Write-Host "`n--- Summary ---"
foreach ($entry in $results.GetEnumerator()) {
    Write-Host ("  Python {0,-5} {1}" -f $entry.Key, $entry.Value)
}

$failed = @($results.GetEnumerator() | Where-Object { $_.Value -like "FAILED*" })
$missing = @($results.GetEnumerator() | Where-Object { $_.Value -eq "NO WHEEL" })

if ($missing.Count -gt 0) {
    Write-Host "`nWarning: no wheel for $($missing.Count) version(s): $($missing.Key -join ', ')"
}

if ($failed.Count -gt 0) {
    Write-Host "`nTests failed for $($failed.Count) version(s): $($failed.Key -join ', ')`n"
    exit 1
}

Write-Host "`nAll done!`n"
exit 0
