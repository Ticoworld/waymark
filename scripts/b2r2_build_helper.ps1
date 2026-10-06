param([string]$OutputRelativePath='runs/wo3b2-r2/state-helper')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$sdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$jdk = 'C:/Program Files/Android/Android Studio/jbr'
$out = [IO.Path]::GetFullPath((Join-Path $root $OutputRelativePath))
if (-not $out.StartsWith(([IO.Path]::GetFullPath((Join-Path $root 'runs')) + [IO.Path]::DirectorySeparatorChar))) { throw 'Output must be under runs' }
New-Item -ItemType Directory -Force "$out/classes" | Out-Null
& "$jdk/bin/javac.exe" -encoding UTF-8 -source 17 -target 17 -classpath "$sdk/platforms/android-36/android.jar" -d "$out/classes" "$root/scripts/b2r2-helper/H02State.java"
if ($LASTEXITCODE) { throw 'Helper javac failed' }
& "$jdk/bin/jar.exe" cf "$out/classes.jar" -C "$out/classes" .
if ($LASTEXITCODE) { throw 'Helper jar failed' }
$env:JAVA_HOME=$jdk
& "$sdk/build-tools/36.0.0/d8.bat" --lib "$sdk/platforms/android-36/android.jar" --min-api 26 --output "$out/helper.jar" "$out/classes.jar"
if ($LASTEXITCODE) { throw 'Helper dex failed' }
Get-FileHash "$out/helper.jar" -Algorithm SHA256
