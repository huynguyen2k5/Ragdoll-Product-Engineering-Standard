param(
    [string]$Python = "python",
    [string]$BinDir = "",
    [string]$Repository = "",
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"

function Test-RagdollSource([string]$Path) {
    if (-not $Path) { return $false }
    return (Test-Path (Join-Path $Path "pyproject.toml")) -and (Test-Path (Join-Path $Path "ragdoll"))
}

function Test-Python([string]$Executable) {
    try {
        & $Executable -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
    } catch {
        throw "Ragdoll requires Python 3.11 or newer. Use -Python to select another Python executable."
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Ragdoll requires Python 3.11 or newer. Use -Python to select another Python executable."
    }
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLowerInvariant()
}

function Expand-RagdollArchive([string]$Archive, [string]$Destination) {
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Expand-Archive -Path $Archive -DestinationPath $Destination -Force
    $Candidates = @(Get-ChildItem -Path $Destination -Recurse -Filter "pyproject.toml" -File | Where-Object {
        (Test-Path (Join-Path $_.Directory.FullName "install.ps1")) -and
        (Test-Path (Join-Path $_.Directory.FullName "ragdoll"))
    } | ForEach-Object { $_.Directory.FullName } | Select-Object -Unique)
    if ($Candidates.Count -ne 1) {
        throw "Expected exactly one Ragdoll source tree in archive; found $($Candidates.Count)."
    }
    return $Candidates[0]
}

function Get-RagdollRelease([string]$Repo, [string]$RequestedVersion) {
    if (-not $Repo -or $Repo -notmatch '^[^/]+/[^/]+$') {
        throw "RAGDOLL_REPO must be owner/repository."
    }
    $Headers = @{
        Accept = "application/vnd.github+json"
        "User-Agent" = "ragdoll-installer"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    if (-not $RequestedVersion -or $RequestedVersion -eq "latest") {
        $Uri = "https://api.github.com/repos/$Repo/releases/latest"
    } else {
        $Encoded = [Uri]::EscapeDataString($RequestedVersion)
        $Uri = "https://api.github.com/repos/$Repo/releases/tags/$Encoded"
    }
    $Release = Invoke-RestMethod -Uri $Uri -Headers $Headers -Method Get
    $ZipAssets = @($Release.assets | Where-Object {
        $_.name -like "ragdoll-product-engineering-standard-*.zip" -and $_.browser_download_url
    })
    $SumsAssets = @($Release.assets | Where-Object { $_.name -eq "SHA256SUMS" -and $_.browser_download_url })
    if ($ZipAssets.Count -ne 1) { throw "Release must contain exactly one Ragdoll source ZIP asset." }
    if ($SumsAssets.Count -ne 1) { throw "Release must contain SHA256SUMS." }
    return [pscustomobject]@{
        Tag = [string]$Release.tag_name
        AssetName = [string]$ZipAssets[0].name
        AssetUrl = [string]$ZipAssets[0].browser_download_url
        SumsUrl = [string]$SumsAssets[0].browser_download_url
    }
}

Test-Python $Python

$SourceDir = ""
if ($PSScriptRoot -and (Test-RagdollSource $PSScriptRoot)) {
    $SourceDir = $PSScriptRoot
}

$BootstrapTemp = $null
try {
    if (-not $SourceDir) {
        $BootstrapTemp = Join-Path ([IO.Path]::GetTempPath()) ("ragdoll-install-" + [Guid]::NewGuid().ToString("N"))
        New-Item -ItemType Directory -Force -Path $BootstrapTemp | Out-Null
        $ExtractDir = Join-Path $BootstrapTemp "src"

        if ($env:RAGDOLL_INSTALL_ARCHIVE) {
            $Archive = (Resolve-Path $env:RAGDOLL_INSTALL_ARCHIVE).Path
            if (-not $env:RAGDOLL_INSTALL_SHA256) {
                throw "RAGDOLL_INSTALL_SHA256 is required with RAGDOLL_INSTALL_ARCHIVE."
            }
            $Actual = Get-Sha256 $Archive
            if ($Actual -ne $env:RAGDOLL_INSTALL_SHA256.ToLowerInvariant()) {
                throw "Local Ragdoll archive checksum verification failed."
            }
            $SourceDir = Expand-RagdollArchive $Archive $ExtractDir
        } else {
            if (-not $Repository) { $Repository = if ($env:RAGDOLL_REPO) { $env:RAGDOLL_REPO } else { "huynguyen2k5/Ragdoll-Product-Engineering-Standard" } }
            if (-not $Version) { $Version = if ($env:RAGDOLL_VERSION) { $env:RAGDOLL_VERSION } else { "latest" } }
            $Release = Get-RagdollRelease $Repository $Version
            $Archive = Join-Path $BootstrapTemp $Release.AssetName
            $Sums = Join-Path $BootstrapTemp "SHA256SUMS"
            Invoke-WebRequest -Uri $Release.AssetUrl -OutFile $Archive -Headers @{"User-Agent"="ragdoll-installer"}
            Invoke-WebRequest -Uri $Release.SumsUrl -OutFile $Sums -Headers @{"User-Agent"="ragdoll-installer"}
            $EscapedName = [Regex]::Escape($Release.AssetName)
            $Match = Select-String -Path $Sums -Pattern "^([0-9a-fA-F]{64})\s+\*?$EscapedName$" | Select-Object -First 1
            if (-not $Match) { throw "Could not find a valid SHA-256 entry for $($Release.AssetName)." }
            $Expected = $Match.Matches[0].Groups[1].Value.ToLowerInvariant()
            $Actual = Get-Sha256 $Archive
            if ($Actual -ne $Expected) {
                throw "Ragdoll release checksum verification failed. Expected $Expected, got $Actual."
            }
            Write-Host "Verified Ragdoll release $($Release.Tag) from $Repository."
            $SourceDir = Expand-RagdollArchive $Archive $ExtractDir
        }
    }

    $DataHome = if ($env:RAGDOLL_HOME) { $env:RAGDOLL_HOME } else { Join-Path $HOME ".ragdoll" }
    $RuntimeDir = Join-Path $DataHome "runtime"
    $AppDir = Join-Path $RuntimeDir "app"
    if (-not $BinDir) {
        $BinDir = Join-Path $env:LOCALAPPDATA "Ragdoll\bin"
    }
    $CommandPath = Join-Path $BinDir "ragdoll.cmd"

    New-Item -ItemType Directory -Force -Path $RuntimeDir, $BinDir, $DataHome | Out-Null
    if (Test-Path $AppDir) { Remove-Item -Recurse -Force $AppDir }
    New-Item -ItemType Directory -Force -Path $AppDir | Out-Null

    $Items = @("ragdoll", "tools", "scripts", "references", "context-standard", "project-history-standard", "assets", "integrations", "project-context")
    foreach ($Item in $Items) {
        $Source = Join-Path $SourceDir $Item
        if (Test-Path $Source) {
            Copy-Item -Recurse -Force $Source $AppDir
        }
    }
    $Files = @("SKILL.md", "README.md", "PRIVACY.md", "SECURITY.md", "CHANGELOG.md", "ROADMAP.md", "pyproject.toml", ".env.example")
    foreach ($File in $Files) {
        $Source = Join-Path $SourceDir $File
        if (Test-Path $Source) {
            Copy-Item -Force $Source (Join-Path $AppDir $File)
        }
    }

    $EnvPath = Join-Path $DataHome ".env"
    if (-not (Test-Path $EnvPath)) {
        Copy-Item (Join-Path $SourceDir ".env.example") $EnvPath
    }

    $CmdContent = @"
@echo off
set "PYTHONPATH=$AppDir;%PYTHONPATH%"
if not defined RAGDOLL_HOME set "RAGDOLL_HOME=$DataHome"
"$Python" -m ragdoll %*
"@
    Set-Content -Path $CommandPath -Value $CmdContent -Encoding ASCII

    $CurrentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $PathEntries = @($CurrentUserPath -split ";" | Where-Object { $_ })
    if ($PathEntries -notcontains $BinDir) {
        $NewPath = if ($CurrentUserPath) { "$CurrentUserPath;$BinDir" } else { $BinDir }
        [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    }

    $env:PYTHONPATH = "$AppDir;$env:PYTHONPATH"
    $env:RAGDOLL_HOME = $DataHome
    & $Python -m ragdoll init | Out-Null

    Write-Host "Ragdoll installed successfully."
    Write-Host "Command: $CommandPath"
    Write-Host "Data: $DataHome"
    Write-Host "Config: $EnvPath"
    Write-Host "History is preserved across reinstall/uninstall unless explicitly purged."
    Write-Host "Open a new terminal so the updated user PATH is loaded."
    Write-Host "Next: edit $EnvPath, add one provider API key, then run 'ragdoll doctor' and 'ragdoll start'."
} finally {
    if ($BootstrapTemp -and (Test-Path $BootstrapTemp)) {
        Remove-Item -Recurse -Force $BootstrapTemp -ErrorAction SilentlyContinue
    }
}
