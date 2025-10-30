# ClockApp Ver2 빌드 및 인스톨러 생성 PowerShell 스크립트
# UTF-8 인코딩 지원

param(
    [switch]$BuildOnly,
    [switch]$InstallerOnly,
    [switch]$Clean
)

# 한글 출력 지원
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "ClockApp Ver2 빌드 및 인스톨러 생성 스크립트" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# 스크립트 디렉토리로 이동
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 함수: 에러 처리
function Write-Error-Exit {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# 함수: 성공 메시지
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

# 함수: 정보 메시지
function Write-Info {
    param([string]$Message)
    Write-Host "📋 $Message" -ForegroundColor Yellow
}

# 정리 작업
if ($Clean -or -not $InstallerOnly) {
    Write-Host "[1/4] 기존 빌드 파일 정리..." -ForegroundColor Blue
    
    if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
    if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
    New-Item -ItemType Directory -Path "dist" -Force | Out-Null
    
    Write-Success "기존 빌드 파일 정리 완료"
}

# PyInstaller 빌드
if (-not $InstallerOnly) {
    Write-Host ""
    Write-Host "[2/4] PyInstaller로 실행파일 생성..." -ForegroundColor Blue
    
    # Python 및 PyInstaller 확인
    try {
        $pythonVersion = py -3 --version 2>&1
        Write-Info "Python 버전: $pythonVersion"
    } catch {
        Write-Error-Exit "Python 3가 설치되어 있지 않습니다. https://python.org에서 설치해주세요."
    }
    
    try {
        py -3 -c "import PyInstaller" 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Info "PyInstaller 설치 중..."
            py -3 -m pip install pyinstaller
        }
    } catch {
        Write-Error-Exit "PyInstaller 설치에 실패했습니다."
    }
    
    # 필요한 패키지 확인
    $required_packages = @("PIL", "pystray", "tkinter")
    foreach ($package in $required_packages) {
        try {
            py -3 -c "import $package" 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Info "$package 패키지가 없습니다. 설치를 진행합니다..."
                if ($package -eq "PIL") {
                    py -3 -m pip install Pillow
                } elseif ($package -eq "pystray") {
                    py -3 -m pip install pystray
                }
            }
        } catch {
            Write-Info "$package 패키지 확인 중 오류 발생"
        }
    }
    
    # PyInstaller 실행
    py -3 -m PyInstaller ClockApp-Ver2.spec --clean --noconfirm
    
    if (-not (Test-Path "dist\ClockApp-Ver2\ClockApp-Ver2.exe")) {
        Write-Error-Exit "실행파일 생성에 실패했습니다. 로그를 확인해주세요."
    }
    
    Write-Success "실행파일 생성 완료: dist\ClockApp-Ver2\ClockApp-Ver2.exe"
    
    # 파일 크기 확인
    $exeSize = (Get-Item "dist\ClockApp-Ver2\ClockApp-Ver2.exe").Length
    $exeSizeMB = [math]::Round($exeSize / 1MB, 2)
    Write-Info "실행파일 크기: $exeSizeMB MB"
}

# 추가 파일 복사
if (-not $InstallerOnly) {
    Write-Host ""
    Write-Host "[3/4] 추가 파일들 복사..." -ForegroundColor Blue
    
    $additionalFiles = @(
        "migrate_settings.py",
        "LICENSE.txt",
        "README-Ver2.md"
    )
    
    foreach ($file in $additionalFiles) {
        if (Test-Path $file) {
            Copy-Item $file "dist\ClockApp-Ver2\" -Force
            Write-Info "복사됨: $file"
        } else {
            Write-Info "파일 없음: $file"
        }
    }
    
    # 아이콘 파일들 복사
    Get-ChildItem "*.png", "*.ico" | ForEach-Object {
        Copy-Item $_.FullName "dist\ClockApp-Ver2\" -Force
        Write-Info "복사됨: $($_.Name)"
    }
    
    Write-Success "추가 파일들 복사 완료"
}

# Inno Setup 인스톨러 생성
if (-not $BuildOnly) {
    Write-Host ""
    Write-Host "[4/4] Inno Setup 인스톨러 생성..." -ForegroundColor Blue
    
    # Inno Setup 경로 찾기
    $innoSetupPaths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 5\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 5\ISCC.exe"
    )
    
    $innoSetupPath = $null
    foreach ($path in $innoSetupPaths) {
        if (Test-Path $path) {
            $innoSetupPath = $path
            break
        }
    }
    
    if ($innoSetupPath) {
        Write-Info "Inno Setup 발견: $innoSetupPath"
        
        # 인스톨러 스크립트 실행
        & $innoSetupPath "ClockApp-Ver2-Setup.iss"
        
        if (Test-Path "dist\ClockApp-Ver2-Setup.exe") {
            Write-Success "인스톨러 생성 완료: dist\ClockApp-Ver2-Setup.exe"
            
            # 인스톨러 파일 크기 확인
            $installerSize = (Get-Item "dist\ClockApp-Ver2-Setup.exe").Length
            $installerSizeMB = [math]::Round($installerSize / 1MB, 2)
            Write-Info "인스톨러 크기: $installerSizeMB MB"
        } else {
            Write-Error-Exit "인스톨러 생성에 실패했습니다."
        }
    } else {
        Write-Info "Inno Setup이 설치되어 있지 않습니다."
        Write-Info "다음 사이트에서 Inno Setup을 다운로드하여 설치하세요:"
        Write-Info "https://jrsoftware.org/isdl.php"
        Write-Info ""
        Write-Info "설치 후 다음 명령을 수동으로 실행하세요:"
        Write-Info '"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ClockApp-Ver2-Setup.iss'
    }
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🎉 빌드 완료!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

if (Test-Path "dist\ClockApp-Ver2\ClockApp-Ver2.exe") {
    Write-Host "📁 실행파일 위치: dist\ClockApp-Ver2\" -ForegroundColor Green
    Write-Host "🧪 테스트 실행: .\dist\ClockApp-Ver2\ClockApp-Ver2.exe" -ForegroundColor Yellow
}

if (Test-Path "dist\ClockApp-Ver2-Setup.exe") {
    Write-Host "📦 인스톨러 위치: dist\ClockApp-Ver2-Setup.exe" -ForegroundColor Green
    Write-Host "🚀 인스톨러 실행: .\dist\ClockApp-Ver2-Setup.exe" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "사용법:" -ForegroundColor Cyan
Write-Host "  .\build.ps1                 # 전체 빌드 (실행파일 + 인스톨러)" -ForegroundColor White
Write-Host "  .\build.ps1 -BuildOnly      # 실행파일만 빌드" -ForegroundColor White
Write-Host "  .\build.ps1 -InstallerOnly  # 인스톨러만 생성" -ForegroundColor White
Write-Host "  .\build.ps1 -Clean          # 정리 후 전체 빌드" -ForegroundColor White
Write-Host ""

if (-not $BuildOnly -and -not $InstallerOnly) {
    $response = Read-Host "테스트를 위해 실행파일을 실행하시겠습니까? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        if (Test-Path "dist\ClockApp-Ver2\ClockApp-Ver2.exe") {
            Start-Process "dist\ClockApp-Ver2\ClockApp-Ver2.exe"
        }
    }
}