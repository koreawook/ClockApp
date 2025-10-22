"""
ClockApp Ver2 - 설정 관리 시스템
설정 파일 호환성 및 마이그레이션 기능 구현
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

class SettingsManager:
    """설정 파일 관리 및 마이그레이션 클래스"""
    
    def __init__(self):
        # AppData 경로 설정
        self.app_data_dir = Path(os.getenv('APPDATA')) / 'ClockApp'
        self.settings_file = self.app_data_dir / 'settings.json'
        self.backup_dir = self.app_data_dir / 'backup'
        self.cache_dir = self.app_data_dir / 'cache'
        self.logs_dir = self.app_data_dir / 'logs'
        
        # Ver1 설정 파일 경로 (실행 파일과 같은 폴더)
        self.ver1_settings = Path(__file__).parent / 'clock_settings.json'
        
        # 기본 설정값
        self.default_settings = {
            "version": "2.0",
            "app_settings": {
                "time_interval": 45,  # 45분 작업
                "break_duration": 15,  # 15분 휴식
                "break_enabled": True,
                "auto_start": False,
                "theme": "default"
            },
            "meal_settings": {
                "lunch": {
                    "hour": 12,
                    "minute": 0, 
                    "enabled": True
                },
                "dinner": {
                    "hour": 18,
                    "minute": 0,
                    "enabled": True
                }
            },
            "ui_settings": {
                "transparency": 0.9,
                "always_on_top": True,
                "minimize_to_tray": True,
                "window_position": {"x": 100, "y": 100}
            },
            "weather_settings": {
                "enabled": True,
                "api_key": "",
                "city": "Seoul",
                "country": "KR",
                "update_interval": 1800  # 30분
            }
        }
        
        # 디렉터리 생성
        self._create_directories()
        
    def _create_directories(self):
        """필요한 디렉터리 생성"""
        try:
            self.app_data_dir.mkdir(parents=True, exist_ok=True)
            self.backup_dir.mkdir(exist_ok=True)
            self.cache_dir.mkdir(exist_ok=True)
            self.logs_dir.mkdir(exist_ok=True)
            print(f"✓ 디렉터리 생성 완료: {self.app_data_dir}")
        except Exception as e:
            print(f"❌ 디렉터리 생성 실패: {e}")
            
    def check_ver1_settings(self):
        """Ver1 설정 파일 존재 여부 확인"""
        return self.ver1_settings.exists()
        
    def migrate_from_ver1(self):
        """Ver1 설정을 Ver2 형식으로 마이그레이션"""
        if not self.check_ver1_settings():
            print("Ver1 설정 파일이 없습니다.")
            return False
            
        try:
            # Ver1 설정 로드
            with open(self.ver1_settings, 'r', encoding='utf-8') as f:
                ver1_data = json.load(f)
                
            print(f"Ver1 설정 발견: {ver1_data}")
            
            # Ver2 형식으로 변환
            migrated_settings = self.default_settings.copy()
            
            # Ver1 → Ver2 매핑
            if "time_interval" in ver1_data:
                migrated_settings["app_settings"]["time_interval"] = ver1_data["time_interval"]
                
            if "lunch_hour" in ver1_data and "lunch_minute" in ver1_data:
                migrated_settings["meal_settings"]["lunch"]["hour"] = ver1_data["lunch_hour"]
                migrated_settings["meal_settings"]["lunch"]["minute"] = ver1_data["lunch_minute"]
                
            if "dinner_hour" in ver1_data and "dinner_minute" in ver1_data:
                migrated_settings["meal_settings"]["dinner"]["hour"] = ver1_data["dinner_hour"]
                migrated_settings["meal_settings"]["dinner"]["minute"] = ver1_data["dinner_minute"]
                
            if "break_enabled" in ver1_data:
                migrated_settings["app_settings"]["break_enabled"] = ver1_data["break_enabled"]
                
            if "lunch_enabled" in ver1_data:
                migrated_settings["meal_settings"]["lunch"]["enabled"] = ver1_data["lunch_enabled"]
                
            if "dinner_enabled" in ver1_data:
                migrated_settings["meal_settings"]["dinner"]["enabled"] = ver1_data["dinner_enabled"]
            
            # 마이그레이션 정보 추가
            migrated_settings["migration"] = {
                "from_version": "1.0",
                "migrated_at": datetime.now().isoformat(),
                "original_file": str(self.ver1_settings)
            }
            
            # Ver2 설정 파일로 저장
            self.save_settings(migrated_settings)
            
            # Ver1 설정 백업
            backup_file = self.backup_dir / f'settings_v1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            shutil.copy2(self.ver1_settings, backup_file)
            
            print(f"✅ Ver1 → Ver2 마이그레이션 완료!")
            print(f"   백업 위치: {backup_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 마이그레이션 실패: {e}")
            return False
            
    def load_settings(self):
        """설정 로드 (우선순위: Ver2 → Ver1 → 기본값)"""
        
        # 1. Ver2 설정 파일 확인
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                print(f"✓ Ver2 설정 로드: {self.settings_file}")
                return settings
            except Exception as e:
                print(f"Ver2 설정 로드 실패: {e}")
                
        # 2. Ver1 설정 자동 마이그레이션
        if self.check_ver1_settings():
            print("Ver1 설정 발견 - 자동 마이그레이션 시작")
            if self.migrate_from_ver1():
                return self.load_settings()  # 마이그레이션 후 재시도
                
        # 3. 기본값 사용
        print("기본 설정값 사용")
        return self.default_settings
        
    def save_settings(self, settings):
        """설정 저장"""
        try:
            # 버전 정보 업데이트
            settings["version"] = "2.0"
            settings["last_updated"] = datetime.now().isoformat()
            
            # 설정 파일 저장
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
                
            print(f"✅ 설정 저장 완료: {self.settings_file}")
            
            # 백업 생성
            self._create_backup(settings)
            
            return True
            
        except Exception as e:
            print(f"❌ 설정 저장 실패: {e}")
            return False
            
    def _create_backup(self, settings):
        """설정 백업 생성"""
        try:
            backup_file = self.backup_dir / f'settings_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
                
            # 오래된 백업 파일 정리 (최대 10개 보관)
            backup_files = sorted(self.backup_dir.glob('settings_backup_*.json'))
            if len(backup_files) > 10:
                for old_file in backup_files[:-10]:
                    old_file.unlink()
                    
        except Exception as e:
            print(f"백업 생성 실패: {e}")
            
    def get_ver1_compatible_settings(self, ver2_settings):
        """Ver2 설정을 Ver1 형식으로 변환 (역호환성)"""
        ver1_format = {
            "time_interval": ver2_settings["app_settings"]["time_interval"],
            "lunch_hour": ver2_settings["meal_settings"]["lunch"]["hour"],
            "lunch_minute": ver2_settings["meal_settings"]["lunch"]["minute"],
            "dinner_hour": ver2_settings["meal_settings"]["dinner"]["hour"],
            "dinner_minute": ver2_settings["meal_settings"]["dinner"]["minute"],
            "break_enabled": ver2_settings["app_settings"]["break_enabled"],
            "lunch_enabled": ver2_settings["meal_settings"]["lunch"]["enabled"],
            "dinner_enabled": ver2_settings["meal_settings"]["dinner"]["enabled"]
        }
        
        return ver1_format
        
    def export_settings(self, export_path):
        """설정 내보내기"""
        try:
            settings = self.load_settings()
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            print(f"✅ 설정 내보내기 완료: {export_path}")
            return True
        except Exception as e:
            print(f"❌ 설정 내보내기 실패: {e}")
            return False
            
    def import_settings(self, import_path):
        """설정 가져오기"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
                
            # 설정 유효성 검증
            if self._validate_settings(imported_settings):
                self.save_settings(imported_settings)
                print(f"✅ 설정 가져오기 완료: {import_path}")
                return True
            else:
                print("❌ 유효하지 않은 설정 파일")
                return False
                
        except Exception as e:
            print(f"❌ 설정 가져오기 실패: {e}")
            return False
            
    def _validate_settings(self, settings):
        """설정 파일 유효성 검증"""
        required_keys = ["app_settings", "meal_settings"]
        return all(key in settings for key in required_keys)
        
    def reset_settings(self):
        """설정 초기화"""
        try:
            # 현재 설정 백업
            if self.settings_file.exists():
                backup_file = self.backup_dir / f'settings_reset_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                shutil.copy2(self.settings_file, backup_file)
                
            # 기본값으로 초기화
            self.save_settings(self.default_settings.copy())
            print("✅ 설정이 초기화되었습니다")
            return True
            
        except Exception as e:
            print(f"❌ 설정 초기화 실패: {e}")
            return False
            
    def get_settings_info(self):
        """설정 파일 정보 반환"""
        info = {
            "ver2_exists": self.settings_file.exists(),
            "ver1_exists": self.check_ver1_settings(),
            "settings_path": str(self.settings_file),
            "backup_dir": str(self.backup_dir),
            "app_data_dir": str(self.app_data_dir)
        }
        
        if self.settings_file.exists():
            try:
                settings = self.load_settings()
                info["version"] = settings.get("version", "unknown")
                info["last_updated"] = settings.get("last_updated", "unknown")
                if "migration" in settings:
                    info["migrated_from"] = settings["migration"].get("from_version")
                    info["migration_date"] = settings["migration"].get("migrated_at")
            except:
                pass
                
        return info

# 사용 예시
if __name__ == "__main__":
    # 설정 관리자 초기화
    settings_manager = SettingsManager()
    
    # 설정 로드 (자동 마이그레이션 포함)
    settings = settings_manager.load_settings()
    print("현재 설정:", json.dumps(settings, indent=2, ensure_ascii=False))
    
    # 설정 정보 출력
    info = settings_manager.get_settings_info()
    print("\n설정 파일 정보:")
    for key, value in info.items():
        print(f"  {key}: {value}")