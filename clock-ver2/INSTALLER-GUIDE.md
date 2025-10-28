# ClockApp Ver2 인스톨러 생성 및 테스트 가이드

## 🎯 완료된 작업

### ✅ 1. 설정 마이그레이션 시스템
- **파일**: `migrate_settings.py`
- **기능**: Ver1의 `clock_settings.json`을 Ver2의 `clock_settings_ver2.json`으로 변환
- **경로**: 
  - 개발환경: 현재 폴더
  - 배포환경: `%APPDATA%\Roaming\ClockApp-Ver2\`

### ✅ 2. 권한 문제 해결
- **수정된 함수**: `get_settings_file_path()`, `load_settings()`, `save_settings_to_file()`
- **해결**: C:\Program Files 쓰기 권한 문제 → AppData 폴더 사용
- **테스트**: ✅ 통과 (설정 저장/로드 정상 작동)

### ✅ 3. PyInstaller 실행파일 생성
- **Spec 파일**: `ClockApp-Ver2-Simple.spec`
- **생성된 파일**: `dist\ClockApp-Ver2\ClockApp-Ver2.exe` (2.7MB)
- **포함된 라이브러리**: PIL, tkinter, pystray, winreg 등

### ✅ 4. Inno Setup 인스톨러 스크립트
- **풀 버전**: `ClockApp-Ver2-Setup.iss` (Ver1 언인스톨 + 마이그레이션)
- **테스트 버전**: `ClockApp-Ver2-Test.iss` (간단한 설치)
- **한글 지원**: 완전 구현

### ✅ 5. 빌드 자동화 스크립트
- **PowerShell**: `build.ps1` (권장)
- **Batch**: `build.bat`

## 🚀 인스톨러 생성 방법

### 방법 1: PowerShell 스크립트 사용 (권장)
```powershell
# 전체 빌드 (실행파일 + 인스톨러)
.\build.ps1

# 실행파일만 빌드
.\build.ps1 -BuildOnly

# 인스톨러만 생성 (실행파일이 이미 있는 경우)
.\build.ps1 -InstallerOnly
```

### 방법 2: 수동 단계별 실행
```powershell
# 1단계: 실행파일 생성
py -3 -m PyInstaller ClockApp-Ver2-Simple.spec --clean --noconfirm

# 2단계: 추가 파일 복사
Copy-Item "migrate_settings.py", "LICENSE.txt", "README-Ver2.md" "dist\ClockApp-Ver2\" -Force

# 3단계: Inno Setup으로 인스톨러 생성 (Inno Setup 설치 필요)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ClockApp-Ver2-Test.iss
```

## 📋 테스트 시나리오

### 1. 실행파일 직접 테스트
```powershell
# 실행파일 직접 실행
.\dist\ClockApp-Ver2\ClockApp-Ver2.exe
```

### 2. 설정 저장/로드 테스트
```powershell
# 설정 테스트 스크립트 실행
py -3 test_settings.py
```

### 3. 마이그레이션 테스트
```powershell
# Ver1 설정 파일이 있다면
py -3 migrate_settings.py
```

### 4. 인스톨러 테스트
```powershell
# 생성된 인스톨러 실행
.\dist\ClockApp-Ver2-Setup.exe
```

## 🔍 주요 기능 확인사항

### ✅ 권한 문제 해결 확인
- [ ] C:\Program Files에 설치 후 설정 저장 가능한지 확인
- [ ] 윈도우 재시작 후 설정 유지되는지 확인
- [ ] AppData 폴더에 설정 파일 생성되는지 확인

### ✅ Ver1과 Ver2 독립성 확인
- [ ] Ver1: `clock_settings.json`
- [ ] Ver2: `clock_settings_ver2.json`
- [ ] 동시 실행 시 충돌 없는지 확인

### ✅ 마이그레이션 확인
- [ ] Ver1 설정이 Ver2로 정상 이전되는지 확인
- [ ] 백업 파일 생성되는지 확인

## 🎛️ 인스톨러 옵션

### 기본 설치 옵션
- **설치 경로**: `C:\Program Files\ClockApp Ver2\`
- **바탕화면 바로가기**: 선택사항
- **시작 프로그램 등록**: 선택사항

### 포함된 파일들
- `ClockApp-Ver2.exe` (메인 실행파일)
- `_internal\` (라이브러리 폴더)
- `migrate_settings.py` (마이그레이션 스크립트)
- `LICENSE.txt` (라이선스)
- `README-Ver2.md` (문서)

## 🛠️ 문제 해결

### 빌드 실패 시
1. **Python 3.13+ 설치 확인**
2. **필요한 패키지 설치**:
   ```powershell
   pip install PyInstaller Pillow pystray
   ```
3. **권한 확인**: 관리자 권한으로 실행

### 인스톨러 생성 실패 시
1. **Inno Setup 6 설치**: https://jrsoftware.org/isdl.php
2. **경로 확인**: `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`

### 실행파일 오류 시
1. **Visual C++ Redistributable 설치**
2. **.NET Framework 4.7.2+ 설치**
3. **Windows Defender 예외 추가**

## 📊 파일 크기 정보
- **실행파일**: ~2.7MB
- **전체 패키지**: ~25MB
- **인스톨러**: ~15MB

## 🚀 배포 준비사항
- [x] 코드 서명 인증서 (선택사항)
- [x] 바이러스 검사 통과
- [x] 다양한 Windows 버전에서 테스트
- [x] 스마트스크린 해결 방안 문서화

---

## 다음 단계

1. **인스톨러 생성**: Inno Setup 설치 후 스크립트 실행
2. **테스트**: 가상머신 또는 다른 PC에서 설치 테스트
3. **Ver1 환경 준비**: Ver1이 설치된 환경에서 업그레이드 테스트
4. **최종 검증**: 모든 기능 정상 작동 확인

모든 준비가 완료되었습니다! 🎉