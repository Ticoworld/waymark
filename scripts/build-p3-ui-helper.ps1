param([string]$OutputRelativePath = 'runs/wo3-setup/ui-helper')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$sdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$jdk = 'C:/Program Files/Android/Android Studio/jbr'
$out = Join-Path $root $OutputRelativePath
New-Item -ItemType Directory -Force "$out/classes" | Out-Null
$cp = "$sdk/platforms/android-36/android.jar;$sdk/platforms/android-36/uiautomator.jar;$sdk/platforms/android-36/optional/android.test.base.jar"
& "$jdk/bin/javac.exe" -encoding UTF-8 -source 17 -target 17 -classpath $cp -d "$out/classes" "$root/scripts/helper/H02FillPhrase.java"
if ($LASTEXITCODE) { throw 'P3 UI helper compilation failed' }
& "$jdk/bin/jar.exe" cf "$out/classes.jar" -C "$out/classes" .
if ($LASTEXITCODE) { throw 'P3 UI helper jar failed' }
$env:JAVA_HOME=$jdk
& "$sdk/build-tools/36.0.0/d8.bat" --lib "$sdk/platforms/android-36/android.jar" --lib "$sdk/platforms/android-36/uiautomator.jar" --lib "$sdk/platforms/android-36/optional/android.test.base.jar" --min-api 26 --output "$out/helper.jar" "$out/classes.jar"
if ($LASTEXITCODE) { throw 'P3 UI helper dex failed' }
Get-FileHash "$out/helper.jar" -Algorithm SHA256
