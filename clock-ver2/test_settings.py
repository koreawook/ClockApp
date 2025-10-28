#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClockApp Ver2 설정 저장/로드 테스트 스크립트
"""

import os
import sys
import json

def get_settings_file_path():
    """설정 파일 경로 반환 (권한 문제 해결을 위해 AppData 사용)"""
    if getattr(sys, 'frozen', False):
        # 패키징된 실행파일인 경우 사용자 AppData 폴더 사용
        appdata_path = os.path.expanduser("~\\AppData\\Roaming\\ClockApp-Ver2")
        if not os.path.exists(appdata_path):
            try:
                os.makedirs(appdata_path)
                print(f"설정 폴더 생성: {appdata_path}")
            except Exception as e:
                print(f"설정 폴더 생성 실패: {e}")
                # 실패 시 현재 폴더 사용
                return os.path.join(os.path.dirname(sys.executable), "clock_settings_ver2.json")
        return os.path.join(appdata_path, "clock_settings_ver2.json")
    else:
        # 개발 중에는 현재 스크립트 폴더 사용
        return os.path.join(os.path.dirname(__file__), "clock_settings_ver2.json")

def save_settings_to_file(settings):
    """설정값을 파일에 저장"""
    try:
        settings_file = get_settings_file_path()
        print(f"설정 저장 경로: {settings_file}")
        
        # 설정 폴더가 없으면 생성
        settings_dir = os.path.dirname(settings_file)
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)
            print(f"설정 폴더 생성: {settings_dir}")
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        print(f"설정 저장 성공: {settings}")
        return True
    except Exception as e:
        print(f"설정 저장 실패: {e}")
        return False

def load_settings():
    """설정 파일에서 설정값 불러오기"""
    default_settings = {
        "time_interval": 20,        # 반복시간 20분
        "lunch_hour": 12,
        "lunch_minute": 10,         # 점심 12:10
        "dinner_hour": 18,          # 저녁 6시
        "dinner_minute": 0,
        "break_enabled": True,      # 휴식 알림 활성화
        "lunch_enabled": True,      # 점심 알림 활성화
        "dinner_enabled": False     # 저녁 알림 비활성화
    }
    
    try:
        settings_file = get_settings_file_path()
        print(f"설정 파일 경로: {settings_file}")
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                print(f"설정 불러오기 성공: {settings}")
                return settings
        else:
            print("설정 파일이 없어서 기본값 사용")
            return default_settings
    except Exception as e:
        print(f"설정 불러오기 실패, 기본값 사용: {e}")
        return default_settings

def main():
    print("=== ClockApp Ver2 설정 저장/로드 테스트 ===")
    
    # 1. 현재 환경 확인
    print(f"\n1. 환경 정보")
    print(f"   패키징 상태: {getattr(sys, 'frozen', False)}")
    print(f"   현재 디렉토리: {os.getcwd()}")
    
    # 2. 설정 파일 경로 확인
    print(f"\n2. 설정 파일 경로")
    settings_path = get_settings_file_path()
    print(f"   설정 파일: {settings_path}")
    print(f"   파일 존재: {os.path.exists(settings_path)}")
    
    # 3. 기본 설정 로드 테스트
    print(f"\n3. 설정 로드 테스트")
    settings = load_settings()
    
    # 4. 설정 수정 및 저장 테스트
    print(f"\n4. 설정 저장 테스트")
    test_settings = {
        "time_interval": 25,        # 25분으로 변경
        "lunch_hour": 12,
        "lunch_minute": 30,         # 점심 12:30으로 변경
        "dinner_hour": 19,          # 저녁 7시로 변경
        "dinner_minute": 0,
        "break_enabled": True,
        "lunch_enabled": True,
        "dinner_enabled": True      # 저녁 알림 활성화로 변경
    }
    
    if save_settings_to_file(test_settings):
        print("   설정 저장 성공!")
    else:
        print("   설정 저장 실패!")
        return
    
    # 5. 저장된 설정 다시 로드 테스트
    print(f"\n5. 저장된 설정 재로드 테스트")
    reloaded_settings = load_settings()
    
    # 6. 설정 값 비교
    print(f"\n6. 설정 값 검증")
    if reloaded_settings == test_settings:
        print("   ✅ 설정 값이 정확히 일치합니다!")
    else:
        print("   ❌ 설정 값에 차이가 있습니다!")
        print(f"   저장한 값: {test_settings}")
        print(f"   로드한 값: {reloaded_settings}")
    
    # 7. 패키징된 환경 시뮬레이션
    print(f"\n7. 패키징된 환경 시뮬레이션")
    original_frozen = getattr(sys, 'frozen', None)
    sys.frozen = True
    
    packaged_path = get_settings_file_path()
    print(f"   패키징된 환경 설정 경로: {packaged_path}")
    print(f"   AppData 폴더 사용: {'AppData' in packaged_path}")
    
    # 원래 상태로 복원
    if original_frozen is None:
        if hasattr(sys, 'frozen'):
            delattr(sys, 'frozen')
    else:
        sys.frozen = original_frozen
    
    print(f"\n=== 테스트 완료 ===")

if __name__ == "__main__":
    main()

import json
import os

def load_settings():
    """설정 파일에서 설정값 불러오기"""
    default_settings = {
        "time_interval": 20,        # 반복시간 20분
        "lunch_hour": 12,
        "lunch_minute": 10,         # 점심 12:10
        "dinner_hour": 18,          # 저녁 6시
        "dinner_minute": 0,
        "break_enabled": True,      # 휴식 알림 활성화
        "lunch_enabled": True,      # 점심 알림 활성화
        "dinner_enabled": False     # 저녁 알림 비활성화
    }
    
    try:
        settings_file = os.path.join(os.path.dirname(__file__), "clock_settings.json")
        print(f"🔍 설정 파일 경로: {settings_file}")
        print(f"📁 파일 존재 여부: {os.path.exists(settings_file)}")
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                print(f"✅ 설정 불러오기 성공: {settings}")
                return settings
        else:
            print("❌ 설정 파일이 없어서 기본값 사용")
            return default_settings
    except Exception as e:
        print(f"❌ 설정 불러오기 실패, 기본값 사용: {e}")
        return default_settings

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 ClockApp Ver2 - 설정 로드 테스트")
    print("=" * 60)
    
    settings = load_settings()
    
    print("\n📋 최종 설정값:")
    print(f"   🔄 휴식 간격: {settings['time_interval']}분")
    print(f"   🍱 점심시간: {settings['lunch_hour']:02d}:{settings['lunch_minute']:02d}")
    print(f"   🍽️ 저녁시간: {settings['dinner_hour']:02d}:{settings['dinner_minute']:02d}")
    print(f"   🔔 휴식 알림: {'활성화' if settings.get('break_enabled', True) else '비활성화'}")
    print(f"   🍱 점심 알림: {'활성화' if settings.get('lunch_enabled', True) else '비활성화'}")
    print(f"   🍽️ 저녁 알림: {'활성화' if settings.get('dinner_enabled', False) else '비활성화'}")
    print("=" * 60)