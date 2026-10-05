param([ValidateSet('compileDebugKotlin','assembleDebug')][string]$Task = 'assembleDebug')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$source = Join-Path $root 'repos/pocket-node'
if ((git -C $source rev-parse HEAD).Trim() -ne 'b28979de744798ffb75367b031d4871ec3af1a12') { throw 'Pocket pin mismatch' }
if (git -C $source status --porcelain=v1) { throw 'Pocket source must be clean' }
if ($Task -eq 'assembleDebug' -and !(Test-Path "$source/android/app/src/main/jniLibs/x86_64/libckb_light_client_lib.so")) { throw 'Build native library first' }
$env:BUILD_X86_64 = '1'
$env:H02_BUILD_ROOT = Join-Path $root 'runs/wo2/gradle'
$env:ANDROID_HOME = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$env:JAVA_HOME = 'C:/Program Files/Android/Android Studio/jbr'
if ($Task -eq 'assembleDebug') {
    $signing = Join-Path $root 'runs/wo2/signing'
    New-Item -ItemType Directory -Force $signing | Out-Null
    if (!(Test-Path "$signing/debug.keystore")) {
        & "$env:JAVA_HOME/bin/keytool.exe" -genkeypair -keystore "$signing/debug.keystore" -storepass android -keypass android -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 3650 -dname 'CN=H02 Debug,O=Local Test,C=NG'
        if ($LASTEXITCODE) { throw 'Isolated debug signing key generation failed' }
    }
}
Push-Location "$source/android"
try {
    & .\gradlew.bat --no-daemon --console=plain --max-workers=4 -I "$root/scripts/wo2-build.init.gradle" $Task -x cargoBuild
    if ($LASTEXITCODE) { throw 'Pinned Android build failed' }
} finally { Pop-Location }
