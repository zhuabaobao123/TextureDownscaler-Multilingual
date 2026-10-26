@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
cd /d E:\TextureDownscaler-src-2.6
set VCPKG_ROOT=E:\vcpkg
cmake --build build\cn --parallel > E:\TextureDownscaler-src-2.6\build_cn.log 2>&1
exit /b %ERRORLEVEL%
