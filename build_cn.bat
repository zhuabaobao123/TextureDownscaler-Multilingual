@echo off
setlocal
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] vcvars64.bat failed
    exit /b 1
)

cd /d E:\TextureDownscaler-src-2.6
set VCPKG_ROOT=E:\vcpkg

cmake -S . -B build\cn -G Ninja ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_CXX_COMPILER=cl.exe ^
    -DCMAKE_TOOLCHAIN_FILE=E:/vcpkg/scripts/buildsystems/vcpkg.cmake ^
    -DVCPKG_TARGET_TRIPLET=x64-windows-static ^
    -DVCPKG_MANIFEST_MODE=OFF ^
    -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded ^
    -DCMAKE_CXX_FLAGS="/permissive- /Zc:preprocessor /EHsc /MP /W4 /utf-8 -DWIN32_LEAN_AND_MEAN -DNOMINMAX -DUNICODE -D_UNICODE" ^
    -DBUILD_TESTS=OFF
