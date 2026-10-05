@echo off
"%H02_NDK_BIN%\clang.exe" --driver-mode=cl --target=x86_64-pc-windows-msvc %*
