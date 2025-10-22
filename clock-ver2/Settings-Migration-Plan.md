# 🔄 ClockApp Ver2 - 설정 파일 호환성 가이드

## 📁 설정 파일 위치 변경 계획

### 🎯 현재 상황 (Ver1)
- **위치**: 실행파일과 같은 폴더 (`clock_settings.json`)
- **문제**: 프로그램 업데이트 시 설정 파일 손실 위험

### 🚀 Ver2 개선 사항  
- **새 위치**: `%APPDATA%\ClockApp\settings.json`
- **호환성**: Ver1 설정 자동 감지 및 마이그레이션
- **버전 관리**: 설정 파일에 버전 정보 추가

## 📋 마이그레이션 전략

### 1️⃣ 설정 파일 우선순위
```
1. %APPDATA%\ClockApp\settings.json (Ver2 표준)
2. .\clock_settings.json (Ver1 호환)  
3. 기본값 사용
```

### 2️⃣ 자동 마이그레이션
- Ver1 설정 파일 발견 시 자동으로 AppData로 복사
- 원본 Ver1 설정은 보존 (백업)
- 마이그레이션 완료 후 알림 메시지

### 3️⃣ 설정 구조 개선
```json
{
    "version": "2.0",
    "app_settings": {
        "time_interval": 45,
        "break_enabled": true
    },
    "meal_settings": {
        "lunch": {"hour": 12, "minute": 0, "enabled": true},
        "dinner": {"hour": 18, "minute": 0, "enabled": true}
    },
    "ui_settings": {
        "theme": "default",
        "transparency": 0.9
    },
    "migration": {
        "from_version": "1.0",
        "migrated_at": "2025-10-22T13:15:00"
    }
}
```

## 🛠️ 구현 방법

### 📂 폴더 구조
```
%APPDATA%\ClockApp\
├── settings.json          # 메인 설정 파일
├── backup\               # 설정 백업
│   ├── settings_v1.json  # Ver1에서 마이그레이션된 설정
│   └── settings_backup.json
├── cache\               # 캐시 파일들  
│   └── weather_cache.json
└── logs\               # 로그 파일
    └── clockapp.log
```

### 🔄 호환성 보장
1. **Ver2 설치 시**: Ver1 설정 자동 감지
2. **Ver1 → Ver2**: 설정값 완벽 보존  
3. **Ver2 → Ver1**: 역호환성 지원 (필요 시)
4. **설정 동기화**: 두 버전 동시 사용 가능

---
*Ver1 사용자의 설정을 완벽하게 보존하는 업그레이드 경험 제공* 🔄