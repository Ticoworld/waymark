$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$env:ANDROID_AVD_HOME = Join-Path $root 'runs/wo2/avd'
$sdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$name = 'H02_P0_API36_X64'
$dest = Join-Path $env:ANDROID_AVD_HOME "$name.avd"
if (Test-Path $dest) { throw 'AVD exists; will not overwrite or wipe it' }
New-Item -ItemType Directory -Force $env:ANDROID_AVD_HOME | Out-Null
'no' | & "$sdk/cmdline-tools/cmdline-tools/bin/avdmanager.bat" create avd --name $name --package 'system-images;android-36;default;x86_64' --path $dest --device pixel_6
if ($LASTEXITCODE) { throw 'AVD creation failed' }
$config = Join-Path $dest 'config.ini'
$lines = Get-Content $config | Where-Object { $_ -notmatch '^(disk.dataPartition.size|hw.ramSize|hw.cpu.ncore|hw.keyboard)=' }
$lines += @('disk.dataPartition.size=4G','hw.ramSize=2048','hw.cpu.ncore=2','hw.keyboard=yes')
$lines | Set-Content -Encoding ASCII $config
Write-Output "Created $name at $dest; not launched"
