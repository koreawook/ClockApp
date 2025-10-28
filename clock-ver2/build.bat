@echo off
chcp 65001 >nul
echo ===============================================
echo ClockApp Ver2 빌드 및 인스톨러 생성 스크립트
echo ===============================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [1/4] 기존 빌드 파일 정리...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
mkdir dist 2>nul

echo.
echo [2/4] PyInstaller로 실행파일 생성...
py -3 -m PyInstaller ClockApp-Ver2.spec --clean --noconfirm

if not exist "dist\ClockApp-Ver2\ClockApp-Ver2.exe" (
    echo ❌ 실행파일 생성 실패!
    echo 다음을 확인해주세요:
    echo - Python 3가 설치되어 있나요?
    echo - PyInstaller가 설치되어 있나요? ^(pip install pyinstaller^)
    echo - 필요한 패키지들이 설치되어 있나요?
    pause
    exit /b 1
)

echo ✅ 실행파일 생성 완료: dist\ClockApp-Ver2\ClockApp-Ver2.exe

echo.
echo [3/4] 추가 파일들 복사...
copy "migrate_settings.py" "dist\ClockApp-Ver2\" >nul 2>&1
copy "LICENSE.txt" "dist\ClockApp-Ver2\" >nul 2>&1
copy "README-Ver2.md" "dist\ClockApp-Ver2\" >nul 2>&1
copy "*.png" "dist\ClockApp-Ver2\" >nul 2>&1
copy "*.ico" "dist\ClockApp-Ver2\" >nul 2>&1

echo ✅ 추가 파일들 복사 완료

echo.
echo [4/4] Inno Setup 인스톨러 생성...
echo 📋 Inno Setup이 설치되어 있다면 다음 명령을 실행하세요:
echo.
echo "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ClockApp-Ver2-Setup.iss
echo.
echo 또는 Inno Setup Compiler를 직접 실행하여 ClockApp-Ver2-Setup.iss 파일을 컴파일하세요.

echo.
echo ===============================================
echo 🎉 빌드 완료!
echo ===============================================
echo 📁 실행파일 위치: dist\ClockApp-Ver2\
echo 📦 인스톨러 생성 필요: ClockApp-Ver2-Setup.iss
echo.
echo 테스트를 위해 dist\ClockApp-Ver2\ClockApp-Ver2.exe를 직접 실행해볼 수 있습니다.
echo.

pause