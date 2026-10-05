param([Parameter(Mandatory=$true)][ValidateSet('control','candidate')][string]$Role)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$sdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$registry = [IO.Path]::GetFullPath((Join-Path $root "runs/wo3b1-r2/$Role/avd"))
if (-not (Test-Path -LiteralPath (Join-Path $registry 'role.json'))) { throw 'No recorded fresh role AVD' }
if (Get-NetTCPConnection -LocalPort 5580 -State Listen -ErrorAction SilentlyContinue) { throw 'Another emulator owns the port' }
if (-not (Test-Path -LiteralPath (Join-Path $root 'runs/wo3b1-r2/source/LOST.json'))) { throw 'SOURCE has not been declared lost' }
$out = Join-Path $root "runs/wo3b1-r2/$Role/boot"
if (Test-Path -LiteralPath $out) { throw 'Boot evidence already exists; do not overwrite it' }
New-Item -ItemType Directory -Path $out | Out-Null
$env:ANDROID_AVD_HOME = $registry
$flags = @('-avd','H02_P0_API36_X64','-datadir',(Join-Path $registry 'H02_P0_API36_X64.avd'),'-port','5580','-no-window','-no-audio','-no-snapshot','-no-boot-anim','-gpu','host')
$process = Start-Process -FilePath "$sdk/emulator/emulator.exe" -WindowStyle Hidden -ArgumentList $flags -RedirectStandardOutput "$out/emulator.log" -RedirectStandardError "$out/emulator.err" -PassThru
@{role=$Role; registry=$registry; pid=$process.Id; flags=$flags; utc=[DateTime]::UtcNow.ToString('o');serial='emulator-5580'} | ConvertTo-Json | Set-Content -LiteralPath "$out/launch.json"
Write-Output "Started isolated $Role using HOST GPU; no Pocket launch"
