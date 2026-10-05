param([Parameter(Mandatory=$true)][ValidateSet('source','control','candidate')][string]$Role, [ValidatePattern('^boot(?:-[a-z0-9]+)?$')][string]$Attempt='boot')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$sdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$registry = [IO.Path]::GetFullPath((Join-Path $root "runs/wo3b2/$Role/avd"))
if (-not (Test-Path -LiteralPath (Join-Path $registry 'role.json'))) { throw 'No recorded fresh role AVD' }
if (Get-NetTCPConnection -LocalPort 5580 -State Listen -ErrorAction SilentlyContinue) { throw 'Another emulator owns the port' }
if ($Role -ne 'source' -and -not (Test-Path -LiteralPath (Join-Path $root 'runs/wo3b2/source/LOST.json'))) { throw 'SOURCE has not been declared lost' }
# Match the emulator's observed 1.2 x userdata-space admission check.
$config = Join-Path $registry 'H02_P0_API36_X64.avd/config.ini'
$sizeLine = Get-Content -LiteralPath $config | Where-Object { $_ -match '^disk.dataPartition.size=' }
if ($sizeLine -ne 'disk.dataPartition.size=6442450944') { throw 'Unexpected userdata size' }
$drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($registry))
$minimum = [long][math]::Ceiling(6442450944 * 1.2)
if ($drive.AvailableFreeSpace -lt $minimum) { throw "Insufficient host space: $($drive.AvailableFreeSpace) bytes available; emulator requires at least $minimum bytes before userdata creation. Preserve old evidence; do not shrink the qualified partition." }
$out = Join-Path $root "runs/wo3b2/$Role/$Attempt"
if (Test-Path -LiteralPath $out) { throw 'Boot evidence already exists; do not overwrite it' }
New-Item -ItemType Directory -Path $out | Out-Null
$env:ANDROID_AVD_HOME = $registry
$flags = @('-avd','H02_P0_API36_X64','-datadir',(Join-Path $registry 'H02_P0_API36_X64.avd'),'-port','5580','-no-window','-no-audio','-no-snapshot','-no-boot-anim','-gpu','host')
$process = Start-Process -FilePath "$sdk/emulator/emulator.exe" -WindowStyle Hidden -ArgumentList $flags -RedirectStandardOutput "$out/emulator.log" -RedirectStandardError "$out/emulator.err" -PassThru
@{role=$Role; registry=$registry; pid=$process.Id; flags=$flags; utc=[DateTime]::UtcNow.ToString('o');serial='emulator-5580'} | ConvertTo-Json | Set-Content -LiteralPath "$out/launch.json"
Start-Sleep -Seconds 3
$process.Refresh()
if ($process.HasExited) { throw "Emulator launcher exited; inspect $out/emulator.log and emulator.err" }
Write-Output "Launch requested for isolated $Role using HOST GPU. Boot is NOT yet qualified; run provisioning against attempt $Attempt."
