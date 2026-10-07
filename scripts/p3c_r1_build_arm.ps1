# Host adaptation of the pinned build-android-jni.sh ARM loop; no production edits.
param([switch]$AndroidOnly)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$source = Join-Path $root 'repos/pocket-node'
if ((git -C $source rev-parse HEAD).Trim() -ne 'b28979de744798ffb75367b031d4871ec3af1a12') { throw 'Wrong source pin' }
if (git -C $source status --porcelain=v1) { throw 'Source is not clean' }
$sdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$ndk = Join-Path $sdk 'ndk/27.0.12077973'
$bin = Join-Path $ndk 'toolchains/llvm/prebuilt/windows-x86_64/bin'
$out = Join-Path $root 'runs/wo3c-r1/native'
New-Item -ItemType Directory -Force $out | Out-Null
$env:OPENSSL_SRC_PERL = 'C:/Program Files/Git/usr/bin/perl.exe'
$env:PERL5LIB = '/' + $root.Substring(0,1).ToLower() + $root.Substring(2).Replace('\','/') + '/runs/wo2/perl/lib'
$env:MSYS2_ENV_CONV_EXCL = 'PERL5LIB'
$env:PATH = "$env:USERPROFILE\.cargo\bin;$root/runs/wo2/tools;$bin;C:/Program Files/Git/usr/bin;$env:PATH"
$env:SHELL = 'sh.exe'
$env:RUSTUP_TOOLCHAIN = '1.92.0-x86_64-pc-windows-msvc'
$env:CARGO_TARGET_DIR = Join-Path $out 'target'
$env:CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_LINKER = "$env:USERPROFILE/.rustup/toolchains/1.92.0-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin/rust-lld.exe"
$crt = Join-Path $root 'runs/wo2/msvc/VC/Tools/MSVC/14.44.35207/lib/x64'
if (!(Test-Path "$crt/libcmt.lib")) { throw 'Missing qualified host CRT' }
$env:LIB = "$crt;C:/Program Files (x86)/Windows Kits/10/Lib/10.0.18362.0/um/x64;C:/Program Files (x86)/Windows Kits/10/Lib/10.0.18362.0/ucrt/x64"
$env:H02_NDK_BIN = $bin
$env:CC_x86_64_pc_windows_msvc = Join-Path $PSScriptRoot 'host-cl.cmd'
$env:AR_x86_64_pc_windows_msvc = Join-Path $bin 'llvm-lib.exe'
$env:INCLUDE = "$root/runs/wo2/msvc/VC/Tools/MSVC/14.44.35207/include;C:/Program Files (x86)/Windows Kits/10/Include/10.0.18362.0/ucrt;C:/Program Files (x86)/Windows Kits/10/Include/10.0.18362.0/shared;C:/Program Files (x86)/Windows Kits/10/Include/10.0.18362.0/um"
Remove-Item Env:BUILD_X86_64 -ErrorAction SilentlyContinue
Remove-Item Env:RUSTFLAGS -ErrorAction SilentlyContinue
$env:CFLAGS = '-fPIC -D__ANDROID_API__=21'
$env:CXXFLAGS = '-fPIC -D__ANDROID_API__=21'
Push-Location (Join-Path $source 'external/ckb-light-client')
try {
    # This qualification is explicitly ARM64; repository application logic and signer are unchanged.
    $phoneTargetSpecs = if ($AndroidOnly) { @() } else { ,@('aarch64-linux-android','aarch64_linux_android','arm64-v8a','aarch64-linux-android') }
    foreach ($spec in $phoneTargetSpecs) {
        $target = $spec[0]; $envSuffix = $spec[1]; $abi = $spec[2]; $clangTarget = $spec[3]
        $stub = Join-Path $out "stubs/$abi"
        New-Item -ItemType Directory -Force $stub | Out-Null
        Set-Item "Env:CC_$envSuffix" ($bin.Replace('\','/') + '/clang.exe')
        Set-Item "Env:CFLAGS_$envSuffix" "--target=$($clangTarget)21 -fPIC -D__ANDROID_API__=21"
        Set-Item "Env:CXX_$envSuffix" (Join-Path $bin "$($clangTarget)21-clang++.cmd")
        Set-Item "Env:AR_$envSuffix" ($bin.Replace('\','/') + '/llvm-ar.exe')
        Set-Item "Env:RANLIB_$envSuffix" ($bin.Replace('\','/') + '/llvm-ranlib.exe')
        $cargoPrefix = 'CARGO_TARGET_' + $envSuffix.ToUpper()
        Set-Item "Env:$($cargoPrefix)_LINKER" (Join-Path $bin "$($clangTarget)21-clang.cmd")
        Set-Item "Env:$($cargoPrefix)_RUSTFLAGS" "-L $stub -l static=android_stubs"
        $env:BINDGEN_EXTRA_CLANG_ARGS = "--sysroot=$ndk/toolchains/llvm/prebuilt/windows-x86_64/sysroot --target=$clangTarget -D__ANDROID_API__=21"
        & "$bin/clang.exe" "--target=$($clangTarget)21" -c android-stubs.c -o "$stub/android-stubs.o"
        if ($LASTEXITCODE) { throw 'Stub compilation failed' }
        & "$bin/llvm-ar.exe" rcs "$stub/libandroid_stubs.a" "$stub/android-stubs.o"
        if ($LASTEXITCODE) { throw 'Stub archive failed' }
        & "$env:USERPROFILE/.cargo/bin/cargo.exe" build --locked --release --target $target --package ckb-light-client-lib --features jni-bridge,portable -j 4
        if ($LASTEXITCODE) { throw "Native build failed for $target" }
        $jni = Join-Path $source "android/app/src/main/jniLibs/$abi"
        New-Item -ItemType Directory -Force $jni | Out-Null
        Copy-Item -LiteralPath "$env:CARGO_TARGET_DIR/$target/release/libckb_light_client_lib.so" -Destination $jni
        & "$bin/llvm-strip.exe" --strip-all "$jni/libckb_light_client_lib.so"
        if ($LASTEXITCODE) { throw 'Strip failed' }
        $libcTarget = if ($abi -eq 'armeabi-v7a') { 'arm-linux-androideabi' } else { $target }
        Copy-Item -LiteralPath "$ndk/toolchains/llvm/prebuilt/windows-x86_64/sysroot/usr/lib/$libcTarget/libc++_shared.so" -Destination $jni
        & "$bin/llvm-strip.exe" --strip-all "$jni/libc++_shared.so"
        if ($LASTEXITCODE) { throw 'Strip libc++ failed' }
        Get-FileHash "$jni/*.so" -Algorithm SHA256
    }
} finally { Pop-Location }
if (!(Test-Path "$source/android/app/src/main/jniLibs/arm64-v8a/libckb_light_client_lib.so")) { throw 'Missing compiled ARM64 native library' }
$env:H02_PHONE_BUILD_ROOT = Join-Path $root 'runs/wo3c-r1/gradle'
$env:ANDROID_HOME = $sdk
$env:JAVA_HOME = 'C:/Program Files/Android/Android Studio/jbr'
Push-Location "$source/android"
try {
    & .\gradlew.bat --no-daemon --console=plain --max-workers=4 -I "$root/scripts/p3c-r1-build.init.gradle" assembleDebug -x cargoBuild
    if ($LASTEXITCODE) { throw 'Android ARM build failed' }
} finally { Pop-Location }
if (git -C $source status --porcelain=v1) { throw 'Production source changed unexpectedly' }
Get-FileHash "$env:H02_PHONE_BUILD_ROOT/app/outputs/apk/debug/app-debug.apk" -Algorithm SHA256
