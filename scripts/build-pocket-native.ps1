$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$source = Join-Path $root 'repos/pocket-node'
$pin = 'b28979de744798ffb75367b031d4871ec3af1a12'
if ((git -C $source rev-parse HEAD).Trim() -ne $pin) { throw 'Pocket pin mismatch' }
if (git -C $source status --porcelain=v1) { throw 'Pocket source must be clean' }
$sdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$ndk = Join-Path $sdk 'ndk/27.0.12077973'
$bin = Join-Path $ndk 'toolchains/llvm/prebuilt/windows-x86_64/bin'
$out = Join-Path $root 'runs/wo2/native'
New-Item -ItemType Directory -Force $out | Out-Null
$tools = Join-Path $root 'runs/wo2/tools'
New-Item -ItemType Directory -Force $tools | Out-Null
Copy-Item -LiteralPath (Get-Command mingw32-make.exe).Source -Destination "$tools/make.exe"
$env:OPENSSL_SRC_PERL = 'C:/Program Files/Git/usr/bin/perl.exe'
$env:PERL5LIB = '/' + $root.Substring(0,1).ToLower() + $root.Substring(2).Replace('\','/') + '/runs/wo2/perl/lib'
# Git sh -> native make -> Git Perl must retain the POSIX module path.
# Otherwise MSYS converts /c/... to C:/..., which Perl splits at the colon.
$env:MSYS2_ENV_CONV_EXCL = 'PERL5LIB'
$env:PATH = "$env:USERPROFILE\.cargo\bin;$tools;$bin;C:/Program Files/Git/usr/bin;$env:PATH"
$env:SHELL = 'sh.exe'
$env:RUSTUP_TOOLCHAIN = '1.92.0-x86_64-pc-windows-msvc'
$env:CARGO_TARGET_DIR = Join-Path $out 'target'
$env:CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_LINKER = "$env:USERPROFILE/.rustup/toolchains/1.92.0-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin/rust-lld.exe"
$crt = Join-Path $root 'runs/wo2/msvc/VC/Tools/MSVC/14.44.35207/lib/x64'
if (!(Test-Path "$crt/libcmt.lib")) { throw 'Prepare pinned local MSVC CRT libraries first' }
$env:LIB = "$crt;C:/Program Files (x86)/Windows Kits/10/Lib/10.0.18362.0/um/x64;C:/Program Files (x86)/Windows Kits/10/Lib/10.0.18362.0/ucrt/x64"
$env:H02_NDK_BIN = $bin
$env:CC_x86_64_pc_windows_msvc = Join-Path $PSScriptRoot 'host-cl.cmd'
$env:AR_x86_64_pc_windows_msvc = Join-Path $bin 'llvm-lib.exe'
$env:INCLUDE = "$root/runs/wo2/msvc/VC/Tools/MSVC/14.44.35207/include;C:/Program Files (x86)/Windows Kits/10/Include/10.0.18362.0/ucrt;C:/Program Files (x86)/Windows Kits/10/Include/10.0.18362.0/shared;C:/Program Files (x86)/Windows Kits/10/Include/10.0.18362.0/um"
$env:CC_x86_64_linux_android = ($bin.Replace('\','/') + '/clang.exe')
$env:CFLAGS_x86_64_linux_android = '--target=x86_64-linux-android21'
$env:CXX_x86_64_linux_android = Join-Path $bin 'x86_64-linux-android21-clang++.cmd'
$env:AR_x86_64_linux_android = ($bin.Replace('\','/') + '/llvm-ar.exe')
$env:RANLIB_x86_64_linux_android = ($bin.Replace('\','/') + '/llvm-ranlib.exe')
$env:CARGO_TARGET_X86_64_LINUX_ANDROID_LINKER = Join-Path $bin 'x86_64-linux-android21-clang.cmd'
$env:CARGO_TARGET_X86_64_LINUX_ANDROID_RUSTFLAGS = "-L $out -l static=android_stubs"
$env:BINDGEN_EXTRA_CLANG_ARGS = "--target=x86_64-linux-android21 --sysroot=$ndk/toolchains/llvm/prebuilt/windows-x86_64/sysroot"
Remove-Item Env:RUSTFLAGS -ErrorAction SilentlyContinue
Push-Location (Join-Path $source 'external/ckb-light-client')
try {
    & $env:CC_x86_64_linux_android --target=x86_64-linux-android21 -c android-stubs.c -o "$out/android-stubs.o"
    if ($LASTEXITCODE) { throw 'Android stub compilation failed' }
    & $env:AR_x86_64_linux_android rcs "$out/libandroid_stubs.a" "$out/android-stubs.o"
    if ($LASTEXITCODE) { throw 'Android stub archive failed' }
    & "$env:USERPROFILE/.cargo/bin/cargo.exe" build --locked --release --target x86_64-linux-android --package ckb-light-client-lib --features jni-bridge,portable -j 4
    if ($LASTEXITCODE) { throw 'Pinned native build failed' }
    $jni = Join-Path $source 'android/app/src/main/jniLibs/x86_64'
    New-Item -ItemType Directory -Force $jni | Out-Null
    Copy-Item -LiteralPath "$env:CARGO_TARGET_DIR/x86_64-linux-android/release/libckb_light_client_lib.so" -Destination $jni
    & "$bin/llvm-strip.exe" --strip-all "$jni/libckb_light_client_lib.so"
    if ($LASTEXITCODE) { throw 'Strip failed' }
    Copy-Item -LiteralPath "$ndk/toolchains/llvm/prebuilt/windows-x86_64/sysroot/usr/lib/x86_64-linux-android/libc++_shared.so" -Destination $jni
    Get-FileHash "$jni/*.so" -Algorithm SHA256
} finally { Pop-Location }
