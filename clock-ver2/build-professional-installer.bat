@echo off
:: =====================================================================================
:: ClockApp Ver2 Professional Installer Build Script
:: 프로페셔널 Inno Setup 인스톨러 빌드 스크립트
:: =====================================================================================
:: 개발자: KoreawookDevTeam
:: 버전: 2.0.0
:: 설명: 현대적이고 프로페셔널한 GUI 인스톨러를 빌드합니다
:: =====================================================================================

setlocal enabledelayedexpansion

:: 색상 설정
set "COLOR_HEADER=96"
set "COLOR_SUCCESS=92"
set "COLOR_ERROR=91"
set "COLOR_WARNING=93"
set "COLOR_INFO=94"

:: 헤더 출력
call :print_header

:: 변수 설정
set "PROJECT_NAME=ClockApp Ver2"
set "VERSION=2.0.0"
set "SCRIPT_NAME=ClockApp-Ver2-Professional-Setup.iss"
set "OUTPUT_DIR=dist"
set "BUILD_DATE=%date:~0,4%-%date:~5,2%-%date:~8,2%"
set "BUILD_TIME=%time:~0,2%:%time:~3,2%:%time:~6,2%"

echo [%COLOR_INFO%m📋 빌드 정보[0m
echo    프로젝트: %PROJECT_NAME%
echo    버전: %VERSION%
echo    빌드 시간: %BUILD_DATE% %BUILD_TIME%
echo    스크립트: %SCRIPT_NAME%
echo    출력 경로: %OUTPUT_DIR%
echo.

:: 1단계: 환경 확인
echo [%COLOR_INFO%m🔍 [1/6] 환경 확인[0m
call :check_requirements
if !errorlevel! neq 0 goto :error_exit

:: 2단계: 기존 빌드 정리
echo [%COLOR_INFO%m🧹 [2/6] 기존 빌드 정리[0m
call :cleanup_previous_builds

:: 3단계: 실행 파일 확인
echo [%COLOR_INFO%m🔍 [3/6] 실행 파일 확인[0m
call :check_exe_file
if !errorlevel! neq 0 goto :error_exit

:: 4단계: 리소스 파일 확인
echo [%COLOR_INFO%m📁 [4/6] 리소스 파일 확인[0m
call :check_resources

:: 5단계: Inno Setup 컴파일
echo [%COLOR_INFO%m🔨 [5/6] Inno Setup 컴파일[0m
call :compile_installer
if !errorlevel! neq 0 goto :error_exit

:: 6단계: 빌드 완료 및 검증
echo [%COLOR_INFO%m✅ [6/6] 빌드 검증[0m
call :verify_build
if !errorlevel! neq 0 goto :error_exit

:: 성공 메시지
echo.
echo [%COLOR_SUCCESS%m🎉 인스톨러 빌드 완료![0m
echo    📦 출력 파일: %OUTPUT_DIR%\ClockApp-Ver2-Professional-Setup-v%VERSION%.exe
echo    📊 파일 크기: 
for %%F in ("%OUTPUT_DIR%\ClockApp-Ver2-Professional-Setup-v%VERSION%.exe") do echo       %%~zF bytes
echo    📅 빌드 시간: %BUILD_DATE% %BUILD_TIME%
echo.
echo [%COLOR_WARNING%m💡 다음 단계:[0m
echo    1. 디지털 서명 추가 (선택사항)
echo    2. Windows Defender SmartScreen 해제 신청
echo    3. GitHub Release 배포
echo    4. 사용자 테스트
echo.

pause
goto :eof

:: =====================================================================================
:: 함수 정의
:: =====================================================================================

:print_header
echo.
echo [%COLOR_HEADER%m╔══════════════════════════════════════════════════════════════════════════════════╗[0m
echo [%COLOR_HEADER%m║                         ClockApp Ver2 Professional Installer                      ║[0m
echo [%COLOR_HEADER%m║                              프로페셔널 GUI 인스톨러 빌더                              ║[0m
echo [%COLOR_HEADER%m║                                                                                  ║[0m
echo [%COLOR_HEADER%m║  🎯 특징:                                                                         ║[0m
echo [%COLOR_HEADER%m║    • Modern Windows 11 스타일 UI                                                  ║[0m
echo [%COLOR_HEADER%m║    • Ver1 자동 감지 및 제거                                                         ║[0m
echo [%COLOR_HEADER%m║    • 설정 자동 마이그레이션                                                          ║[0m
echo [%COLOR_HEADER%m║    • 다국어 지원 (한/영/일)                                                         ║[0m
echo [%COLOR_HEADER%m║    • 디지털 서명 준비됨                                                             ║[0m
echo [%COLOR_HEADER%m║                                                                                  ║[0m
echo [%COLOR_HEADER%m║  Developer: KoreawookDevTeam                                                     ║[0m
echo [%COLOR_HEADER%m║  Version: 2.0.0                                                                  ║[0m
echo [%COLOR_HEADER%m╚══════════════════════════════════════════════════════════════════════════════════╝[0m
echo.
goto :eof

:check_requirements
echo    • Inno Setup 확인 중...
where iscc >nul 2>&1
if !errorlevel! neq 0 (
    echo [%COLOR_ERROR%m    ❌ Inno Setup이 설치되지 않았거나 PATH에 없습니다.[0m
    echo [%COLOR_ERROR%m       다운로드: https://jrsoftware.org/isinfo.php[0m
    exit /b 1
)
echo [%COLOR_SUCCESS%m    ✅ Inno Setup 찾음[0m

echo    • 스크립트 파일 확인 중...
if not exist "%SCRIPT_NAME%" (
    echo [%COLOR_ERROR%m    ❌ %SCRIPT_NAME% 파일을 찾을 수 없습니다.[0m
    exit /b 1
)
echo [%COLOR_SUCCESS%m    ✅ 스크립트 파일 찾음[0m

echo    • PowerShell 확인 중...
where powershell >nul 2>&1
if !errorlevel! neq 0 (
    echo [%COLOR_WARNING%m    ⚠️  PowerShell을 찾을 수 없습니다. 일부 기능이 제한될 수 있습니다.[0m
) else (
    echo [%COLOR_SUCCESS%m    ✅ PowerShell 찾음[0m
)

goto :eof

:cleanup_previous_builds
if exist "%OUTPUT_DIR%\ClockApp-Ver2-Professional-Setup-v*.exe" (
    echo    • 이전 빌드 파일 삭제 중...
    del /q "%OUTPUT_DIR%\ClockApp-Ver2-Professional-Setup-v*.exe" 2>nul
    echo [%COLOR_SUCCESS%m    ✅ 이전 빌드 정리 완료[0m
) else (
    echo [%COLOR_INFO%m    ℹ️  이전 빌드 파일 없음[0m
)

if not exist "%OUTPUT_DIR%" (
    echo    • 출력 디렉토리 생성 중...
    mkdir "%OUTPUT_DIR%"
    echo [%COLOR_SUCCESS%m    ✅ 출력 디렉토리 생성됨[0m
)
goto :eof

:check_exe_file
echo    • 메인 실행 파일 확인 중...
if not exist "dist\ClockApp-Ver2.exe" (
    echo [%COLOR_ERROR%m    ❌ dist\ClockApp-Ver2.exe를 찾을 수 없습니다.[0m
    echo [%COLOR_ERROR%m       먼저 PyInstaller로 실행 파일을 빌드해 주세요.[0m
    echo [%COLOR_INFO%m       명령어: python -m PyInstaller ClockApp-Ver2.spec[0m
    exit /b 1
)

:: 파일 크기 확인
for %%F in ("dist\ClockApp-Ver2.exe") do set "exe_size=%%~zF"
echo [%COLOR_SUCCESS%m    ✅ 실행 파일 찾음 (크기: !exe_size! bytes)[0m

:: 파일이 너무 작으면 경고
if !exe_size! lss 10000000 (
    echo [%COLOR_WARNING%m    ⚠️  실행 파일이 예상보다 작습니다. 빌드를 확인해 주세요.[0m
)
goto :eof

:check_resources
echo    • 리소스 파일 확인 중...

:: 필수 파일들
set "required_files=LICENSE.txt README-Ver2.md clock_app.ico"
for %%f in (%required_files%) do (
    if not exist "%%f" (
        echo [%COLOR_WARNING%m    ⚠️  %%f 파일을 찾을 수 없습니다.[0m
    ) else (
        echo [%COLOR_SUCCESS%m    ✅ %%f 찾음[0m
    )
)

:: 스트레칭 이미지 폴더
if exist "stretchimage" (
    echo [%COLOR_SUCCESS%m    ✅ 스트레칭 이미지 폴더 찾음[0m
) else (
    echo [%COLOR_WARNING%m    ⚠️  stretchimage 폴더를 찾을 수 없습니다.[0m
)

:: 설정 파일들
if exist "clock_settings_ver2.json" (
    echo [%COLOR_SUCCESS%m    ✅ 기본 설정 파일 찾음[0m
) else (
    echo [%COLOR_WARNING%m    ⚠️  clock_settings_ver2.json 파일을 찾을 수 없습니다.[0m
)

goto :eof

:compile_installer
echo    • Inno Setup 컴파일 시작...
echo [%COLOR_INFO%m      컴파일러: iscc.exe[0m
echo [%COLOR_INFO%m      스크립트: %SCRIPT_NAME%[0m
echo.

:: 컴파일 실행
iscc "%SCRIPT_NAME%" /q
set "compile_result=!errorlevel!"

if !compile_result! neq 0 (
    echo.
    echo [%COLOR_ERROR%m    ❌ 컴파일 실패 (오류 코드: !compile_result!)[0m
    echo [%COLOR_ERROR%m       스크립트를 확인하고 다시 시도해 주세요.[0m
    exit /b 1
)

echo [%COLOR_SUCCESS%m    ✅ 컴파일 성공![0m
goto :eof

:verify_build
set "output_file=%OUTPUT_DIR%\ClockApp-Ver2-Professional-Setup-v%VERSION%.exe"

if not exist "!output_file!" (
    echo [%COLOR_ERROR%m    ❌ 출력 파일을 찾을 수 없습니다: !output_file![0m
    exit /b 1
)

:: 파일 크기 확인
for %%F in ("!output_file!") do set "installer_size=%%~zF"
echo [%COLOR_SUCCESS%m    ✅ 인스톨러 파일 생성됨[0m
echo [%COLOR_INFO%m      파일: !output_file![0m
echo [%COLOR_INFO%m      크기: !installer_size! bytes[0m

:: 파일 크기가 너무 작으면 경고
if !installer_size! lss 20000000 (
    echo [%COLOR_WARNING%m    ⚠️  인스톨러 파일이 예상보다 작습니다.[0m
)

:: 파일 서명 상태 확인 (선택사항)
where signtool >nul 2>&1
if !errorlevel! equ 0 (
    echo    • 디지털 서명 확인 중...
    signtool verify /pa "!output_file!" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [%COLOR_SUCCESS%m    ✅ 디지털 서명 확인됨[0m
    ) else (
        echo [%COLOR_WARNING%m    ⚠️  디지털 서명이 없습니다. (SmartScreen 경고 발생 가능)[0m
    )
)

goto :eof

:error_exit
echo.
echo [%COLOR_ERROR%m💥 빌드 실패![0m
echo [%COLOR_ERROR%m   오류가 발생했습니다. 위의 메시지를 확인하고 문제를 해결해 주세요.[0m
echo.
pause
exit /b 1