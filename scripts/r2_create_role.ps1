param([Parameter(Mandatory=$true)][ValidateSet('control','candidate')][string]$Role)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$sdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$env:JAVA_HOME = 'C:/Program Files/Android/Android Studio/jbr'
$registry = [IO.Path]::GetFullPath((Join-Path $root "runs/wo3b1-r2/$Role/avd"))
if (Test-Path -LiteralPath $registry) { throw 'Role registry exists; refusing replacement' }
New-Item -ItemType Directory -Path $registry | Out-Null
$env:ANDROID_AVD_HOME = $registry
$dest = Join-Path $registry 'H02_P0_API36_X64.avd'
'no' | & "$sdk/cmdline-tools/cmdline-tools/bin/avdmanager.bat" create avd --name H02_P0_API36_X64 --package 'system-images;android-36;default;x86_64' --path $dest --device pixel_6
if ($LASTEXITCODE) { throw 'Isolated AVD creation failed' }
$config = Join-Path $dest 'config.ini'
$lines = Get-Content -LiteralPath $config | Where-Object { $_ -notmatch '^(disk.dataPartition.size|hw.ramSize|hw.cpu.ncore|hw.keyboard)=' }
$lines += @('disk.dataPartition.size=6442450944','hw.ramSize=2048','hw.cpu.ncore=2','hw.keyboard=yes')
$lines | Set-Content -LiteralPath $config -Encoding ASCII
@{ role=$Role; registry=$registry; avd='H02_P0_API36_X64'; origin='Fresh installed API36 image; no SOURCE data copied'; graphics='host'; api=36; abi='x86_64'; ramMiB=2048; cpu=2 } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $registry 'role.json')
Write-Output "Fresh $Role AVD created; not launched: $registry"
