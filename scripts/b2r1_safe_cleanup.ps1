# One-off, exact-allowlist cleanup for WO-3B2-R1. Never invokes ADB or a build.
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$run = Join-Path $root 'runs/wo3b2-r1'
$plan = Get-Content -Raw -LiteralPath (Join-Path $run 'cleanup-classification.json') | ConvertFrom-Json
if (-not $plan.classificationComplete) { throw 'Classification incomplete' }
$processes = Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'qemu-system*' -or $_.Name -in @('emulator.exe','cargo.exe','rustc.exe') }
if ($processes) { throw 'An emulator or native build is active; no cleanup' }
$allowed = @()
foreach ($base in @('runs/wo2/avd/H02_P0_API36_X64.avd','runs/wo3b1-r2/control/avd/H02_P0_API36_X64.avd','runs/wo3b1-r2/candidate/avd/H02_P0_API36_X64.avd')) {
    foreach ($name in @('userdata-qemu.img','userdata-qemu.img.qcow2','cache.img','cache.img.qcow2','encryptionkey.img','encryptionkey.img.qcow2','snapshots/default_boot/ram.img')) {
        $allowed += [IO.Path]::GetFullPath((Join-Path $root "$base/$name"))
    }
}
$allowed += [IO.Path]::GetFullPath((Join-Path $root 'runs/wo2/native/target'))
$allowed += [IO.Path]::GetFullPath((Join-Path $root 'runs/wo2/gradle/app/intermediates'))
if ($plan.items.Count -ne $allowed.Count) { throw 'Unexpected plan count' }
foreach ($item in $plan.items) {
    $target = [IO.Path]::GetFullPath($item.path)
    if ($allowed -notcontains $target -or $item.class -ne 'SAFE TO DELETE / REGENERATE') { throw 'Unapproved target' }
    if (-not $target.StartsWith((Join-Path $root 'runs') + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Outside H02 runs' }
    $node = Get-Item -LiteralPath $target -Force
    while ($node.FullName -ne $root) {
        if ($node.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse ancestor refused' }
        $node = Get-Item -LiteralPath (Split-Path $node.FullName -Parent) -Force
    }
    if ($item.kind -eq 'directory') {
        $children = @(Get-ChildItem -LiteralPath $target -Recurse -Force)
        if ($children | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) { throw 'Reparse child refused' }
        if ($children | Where-Object { $_.Name -in @('.git','AGENTS.md') }) { throw 'Repository/source metadata inside target' }
    }
}
$apk = Join-Path $root 'runs/wo2/gradle/app/outputs/apk/debug/app-debug.apk'
$expected = '903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f'
if ((Get-FileHash -LiteralPath $apk).Hash.ToLower() -ne $expected) { throw 'Approved APK not verified' }
$receipt = Join-Path $run 'cleanup-receipts.jsonl'
if (Test-Path -LiteralPath $receipt) { throw 'Receipt already exists; do not repeat cleanup' }
$enc = [Text.UTF8Encoding]::new($false)
function FreeBytes { return [IO.DriveInfo]::new([IO.Path]::GetPathRoot($root)).AvailableFreeSpace }
function Record($value) { [IO.File]::AppendAllText($receipt,($value | ConvertTo-Json -Depth 8 -Compress) + "`n",$enc) }
Record @{event='begin';utc=[DateTime]::UtcNow.ToString('o');freeBytes=(FreeBytes)}
foreach ($group in ($plan.items | Group-Object group)) {
    $before = FreeBytes
    Record @{event='before_delete';group=$group.Name;utc=[DateTime]::UtcNow.ToString('o');freeBytes=$before;items=$group.Group}
    foreach ($item in $group.Group) {
        # Exact paths already resolved, checked under H02/runs and recorded above.
        if ($item.kind -eq 'directory') { Remove-Item -LiteralPath $item.path -Recurse -Force }
        else { Remove-Item -LiteralPath $item.path -Force }
        if (Test-Path -LiteralPath $item.path) { throw 'Target still exists' }
    }
    $after = FreeBytes
    Record @{event='after_delete';group=$group.Name;utc=[DateTime]::UtcNow.ToString('o');freeBytes=$after;observedReclaimedBytes=($after-$before)}
    Write-Output "$($group.Name): observed reclaimed $($after-$before) bytes"
}
if ((Get-FileHash -LiteralPath $apk).Hash.ToLower() -ne $expected) { throw 'APK preservation failed' }
Record @{event='complete';utc=[DateTime]::UtcNow.ToString('o');freeBytes=(FreeBytes);apkSha256=$expected}
Write-Output 'TARGETED_CLEANUP_COMPLETE; no Android launch or recovery'
