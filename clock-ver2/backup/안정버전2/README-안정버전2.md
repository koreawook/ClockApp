# ClockApp Ver2 - 안정버전2 백업

## 백업 일시
- **백업 날짜**: 2025년 10월 30일
- **백업 이유**: 휴식 시간 누적 기능과 스트레칭 이미지 표시가 안정적으로 작동하는 버전

## 주요 기능
✅ **완전히 작동하는 기능들**:
- 휴식 시간 누적 기능 (시간이 제대로 누적되어 저장됨)
- 스트레칭 이미지 표시 (7개 이미지가 랜덤으로 표시)
- 레벨 시스템 (누적 시간에 따른 레벨 증가)
- 시스템 트레이 아이콘
- 점심/저녁 시간 알림
- PyInstaller 빌드 호환성

## 해결된 문제들
1. **휴식 시간 누적 오류**: `save_level_data(level_data)` → `save_level_data(level_data['level'], level_data['total_seconds'])` 수정
2. **스트레칭 이미지 표시 실패**: PyInstaller `_internal` 폴더 경로 문제 해결
3. **디버그 로깅 시스템**: 상세한 로그를 통한 문제 추적 가능
4. **PyInstaller 빌드 안정성**: debug=True, console=True 설정으로 안정적 빌드

## 파일 구성
- `ClockApp-ver2.py`: 메인 애플리케이션 코드
- `ClockApp-Ver2.spec`: PyInstaller 빌드 설정
- `settings_manager.py`: 설정 관리 모듈
- `build.ps1`: 빌드 스크립트
- `ClockApp-Ver2-Setup.iss`: Inno Setup 인스톨러 설정
- `stretchimage/`: 스트레칭 이미지 7개 (PNG 파일)
- `dist/`: 빌드된 실행 파일과 라이브러리
- `clock_settings_ver2.json`: 기본 설정 파일

## 빌드 방법
```powershell
# 전체 빌드 (실행파일 + 인스톨러)
.\build.ps1

# 실행파일만 빌드
.\build.ps1 -BuildOnly

# 인스톨러만 생성
.\build.ps1 -InstallerOnly
```

## 설정 파일 위치
- **개발 중**: `clock_settings_ver2.json` (소스 폴더)
- **빌드 후**: `%AppData%\Roaming\ClockApp-Ver2\clock_settings_ver2.json`
- **레벨 데이터**: `%AppData%\Roaming\ClockApp-Ver2\rest_level_data.json`

## 디버그 로그
- `rest_popup_debug.txt`: 휴식 팝업 관련 로그
- `level_data_debug.txt`: 레벨 데이터 저장/로드 로그

## 레벨 시스템
- 레벨 1: 30초
- 레벨 2: 60초 (30 + 30)
- 레벨 3: 120초 (60 + 60)
- 레벨 4: 240초 (120 + 120)
- ...

## 안정성 검증
- ✅ 휴식 시간이 올바르게 누적됨
- ✅ 스트레칭 이미지가 정상 표시됨
- ✅ 레벨 업그레이드가 정상 작동함
- ✅ 시스템 트레이 아이콘 생성됨
- ✅ PyInstaller 빌드가 안정적임
- ✅ 인스톨러 생성이 정상 작동함

이 버전은 모든 주요 기능이 안정적으로 작동하는 것을 확인했습니다.