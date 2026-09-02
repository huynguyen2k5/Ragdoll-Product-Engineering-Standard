param(
    [switch]$PurgeData,
    [string]$BinDir = ""
)

$ErrorActionPreference = "Stop"
$DataHome = if ($env:RAGDOLL_HOME) { $env:RAGDOLL_HOME } else { Join-Path $HOME ".ragdoll" }
if (-not $BinDir) {
    $BinDir = Join-Path $env:LOCALAPPDATA "Ragdoll\bin"
}
$CommandPath = Join-Path $BinDir "ragdoll.cmd"

if (Test-Path $CommandPath) {
    try { & $CommandPath stop | Out-Null } catch { }
    Remove-Item -Force $CommandPath
}

$CurrentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($CurrentUserPath) {
    $Remaining = @($CurrentUserPath -split ";" | Where-Object { $_ -and $_ -ne $BinDir })
    [Environment]::SetEnvironmentVariable("Path", ($Remaining -join ";"), "User")
}
if ((Test-Path $BinDir) -and -not (Get-ChildItem -Force $BinDir | Select-Object -First 1)) {
    Remove-Item -Force $BinDir
}

$RuntimeDir = Join-Path $DataHome "runtime"
if (Test-Path $RuntimeDir) { Remove-Item -Recurse -Force $RuntimeDir }

if ($PurgeData) {
    if (Test-Path $DataHome) { Remove-Item -Recurse -Force $DataHome }
    Write-Host "Ragdoll runtime and user data were permanently removed."
} else {
    Write-Host "Ragdoll runtime removed. User data preserved at $DataHome"
    Write-Host "Use .\uninstall.ps1 -PurgeData only if you intentionally want to delete Project History and local configuration."
}
