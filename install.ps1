# Instala o actualiza Previo en el proyecto actual.
# Uso: irm https://raw.githubusercontent.com/yeyopepe/previo-sdd/main/install.ps1 | iex
# Uso (versión concreta): $env:PREVIO_VERSION = "v1.2.3"; irm .../install.ps1 | iex
param(
    [string]$Version = $env:PREVIO_VERSION
)
$ErrorActionPreference = "Stop"

$Repo = "yeyopepe/previo-sdd"

if ($Version) {
    try {
        $Release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/tags/$Version"
    }
    catch {
        throw "La versión '$Version' no existe en los releases de Previo."
    }
}
else {
    $Release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest"
}
$Tag = $Release.tag_name
if (-not $Tag) {
    throw "No se ha podido determinar la versión de Previo a instalar."
}
$Tarball = "https://github.com/$Repo/archive/refs/tags/$Tag.tar.gz"

$Tmp = Join-Path $env:TEMP "previo-install-$([guid]::NewGuid())"
New-Item -ItemType Directory -Path $Tmp -Force | Out-Null
try {
    Write-Host "Descargando Previo ($Tag)..."
    $TarPath = Join-Path $Tmp "previo.tar.gz"
    Invoke-WebRequest -Uri $Tarball -OutFile $TarPath

    tar -xzf $TarPath -C $Tmp --strip-components=1
    if ($LASTEXITCODE -ne 0) { throw "Fallo al extraer el paquete descargado." }

    $SrcSkills = Join-Path $Tmp ".claude\skills"
    $DestSkills = ".claude\skills"
    New-Item -ItemType Directory -Path $DestSkills -Force | Out-Null

    # Sincroniza solo las skills del framework (prefijo pv-), sin tocar skills propias del usuario.
    Get-ChildItem -Path $SrcSkills -Directory -Filter "pv-*" | ForEach-Object {
        $Dest = Join-Path $DestSkills $_.Name
        if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
        Copy-Item -Recurse -Path $_.FullName -Destination $Dest
    }

    if (Test-Path $DestSkills) {
        Get-ChildItem -Path $DestSkills -Directory -Filter "pv-*" | ForEach-Object {
            $SrcDir = Join-Path $SrcSkills $_.Name
            if (-not (Test-Path $SrcDir)) {
                Write-Host "Eliminando skill obsoleta: $($_.Name)"
                Remove-Item -Recurse -Force $_.FullName
            }
        }
    }

    # Sincroniza la documentación del framework.
    foreach ($doc in @("pv-guide.md", "pv-guide.en.md", "pv-design.md", "pv-design.en.md")) {
        $DestDoc = Join-Path ".claude" $doc
        $SrcDoc = Join-Path $Tmp ".claude\$doc"
        if (Test-Path $SrcDoc) {
            Copy-Item -Path $SrcDoc -Destination $DestDoc -Force
        }
    }

    Write-Host "Previo instalado/actualizado en .claude/skills."
    Write-Host "Si es la primera instalación, ejecuta /pv-init en tu agente para configurarlo."
}
finally {
    Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
}
