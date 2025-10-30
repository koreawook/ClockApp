# 레벨 데이터 저장 시스템 (Level Data Storage System)

## 📁 데이터 저장 위치

### 배포된 실행파일 환경
```
%APPDATA%\ClockApp-Ver2\rest_level_data.json
```
**실제 경로 예시:**
```
C:\Users\[사용자명]\AppData\Roaming\ClockApp-Ver2\rest_level_data.json
```

### 개발환경 (Python 스크립트)
```
[스크립트 폴더]\rest_level_data.json
```
**실제 경로 예시:**
```
D:\down\homepage\ClockApp\clock-ver2\rest_level_data.json
```

## 📊 데이터 구조

### JSON 파일 형식
```json
{
  "level": 1,
  "total_seconds": 0
}
```

### 필드 설명
- **level**: 현재 레벨 (1부터 시작)
- **total_seconds**: 누적 휴식 시간 (초 단위)

## 🔄 자동 저장 시점

### 1. 휴식 팝업 종료 시
- 휴식 팝업이 닫힐 때마다 경과 시간을 누적
- 새로운 레벨 계산 후 저장

### 2. 실시간 레벨업 시
- 휴식 팝업이 떠있는 동안 레벨업 발생 시 즉시 저장
- 데이터 무결성 보장

### 3. 애플리케이션 종료 시
- 현재 상태 최종 저장 (만약 데이터가 있다면)

## 🔒 데이터 영속성 (재부팅 안전성)

### ✅ 완전히 안전한 항목들
1. **레벨 진행도**: 재부팅 후에도 완전히 복원
2. **누적 휴식 시간**: 초 단위까지 정확히 복원
3. **현재 레벨**: 재부팅 후에도 정확한 레벨 유지

### 📝 저장 메커니즘
```python
def save_level_data(level, total_seconds):
    """레벨 데이터 저장"""
    try:
        file_path = get_level_data_file_path()
        data = {
            "level": level,
            "total_seconds": total_seconds
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"레벨 데이터 저장: 레벨 {level}, 누적시간 {total_seconds}초")
        return True
    except Exception as e:
        print(f"레벨 데이터 저장 실패: {e}")
        return False
```

### 📖 로드 메커니즘
```python
def load_level_data():
    """레벨 데이터 로드"""
    try:
        file_path = get_level_data_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"레벨 데이터 로드: 레벨 {data.get('level', 1)}, 누적시간 {data.get('total_seconds', 0)}초")
                return data
    except Exception as e:
        print(f"레벨 데이터 로드 실패: {e}")
    
    # 기본값 반환
    return {
        "level": 1,
        "total_seconds": 0
    }
```

## 🎮 레벨 시스템 상세

### 레벨 계산 공식
```
레벨 1: 30초
레벨 2: 60초 (누적 90초)
레벨 3: 120초 (누적 210초)
레벨 4: 240초 (누적 450초)
...
레벨 N: 2^(N-1) × 30초
```

### 레벨별 필요 시간
| 레벨 | 이번 레벨 필요시간 | 누적 필요시간 | 실제 시간 |
|------|-------------------|---------------|-----------|
| 1    | 30초              | 30초          | 0분 30초  |
| 2    | 60초              | 90초          | 1분 30초  |
| 3    | 120초             | 210초         | 3분 30초  |
| 4    | 240초             | 450초         | 7분 30초  |
| 5    | 480초             | 930초         | 15분 30초 |
| 6    | 960초             | 1890초        | 31분 30초 |
| 7    | 1920초            | 3810초        | 63분 30초 |
| 8    | 3840초            | 7650초        | 127분 30초|
| 9    | 7680초            | 15330초       | 255분 30초|
| 10   | 15360초           | 30690초       | 511분 30초|

## 🛡️ 오류 처리 및 복구

### 파일 손상 시 복구
```python
# 파일이 손상되었거나 없을 경우 기본값으로 시작
return {
    "level": 1,
    "total_seconds": 0
}
```

### 폴더 생성 실패 시 대안
```python
# AppData 폴더 생성 실패 시 실행파일 폴더에 저장
return os.path.join(os.path.dirname(sys.executable), "rest_level_data.json")
```

## 🔍 디버깅 및 확인

### 콘솔 메시지
```
레벨 데이터 로드: 레벨 3, 누적시간 210초
레벨 데이터 저장: 레벨 3, 누적시간 240초
```

### 수동 파일 확인
1. Windows + R → `%APPDATA%\ClockApp-Ver2`
2. `rest_level_data.json` 파일 열기
3. JSON 형식으로 데이터 확인

## ⚠️ 주의사항

### 파일 위치 변경 금지
- 데이터 파일을 임의로 이동하면 진행도 초기화됨
- AppData 폴더는 Windows가 자동으로 관리

### 수동 편집 주의
- JSON 형식을 정확히 지켜야 함
- 잘못된 형식 시 기본값으로 초기화됨

### 백업 권장
- 중요한 진행도는 주기적으로 백업 권장
- 파일 크기가 작아 쉽게 백업 가능

## 🎯 결론

**레벨 및 누적시간 데이터는 완전히 영속적으로 저장됩니다!**

✅ **재부팅해도 안전**
✅ **컴퓨터 종료해도 안전** 
✅ **앱 재실행해도 안전**
✅ **Windows 업데이트해도 안전**

사용자의 모든 휴식 진행도가 안전하게 보존됩니다.