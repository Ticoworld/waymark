param([Parameter(Mandatory=$true)][ValidateSet('control','candidate')][string]$Role)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$previous=if($Role -eq 'control'){'source'}else{'control'}
$receipt=Join-Path $root "runs/wo3b2/$previous/runtime-retirement.json"
if(-not(Test-Path -LiteralPath $receipt)){throw 'Prior runtime not retired'}
$prior=Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
if(-not $prior.complete){throw 'Incomplete prior runtime retirement'}
foreach($item in $prior.paths){if(Test-Path -LiteralPath $item.path){throw 'Prior runtime still exists'}}
if(-not(Test-Path -LiteralPath (Join-Path $root 'runs/wo3b2/source/LOST.json'))){throw 'SOURCE not lost'}
if(Get-NetTCPConnection -LocalPort 5580 -State Listen -ErrorAction SilentlyContinue){throw 'Emulator remains live'}
$free=[IO.DriveInfo]::new('C:/').AvailableFreeSpace
if($free -lt 10GB){throw 'Below approved 10 GiB pre-launch requirement; STOP'}
$out=Join-Path $root "runs/wo3b2/$Role"
New-Item -ItemType Directory -Force -Path $out | Out-Null
if(Test-Path -LiteralPath "$out/disk-before.json"){throw 'Role already attempted'}
@{utc=[DateTime]::UtcNow.ToString('o');freeBytes=$free;minimumBytes=10GB;predecessor=$previous;priorRetirement=$receipt} | ConvertTo-Json | Set-Content -LiteralPath "$out/disk-before.json"
& "$PSScriptRoot/b2_create_role.ps1" -Role $Role
if($LASTEXITCODE){throw 'Fresh role creation failed'}
$avd=Join-Path $out 'avd/H02_P0_API36_X64.avd'
$runtime=@(Get-ChildItem -LiteralPath $avd -Recurse -File | Where-Object {$_.Name -match '^(userdata|cache|encryptionkey|ram\.)'})
if($runtime.Count){throw 'Unexpected runtime before first boot'}
@{utc=[DateTime]::UtcNow.ToString('o');role=$Role;runtimeImagesAbsent=$true;origin='Installed system image only; new guest userdata and Keystore';predecessorReceipt=$receipt} | ConvertTo-Json | Set-Content -LiteralPath "$out/fresh-runtime.json"
& "$PSScriptRoot/b2_boot_role.ps1" -Role $Role
if($LASTEXITCODE){throw 'Fresh role launch failed'}
