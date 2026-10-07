param([Parameter(Mandatory=$true)][ValidateSet('source','control')][string]$Role, [switch]$CompleteReceiptOnly)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$roleRoot=Join-Path $root "runs/wo3b2/$Role"
$avd=[IO.Path]::GetFullPath((Join-Path $roleRoot 'avd/H02_P0_API36_X64.avd'))
if(Get-NetTCPConnection -LocalPort 5580 -State Listen -ErrorAction SilentlyContinue){throw 'Emulator still listening'}
$running=Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'qemu-system*' -and $_.CommandLine.Replace('\','/').Contains($avd.Replace('\','/'))}
if($running){throw 'Role process still alive'}
$seal=Join-Path $roleRoot 'evidence-seal-r4.json'
if(-not(Test-Path -LiteralPath $seal)){throw 'No verified evidence seal'}
$manifest=Get-Content -LiteralPath $seal -Raw | ConvertFrom-Json
if($manifest.accepted -ne $true -or $manifest.restartPassed -ne $true){throw 'Incomplete role acceptance'}
foreach($item in $manifest.files){
    $p=[IO.Path]::GetFullPath((Join-Path $root $item.path))
    if(-not $p.StartsWith((Join-Path $root 'runs/wo3b2')+[IO.Path]::DirectorySeparatorChar)){throw 'Seal path outside B2'}
    if((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower() -ne $item.sha256){throw 'Evidence digest mismatch'}
}
if($Role -eq 'source' -and -not(Test-Path -LiteralPath "$roleRoot/LOST.json")){throw 'SOURCE loss declaration absent'}
$receipt=Join-Path $roleRoot 'runtime-retirement.json'
$plan=Join-Path $roleRoot 'runtime-retirement-plan.json'
if($CompleteReceiptOnly){
    if((Test-Path -LiteralPath $receipt) -or -not(Test-Path -LiteralPath $plan)){throw 'No interrupted retirement to finalize'}
    $saved=Get-Content -LiteralPath $plan -Raw | ConvertFrom-Json
    if($saved.role -ne $Role -or $saved.evidenceSealSha256 -ne (Get-FileHash -LiteralPath $seal).Hash.ToLower()){throw 'Interrupted plan binding mismatch'}
    foreach($item in $saved.paths){
        $p=[IO.Path]::GetFullPath($item.path)
        if(-not $p.StartsWith($avd+[IO.Path]::DirectorySeparatorChar)){throw 'Plan path outside role'}
        if(Test-Path -LiteralPath $p){throw 'Runtime deletion incomplete; no automatic additional deletion'}
    }
    $after=[IO.DriveInfo]::new('C:/').AvailableFreeSpace
    @{role=$Role;complete=$true;utc=[DateTime]::UtcNow.ToString('o');freeBefore=$saved.freeBefore;freeAfter=$after;reclaimedHostBytes=$after-$saved.freeBefore;logicalBytes=($saved.paths | ForEach-Object {$_.bytes} | Measure-Object -Sum).Sum;paths=$saved.paths;planSha256=(Get-FileHash -LiteralPath $plan).Hash.ToLower();receiptFinalizedAfterHarnessError=$true} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt
    Write-Output "Retirement verified complete; receipt finalized; free $after bytes"
    exit
}
if((Test-Path -LiteralPath $receipt) -or (Test-Path -LiteralPath $plan)){throw 'Retirement already attempted; inspect receipt'}
# Exact generated runtime allowlist. Configs, launch logs, extracted state and
# all host-side private fixtures are outside this list and remain untouched.
$relative=@('userdata-qemu.img','userdata-qemu.img.qcow2','cache.img','cache.img.qcow2','encryptionkey.img','encryptionkey.img.qcow2','snapshots/default_boot/ram.img','initrd')
$paths=@()
foreach($rel in $relative){
    $p=[IO.Path]::GetFullPath((Join-Path $avd $rel))
    if(-not $p.StartsWith($avd+[IO.Path]::DirectorySeparatorChar)){throw 'Runtime path escaped role'}
    if(Test-Path -LiteralPath $p){
        $f=Get-Item -LiteralPath $p
        if($f.PSIsContainer -or ($f.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Unsafe runtime file'}
        $paths+=@{path=$p;bytes=$f.Length;reason='Disposable completed role runtime; compact acceptance/restart evidence sealed; regenerate from installed system image'}
    }
}
if(-not $paths.Count){throw 'No runtime to retire'}
$before=[IO.DriveInfo]::new('C:/').AvailableFreeSpace
@{role=$Role;utc=[DateTime]::UtcNow.ToString('o');freeBefore=$before;paths=$paths;evidenceSealSha256=(Get-FileHash -LiteralPath $seal).Hash.ToLower()} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $plan
foreach($item in $paths){Write-Output "$($item.path) | $($item.bytes) bytes | $($item.reason)"}
foreach($item in $paths){Remove-Item -LiteralPath $item.path -Force}
foreach($item in $paths){if(Test-Path -LiteralPath $item.path){throw 'Runtime deletion incomplete'}}
$after=[IO.DriveInfo]::new('C:/').AvailableFreeSpace
@{role=$Role;complete=$true;utc=[DateTime]::UtcNow.ToString('o');freeBefore=$before;freeAfter=$after;reclaimedHostBytes=$after-$before;logicalBytes=($paths | ForEach-Object {$_.bytes} | Measure-Object -Sum).Sum;paths=$paths;planSha256=(Get-FileHash -LiteralPath $plan).Hash.ToLower()} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt
Write-Output "Runtime retired; host reclaimed $($after-$before) bytes; free $after bytes"
