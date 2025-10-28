#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClockApp Ver1 -> Ver2 설정 마이그레이션 스크립트
Ver1의 clock_settings.json을 Ver2의 clock_settings_ver2.json으로 변환
"""

import os
import sys
import json
import shutil
from pathlib import Path

def get_ver1_settings_path():
    """Ver1 설정 파일 경로를 찾는다"""
    possible_paths = [
        # Program Files에 설치된 경우
        os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'ClockApp', 'clock_settings.json'),
        # 사용자 AppData에 있는 경우 (혹시 Ver1이 수정되었다면)
        os.path.expanduser('~\\AppData\\Roaming\\ClockApp\\clock_settings.json'),
        # 현재 사용자 폴더
        os.path.expanduser('~\\clock_settings.json'),
        # 데스크톱
        os.path.expanduser('~\\Desktop\\clock_settings.json'),
        # 문서 폴더
        os.path.expanduser('~\\Documents\\clock_settings.json')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Ver1 설정 파일 발견: {path}")
            return path
    
    print("Ver1 설정 파일을 찾을 수 없습니다.")
    return None

def get_ver2_settings_path():
    """Ver2 설정 파일 경로 반환"""
    appdata_path = os.path.expanduser("~\\AppData\\Roaming\\ClockApp-Ver2")
    if not os.path.exists(appdata_path):
        os.makedirs(appdata_path)
        print(f"Ver2 설정 폴더 생성: {appdata_path}")
    return os.path.join(appdata_path, "clock_settings_ver2.json")

def migrate_settings():
    """Ver1 설정을 Ver2로 마이그레이션"""
    print("=== ClockApp Ver1 -> Ver2 설정 마이그레이션 ===")
    
    # Ver1 설정 파일 찾기
    ver1_path = get_ver1_settings_path()
    if not ver1_path:
        print("마이그레이션할 Ver1 설정이 없습니다. 기본 설정으로 시작합니다.")
        return False
    
    # Ver2 설정 경로
    ver2_path = get_ver2_settings_path()
    
    try:
        # Ver1 설정 읽기
        with open(ver1_path, 'r', encoding='utf-8') as f:
            ver1_settings = json.load(f)
        print(f"Ver1 설정 로드 성공: {ver1_settings}")
        
        # Ver2 형식으로 변환 (필요시 필드 매핑)
        ver2_settings = {
            "time_interval": ver1_settings.get("time_interval", 20),
            "lunch_hour": ver1_settings.get("lunch_hour", 12),
            "lunch_minute": ver1_settings.get("lunch_minute", 10),
            "dinner_hour": ver1_settings.get("dinner_hour", 18),
            "dinner_minute": ver1_settings.get("dinner_minute", 0),
            "break_enabled": ver1_settings.get("break_enabled", True),
            "lunch_enabled": ver1_settings.get("lunch_enabled", True),
            "dinner_enabled": ver1_settings.get("dinner_enabled", False)
        }
        
        # Ver2 설정 저장
        with open(ver2_path, 'w', encoding='utf-8') as f:
            json.dump(ver2_settings, f, indent=4, ensure_ascii=False)
        
        print(f"Ver2 설정 저장 완료: {ver2_path}")
        print(f"마이그레이션된 설정: {ver2_settings}")
        
        # 백업 생성
        backup_path = ver2_path.replace('.json', '_from_ver1_backup.json')
        shutil.copy2(ver1_path, backup_path)
        print(f"Ver1 설정 백업 생성: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"설정 마이그레이션 실패: {e}")
        return False

def cleanup_ver1():
    """Ver1 관련 파일들 정리 (선택사항)"""
    print("\n=== Ver1 파일 정리 ===")
    
    # Program Files의 Ver1 폴더 확인
    ver1_program_path = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'ClockApp')
    
    if os.path.exists(ver1_program_path):
        print(f"Ver1 설치 폴더 발견: {ver1_program_path}")
        print("주의: 이 폴더는 인스톨러에서 자동으로 제거됩니다.")
    else:
        print("Ver1 설치 폴더를 찾을 수 없습니다.")

def main():
    """메인 함수"""
    print("ClockApp Ver1->Ver2 설정 마이그레이션 도구")
    print("=" * 50)
    
    # 관리자 권한 확인
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        print(f"관리자 권한: {'예' if is_admin else '아니오'}")
    except:
        print("권한 확인 불가")
    
    # 설정 마이그레이션 실행
    success = migrate_settings()
    
    if success:
        print("\n✅ 설정 마이그레이션 완료!")
        print("Ver1의 모든 설정이 Ver2로 성공적으로 이전되었습니다.")
    else:
        print("\n⚠️  마이그레이션할 Ver1 설정이 없습니다.")
        print("Ver2는 기본 설정으로 시작됩니다.")
    
    # Ver1 파일 정리 정보
    cleanup_ver1()
    
    print("\n" + "=" * 50)
    print("마이그레이션 완료")

if __name__ == "__main__":
    main()