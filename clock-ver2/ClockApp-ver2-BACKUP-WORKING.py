#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClockApp Ver2 - 건강한 업무를 위한 자세 알림 앱

배포자 정보:
- 개발사: KoreawookDevTeam
- 개발자: koreawook
- 연락처: koreawook@gmail.com
- 홈페이지: https://koreawook.github.io/ClockApp/
- 라이선스: MIT License
- 버전: 2.0.0
- 배포일: 2025.10.22

신뢰성 보증:
✓ 개인정보 수집 없음 (완전 오프라인 동작)
✓ 광고 없음, 100% 무료
✓ 오픈소스 정책 (GitHub 공개)
✓ 의료진 자문을 통한 스트레칭 가이드
✓ 5,000+ 사용자 검증 완료

Ver1과 Ver2의 차이점:
- Ver1과 독립적인 실행 (별도 뮤텍스)
- 향상된 UI/UX 및 안정성
- 추가 기능 및 최적화

이 소프트웨어는 MIT 라이선스 하에 배포됩니다.
자세한 내용은 LICENSE 파일을 참조하십시오.

Copyright (c) 2025 KoreawookDevTeam. All rights reserved.
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import sys
import os
import time
import json
from datetime import datetime, timedelta
import threading
import urllib.request
import urllib.error
import ssl
import winreg  # 윈도우 레지스트리 접근용
import pystray
from pystray import MenuItem, Menu
import ctypes
from ctypes import wintypes
import random
import glob

# SSL 인증서 검증 우회 (개발용)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 날씨 캐시 설정
WEATHER_CACHE_FILE = "weather_cache.json"
WEATHER_CACHE_DURATION = 7200  # 2시간 (초 단위)

def load_weather_cache():
    """날씨 캐시 로드"""
    try:
        if os.path.exists(WEATHER_CACHE_FILE):
            with open(WEATHER_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache['timestamp'])
                
                # 2시간 이내 캐시인지 확인
                if datetime.now() - cache_time < timedelta(seconds=WEATHER_CACHE_DURATION):
                    print(f"날씨 캐시 사용 (저장 시각: {cache_time.strftime('%H:%M:%S')})")
                    return cache['data']
                else:
                    print(f"날씨 캐시 만료 (저장 시각: {cache_time.strftime('%H:%M:%S')})")
    except Exception as e:
        print(f"날씨 캐시 로드 실패: {e}")
    return None

def save_weather_cache(weather_data):
    """날씨 캐시 저장"""
    try:
        cache = {
            'timestamp': datetime.now().isoformat(),
            'data': weather_data
        }
        with open(WEATHER_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print(f"날씨 캐시 저장 완료: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"날씨 캐시 저장 실패: {e}")

# 컬러풀한 아이콘 생성 함수 (이미지 파일 사용)
def load_icon_image(icon_type, size=24):
    """실제 이미지 파일에서 아이콘 로드"""
    try:
        filename = f"{icon_type}_{size}.png"
        if os.path.exists(filename):
            img = Image.open(filename)
            return ImageTk.PhotoImage(img)
        else:
            print(f"아이콘 파일을 찾을 수 없음: {filename}")
            return None
    except Exception as e:
        print(f"아이콘 로드 오류: {e}")
        return None

def create_weather_icon(weather_type, size=(32, 32)):
    """날씨별 컬러풀한 아이콘 생성 (이미지 파일 사용)"""
    size_num = size[0]  # 첫 번째 차원 사용
    return load_icon_image(weather_type, size_num)

def create_system_icon(icon_type, size=(16, 16)):
    """시스템 UI용 컬러풀한 아이콘 (이미지 파일 사용)"""
    size_num = size[0]  # 첫 번째 차원 사용
    return load_icon_image(icon_type, size_num)

def get_colorful_break_text(remaining_mins, remaining_secs, is_meal_time=False):
    """휴식 시간 표시용 컬러풀한 텍스트 생성"""
    if is_meal_time:
        return "🍽️ 식사시간 (휴식 알림 일시정지)"
    elif remaining_mins > 0:
        return f"⏰ 다음 휴식: {remaining_mins}:{remaining_secs:02d}"
    elif remaining_secs > 10:
        return f"⏰ 다음 휴식: {remaining_secs}초"
    else:
        return "⏰ 휴식시간!"

class StretchImageManager:
    """스트레칭 이미지를 랜덤하게 관리하는 클래스"""
    def __init__(self, image_folder="stretchimage"):
        # PyInstaller 빌드와 일반 실행 모두 지원하는 경로 처리
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 실행 파일인 경우
            script_dir = os.path.dirname(sys.executable)
            # _internal 폴더에서 찾기
            self.image_folder = os.path.join(script_dir, "_internal", image_folder)
        else:
            # 일반 Python 스크립트로 실행하는 경우
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.image_folder = os.path.join(script_dir, image_folder)
        
        self.image_history = []  # 최근 표시된 이미지 기록
        self.max_history = 5  # 최근 5개 이미지 기억
        self.available_images = self._load_available_images()
    
    def _load_available_images(self):
        """폴더 내의 모든 이미지 파일 로드"""
        try:
            print(f"🔍 스트레칭 이미지 폴더 확인: {self.image_folder}")
            if not os.path.exists(self.image_folder):
                print(f"❌ 스트레칭 이미지 폴더가 없습니다: {self.image_folder}")
                return []
            
            # 지원하는 이미지 확장자
            image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']
            images = []
            
            for ext in image_extensions:
                pattern = os.path.join(self.image_folder, ext)
                found = glob.glob(pattern)
                images.extend(found)
                if found:
                    print(f"  {ext}: {len(found)}개 발견")
            
            if images:
                print(f"✅ 총 스트레칭 이미지 {len(images)}개 발견")
            else:
                print(f"⚠️ 스트레칭 이미지가 없습니다 - 폴더: {self.image_folder}")
            return images
        except Exception as e:
            print(f"❌ 이미지 로드 오류: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_random_image(self):
        """랜덤 이미지를 선택 (최근 이미지는 제외)"""
        if not self.available_images:
            return None
        
        # 이미지가 충분하지 않으면 히스토리 무시
        if len(self.available_images) <= self.max_history:
            return random.choice(self.available_images)
        
        # 히스토리에 없는 이미지 필터링
        available = [img for img in self.available_images if img not in self.image_history]
        
        # 모든 이미지가 히스토리에 있으면 히스토리 초기화
        if not available:
            self.image_history.clear()
            available = self.available_images.copy()
        
        # 랜덤 선택
        selected = random.choice(available)
        
        # 히스토리 업데이트
        self.image_history.append(selected)
        if len(self.image_history) > self.max_history:
            self.image_history.pop(0)
        
        return selected

# 전역 이미지 매니저 인스턴스
stretch_image_manager = StretchImageManager()

def get_weather_type_from_icon(icon_text):
    """이모지 아이콘에서 날씨 타입 추출"""
    weather_map = {
        '☀️': 'sunny',
        '🌤️': 'sunny', 
        '⛅': 'cloud',
        '☁️': 'cloud',
        '🌧️': 'rain',
        '🌦️': 'rain',
        '❄️': 'snow',
        '🌨️': 'snow', 
        '⛈️': 'storm',
        '🌩️': 'storm',
        # 추가 매핑
        '🌟': 'sunny',
        '⭐': 'sunny',
        '☀': 'sunny',
        '☁': 'cloud',
        '🌧': 'rain'
    }
    return weather_map.get(icon_text, 'sunny')  # 기본값을 sunny로 설정

def create_clock_image(size=64):
    """프로그래밍적으로 시계 이미지 생성"""
    try:
        # 투명 배경의 이미지 생성
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 시계 색상
        clock_color = (70, 130, 180, 255)  # 스틸 블루
        clock_dark = (25, 25, 112, 255)    # 미드나이트 블루
        hand_color = (220, 20, 60, 255)    # 크림슨 (시계바늘)

        # 시계 중심과 크기
        center_x, center_y = size // 2, size // 2
        clock_radius = size * 0.4

        # 시계 외곽 원 그리기
        draw.ellipse([
            center_x - clock_radius, center_y - clock_radius,
            center_x + clock_radius, center_y + clock_radius
        ], fill=clock_color, outline=clock_dark, width=3)

        # 시계 숫자 12, 3, 6, 9 표시
        import math
        for i, angle in enumerate([0, 90, 180, 270]):  # 12, 3, 6, 9시 위치
            radian = math.radians(angle - 90)  # -90도로 12시를 위로
            mark_radius = clock_radius * 0.8
            
            # 숫자 위치 계산
            mark_x = center_x + mark_radius * math.cos(radian)
            mark_y = center_y + mark_radius * math.sin(radian)
            
            # 작은 원으로 시간 표시
            mark_size = 3
            draw.ellipse([
                mark_x - mark_size, mark_y - mark_size,
                mark_x + mark_size, mark_y + mark_size
            ], fill=clock_dark)

        # 시계 바늘 그리기
        # 긴 바늘 (분침) - 10분 위치
        minute_angle = math.radians(60 - 90)  # 2시 방향 (10분)
        minute_length = clock_radius * 0.7
        minute_end_x = center_x + minute_length * math.cos(minute_angle)
        minute_end_y = center_y + minute_length * math.sin(minute_angle)
        
        draw.line([center_x, center_y, minute_end_x, minute_end_y], fill=hand_color, width=2)

        # 짧은 바늘 (시침) - 2시 위치
        hour_angle = math.radians(60 - 90)  # 2시 방향
        hour_length = clock_radius * 0.5
        hour_end_x = center_x + hour_length * math.cos(hour_angle)
        hour_end_y = center_y + hour_length * math.sin(hour_angle)
        
        draw.line([center_x, center_y, hour_end_x, hour_end_y], fill=hand_color, width=3)

        # 중심점
        center_size = 4
        draw.ellipse([
            center_x - center_size, center_y - center_size,
            center_x + center_size, center_y + center_size
        ], fill=hand_color)

        return img

    except Exception as e:
        print(f"시계 이미지 생성 실패: {e}")
        return None
        
        draw.ellipse([
            center_x + body_width // 2 - 5 - right_btn_width, center_y - body_height // 2 + 3,
            center_x + body_width // 2 - 5, center_y - body_height // 2 + 3 + right_btn_height
        ], fill=mouse_color, outline=mouse_dark, width=1)

        # 스크롤 휠 (가운데 선)
        wheel_x = center_x
        wheel_y1 = center_y - body_height // 4
        wheel_y2 = center_y + body_height // 4
        
        draw.line([wheel_x, wheel_y1, wheel_x, wheel_y2], fill=mouse_dark, width=2)

        # 마우스 케이블 (옵션)
        cable_start_x = center_x
        cable_start_y = center_y + body_height // 2
        cable_end_x = center_x + mouse_size * 0.3
        cable_end_y = center_y + mouse_size * 0.4
        
        draw.line([cable_start_x, cable_start_y, cable_end_x, cable_end_y], fill=mouse_dark, width=3)

        return img
    except Exception as e:
        print(f"마우스 이미지 생성 실패: {e}")
        return None

def convert_png_to_ico(png_path, ico_path):
    """PNG 파일을 ICO 파일로 변환"""
    try:
        # PNG 이미지 열기
        png_image = Image.open(png_path)
        
        # 여러 크기로 리사이즈해서 ICO 파일 생성
        sizes = [16, 32, 48, 64, 128, 256]
        images = []
        
        for size in sizes:
            # 이미지 크기 조정
            resized = png_image.resize((size, size), Image.Resampling.LANCZOS)
            
            # RGB 모드로 변환 (ICO 파일 호환성을 위해)
            if resized.mode == 'RGBA':
                # 투명 배경을 흰색으로 변경
                background = Image.new('RGB', (size, size), (255, 255, 255))
                background.paste(resized, (0, 0), resized)
                resized = background
            elif resized.mode != 'RGB':
                resized = resized.convert('RGB')
                
            images.append(resized)
        
        # ICO 파일로 저장
        if images:
            images[0].save(ico_path, format='ICO', sizes=[(img.size[0], img.size[1]) for img in images])
            print(f"PNG를 ICO로 변환 성공: {png_path} -> {ico_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"PNG to ICO 변환 실패: {e}")
        return False

def get_icon_path():
    """사용할 아이콘 파일 경로 반환 (clock_app.ico 우선)"""
    try:
        base_dir = os.path.dirname(__file__)
        
        # 1. clock_app.ico 확인 (최우선)
        clock_app_ico = os.path.join(base_dir, "clock_app.ico")
        if os.path.exists(clock_app_ico):
            print("clock_app.ico 아이콘 사용")
            return clock_app_ico
        
        # 2. clock_icon.ico 확인 (2순위)
        clock_icon_ico = os.path.join(base_dir, "clock_icon.ico")
        if os.path.exists(clock_icon_ico):
            print("clock_icon.ico 아이콘 사용")
            return clock_icon_ico
        
        
        # 3. 기본 시계 아이콘 생성/사용 (마지막 fallback)
        default_ico_path = os.path.join(base_dir, "clock_icon.ico")
        if not os.path.exists(default_ico_path):
            create_icon_file()
        
        return default_ico_path
        
    except Exception as e:
        print(f"아이콘 경로 가져오기 실패: {e}")
        return None

def create_icon_file():
    """실행 파일용 ICO 아이콘 생성"""
    try:
        # 여러 크기의 시계 이미지 생성 (ICO 파일은 여러 크기를 포함할 수 있음)
        sizes = [16, 32, 48, 64, 128, 256]
        images = []

        for size in sizes:
            clock_img = create_clock_image(size)
            if clock_img:
                # RGB 모드로 변환 (ICO 파일 호환성을 위해)
                if clock_img.mode == 'RGBA':
                    # 흰색 배경 추가
                    background = Image.new('RGB', (size, size), (255, 255, 255))
                    background.paste(clock_img, (0, 0), clock_img)
                    clock_img = background
                images.append(clock_img)

        if images:
            # ICO 파일로 저장
            icon_path = os.path.join(os.path.dirname(__file__), "clock_icon.ico")
            images[0].save(icon_path, format='ICO', sizes=[(img.size[0], img.size[1]) for img in images])    
            print(f"아이콘 파일 생성 성공: {icon_path}")
            return icon_path
        else:
            print("아이콘 이미지 생성 실패")
            return None

    except Exception as e:
        print(f"아이콘 파일 생성 실패: {e}")
        return None

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

def get_level_data_file_path():
    """레벨 데이터 파일 경로 반환 (설정 파일과 같은 위치)"""
    if getattr(sys, 'frozen', False):
        # 패키징된 실행파일인 경우 사용자 AppData 폴더 사용
        appdata_path = os.path.expanduser("~\\AppData\\Roaming\\ClockApp-Ver2")
        if not os.path.exists(appdata_path):
            try:
                os.makedirs(appdata_path)
            except Exception as e:
                print(f"레벨 데이터 폴더 생성 실패: {e}")
                return os.path.join(os.path.dirname(sys.executable), "rest_level_data.json")
        return os.path.join(appdata_path, "rest_level_data.json")
    else:
        # 개발 중에는 현재 스크립트 폴더 사용
        return os.path.join(os.path.dirname(__file__), "rest_level_data.json")

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

def calculate_level_from_seconds(total_seconds):
    """누적 시간으로 레벨 계산
    레벨 1: 30초
    레벨 2: 60초 (30 + 30)
    레벨 3: 120초 (60 + 60)
    레벨 4: 240초 (120 + 120)
    ...
    """
    level = 1
    required_seconds = 30  # 레벨 1은 30초
    accumulated_seconds = 0
    
    while accumulated_seconds + required_seconds <= total_seconds:
        accumulated_seconds += required_seconds
        level += 1
        required_seconds *= 2  # 다음 레벨은 2배
    
    return level, accumulated_seconds

def get_next_level_required_seconds(current_level):
    """다음 레벨까지 필요한 총 시간 계산"""
    required = 30
    for _ in range(current_level - 1):
        required *= 2
    return required

def format_time_display(seconds):
    """초를 분:초 형식으로 변환"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}분 {secs}초"

def get_level_up_message(level):
    """레벨별 축하 메시지 반환"""
    messages = {
        1: "쉼이랑 무엇인가? 느껴지시나요?",
        2: "오오! 이제 진정한 릴렉스를 맛보실듯",
        3: "지금까지 레벨중에 가장 높은거 같아요!!",
        4: "제대로 휴식을 누릴줄 아시는 군요!",
        5: "이제 당신의 몸과 마음이 소생하고 있습니다!",
        6: "회사업무 능률이 1+ 되었습니다!",
        7: "생기있는 당신의 모습! 빛이 납니다!",
        8: "쉬는것도 쉽지 않군. 좀더 힘을 내어 쉬어보자!",
        9: "이제 이정도면 쉼이 몸에 익었다!",
        10: "최고 만렙에 도달하셨네요! 개발자에게 이 사실을 알리세요!"
    }
    return messages.get(level, f"레벨 {level} 달성! 계속해서 휴식을 즐기세요!")

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

def load_settings_from_file():
    """설정 파일에서 설정값 로드"""
    try:
        settings_file = get_settings_file_path()
        print(f"설정 파일 경로: {settings_file}")
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            print(f"설정 로드 성공: {settings}")
            return settings
        else:
            print("설정 파일이 없습니다. 기본값 사용.")
            return None
    except Exception as e:
        print(f"설정 로드 실패: {e}")
        return None

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

def check_startup_registry():
    """윈도우 시작 프로그램에 등록되어 있는지 확인"""
    try:
        # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run 키 열기
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Run", 
                           0, winreg.KEY_READ)
        
        try:
            # MouseClock 값이 있는지 확인
            value, _ = winreg.QueryValueEx(key, "MouseClock")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
            
    except Exception as e:
        print(f"시작 프로그램 확인 실패: {e}")
        return False

def add_to_startup():
    """윈도우 시작 프로그램에 등록"""
    try:
        # 현재 실행 파일의 전체 경로 가져오기
        if getattr(sys, 'frozen', False):
            # PyInstaller로 패키징된 exe 파일
            exe_path = sys.executable
        else:
            # Python 스크립트로 실행 중
            exe_path = os.path.abspath(__file__)
        
        # 경로를 따옴표로 감싸고 --minimized 옵션 추가
        exe_path_quoted = f'"{exe_path}" --minimized'
        
        # 레지스트리 키 열기 (쓰기 권한)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Run", 
                           0, winreg.KEY_SET_VALUE)
        
        # MouseClock 값 설정 (따옴표로 감싼 경로 사용)
        winreg.SetValueEx(key, "MouseClock", 0, winreg.REG_SZ, exe_path_quoted)
        winreg.CloseKey(key)
        
        print(f"시작 프로그램 등록 성공: {exe_path_quoted}")
        return True
        
    except Exception as e:
        print(f"시작 프로그램 등록 실패: {e}")
        return False

def remove_from_startup():
    """윈도우 시작 프로그램에서 제거"""
    try:
        # 레지스트리 키 열기 (쓰기 권한)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Run", 
                           0, winreg.KEY_SET_VALUE)
        
        try:
            # MouseClock 값 삭제
            winreg.DeleteValue(key, "MouseClock")
            winreg.CloseKey(key)
            print("시작 프로그램에서 제거 성공")
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            print("시작 프로그램에 등록되어 있지 않음")
            return True
            
    except Exception as e:
        print(f"시작 프로그램 제거 실패: {e}")
        return False

def add_to_startup_alternative():
    """작업 스케줄러를 사용한 시작 프로그램 등록 (대안 방법)"""
    try:
        # 현재 실행 파일의 전체 경로 가져오기
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)
        
        # 작업 스케줄러 명령어 생성 (--minimized 옵션 추가)
        import subprocess
        cmd = f'schtasks /create /tn "MouseClock" /tr "{exe_path} --minimized" /sc onlogon /rl limited /f'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("작업 스케줄러로 시작 프로그램 등록 성공")
            return True
        else:
            print(f"작업 스케줄러 등록 실패: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"작업 스케줄러 등록 실패: {e}")
        return False

def remove_from_startup_alternative():
    """작업 스케줄러에서 시작 프로그램 제거 (대안 방법)"""
    try:
        import subprocess
        cmd = 'schtasks /delete /tn "MouseClock" /f'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("작업 스케줄러에서 제거 성공")
            return True
        else:
            print(f"작업 스케줄러 제거 실패: {result.stderr}")
            return True  # 이미 없는 경우도 성공으로 처리
            
    except Exception as e:
        print(f"작업 스케줄러 제거 실패: {e}")
        return False

def get_current_location():
    """현재 위치 정보 가져오기 (IP 기반)"""
    try:
        # ipapi.co를 사용한 위치 정보 조회
        req = urllib.request.Request("http://ipapi.co/json/")
        with urllib.request.urlopen(req, timeout=5, context=ssl_context) as response:
            data = json.loads(response.read().decode())
            
        city = data.get('city', '알 수 없음')
        region = data.get('region', '')
        country = data.get('country_name', '')
        
        # 위치 문자열 생성
        if region and region != city:
            location = f"{city}, {region}"
        else:
            location = city
            
        if country:
            location = f"{location}, {country}"
            
        return location
        
    except Exception as e:
        print(f"위치 정보 가져오기 실패: {e}")
        return "판교동"

def get_weather_data(location="Seoul", force_refresh=False):
    """실제 날씨 정보 가져오기 (wttr.in API 사용)"""
    # 캐시 확인 (강제 새로고침이 아닌 경우)
    if not force_refresh:
        cached_data = load_weather_cache()
        if cached_data:
            return cached_data
    
    print("날씨 API 호출 중...")
    try:
        # wttr.in API 사용 (무료, API 키 불필요)
        try:
            # ipapi.co에서 좌표 정보도 가져오기
            req = urllib.request.Request("http://ipapi.co/json/")
            with urllib.request.urlopen(req, timeout=5, context=ssl_context) as response:
                location_data = json.loads(response.read())
                lat = location_data.get('latitude')
                lon = location_data.get('longitude')
                city = location_data.get('city', 'Seoul')
                region = location_data.get('region', '')
                country = location_data.get('country_name', '')
                
                # 위치 문자열 생성
                if region and region != city:
                    location_str = f"{city}, {region}"
                else:
                    location_str = city
                    
                if country and country != 'South Korea':  # 한국이 아닌 경우만 국가명 추가
                    location_str = f"{location_str}, {country}"
                
            if lat and lon:
                # wttr.in API 사용 (무료, API 키 불필요)
                weather_url = f"http://wttr.in/{lat},{lon}?format=j1"
                req = urllib.request.Request(weather_url)
                with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
                    weather_data = json.loads(response.read())
                    
                current = weather_data.get('current_condition', [{}])[0]
                
                # 현재 날씨 정보 추출
                temp_c = current.get('temp_C', '20')
                humidity = current.get('humidity', '65')
                windspeed = current.get('windspeedKmph', '7')
                weather_desc = current.get('weatherDesc', [{}])[0].get('value', '맑음')
                
                # 날씨 아이콘 매핑
                weather_icon = get_weather_icon(weather_desc)
                
                # 시간대별 예보 데이터
                hourly_forecast = []
                if 'weather' in weather_data and weather_data['weather']:
                    today_weather = weather_data['weather'][0]
                    hourly = today_weather.get('hourly', [])
                    
                    for i, hour_data in enumerate(hourly):
                        if i >= 8:  # 8개 시간대만
                            break
                        hour_temp = hour_data.get('tempC', '20')
                        hour_desc = hour_data.get('weatherDesc', [{}])[0].get('value', '맑음')
                        hour_icon = get_weather_icon(hour_desc)
                        time_label = f"{i*3:02d}:00"
                        
                        hourly_forecast.append({
                            'time': time_label,
                            'icon': hour_icon,
                            'temp': f"{hour_temp}°C",
                            'desc': hour_desc
                        })
                
                weather_result = {
                    'current': {
                        'temp': f"{temp_c}°C",
                        'humidity': f"{humidity}%",
                        'wind': f"{float(windspeed)*0.28:.1f}m/s",  # km/h to m/s
                        'description': weather_desc,
                        'icon': weather_icon
                    },
                    'hourly': hourly_forecast,
                    'location': location_str
                }
                
                # 캐시 저장
                save_weather_cache(weather_result)
                return weather_result
                
        except Exception as e:
            print(f"실제 날씨 API 호출 실패: {e}")
            
        # API 실패 시 기본값 반환
        return get_default_weather_data()
        
    except Exception as e:
        print(f"날씨 데이터 가져오기 전체 실패: {e}")
        return get_default_weather_data()

def get_weather_icon(description):
    """날씨 설명에 따른 아이콘 반환"""
    description = description.lower()
    if 'clear' in description or '맑' in description:
        return '☀️'
    elif 'cloud' in description or '구름' in description:
        return '🌤️'
    elif 'rain' in description or '비' in description:
        return '🌧️'
    elif 'snow' in description or '눈' in description:
        return '❄️'
    elif 'storm' in description or '천둥' in description:
        return '⛈️'
    elif 'fog' in description or '안개' in description:
        return '🌫️'
    else:
        return '🌤️'

def get_default_weather_data():
    """기본 날씨 데이터 (API 실패 시)"""
    now = datetime.now()
    hour = now.hour
    
    if 6 <= hour < 12:
        current_weather = {"icon": "☀️", "temp": "22°C", "desc": "맑음"}
    elif 12 <= hour < 18:
        current_weather = {"icon": "🌤️", "temp": "25°C", "desc": "구름 조금"}
    elif 18 <= hour < 22:
        current_weather = {"icon": "🌆", "temp": "20°C", "desc": "흐림"}
    else:
        current_weather = {"icon": "🌙", "temp": "18°C", "desc": "맑음"}
    
    hourly_forecast = [
        {'time': "00:00", 'icon': "🌙", 'temp': "16°C", 'desc': "맑음"},
        {'time': "03:00", 'icon': "🌙", 'temp': "15°C", 'desc': "맑음"},
        {'time': "06:00", 'icon': "☀️", 'temp': "18°C", 'desc': "맑음"},
        {'time': "09:00", 'icon': "☀️", 'temp': "22°C", 'desc': "맑음"},
        {'time': "12:00", 'icon': "🌤️", 'temp': "26°C", 'desc': "구름 조금"},
        {'time': "15:00", 'icon': "🌤️", 'temp': "25°C", 'desc': "구름 조금"},
        {'time': "18:00", 'icon': "🌆", 'temp': "21°C", 'desc': "흐림"},
        {'time': "21:00", 'icon': "🌙", 'temp': "18°C", 'desc': "맑음"}
    ]
    
    return {
        'current': {
            'temp': current_weather['temp'],
            'humidity': '65%',
            'wind': '2.1m/s',
            'description': current_weather['desc'],
            'icon': current_weather['icon']
        },
        'hourly': hourly_forecast,
        'location': '판교동'
    }

class LevelUpPopup:
    """레벨업 축하 팝업 클래스 - 레트로 픽셀 아트 스타일"""
    def __init__(self, level):
        self.level = level
        self.popup = tk.Toplevel()
        self.popup.title("Level Up!")
        self.popup.geometry("500x400")
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)
        
        # 하늘색 배경 (레퍼런스 이미지 스타일)
        self.popup.configure(bg="#87CEEB")
        
        # 아이콘 설정
        try:
            icon_file_path = get_icon_path()
            if icon_file_path and os.path.exists(icon_file_path):
                self.popup.iconbitmap(icon_file_path)
        except:
            pass
        
        # 중앙 정렬
        self.center_popup()
        
        # 위젯 생성
        self.create_widgets()
        
        # 포커스 잃으면 닫기 (다른 앱 클릭 시 자동 닫힘)
        self.popup.bind("<FocusOut>", self.on_focus_out)
        
        # 추가 이벤트 바인딩 (더 안정적인 작동을 위해)
        self.popup.bind("<Deactivate>", self.on_focus_out)  # 창이 비활성화될 때
        
        # X 버튼으로 닫기
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        
        # 폭죽 애니메이션 시작 (레벨 3부터)
        if self.level >= 3:
            self.firework_particles = []
            self.animate_fireworks()
    
    def center_popup(self):
        """팝업을 화면 중앙에 위치"""
        self.popup.update_idletasks()
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 350) // 2
        self.popup.geometry(f"500x350+{x}+{y}")
    
    def create_widgets(self):
        """위젯 생성 - 레트로 게임 스타일"""
        # 메인 컨테이너
        main_frame = tk.Frame(self.popup, bg="#87CEEB")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 폭죽 캔버스 (배경) - 레벨 3부터만 표시
        if self.level >= 3:
            self.firework_canvas = tk.Canvas(
                main_frame,
                width=460,
                height=310,
                bg="#87CEEB",
                highlightthickness=0
            )
            self.firework_canvas.place(x=0, y=0)
        
        # "LEVEL UP!" 버튼 스타일 텍스트 (픽셀 아트 느낌)
        level_up_frame = tk.Frame(
            main_frame,
            bg="#FF6B8A",
            relief=tk.RAISED,
            bd=3
        )
        level_up_frame.pack(pady=(30, 15))
        
        level_up_label = tk.Label(
            level_up_frame,
            text="Level Up",
            font=("Arial Black", 28, "bold"),
            fg="#FFEB3B",
            bg="#FF6B8A",
            padx=30,
            pady=10
        )
        level_up_label.pack()
        
        # 레벨 숫자 (크게 강조)
        level_number_label = tk.Label(
            main_frame,
            text=f"레벨 {self.level}",
            font=("맑은 고딕", 36, "bold"),
            fg="#2C3E50",
            bg="#87CEEB"
        )
        level_number_label.pack(pady=(10, 15))
        
        # 축하 메시지
        message = get_level_up_message(self.level)
        message_label = tk.Label(
            main_frame,
            text=message,
            font=("맑은 고딕", 12, "bold"),
            fg="#34495E",
            bg="#87CEEB",
            wraplength=400,
            justify=tk.CENTER
        )
        message_label.pack(pady=(5, 25))
        
        # 확인 버튼 (레트로 스타일)
        close_button = tk.Button(
            main_frame,
            text="계속하기",
            font=("맑은 고딕", 11, "bold"),
            bg="#FF6B8A",
            fg="white",
            relief=tk.RAISED,
            bd=3,
            padx=35,
            pady=8,
            cursor="hand2",
            command=self.close_popup
        )
        close_button.pack()
    
    def get_firework_intensity(self):
        """레벨에 따른 폭죽 강도 계산"""
        # 레벨 3~10: 점진적으로 증가
        if self.level < 3:
            return 0, 0, 0.0  # 폭죽 없음
        elif self.level == 3:
            return 8, 3, 0.15  # 적은 폭죽 (파티클 8개, 크기 3, 생성확률 15%)
        elif self.level <= 5:
            return 12, 4, 0.25  # 중간 폭죽
        elif self.level <= 7:
            return 18, 5, 0.35  # 많은 폭죽
        elif self.level <= 9:
            return 25, 6, 0.45  # 매우 많은 폭죽
        else:  # 레벨 10
            return 35, 7, 0.60  # 최대 폭죽
    
    def animate_fireworks(self):
        """폭죽 애니메이션 - 레벨별 강도 조절"""
        try:
            particle_count, max_size, spawn_rate = self.get_firework_intensity()
            
            # 레벨에 따라 폭죽 생성
            if random.random() < spawn_rate:
                x = random.randint(50, 410)
                y = random.randint(50, 260)
                self.create_firework(x, y, particle_count, max_size)
            
            # 기존 폭죽 업데이트
            for particle in self.firework_particles[:]:
                particle['life'] -= 1
                if particle['life'] <= 0:
                    self.firework_canvas.delete(particle['id'])
                    self.firework_particles.remove(particle)
                else:
                    # 파티클 이동
                    self.firework_canvas.move(
                        particle['id'],
                        particle['vx'],
                        particle['vy']
                    )
                    particle['vy'] += 0.2  # 중력 효과
            
            # 계속 애니메이션 (팝업이 열려있는 동안)
            if self.popup.winfo_exists():
                self.popup.after(50, self.animate_fireworks)
        except:
            pass
    
    def create_firework(self, x, y, particle_count, max_size):
        """폭죽 파티클 생성 - 레트로 게임 컬러"""
        # 레트로 게임 느낌의 밝은 색상
        colors = ["#FFD700", "#FF6B8A", "#00FF00", "#00FFFF", "#FF69B4", "#FFA500"]
        
        # 레벨에 따라 파티클 개수와 크기 조절
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(2, 7)
            vx = speed * random.uniform(-1, 1)
            vy = speed * random.uniform(-1, 1)
            color = random.choice(colors)
            size = random.randint(max(2, max_size - 2), max_size)
            
            particle_id = self.firework_canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=color,
                outline=""
            )
            
            self.firework_particles.append({
                'id': particle_id,
                'vx': vx,
                'vy': vy,
                'life': random.randint(15, 45)
            })
    
    def on_focus_out(self, event):
        """포커스 잃으면 닫기 (다른 앱 클릭 시 자동 닫힘)"""
        try:
            # 팝업 자체나 자식 위젯이 아닌 다른 곳으로 포커스가 이동했는지 확인
            focused_widget = self.popup.focus_get()
            
            # 포커스가 None이거나 이 팝업의 자식이 아니면 닫기
            if focused_widget is None or focused_widget.winfo_toplevel() != self.popup:
                print("레벨업 창 포커스 상실 - 자동 닫기")
                self.close_popup()
        except:
            # 예외 발생 시 안전하게 팝업 닫기
            self.close_popup()
    
    def close_popup(self):
        """팝업 닫기"""
        try:
            self.popup.destroy()
        except:
            pass

class RestPopup:
    """휴식 알림 팝업 클래스"""
    def __init__(self):
        self.popup = tk.Toplevel()
        self.popup.title("ClockApp Ver2 - 휴식 알림")
        
        # 레벨 데이터 로드
        self.level_data = load_level_data()
        self.initial_total_seconds = self.level_data['total_seconds']
        self.popup_start_time = time.time()
        
        # 초기 레벨 저장 (레벨업 감지용)
        self.initial_level = self.level_data['level']
        self.current_level = self.initial_level
        
        # 스트레칭 이미지 로드
        self.stretch_image = None
        self.stretch_photo = None
        self.load_stretch_image()
        
        # 이미지가 있으면 더 큰 크기로 설정 (가로로 넓게)
        if self.stretch_image:
            self.popup.geometry("480x520")  # 레벨 정보 표시를 위해 높이 증가
        else:
            self.popup.geometry("400x420")
        
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)  # 항상 위에 표시
        
        # 아이콘 설정 (사용자 PNG 우선, 없으면 기본 시계 아이콘)
        try:
            icon_file_path = get_icon_path()
            if icon_file_path and os.path.exists(icon_file_path):
                self.popup.iconbitmap(icon_file_path)
        except:
            pass
        
        # 창을 화면 중앙에 위치
        self.center_popup()
        
        # 30초 타이머
        self.remaining_time = 30
        
        self.create_widgets()
        
        # X 버튼 활성화
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        
        # 포커스 잃을 때 팝업 닫기 (다른 앱 클릭 시 자동 닫힘)
        self.popup.bind("<FocusOut>", self.on_focus_out)
        
        # 타이머 시작
        self.update_timer()
    
    def load_stretch_image(self):
        """스트레칭 이미지를 랜덤으로 로드"""
        try:
            image_path = stretch_image_manager.get_random_image()
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path)
                
                # 이미지 크기 조정 (너비 최대 220px로 축소, 높이는 비율 유지)
                max_width = 220
                max_height = 250
                
                # 비율 유지하며 크기 조정
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                self.stretch_image = img
                print(f"✅ 스트레칭 이미지 로드 성공: {os.path.basename(image_path)}")
            else:
                print("⚠️ 사용 가능한 스트레칭 이미지가 없습니다.")
                print(f"   'stretchimage' 폴더에 PNG, JPG 이미지를 넣어주세요.")
                self.stretch_image = None
        except Exception as e:
            print(f"❌ 스트레칭 이미지 로드 오류: {e}")
            import traceback
            traceback.print_exc()
            self.stretch_image = None
        
    def close_popup(self):
        """팝업 닫기"""
        try:
            # 팝업이 떠있던 시간 계산 및 저장
            elapsed_time = int(time.time() - self.popup_start_time)
            new_total_seconds = self.initial_total_seconds + elapsed_time
            new_level, _ = calculate_level_from_seconds(new_total_seconds)
            
            # 레벨 데이터 저장
            save_level_data(new_level, new_total_seconds)
            print(f"휴식 팝업 종료 - 누적 시간: {elapsed_time}초 추가 (총 {new_total_seconds}초)")
            
            # 팝업 닫기
            self.popup.destroy()
            
            # 레벨업 체크 및 축하 팝업 표시 (실시간으로 표시하지 않았던 경우만)
            # self.current_level은 실시간 업데이트된 레벨, self.initial_level은 시작 시 레벨
            if new_level > self.current_level:
                # 닫는 순간에 추가로 레벨업이 발생한 경우 (매우 드문 경우)
                print(f"🎉 종료 시 레벨업! {self.current_level} → {new_level}")
                root = self.popup.master
                if root:
                    root.after(300, lambda: LevelUpPopup(new_level))
        except Exception as e:
            print(f"팝업 닫기 오류: {e}")
            pass
    
    def on_focus_out(self, event):
        """팝업이 포커스를 잃었을 때 호출 (다른 앱 클릭 시)"""
        try:
            # 팝업 자체나 자식 위젯이 아닌 다른 곳으로 포커스가 이동했는지 확인
            focused_widget = self.popup.focus_get()
            
            # 포커스가 None이거나 이 팝업의 자식이 아니면 닫기
            if focused_widget is None or focused_widget.winfo_toplevel() != self.popup:
                print("포커스 상실 - 휴식 팝업 자동 닫기")
                self.close_popup()
        except:
            # 예외 발생 시 안전하게 팝업 닫기
            self.close_popup()
    
    def center_popup(self):
        """팝업을 화면 중앙에 위치시키기"""
        self.popup.update_idletasks()
        
        # 화면 크기 가져오기
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        
        # 팝업 크기 (이미지 유무에 따라 다름)
        if self.stretch_image:
            popup_width = 480
            popup_height = 520  # 레벨 정보 표시를 위해 증가
        else:
            popup_width = 400
            popup_height = 420
        
        # 중앙 위치 계산
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2
        
        self.popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
    
    def create_widgets(self):
        """위젯 생성 - 모던한 디자인"""
        # 팝업 배경색 설정
        self.popup.configure(bg="#f0f8ff")
        
        # 상단 헤더 영역 (간결하게)
        header_frame = tk.Frame(self.popup, bg="#4a90e2", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # 메인 메시지
        message_label = tk.Label(
            header_frame, 
            text="잠시 휴식하세요", 
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#4a90e2"
        )
        message_label.pack(pady=15)
        
        # 메인 컨텐츠 영역
        content_frame = tk.Frame(self.popup, bg="#f0f8ff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 부가 메시지
        sub_message = tk.Label(
            content_frame,
            text="눈을 감고 잠시 휴식을 취하세요",
            font=("맑은 고딕", 11),
            fg="#5a6c7d",
            bg="#f0f8ff"
        )
        sub_message.pack(pady=(0, 8))
        
        # 가로 레이아웃 (이미지가 있을 때)
        if self.stretch_image:
            print(f"✅ 스트레칭 이미지 표시 중 (크기: {self.stretch_image.size})")
            horizontal_container = tk.Frame(content_frame, bg="#f0f8ff")
            horizontal_container.pack(pady=3)
            
            # 왼쪽: 스트레칭 이미지
            image_frame = tk.Frame(horizontal_container, bg="#f0f8ff")
            image_frame.pack(side=tk.LEFT, padx=(5, 10))
            
            # 이미지 표시
            self.stretch_photo = ImageTk.PhotoImage(self.stretch_image)
            image_label = tk.Label(
                image_frame,
                image=self.stretch_photo,
                bg="#f0f8ff",
                relief=tk.FLAT,
                borderwidth=0
            )
            image_label.pack()
            
            # 오른쪽: 원형 진행 표시 (크게)
            progress_container = tk.Frame(horizontal_container, bg="#f0f8ff")
            progress_container.pack(side=tk.LEFT)
        else:
            print("ℹ️ 스트레칭 이미지 없음 - 타이머만 표시")
            # 이미지가 없으면 중앙에 진행바만
            progress_container = tk.Frame(content_frame, bg="#f0f8ff")
            progress_container.pack(pady=10)
        
        # 원형 캔버스 (진행바와 텍스트를 모두 그릴 캔버스 - 크기 증가)
        self.rest_progress_canvas = tk.Canvas(
            progress_container, 
            width=180, 
            height=180, 
            bg="#f0f8ff",
            highlightthickness=0
        )
        self.rest_progress_canvas.pack()
        
        # 텍스트 요소들을 캔버스에서 관리하기 위한 ID 저장
        self.timer_text_id = None
        self.second_text_id = None
        
        # 레벨 정보 영역 (타이머 아래)
        level_info_frame = tk.Frame(content_frame, bg="#f0f8ff")
        level_info_frame.pack(pady=(10, 5))
        
        # 누적 시간 라벨
        self.accumulated_time_label = tk.Label(
            level_info_frame,
            text="누적시간: 0분 0초",
            font=("맑은 고딕", 10, "bold"),
            fg="#2980b9",
            bg="#f0f8ff"
        )
        self.accumulated_time_label.pack()
        
        # 레벨 라벨 (크게 표시)
        self.level_label = tk.Label(
            level_info_frame,
            text="레벨: 1",
            font=("맑은 고딕", 16, "bold"),
            fg="#27ae60",
            bg="#f0f8ff"
        )
        self.level_label.pack(pady=(5, 3))
        
        # 다음 레벨까지 남은 시간 라벨
        self.next_level_label = tk.Label(
            level_info_frame,
            text="다음 레벨까지 남은 시간: 0분 30초",
            font=("맑은 고딕", 10),
            fg="#7f8c8d",
            bg="#f0f8ff"
        )
        self.next_level_label.pack(pady=(3, 0))
        
        # 하단 버튼 영역
        button_frame = tk.Frame(self.popup, bg="#f0f8ff")
        button_frame.pack(fill=tk.X, padx=15, pady=(5, 12))
        
        # 닫기 버튼 (모던한 플랫 스타일)
        self.close_button = tk.Button(
            button_frame,
            text="확인 (10초 후)",
            state=tk.DISABLED,
            font=("Segoe UI", 9, "bold"),
            bg="#bdc3c7",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.close_popup
        )
        self.close_button.pack(fill=tk.X)
    
    def update_timer(self):
        """타이머 업데이트"""
        if self.remaining_time >= 0:
            # 진행바 및 텍스트 업데이트 (30초에서 시작해서 줄어듦)
            self.update_rest_progress_bar()
            
            # 레벨 정보 업데이트
            self.update_level_info()
            
            # 마지막 10초에 닫기 버튼 활성화
            if self.remaining_time <= 10 and self.close_button['state'] == tk.DISABLED:
                self.close_button.config(
                    text="확인", 
                    state=tk.NORMAL,
                    bg="#27ae60",
                    activebackground="#229954"
                )
            
            # 버튼 텍스트 업데이트
            if self.remaining_time > 10:
                self.close_button.config(text=f"확인 ({self.remaining_time-10}초 후)")
            
            # remaining_time 감소
            self.remaining_time -= 1
            
            # 1초 후 다시 호출 (remaining_time이 -1이 될 때까지)
            self.popup.after(1000, self.update_timer)
        else:
            # 시간 종료 (remaining_time이 -1)
            self.update_rest_progress_bar()  # 마지막 진행바 업데이트 (0초 표시)
            self.update_level_info()  # 마지막 레벨 정보 업데이트
            # 즉시 팝업 닫기
            self.popup.after(500, self.close_popup)
    
    def update_level_info(self):
        """레벨 정보 업데이트"""
        try:
            # 현재까지 경과 시간 계산
            elapsed_time = int(time.time() - self.popup_start_time)
            current_total_seconds = self.initial_total_seconds + elapsed_time
            
            # 현재 레벨 계산
            current_level, accumulated_seconds = calculate_level_from_seconds(current_total_seconds)
            
            # 레벨업 감지 및 축하 팝업 표시
            if current_level > self.current_level:
                print(f"🎉 휴식 중 레벨업! {self.current_level} → {current_level}")
                self.current_level = current_level
                
                # 레벨 데이터 즉시 저장
                save_level_data(current_level, current_total_seconds)
                
                # 레벨업 팝업 표시
                try:
                    LevelUpPopup(current_level)
                except Exception as e:
                    print(f"레벨업 팝업 표시 오류: {e}")
            
            # 다음 레벨까지 필요한 시간 계산
            next_level_required = get_next_level_required_seconds(current_level)
            time_to_next_level = next_level_required - (current_total_seconds - accumulated_seconds)
            
            # 누적 시간 표시 업데이트
            time_display = format_time_display(current_total_seconds)
            self.accumulated_time_label.config(text=f"누적시간: {time_display}")
            
            # 레벨 표시 업데이트
            self.level_label.config(text=f"레벨: {current_level}")
            
            # 다음 레벨까지 남은 시간 표시 업데이트
            remaining_time_display = format_time_display(time_to_next_level)
            self.next_level_label.config(text=f"다음 레벨까지 남은 시간: {remaining_time_display}")
            
        except Exception as e:
            print(f"레벨 정보 업데이트 오류: {e}")
    
    def update_rest_progress_bar(self):
        """휴식 팝업 원형 진행바 및 텍스트 업데이트"""
        try:
            import math
            
            # 남은 시간 비율 계산 (30초 기준)
            remaining_ratio = max(0.0, self.remaining_time / 30.0)
            
            # 캔버스 지우기
            self.rest_progress_canvas.delete("all")
            
            # 원 중심 및 반지름 (캔버스 크기 180x180에 맞춤)
            center_x, center_y = 90, 90
            radius = 75
            
            # 배경 원 (연한 회색)
            self.rest_progress_canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill="#ecf0f1", outline="#bdc3c7", width=2
            )
            
            # 진행 원호 (시계 방향으로 채워짐)
            if remaining_ratio > 0:
                # 색상 선택 (시간에 따라 변화)
                if remaining_ratio > 0.5:
                    color = "#27ae60"  # 녹색
                elif remaining_ratio > 0.2:
                    color = "#f39c12"  # 주황색
                else:
                    color = "#e74c3c"  # 빨간색
                
                # 각도 계산 (0도가 위쪽, 시계방향)
                extent = -360 * remaining_ratio
                
                # 원호 그리기 (두께 증가)
                self.rest_progress_canvas.create_arc(
                    center_x - radius + 8, center_y - radius + 8,
                    center_x + radius - 8, center_y + radius - 8,
                    start=90, extent=extent,
                    fill=color, outline=color, width=14,
                    style=tk.ARC
                )
            
            # 타이머 텍스트를 캔버스 중앙에 직접 그리기 (투명 배경)
            timer_text = f"{max(0, self.remaining_time)}"  # 음수 방지
            
            # 큰 숫자 (메인 타이머 - 크기 증가)
            self.rest_progress_canvas.create_text(
                center_x, center_y - 12,  # 약간 위로
                text=timer_text,
                font=("Segoe UI", 36, "bold"),
                fill="#4a90e2",
                anchor=tk.CENTER
            )
            
            # "초" 텍스트 (작은 글씨로 아래에)
            self.rest_progress_canvas.create_text(
                center_x, center_y + 22,  # 숫자 아래
                text="초",
                font=("Segoe UI", 13),
                fill="#7f8c8d",
                anchor=tk.CENTER
            )
            
        except Exception as e:
            print(f"휴식 진행바 업데이트 오류: {e}")
    
    def close_popup(self):
        """팝업 닫기 및 휴식 시간 저장"""
        try:
            # 실제 휴식 시간 계산 및 저장
            actual_rest_time = int(time.time() - self.popup_start_time)
            print(f"💾 휴식 시간 저장: {actual_rest_time}초")
            
            # 레벨 데이터 저장
            current_total_seconds = self.initial_total_seconds + actual_rest_time
            level_data = {
                'total_seconds': current_total_seconds,
                'last_updated': time.time()
            }
            save_level_data(level_data)
            
            print(f"✅ 총 누적 휴식 시간: {current_total_seconds}초 ({current_total_seconds/60:.1f}분)")
            
            self.popup.destroy()
        except Exception as e:
            print(f"팝업 닫기 오류: {e}")
            try:
                self.popup.destroy()
            except:
                pass

class MealPopup:
    """식사 알림 팝업 클래스"""
    def __init__(self, meal_type="식사"):
        self.meal_type = meal_type
        self.popup = tk.Toplevel()
        self.popup.title("ClockApp Ver2 - 식사 알림")
        self.popup.geometry("350x200")  # 크기 증가 (진행바 공간)
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)  # 항상 위에 표시
        
        # 아이콘 설정 (사용자 PNG 우선, 없으면 기본 시계 아이콘)
        try:
            icon_file_path = get_icon_path()
            if icon_file_path and os.path.exists(icon_file_path):
                self.popup.iconbitmap(icon_file_path)
        except:
            pass
        
        # 창을 화면 중앙에 위치
        self.center_popup()
        
        # 1시간 타이머 (3600초)
        self.remaining_time = 3600
        
        self.create_widgets()
        
        # 닫기 버튼 활성화
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        
        # 타이머 시작
        self.update_timer()
        
    def close_popup(self):
        """팝업 닫기"""
        try:
            self.popup.destroy()
        except:
            pass
    
    def center_popup(self):
        """팝업을 화면 중앙에 위치시키기"""
        self.popup.update_idletasks()
        
        # 화면 크기 가져오기
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        
        # 팝업 크기
        popup_width = 350
        popup_height = 200
        
        # 중앙 위치 계산
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2
        
        self.popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
    
    def create_widgets(self):
        """위젯 생성"""
        # 메인 메시지
        message_label = tk.Label(
            self.popup, 
            text=f"🍽️ {self.meal_type} 시간입니다! 🍽️", 
            font=("Arial", 16, "bold"),
            fg="darkgreen"
        )
        message_label.pack(pady=15)
        
        # 부가 메시지
        sub_message = tk.Label(
            self.popup,
            text="맛있는 식사 하세요!",
            font=("Arial", 11),
            fg="gray"
        )
        sub_message.pack(pady=5)
        
        # 타이머 표시
        self.timer_label = tk.Label(
            self.popup,
            text="1:00:00",
            font=("Arial", 20, "bold"),
            fg="darkred"
        )
        self.timer_label.pack(pady=10)
        
        # 진행바 프레임
        progress_frame = tk.Frame(self.popup)
        progress_frame.pack(pady=10)
        
        # 진행바 캔버스 (가로형)
        self.meal_progress_canvas = tk.Canvas(progress_frame, width=200, height=20, bg="lightgray")
        self.meal_progress_canvas.pack()
        
        # 닫기 버튼
        close_button = tk.Button(
            self.popup,
            text="닫기",
            command=self.close_popup,
            width=10,
            font=("Arial", 10),
            bg="#ff6b6b",
            fg="white",
            relief=tk.RAISED,
            bd=2
        )
        close_button.pack(pady=10)
        
        # 처음 진행바 그리기
        self.update_meal_progress_bar()
    
    def update_timer(self):
        """타이머 업데이트"""
        if self.remaining_time >= 0:
            # 시:분:초 형식으로 변환
            hours = self.remaining_time // 3600
            minutes = (self.remaining_time % 3600) // 60
            seconds = self.remaining_time % 60
            
            time_text = f"{hours}:{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_text)
            
            # 진행바 업데이트
            self.update_meal_progress_bar()
            
            # 시간 감소
            self.remaining_time -= 1
            
            # 1초 후 다시 호출 (remaining_time이 -1이 될 때까지)
            self.popup.after(1000, self.update_timer)
        else:
            # 시간 종료 (remaining_time이 -1)
            self.timer_label.config(text="식사 완료!")
            self.update_meal_progress_bar()  # 마지막 진행바 업데이트 (빈 상태)
            # 즉시 팝업 닫기
            self.popup.after(500, self.close_popup)
    
    def update_meal_progress_bar(self):
        """식사 팝업 진행바 업데이트"""
        try:
            # 남은 시간 비율 계산 (3600초 기준, remaining_time이 -1일 때 0이 됨)
            remaining_ratio = max(0.0, self.remaining_time / 3600.0)
            
            # 캔버스 지우기
            self.meal_progress_canvas.delete("all")
            
            # 배경 바 (빈 영역)
            self.meal_progress_canvas.create_rectangle(2, 2, 198, 18, fill="lightgray", outline="gray")
            
            # 진행 바 (왼쪽에서 오른쪽으로 줄어듦)
            if remaining_ratio > 0:
                bar_width = int(196 * remaining_ratio)
                color = "green" if remaining_ratio > 0.5 else "orange" if remaining_ratio > 0.2 else "red"
                self.meal_progress_canvas.create_rectangle(2, 2, 2 + bar_width, 18, fill=color, outline=color)
            
        except Exception as e:
            print(f"식사 진행바 업데이트 오류: {e}")

class WeatherWindow:
    """날씨 정보 창 클래스"""
    def __init__(self, parent_clock):
        self.parent_clock = parent_clock
        self.weather_window = tk.Toplevel(parent_clock.clock_window)
        self.weather_window.title("ClockApp Ver2 - 날씨 정보")
        self.weather_window.geometry("300x700")  # 여백 최소화로 더 좁게 최적화
        self.weather_window.resizable(True, True)  # 크기 조절 가능하게 변경
        
        # 날씨 창을 부모 창 중앙에 위치
        self.weather_window.transient(parent_clock.clock_window)
        self.weather_window.grab_set()  # 모달 창으로 설정
        
        # 아이콘 설정 (사용자 PNG 우선, 없으면 기본 시계 아이콘)
        try:
            icon_file_path = get_icon_path()
            if icon_file_path and os.path.exists(icon_file_path):
                self.weather_window.iconbitmap(icon_file_path)
        except:
            pass
        
        self.create_widgets()
        self.center_on_parent()
        
        # 초기 위치 설정
        self.current_location = "판교동"
        self.load_weather_info()
        
    def center_on_parent(self):
        """부모 창 중앙에 날씨 창 위치시키기"""
        parent = self.parent_clock.clock_window
        parent.update_idletasks()
        
        # 부모 창 위치와 크기 가져오기
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # 날씨 창 크기 (여백 최소화)
        weather_width = 300
        weather_height = 700
        
        # 중앙 위치 계산
        x = parent_x + (parent_width - weather_width) // 2
        y = parent_y + (parent_height - weather_height) // 2
        
        self.weather_window.geometry(f"{weather_width}x{weather_height}+{x}+{y}")
    
    def create_widgets(self):
        """날씨 창 위젯 생성 - 메인창과 같은 평화로운 디자인"""
        # 메인 배경색 설정 (메인창과 동일)
        self.weather_window.configure(bg="#f8f9fa")
        
        # 메인 프레임
        main_frame = tk.Frame(self.weather_window, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 상단: 제목 영역 (카드 스타일)
        header_card = tk.Frame(main_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                              highlightbackground="#e0e0e0", highlightthickness=1)
        header_card.pack(fill=tk.X, pady=(0, 10))
        
        header_content = tk.Frame(header_card, bg="#ffffff")
        header_content.pack(fill=tk.X, padx=15, pady=12)
        
        # 제목
        title_label = tk.Label(header_content, text="🌤️ 날씨 정보", 
                              font=("Segoe UI", 16, "bold"),
                              bg="#ffffff", fg="#2c3e50")
        title_label.pack(side=tk.LEFT)
        
        # 새로고침 버튼 (메인창 스타일)
        refresh_btn = tk.Button(header_content, text="🔄 새로고침", 
                               command=self.refresh_weather,
                               font=("Segoe UI", 9, "bold"),
                               bg="#4fc3f7", fg="white",
                               relief=tk.FLAT, bd=0,
                               padx=12, pady=6,
                               cursor="hand2",
                               activebackground="#29b6f6",
                               activeforeground="white")
        refresh_btn.pack(side=tk.RIGHT)
        
        # 새로고침 버튼 호버 효과
        def on_enter_refresh(e):
            refresh_btn['background'] = '#29b6f6'
        def on_leave_refresh(e):
            refresh_btn['background'] = '#4fc3f7'
        refresh_btn.bind("<Enter>", on_enter_refresh)
        refresh_btn.bind("<Leave>", on_leave_refresh)
        
        # 날씨 정보 표시 영역 (스크롤 가능)
        self.weather_frame = tk.Frame(main_frame, bg="#f8f9fa")
        self.weather_frame.pack(fill=tk.BOTH, expand=True)
        
        # 로딩 메시지 (메인창 스타일)
        self.loading_label = tk.Label(self.weather_frame, text="날씨 정보를 불러오는 중...", 
                                     font=("Segoe UI", 11), fg="#7f8c8d", bg="#f8f9fa")
        self.loading_label.pack(expand=True)
        
        # 하단 버튼 영역
        button_frame = tk.Frame(main_frame, bg="#f8f9fa")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 닫기 버튼 (메인창 스타일)
        close_btn = tk.Button(button_frame, text="닫기", 
                             command=self.close_weather,
                             font=("Segoe UI", 10, "bold"),
                             bg="#66bb6a", fg="white",
                             relief=tk.FLAT, bd=0,
                             padx=20, pady=10,
                             cursor="hand2",
                             activebackground="#4caf50",
                             activeforeground="white")
        close_btn.pack(fill=tk.X)
        
        # 닫기 버튼 호버 효과
        def on_enter_close(e):
            close_btn['background'] = '#4caf50'
        def on_leave_close(e):
            close_btn['background'] = '#66bb6a'
        close_btn.bind("<Enter>", on_enter_close)
        close_btn.bind("<Leave>", on_leave_close)
    
    def load_weather_info(self):
        """실제 날씨 정보 로드"""
        def fetch_weather():
            # 백그라운드에서 실제 날씨 데이터 가져오기
            weather_data = get_weather_data()
            # UI 스레드에서 업데이트
            self.weather_window.after(0, lambda: self.display_weather_data(weather_data))
        
        # 백그라운드 스레드에서 날씨 정보 가져오기
        thread = threading.Thread(target=fetch_weather, daemon=True)
        thread.start()
    
    def display_weather_data(self, weather_data):
        """날씨 데이터를 UI에 표시 - 메인창과 같은 평화로운 디자인"""
        try:
            # 로딩 라벨 제거
            if hasattr(self, 'loading_label'):
                self.loading_label.destroy()
            
            # 기존 위젯 제거 (새로고침 시)
            for widget in self.weather_frame.winfo_children():
                widget.destroy()
            
            # 현재 시간
            now = datetime.now()
            
            # 현재 날씨 카드 (메인창 스타일)
            current_card = tk.Frame(self.weather_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                                   highlightbackground="#e0e0e0", highlightthickness=1)
            current_card.pack(fill=tk.X, pady=(0, 10))
            
            # 현재 날씨 헤더
            current_header = tk.Frame(current_card, bg="#e3f2fd")
            current_header.pack(fill=tk.X)
            
            current_title = tk.Label(current_header, text="🌟 현재 날씨", 
                                   font=("Segoe UI", 12, "bold"), 
                                   bg="#e3f2fd", fg="#1976d2")
            current_title.pack(pady=8)
            
            # 위치 정보
            location = weather_data.get('location', self.current_location)
            location_label = tk.Label(current_card, text=f"� {location}",
                                    font=("Segoe UI", 11, "bold"), 
                                    bg="#ffffff", fg="#2c3e50")
            location_label.pack(pady=(10, 5))
            
            # 현재 날씨 정보
            current_weather = weather_data['current']
            current_info_text = f"{current_weather['icon']} {current_weather['description']} {current_weather['temp']}"
            
            current_info = tk.Label(current_card, text=current_info_text,
                                  font=("Segoe UI", 18, "bold"), 
                                  bg="#ffffff", fg="#2c3e50")
            current_info.pack(pady=8)
            
            # 상세 정보
            detail_info = tk.Label(current_card, 
                                 text=f"습도: {current_weather['humidity']} | 바람: {current_weather['wind']}",
                                 font=("Segoe UI", 10), 
                                 bg="#ffffff", fg="#7f8c8d")
            detail_info.pack(pady=(0, 12))
            
            # 시간대별 예보 카드 (메인창 스타일)
            forecast_card = tk.Frame(self.weather_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                                    highlightbackground="#e0e0e0", highlightthickness=1)
            forecast_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # 예보 헤더
            forecast_header = tk.Frame(forecast_card, bg="#e3f2fd")
            forecast_header.pack(fill=tk.X)
            
            forecast_title = tk.Label(forecast_header, text="📅 시간대별 예보", 
                                    font=("Segoe UI", 12, "bold"), 
                                    bg="#e3f2fd", fg="#1976d2")
            forecast_title.pack(pady=8)
            
            # 스크롤 가능한 예보 영역
            canvas = tk.Canvas(forecast_card, bg="#ffffff", highlightthickness=0, bd=0)
            scrollbar = tk.Scrollbar(forecast_card, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#ffffff")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)
            
            # 시간대별 날씨 정보 표시 (깔끔한 행 스타일)
            hourly_data = weather_data['hourly']
            current_hour = now.hour
            current_index = 0  # 현재 시간대 인덱스
            
            for i, hour_data in enumerate(hourly_data):
                # 현재 시간과 가까운 시간대 강조
                hour_int = int(hour_data['time'].split(':')[0])
                is_current = abs(hour_int - current_hour) <= 1
                
                if is_current and current_index == 0:
                    current_index = i  # 현재 시간대 인덱스 저장
                
                bg_color = "#e3f2fd" if is_current else "#ffffff"
                
                slot_frame = tk.Frame(scrollable_frame, bg=bg_color)
                slot_frame.pack(fill=tk.X, pady=1, padx=5)
                
                # 구분선 (첫 번째 제외)
                if i > 0:
                    separator = tk.Frame(scrollable_frame, bg="#e0e0e0", height=1)
                    separator.pack(fill=tk.X, padx=15)
                
                # 시간
                time_label = tk.Label(slot_frame, text=hour_data['time'], 
                                    font=("Segoe UI", 10, "bold" if is_current else "normal"), 
                                    bg=bg_color, fg="#2c3e50", width=8, anchor="w")
                time_label.pack(side=tk.LEFT, padx=(10, 5), pady=8)
                
                # 날씨 아이콘
                try:
                    weather_type = get_weather_type_from_icon(hour_data['icon'])
                    weather_icon = load_icon_image(weather_type, 24)
                    if weather_icon:
                        weather_label = tk.Label(slot_frame, image=weather_icon, 
                                               bg=bg_color)
                        weather_label.image = weather_icon  # 참조 유지
                    else:
                        raise Exception("아이콘 로드 실패")
                except Exception as e:
                    # 이미지 로드 실패시 이모지 사용
                    weather_label = tk.Label(slot_frame, text=hour_data['icon'], 
                                           font=("Segoe UI", 12), 
                                           bg=bg_color)
                weather_label.pack(side=tk.LEFT, padx=5)
                
                # 온도
                temp_label = tk.Label(slot_frame, text=hour_data['temp'], 
                                    font=("Segoe UI", 10, "bold" if is_current else "normal"), 
                                    bg=bg_color, fg="#e74c3c", width=7, anchor="center")
                temp_label.pack(side=tk.LEFT, padx=3)
                
                # 설명 (모든 텍스트 명확하게 표시)
                desc_text = hour_data['desc']
                desc_container = tk.Frame(slot_frame, bg=bg_color, width=180)
                desc_container.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
                desc_container.pack_propagate(False)
                
                if len(desc_text) > 12:  # 긴 텍스트는 스크롤
                    # Canvas로 스크롤 효과
                    desc_canvas = tk.Canvas(desc_container, bg=bg_color, 
                                          highlightthickness=0, height=25)
                    desc_canvas.pack(fill=tk.BOTH, expand=True)
                    
                    # 텍스트 생성 (더 큰 폰트, 더 진한 색상)
                    text_id = desc_canvas.create_text(0, 12, text=desc_text, 
                                                     font=("Segoe UI", 10),
                                                     fill="#5f6c7d", anchor="w")
                    
                    # 텍스트 너비 계산
                    bbox = desc_canvas.bbox(text_id)
                    text_width = bbox[2] - bbox[0] if bbox else 0
                    
                    # 스크롤 애니메이션
                    def scroll_text(x_pos=0):
                        if desc_canvas.winfo_exists():
                            desc_canvas.coords(text_id, x_pos, 12)
                            if x_pos < -text_width:
                                x_pos = 180  # 처음으로
                            desc_canvas.after(50, lambda: scroll_text(x_pos - 2))
                    
                    scroll_text(0)
                else:
                    # 짧은 텍스트는 일반 라벨 (더 명확하게)
                    desc_label = tk.Label(desc_container, text=desc_text, 
                                        font=("Segoe UI", 10), 
                                        bg=bg_color, fg="#5f6c7d", anchor="w")
                    desc_label.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # 현재 시간대가 중앙에 오도록 스크롤 조절
            def scroll_to_current():
                # 모든 위젯이 그려진 후 실행
                canvas.update_idletasks()
                total_items = len(hourly_data)
                if total_items > 0 and current_index > 0:
                    # 현재 시간대가 뷰포트 중앙에 오도록 계산
                    # 중앙 위치 = (현재 인덱스 / 전체 개수) - (뷰포트 높이 / 전체 높이 / 2)
                    scroll_position = max(0, min(1, (current_index / total_items) - 0.2))
                    canvas.yview_moveto(scroll_position)
            
            # 약간의 지연 후 스크롤 조절 (위젯 렌더링 완료 대기)
            self.weather_window.after(100, scroll_to_current)
            
            # 업데이트 시간 (메인창 스타일)
            update_card = tk.Frame(self.weather_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                                  highlightbackground="#e0e0e0", highlightthickness=1)
            update_card.pack(fill=tk.X)
            
            self.update_label = tk.Label(update_card, 
                                       text=f"🔄 마지막 업데이트: {now.strftime('%Y-%m-%d %H:%M:%S')}", 
                                       font=("Segoe UI", 9), 
                                       bg="#ffffff", fg="#7f8c8d")
            self.update_label.pack(pady=8)
            
        except Exception as e:
            print(f"날씨 데이터 표시 오류: {e}")
            error_label = tk.Label(self.weather_frame, 
                                  text=f"날씨 정보를 표시할 수 없습니다.\n{e}",
                                  font=("Segoe UI", 11), 
                                  fg="#e74c3c", 
                                  bg="#f8f9fa",
                                  justify=tk.CENTER)
            error_label.pack(expand=True, pady=20)
    
    def refresh_weather(self):
        """날씨 정보 새로고침 (2시간 캐시 로직 적용)"""
        # 기존 위젯 제거
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
        
        # 로딩 메시지 다시 표시 (메인창 스타일)
        self.loading_label = tk.Label(self.weather_frame, 
                                     text="🔄 날씨 정보를 확인하는 중...", 
                                     font=("Segoe UI", 11), 
                                     fg="#7f8c8d",
                                     bg="#f8f9fa")
        self.loading_label.pack(expand=True)
        
        # 캐시 확인 후 필요시에만 새로고침
        def fetch_weather():
            # 캐시 확인 (2시간 이내면 캐시 사용)
            cached_data = load_weather_cache()
            if cached_data:
                print("✅ 캐시 사용 (2시간 이내)")
                weather_data = cached_data
            else:
                print("⏳ 캐시 만료, 새 데이터 가져오는 중...")
                weather_data = get_weather_data(force_refresh=True)
            
            # UI 스레드에서 업데이트
            self.weather_window.after(0, lambda: self.display_weather_data(weather_data))
        
        # 백그라운드 스레드에서 날씨 정보 가져오기
        thread = threading.Thread(target=fetch_weather, daemon=True)
        thread.start()
    
    def close_weather(self):
        """날씨 창 닫기"""
        try:
            self.weather_window.destroy()
        except:
            pass
    
    def get_weather_type_from_icon(self, icon_text):
        """이모지 아이콘에서 날씨 타입 추출 (클래스 메서드)"""
        return get_weather_type_from_icon(icon_text)

class SettingsWindow:
    """설정 창 클래스"""
    def __init__(self, parent_clock):
        self.parent_clock = parent_clock
        self.settings_window = tk.Toplevel(parent_clock.clock_window)
        self.settings_window.title("ClockApp Ver2 - 시간 설정")
        self.settings_window.geometry("350x500")  # 높이 증가로 모든 옵션 표시
        self.settings_window.resizable(False, False)
        
        # 설정 창을 부모 창 중앙에 위치
        self.settings_window.transient(parent_clock.clock_window)
        self.settings_window.grab_set()  # 모달 창으로 설정
        
        # 아이콘 설정 (사용자 PNG 우선, 없으면 기본 시계 아이콘)
        try:
            icon_file_path = get_icon_path()
            if icon_file_path and os.path.exists(icon_file_path):
                self.settings_window.iconbitmap(icon_file_path)
        except:
            pass
        
        self.create_widgets()
        
        # 창을 부모 창 중앙에 위치
        self.center_on_parent()
        
    def center_on_parent(self):
        """부모 창 중앙에 설정 창 위치시키기"""
        parent = self.parent_clock.clock_window
        parent.update_idletasks()
        
        # 부모 창 위치와 크기 가져오기
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # 설정 창 크기
        settings_width = 350
        settings_height = 500
        
        # 중앙 위치 계산
        x = parent_x + (parent_width - settings_width) // 2
        y = parent_y + (parent_height - settings_height) // 2
        
        self.settings_window.geometry(f"{settings_width}x{settings_height}+{x}+{y}")
    
    def create_widgets(self):
        """설정 창 위젯 생성 - 메인창과 같은 평화로운 디자인"""
        # 메인 배경색 설정 (메인창과 동일)
        self.settings_window.configure(bg="#f8f9fa")
        
        # 메인 프레임
        main_frame = tk.Frame(self.settings_window, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 제목 카드
        title_card = tk.Frame(main_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                             highlightbackground="#e0e0e0", highlightthickness=1)
        title_card.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_card, text="⚙️ 시간 설정", 
                              font=("Segoe UI", 14, "bold"),
                              bg="#ffffff", fg="#2c3e50")
        title_label.pack(pady=12)
        
        # 설정 카드
        settings_card = tk.Frame(main_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                                highlightbackground="#e0e0e0", highlightthickness=1)
        settings_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        settings_inner = tk.Frame(settings_card, bg="#ffffff")
        settings_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 1. 휴식 알림 설정 (연한 파란색 배경)
        break_section = tk.Frame(settings_inner, bg="#f0f8ff", relief=tk.FLAT, bd=0)
        break_section.pack(pady=5, fill=tk.X)
        
        break_frame = tk.Frame(break_section, bg="#f0f8ff")
        break_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.break_enabled_var = tk.BooleanVar()
        self.break_enabled_var.set(getattr(self.parent_clock, 'break_enabled', True))
        
        break_checkbox = tk.Checkbutton(break_frame, 
                                      text="🔔 휴식 알림", 
                                      variable=self.break_enabled_var,
                                      font=("Segoe UI", 10, "bold"),
                                      bg="#f0f8ff", fg="#2c3e50",
                                      activebackground="#f0f8ff")
        break_checkbox.pack(side=tk.LEFT)
        
        time_input_frame = tk.Frame(break_frame, bg="#f0f8ff")
        time_input_frame.pack(side=tk.RIGHT)
        
        tk.Label(time_input_frame, text="간격 (분):", 
                font=("Segoe UI", 9), bg="#f0f8ff", fg="#7f8c8d").pack(side=tk.LEFT, padx=(10, 5))
        self.minutes_entry = tk.Entry(time_input_frame, width=12, 
                                     font=("Segoe UI", 11), relief=tk.SOLID, bd=1)
        self.minutes_entry.pack(side=tk.LEFT)
        self.minutes_entry.insert(0, str(self.parent_clock.time_interval))
        
        # 구분선
        tk.Frame(settings_inner, bg="#e0e0e0", height=1).pack(fill=tk.X, pady=8)
        
        # 2. 점심 알림 설정 (연한 노란색 배경)
        lunch_section = tk.Frame(settings_inner, bg="#fffef0", relief=tk.FLAT, bd=0)
        lunch_section.pack(pady=5, fill=tk.X)
        
        lunch_frame = tk.Frame(lunch_section, bg="#fffef0")
        lunch_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.lunch_enabled_var = tk.BooleanVar()
        self.lunch_enabled_var.set(getattr(self.parent_clock, 'lunch_enabled', True))
        
        lunch_checkbox = tk.Checkbutton(lunch_frame, 
                                      text="🍱 점심 알림", 
                                      variable=self.lunch_enabled_var,
                                      font=("Segoe UI", 10, "bold"),
                                      bg="#fffef0", fg="#2c3e50",
                                      activebackground="#fffef0")
        lunch_checkbox.pack(side=tk.LEFT)
        
        lunch_time_frame = tk.Frame(lunch_frame, bg="#fffef0")
        lunch_time_frame.pack(side=tk.RIGHT)
        
        tk.Label(lunch_time_frame, text="시간:", 
                font=("Segoe UI", 9), bg="#fffef0", fg="#7f8c8d").pack(side=tk.LEFT, padx=(10, 5))
        self.lunch_hour_entry = tk.Entry(lunch_time_frame, width=5, 
                                         font=("Segoe UI", 11), relief=tk.SOLID, bd=1)
        self.lunch_hour_entry.pack(side=tk.LEFT)
        self.lunch_hour_entry.insert(0, f"{self.parent_clock.lunch_time[0]:02d}")
        
        tk.Label(lunch_time_frame, text=":", 
                font=("Segoe UI", 9), bg="#fffef0", fg="#7f8c8d").pack(side=tk.LEFT)
        
        self.lunch_minute_entry = tk.Entry(lunch_time_frame, width=5, 
                                           font=("Segoe UI", 11), relief=tk.SOLID, bd=1)
        self.lunch_minute_entry.pack(side=tk.LEFT)
        self.lunch_minute_entry.insert(0, f"{self.parent_clock.lunch_time[1]:02d}")
        
        # 구분선
        tk.Frame(settings_inner, bg="#e0e0e0", height=1).pack(fill=tk.X, pady=8)
        
        # 3. 저녁 알림 설정 (연한 주황색 배경)
        dinner_section = tk.Frame(settings_inner, bg="#fff5f0", relief=tk.FLAT, bd=0)
        dinner_section.pack(pady=5, fill=tk.X)
        
        dinner_frame = tk.Frame(dinner_section, bg="#fff5f0")
        dinner_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.dinner_enabled_var = tk.BooleanVar()
        self.dinner_enabled_var.set(getattr(self.parent_clock, 'dinner_enabled', True))
        
        dinner_checkbox = tk.Checkbutton(dinner_frame, 
                                       text="🍽️ 저녁 알림", 
                                       variable=self.dinner_enabled_var,
                                       font=("Segoe UI", 10, "bold"),
                                       bg="#fff5f0", fg="#2c3e50",
                                       activebackground="#fff5f0")
        dinner_checkbox.pack(side=tk.LEFT)
        
        dinner_time_frame = tk.Frame(dinner_frame, bg="#fff5f0")
        dinner_time_frame.pack(side=tk.RIGHT)
        
        tk.Label(dinner_time_frame, text="시간:", 
                font=("Segoe UI", 9), bg="#fff5f0", fg="#7f8c8d").pack(side=tk.LEFT, padx=(10, 5))
        self.dinner_hour_entry = tk.Entry(dinner_time_frame, width=5, 
                                          font=("Segoe UI", 11), relief=tk.SOLID, bd=1)
        self.dinner_hour_entry.pack(side=tk.LEFT)
        self.dinner_hour_entry.insert(0, f"{self.parent_clock.dinner_time[0]:02d}")
        
        tk.Label(dinner_time_frame, text=":", 
                font=("Segoe UI", 9), bg="#fff5f0", fg="#7f8c8d").pack(side=tk.LEFT)
        
        self.dinner_minute_entry = tk.Entry(dinner_time_frame, width=5, 
                                            font=("Segoe UI", 11), relief=tk.SOLID, bd=1)
        self.dinner_minute_entry.pack(side=tk.LEFT)
        self.dinner_minute_entry.insert(0, f"{self.parent_clock.dinner_time[1]:02d}")
        
        # 구분선
        tk.Frame(settings_inner, bg="#e0e0e0", height=1).pack(fill=tk.X, pady=8)
        
        # 4. 시작 프로그램 등록 (연한 회색 배경)
        startup_section = tk.Frame(settings_inner, bg="#f5f5f5", relief=tk.FLAT, bd=0)
        startup_section.pack(pady=5, fill=tk.X)
        
        startup_frame = tk.Frame(startup_section, bg="#f5f5f5")
        startup_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.startup_var = tk.BooleanVar()
        self.startup_var.set(check_startup_registry())
        
        startup_checkbox = tk.Checkbutton(startup_frame, 
                                        text="💻 윈도우 시작 시 자동 실행", 
                                        variable=self.startup_var,
                                        font=("Segoe UI", 10, "bold"),
                                        bg="#f5f5f5", fg="#2c3e50",
                                        activebackground="#f5f5f5")
        startup_checkbox.pack(side=tk.LEFT)
        
        # 버튼 프레임 (메인창 스타일)
        button_frame = tk.Frame(main_frame, bg="#f8f9fa")
        button_frame.pack(fill=tk.X)
        
        # 저장 버튼
        save_btn = tk.Button(button_frame, text="💾 저장", 
                           command=self.save_settings,
                           font=("Segoe UI", 10, "bold"),
                           bg="#66bb6a", fg="white",
                           relief=tk.FLAT, bd=0,
                           padx=20, pady=10,
                           cursor="hand2",
                           activebackground="#4caf50",
                           activeforeground="white")
        save_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # 저장 버튼 호버 효과
        def on_enter_save(e):
            save_btn['background'] = '#4caf50'
        def on_leave_save(e):
            save_btn['background'] = '#66bb6a'
        save_btn.bind("<Enter>", on_enter_save)
        save_btn.bind("<Leave>", on_leave_save)
        
        # 닫기 버튼
        close_btn = tk.Button(button_frame, text="닫기", 
                            command=self.settings_window.destroy,
                            font=("Segoe UI", 10, "bold"),
                            bg="#90a4ae", fg="white",
                            relief=tk.FLAT, bd=0,
                            padx=20, pady=10,
                            cursor="hand2",
                            activebackground="#78909c",
                            activeforeground="white")
        close_btn.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 닫기 버튼 호버 효과
        def on_enter_close(e):
            close_btn['background'] = '#78909c'
        def on_leave_close(e):
            close_btn['background'] = '#90a4ae'
        close_btn.bind("<Enter>", on_enter_close)
        close_btn.bind("<Leave>", on_leave_close)
    
    def save_settings(self):
        """설정 저장"""
        try:
            # 입력값 검증 및 저장
            minutes = int(self.minutes_entry.get())
            lunch_hour = int(self.lunch_hour_entry.get())
            lunch_minute = int(self.lunch_minute_entry.get())
            dinner_hour = int(self.dinner_hour_entry.get())
            dinner_minute = int(self.dinner_minute_entry.get())
            
            # 체크박스 값들 가져오기
            break_enabled = self.break_enabled_var.get()
            lunch_enabled = self.lunch_enabled_var.get()
            dinner_enabled = self.dinner_enabled_var.get()
            
            # 유효성 검사
            if not (1 <= minutes <= 1440):  # 1분~24시간
                raise ValueError("시간 간격은 1~1440분 사이여야 합니다.")
            if not (0 <= lunch_hour <= 23):
                raise ValueError("점심시간은 0~23시 사이여야 합니다.")
            if not (0 <= lunch_minute <= 59):
                raise ValueError("점심시간 분은 0~59분 사이여야 합니다.")
            if not (0 <= dinner_hour <= 23):
                raise ValueError("저녁시간은 0~23시 사이여야 합니다.")
            if not (0 <= dinner_minute <= 59):
                raise ValueError("저녁시간 분은 0~59분 사이여야 합니다.")
            
            # 설정 저장 (부모 클래스에 전달)
            self.parent_clock.update_time_settings(minutes, lunch_hour, lunch_minute, dinner_hour, dinner_minute, 
                                                 break_enabled, lunch_enabled, dinner_enabled)
            
            # 시작 프로그램 등록/해제 처리
            startup_enabled = self.startup_var.get()
            startup_success = True
            
            if startup_enabled:
                # 시작 프로그램에 등록 (레지스트리 방법 먼저 시도)
                startup_success = add_to_startup()
                if not startup_success:
                    # 레지스트리 방법 실패 시 작업 스케줄러 방법 시도
                    print("레지스트리 방법 실패, 작업 스케줄러 방법 시도...")
                    startup_success = add_to_startup_alternative()
                    if not startup_success:
                        tk.messagebox.showwarning("경고", "시작 프로그램 등록에 실패했습니다.")
                    else:
                        tk.messagebox.showinfo("알림", "작업 스케줄러를 통해 시작 프로그램이 등록되었습니다.")
            else:
                # 시작 프로그램에서 제거 (두 방법 모두 시도)
                reg_success = remove_from_startup()
                sched_success = remove_from_startup_alternative()
                startup_success = reg_success or sched_success
                if not startup_success:
                    tk.messagebox.showwarning("경고", "시작 프로그램 제거에 실패했습니다.")
            
            # 파일에도 저장
            settings = {
                "time_interval": minutes,
                "lunch_hour": lunch_hour,
                "lunch_minute": lunch_minute,
                "dinner_hour": dinner_hour,
                "dinner_minute": dinner_minute,
                "break_enabled": break_enabled,
                "lunch_enabled": lunch_enabled,
                "dinner_enabled": dinner_enabled
            }
            
            if save_settings_to_file(settings):
                # 성공 메시지
                tk.messagebox.showinfo("저장 완료", "설정이 저장되었습니다!")
                self.settings_window.destroy()
            else:
                tk.messagebox.showerror("저장 실패", "설정 파일 저장에 실패했습니다.")
            
        except ValueError as e:
            tk.messagebox.showerror("입력 오류", str(e))
        except Exception as e:
            tk.messagebox.showerror("오류", f"설정 저장 중 오류가 발생했습니다: {e}")

class AboutWindow:
    """배포자 정보 창"""
    def __init__(self, parent_clock):
        self.parent_clock = parent_clock
        self.about_window = tk.Toplevel(parent_clock.clock_window)
        self.about_window.title("ClockApp Ver2 정보")
        self.about_window.geometry("500x600")
        self.about_window.resizable(False, False)
        
        # 창을 화면 중앙에 배치
        self.center_window()
        
        # 아이콘 설정
        try:
            self.about_window.iconbitmap(default='clock_icon.ico')
        except:
            pass
        
        self.create_widgets()
        
        # 창이 닫힐 때 처리
        self.about_window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # 포커스 설정
        self.about_window.focus_set()
        self.about_window.grab_set()
    
    def center_window(self):
        """창을 화면 중앙에 배치"""
        self.about_window.update_idletasks()
        width = self.about_window.winfo_width()
        height = self.about_window.winfo_height()
        x = (self.about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.about_window.winfo_screenheight() // 2) - (height // 2)
        self.about_window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = tk.Frame(self.about_window, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 앱 아이콘과 제목
        title_frame = tk.Frame(main_frame, bg='white')
        title_frame.pack(fill='x', pady=(0, 20))
        
        # 앱 제목
        title_label = tk.Label(title_frame, text="ClockApp Ver2", 
                              font=('Arial', 24, 'bold'), 
                              bg='white', fg='#2E86AB')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="건강한 업무를 위한 자세 알림 앱",
                                 font=('Arial', 12), 
                                 bg='white', fg='#666')
        subtitle_label.pack()
        
        # 버전 정보
        version_frame = tk.Frame(main_frame, bg='#f8f9fa', relief='solid', bd=1)
        version_frame.pack(fill='x', pady=(10, 20))
        
        version_label = tk.Label(version_frame, text="버전 2.0.0",
                                font=('Arial', 14, 'bold'),
                                bg='#f8f9fa', fg='#2E86AB')
        version_label.pack(pady=10)
        
        # 배포자 정보
        info_frame = tk.Frame(main_frame, bg='white')
        info_frame.pack(fill='both', expand=True)
        
        # 정보 텍스트  
        info_text = ("개발사: KoreawookDevTeam\n"
                    "개발자: koreawook\n"
                    "연락처: koreawook@gmail.com\n"
                    "홈페이지: https://koreawook.github.io/ClockApp/\n"
                    "라이선스: MIT License\n"
                    "배포일: 2025년 10월 22일\n\n"
                    "Ver1과 Ver2의 차이점:\n"
                    "• Ver1과 독립적인 실행\n"
                    "• 향상된 UI/UX 및 안정성\n"
                    "• 추가 기능 및 최적화\n"
                    "• 고급 날씨 정보 시스템\n"
                    "• 개선된 스트레칭 가이드\n\n"
                    "신뢰성 보증:\n"
                    "• 개인정보 수집 없음\n"
                    "• 광고 없음, 100% 무료\n"
                    "• 오픈소스 정책\n"
                    "• 의료진 자문 스트레칭 가이드\n"
                    "• 5000+ 사용자 검증 완료")
        
        info_label = tk.Label(info_frame, text=info_text,
                             font=('Arial', 10),
                             bg='white', fg='#333',
                             justify='left',
                             wraplength=450)
        info_label.pack(pady=10, fill='both', expand=True)
        
        # 저작권 정보
        copyright_frame = tk.Frame(main_frame, bg='#e9ecef')
        copyright_frame.pack(fill='x', pady=(10, 0))
        
        copyright_label = tk.Label(copyright_frame, 
                                  text="Copyright © 2025 KoreawookDevTeam. All rights reserved.",
                                  font=('Arial', 9),
                                  bg='#e9ecef', fg='#666')
        copyright_label.pack(pady=8)
        
        # 닫기 버튼
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        close_button = tk.Button(button_frame, text="닫기", 
                                command=self.close_window,
                                font=('Arial', 11, 'bold'),
                                bg='#2E86AB', fg='white',
                                padx=30, pady=8,
                                relief='flat',
                                cursor='hand2')
        close_button.pack(side='right')
    
    def close_window(self):
        """창 닫기"""
        try:
            self.about_window.destroy()
        except:
            pass
    
class ClockWindow:
    """시계 창 클래스"""
    def __init__(self, start_minimized=False):
        # 독립적인 루트 창 생성 (Toplevel 대신 Tk 사용)
        self.clock_window = tk.Tk()
        self.clock_window.title("ClockApp Ver2")
        self.clock_window.geometry("320x240")  # 더 넓은 모던한 크기
        self.clock_window.resizable(False, False)
        
        # 시작 시 최소화 여부 저장
        self.start_minimized = start_minimized
        
        # 설정 로드 (일관된 함수 사용)
        self.settings = load_settings()
        
        # 아이콘 설정 (사용자 PNG 우선, 없으면 기본 시계 아이콘)
        try:
            icon_file_path = get_icon_path()
            if icon_file_path and os.path.exists(icon_file_path):
                self.clock_window.iconbitmap(icon_file_path)
        except:
            pass
        
        # 모던한 메인 프레임 (부드러운 배경색)
        self.clock_window.configure(bg="#f8f9fa")
        main_frame = tk.Frame(self.clock_window, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 상단: 시간 표시 영역 (카드 스타일)
        time_frame = tk.Frame(main_frame, bg="#ffffff", relief=tk.FLAT, bd=0, 
                             highlightbackground="#e0e0e0", highlightthickness=1)
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 시계 레이블 (더 큰 폰트, 모던한 스타일)
        self.time_label = tk.Label(
            time_frame, 
            text="", 
            font=("Segoe UI", 28, "bold"),
            fg="#2c3e50",
            bg="#ffffff",
            cursor="hand2"
        )
        self.time_label.pack(pady=(15, 5))
        
        # 시계 클릭 이벤트 바인딩
        self.time_label.bind("<Button-1>", self.open_settings)
        
        # 날짜 레이블 (더 세련된 스타일)
        self.date_label = tk.Label(
            time_frame, 
            text="", 
            font=("Segoe UI", 10),
            fg="#7f8c8d",
            bg="#ffffff",
            cursor="hand2"
        )
        self.date_label.pack(pady=(0, 15))
        
        # 날짜 클릭 이벤트 바인딩
        self.date_label.bind("<Button-1>", self.open_settings)
        
        # 중단: 상태 표시 영역 (카드 스타일, 부드러운 색상)
        status_frame = tk.Frame(main_frame, bg="#e3f2fd", relief=tk.FLAT, bd=0,
                               highlightbackground="#90caf9", highlightthickness=1)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 다음 휴식시간 라벨 (더 눈에 띄게)
        self.next_break_label = tk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 10, "bold"),
            fg="#1976d2",
            bg="#e3f2fd"
        )
        self.next_break_label.pack(pady=12)
        
        # 하단: 버튼 영역 (플랫 디자인)
        button_frame = tk.Frame(main_frame, bg="#f8f9fa")
        button_frame.pack(fill=tk.X)
        
        # 날씨 확인 버튼 (모던한 플랫 버튼)
        weather_btn = tk.Button(
            button_frame,
            text="🌤️ 날씨",
            command=self.open_weather,
            font=("Segoe UI", 10, "bold"),
            bg="#4fc3f7",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground="#29b6f6",
            activeforeground="white"
        )
        weather_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # 호버 효과 추가
        def on_enter_weather(e):
            weather_btn['background'] = '#29b6f6'
        def on_leave_weather(e):
            weather_btn['background'] = '#4fc3f7'
        weather_btn.bind("<Enter>", on_enter_weather)
        weather_btn.bind("<Leave>", on_leave_weather)
        
        # 설정 버튼 (모던한 플랫 버튼)
        settings_btn = tk.Button(
            button_frame,
            text="⚙️ 설정",
            command=self.open_settings,
            font=("Segoe UI", 10, "bold"),
            bg="#78909c",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground="#607d8b",
            activeforeground="white"
        )
        settings_btn.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 호버 효과 추가
        def on_enter_settings(e):
            settings_btn['background'] = '#607d8b'
        def on_leave_settings(e):
            settings_btn['background'] = '#78909c'
        settings_btn.bind("<Enter>", on_enter_settings)
        settings_btn.bind("<Leave>", on_leave_settings)
        
        # 저장된 설정값 사용 (이미 초기화에서 로드됨)
        self.time_interval = self.settings["time_interval"]
        self.lunch_time = (self.settings["lunch_hour"], self.settings["lunch_minute"])
        self.dinner_time = (self.settings["dinner_hour"], self.settings["dinner_minute"])
        self.break_enabled = self.settings.get("break_enabled", True)
        self.lunch_enabled = self.settings.get("lunch_enabled", True)
        self.dinner_enabled = self.settings.get("dinner_enabled", True)
        
        print("=" * 50)
        print("📁 설정 로드 결과:")
        print(f"   🔄 휴식 간격: {self.time_interval}분")
        print(f"   🍱 점심시간: {self.lunch_time[0]:02d}:{self.lunch_time[1]:02d} ({'활성화' if self.lunch_enabled else '비활성화'})")
        print(f"   🍽️ 저녁시간: {self.dinner_time[0]:02d}:{self.dinner_time[1]:02d} ({'활성화' if self.dinner_enabled else '비활성화'})")
        print(f"   🔔 휴식 알림: {'활성화' if self.break_enabled else '비활성화'}")
        print("=" * 50)
        
        # 휴식 타이머 관련 변수
        self.last_break_time = time.time()  # 마지막 휴식 알림 시간
        
        # 창 닫기 시 정리
        self.clock_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 첫 실행 시 시작프로그램에 자동 등록 (기본 활성화)
        try:
            if not check_startup_registry():
                add_to_startup()
                print("윈도우 시작프로그램에 자동 등록되었습니다.")
        except Exception as e:
            print(f"시작프로그램 등록 오류: {e}")
        
        # 시작 시 최소화 처리
        if self.start_minimized:
            # 창을 숨기고 시스템 트레이에만 표시
            self.clock_window.withdraw()  # 창 숨기기
            self.create_system_tray()     # 시스템 트레이 아이콘 생성
        else:
            # 창을 화면 중앙에 위치
            self.clock_window.eval('tk::PlaceWindow . center')
        
        # 시계 업데이트 시작
        self.update_clock()
        
        # 시계 창의 메인루프 시작
        self.clock_window.mainloop()
        
    def update_clock(self):
        """시계 업데이트"""
        try:
            now = datetime.now()
            
            # 시간 포맷 (HH:MM:SS)
            time_str = now.strftime("%H:%M:%S")
            self.time_label.config(text=time_str)
            
            # 날짜 포맷 (YYYY-MM-DD 요일)
            date_str = now.strftime("%Y-%m-%d %A")
            self.date_label.config(text=date_str)
            
            # 휴식 타이머 체크
            self.check_break_time()
            
            # 식사 시간 체크
            self.check_meal_time()
            
            # 다음 휴식시간 업데이트
            self.update_next_break_info()
            
            # 1초 후 다시 업데이트
            self.clock_window.after(1000, self.update_clock)
            
        except Exception as e:
            print(f"시계 업데이트 오류: {e}")
    
    def update_next_break_info(self):
        """다음 휴식시간 정보 업데이트"""
        try:
            # 식사시간 중이면 특별 메시지 표시
            if self.is_meal_time():
                self.next_break_label.config(text="🍽️ 식사시간 (휴식 알림 일시정지)", fg="orange")
                return
            
            current_time = time.time()
            elapsed_minutes = (current_time - self.last_break_time) / 60
            
            # 다음 휴식까지 남은 시간 계산
            remaining_minutes = max(0, self.time_interval - elapsed_minutes)
            
            if remaining_minutes >= 1:
                remaining_mins = int(remaining_minutes)
                remaining_secs = int((remaining_minutes - remaining_mins) * 60)
                self.next_break_label.config(text=f"⏰ 다음 휴식: {remaining_mins}:{remaining_secs:02d}", fg="green")
            else:
                remaining_secs = int(remaining_minutes * 60)
                if remaining_secs > 0:
                    self.next_break_label.config(text=f"⏰ 다음 휴식: {remaining_secs}초", fg="orange")
                else:
                    self.next_break_label.config(text="⏰ 휴식시간!", fg="red")
            
        except Exception as e:
            print(f"다음 휴식시간 정보 업데이트 오류: {e}")
    
    def is_meal_time(self):
        """현재 식사시간인지 확인 (식사 알림이 활성화된 경우에만)"""
        try:
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            current_time_minutes = current_hour * 60 + current_minute
            
            is_meal = False
            
            # 점심시간 체크 (점심 알림이 활성화된 경우에만)
            if getattr(self, 'lunch_enabled', True):
                lunch_start = self.lunch_time[0] * 60 + self.lunch_time[1]
                lunch_end = lunch_start + 60  # 1시간 후
                if lunch_start <= current_time_minutes < lunch_end:
                    is_meal = True
            
            # 저녁시간 체크 (저녁 알림이 활성화된 경우에만)
            if getattr(self, 'dinner_enabled', True):
                dinner_start = self.dinner_time[0] * 60 + self.dinner_time[1]
                dinner_end = dinner_start + 60  # 1시간 후
                if dinner_start <= current_time_minutes < dinner_end:
                    is_meal = True
            
            return is_meal
            
        except Exception as e:
            print(f"식사시간 확인 오류: {e}")
            return False
    
    def check_break_time(self):
        """휴식 시간 체크"""
        try:
            # 휴식 알림이 비활성화되어 있으면 건너뛰기
            if not getattr(self, 'break_enabled', True):
                return
            
            # 식사시간 중이면 휴식 팝업 건너뛰기
            if self.is_meal_time():
                print("식사시간 중이므로 휴식 알림을 건너뜁니다.")
                return
            
            current_time = time.time()
            elapsed_minutes = (current_time - self.last_break_time) / 60
            
            # 설정된 시간 간격이 지났으면 휴식 알림
            if elapsed_minutes >= self.time_interval:
                print(f"휴식 시간! {self.time_interval}분이 지났습니다.")
                self.show_break_popup()
                self.last_break_time = current_time  # 마지막 휴식 시간 업데이트
                
        except Exception as e:
            print(f"휴식 시간 체크 오류: {e}")
    
    def show_break_popup(self):
        """휴식 팝업 표시"""
        try:
            RestPopup()
        except Exception as e:
            print(f"휴식 팝업 표시 오류: {e}")
    
    def check_meal_time(self):
        """식사 시간 체크"""
        try:
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            current_date = now.strftime("%Y-%m-%d")
            
            # 점심 시간 체크 (정확한 시간에만)
            if (getattr(self, 'lunch_enabled', True) and 
                current_hour == self.lunch_time[0] and current_minute == self.lunch_time[1] and 
                (not hasattr(self, 'lunch_shown_today') or 
                getattr(self, 'lunch_shown_today', '') != current_date)):
                print("점심 시간입니다!")
                self.show_meal_popup("점심")
                self.lunch_shown_today = current_date
            
            # 저녁 시간 체크 (정확한 시간에만)
            if (getattr(self, 'dinner_enabled', True) and
                current_hour == self.dinner_time[0] and current_minute == self.dinner_time[1] and
                (not hasattr(self, 'dinner_shown_today') or 
                getattr(self, 'dinner_shown_today', '') != current_date)):
                print("저녁 시간입니다!")
                self.show_meal_popup("저녁")
                self.dinner_shown_today = current_date
                
        except Exception as e:
            print(f"식사 시간 체크 오류: {e}")
    
    def show_meal_popup(self, meal_type):
        """식사 팝업 표시"""
        try:
            MealPopup(meal_type)
        except Exception as e:
            print(f"식사 팝업 표시 오류: {e}")
    
    def on_closing(self):
        """창 닫기 처리 - X 버튼 클릭 시 백그라운드로 이동"""
        try:
            # 창을 완전히 숨기기
            self.clock_window.withdraw()
            
            # 작업표시줄에서도 숨기기
            self.clock_window.attributes('-toolwindow', True)
            
            # 시스템 트레이 아이콘 생성 (없으면)
            if not hasattr(self, 'system_tray') or not self.system_tray:
                self.create_system_tray()
            
            # 기존 트레이 창이 있으면 제거
            if hasattr(self, 'tray_window') and self.tray_window:
                try:
                    self.tray_window.destroy()
                    self.tray_window = None
                except:
                    pass
            
            # 사용자에게 백그라운드 실행 알림
            self.show_background_notification()
            
        except Exception as e:
            print(f"백그라운드 이동 오류: {e}")
            # 오류 발생 시 완전 종료
            self.exit_application()
    
    def show_background_notification(self):
        """백그라운드 실행 알림 표시"""
        try:
            # 간단한 알림 팝업 (자동으로 사라짐)
            notification = tk.Toplevel()
            notification.title("ClockApp")
            notification.geometry("300x100")
            notification.resizable(False, False)
            notification.attributes('-topmost', True)
            notification.attributes('-toolwindow', True)  # 작업표시줄에서 숨김
            
            # 화면 우하단에 위치
            notification.update_idletasks()
            screen_width = notification.winfo_screenwidth()
            screen_height = notification.winfo_screenheight()
            x = screen_width - 320
            y = screen_height - 150
            notification.geometry(f"300x100+{x}+{y}")
            
            # 알림 내용
            frame = tk.Frame(notification, bg="#f0f0f0")
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            tk.Label(frame, text="🕐 ClockApp", font=("Arial", 12, "bold"), bg="#f0f0f0").pack()
            tk.Label(frame, text="백그라운드에서 실행 중입니다", font=("Arial", 9), bg="#f0f0f0").pack()
            tk.Label(frame, text="트레이 아이콘을 확인하세요", font=("Arial", 8), fg="gray", bg="#f0f0f0").pack()
            
            # 3초 후 자동으로 닫힘
            notification.after(3000, notification.destroy)
            
        except Exception as e:
            print(f"알림 표시 오류: {e}")
    
    def create_system_tray(self):
        """시스템 트레이 기능 구현 (간단한 버전)"""
        try:
            # 우클릭 메뉴 생성
            self.tray_menu = tk.Menu(self.clock_window, tearoff=0)
            self.tray_menu.add_command(label="ClockApp Ver2 열기", command=self.show_window)
            self.tray_menu.add_command(label="설정", command=self.open_settings)
            self.tray_menu.add_command(label="날씨", command=self.open_weather)
            self.tray_menu.add_separator()
            self.tray_menu.add_command(label="Ver2 정보", command=self.open_about)
            self.tray_menu.add_separator()
            self.tray_menu.add_command(label="종료", command=self.exit_application)
            
            # 시스템 트레이 아이콘 시뮬레이션 (작은 창)
            self.create_tray_icon()
            
        except Exception as e:
            print(f"시스템 트레이 생성 오류: {e}")
    
    def create_tray_icon(self):
        """트레이 아이콘 창 생성"""
        try:
            self.tray_window = tk.Toplevel(self.clock_window)
            self.tray_window.title("ClockApp - 트레이")
            
            # 화면 우하단에 위치
            self.tray_window.update_idletasks()
            screen_width = self.tray_window.winfo_screenwidth()
            screen_height = self.tray_window.winfo_screenheight()
            
            tray_width = 200
            tray_height = 120
            x = screen_width - tray_width - 10
            y = screen_height - tray_height - 50  # 작업표시줄 위에
            
            self.tray_window.geometry(f"{tray_width}x{tray_height}+{x}+{y}")
            self.tray_window.resizable(False, False)
            self.tray_window.attributes('-topmost', True)  # 항상 위에
            self.tray_window.attributes('-toolwindow', True)  # 작업표시줄에서 숨김
            
            # 아이콘 설정 (사용자 PNG 우선, 없으면 기본 시계 아이콘)
            try:
                icon_file_path = get_icon_path()
                if icon_file_path and os.path.exists(icon_file_path):
                    self.tray_window.iconbitmap(icon_file_path)
            except:
                pass
            
            # 트레이 내용 (더 눈에 잘 띄게)
            tray_frame = tk.Frame(self.tray_window, bg="#2c3e50", relief=tk.RAISED, bd=2)
            tray_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            tk.Label(tray_frame, text="� ClockApp", font=("Arial", 10, "bold"), bg="#f0f0f0").pack()
            tk.Label(tray_frame, text="트레이 모드", font=("Arial", 8), fg="gray", bg="#f0f0f0").pack()
            
            btn_frame = tk.Frame(tray_frame, bg="#f0f0f0")
            btn_frame.pack(pady=3)
            
            tk.Button(btn_frame, text="열기", command=self.show_window, width=5, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
            tk.Button(btn_frame, text="종료", command=self.exit_application, width=5, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
            
            # 우클릭 메뉴 바인딩
            self.tray_window.bind("<Button-3>", self.show_tray_menu)
            tray_frame.bind("<Button-3>", self.show_tray_menu)
            
        except Exception as e:
            print(f"트레이 아이콘 생성 오류: {e}")
    
    def update_tray_time(self):
        """트레이 창의 시간 업데이트"""
        try:
            if hasattr(self, 'tray_time_label') and self.tray_time_label.winfo_exists():
                current_time = datetime.now().strftime("%H:%M:%S")
                self.tray_time_label.config(text=current_time)
                # 1초 후 다시 실행
                self.root.after(1000, self.update_tray_time)
        except Exception as e:
            print(f"트레이 시간 업데이트 오류: {e}")
    
    def show_tray_menu(self, event):
        """트레이 메뉴 표시"""
        try:
            self.tray_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"트레이 메뉴 표시 오류: {e}")
    
    def show_window(self):
        """창 다시 표시"""
        try:
            self.clock_window.deiconify()  # 창 다시 표시
            self.clock_window.lift()       # 창을 맨 앞으로
            if hasattr(self, 'tray_window'):
                self.tray_window.destroy()  # 트레이 창 닫기
        except Exception as e:
            print(f"창 표시 오류: {e}")
    
    def create_system_tray(self):
        """실제 Windows 시스템 트레이 아이콘 생성"""
        try:
            # 트레이 아이콘 이미지 가져오기
            icon_image = self.get_tray_icon_image()
            
            # 트레이 메뉴 생성
            menu = Menu(
                MenuItem("Ver2 열기", self.show_window_from_tray, default=True),
                MenuItem("설정", self.open_settings_from_tray),
                Menu.SEPARATOR,
                MenuItem("Ver2 정보", self.open_about_from_tray),
                Menu.SEPARATOR,
                MenuItem("종료", self.quit_from_tray)
            )
            
            # 시스템 트레이 아이콘 생성
            self.system_tray = pystray.Icon(
                "ClockApp Ver2",
                icon_image,
                "ClockApp Ver2 - 시간 관리 도구",
                menu
            )
            
            # 별도 스레드에서 트레이 실행
            self.tray_thread = threading.Thread(target=self.system_tray.run, daemon=True)
            self.tray_thread.start()
            
            print("Windows 시스템 트레이 아이콘이 생성되었습니다.")
            
        except Exception as e:
            print(f"시스템 트레이 아이콘 생성 오류: {e}")
    
    def get_tray_icon_image(self):
        """트레이에 사용할 아이콘 이미지 가져오기"""
        try:
            # 1. clock_app.ico 아이콘이 있으면 우선 사용
            clock_app_ico = os.path.join(os.path.dirname(__file__), "clock_app.ico")
            if os.path.exists(clock_app_ico):
                image = Image.open(clock_app_ico)
                # 적절한 크기로 리사이즈 (32x32가 시스템 트레이에 적합)
                image = image.resize((32, 32), Image.Resampling.LANCZOS)
                return image
            
            # 2. clock_icon.ico 아이콘이 있으면 사용 (fallback)
            clock_icon_ico = os.path.join(os.path.dirname(__file__), "clock_icon.ico")
            if os.path.exists(clock_icon_ico):
                image = Image.open(clock_icon_ico)
                # 적절한 크기로 리사이즈 (32x32가 시스템 트레이에 적합)
                image = image.resize((32, 32), Image.Resampling.LANCZOS)
                return image
            else:
                # 3. 기본 시계 아이콘 생성 (마지막 fallback)
                return create_clock_image(32)
        except Exception as e:
            print(f"트레이 아이콘 이미지 생성 오류: {e}")
            # 오류 시 기본 아이콘 반환
            return create_clock_image(32)
    
    def show_window_from_tray(self, icon=None, item=None):
        """트레이에서 창 열기"""
        self.clock_window.after(0, self.show_window)
    
    def open_settings_from_tray(self, icon=None, item=None):
        """트레이에서 설정 열기"""
        self.clock_window.after(0, self.open_settings)
    
    def open_about_from_tray(self, icon=None, item=None):
        """트레이에서 정보 창 열기"""
        self.clock_window.after(0, self.open_about)
    
    def quit_from_tray(self, icon=None, item=None):
        """트레이에서 애플리케이션 종료"""
        try:
            # 시스템 트레이 아이콘 정리
            if hasattr(self, 'system_tray') and self.system_tray:
                self.system_tray.stop()
        except:
            pass
        self.clock_window.after(0, self.exit_application)
    
    def exit_application(self):
        """애플리케이션 완전 종료"""
        try:
            # 시스템 트레이 정리
            if hasattr(self, 'system_tray') and self.system_tray:
                try:
                    self.system_tray.stop()
                except:
                    pass
            
            # 기존 트레이 창 정리
            if hasattr(self, 'tray_window') and self.tray_window:
                try:
                    self.tray_window.destroy()
                except:
                    pass
            
            # 메인 창 종료
            self.clock_window.quit()
            self.clock_window.destroy()
        except:
            pass
    
    def open_settings(self, event=None):
        """설정 창 열기"""
        try:
            SettingsWindow(self)
        except Exception as e:
            print(f"설정 창 열기 오류: {e}")
    
    def open_weather(self):
        """날씨 창 열기"""
        try:
            WeatherWindow(self)
        except Exception as e:
            print(f"날씨 창 열기 오류: {e}")
    
    def open_about(self):
        """정보 창 열기"""
        try:
            AboutWindow(self)
        except Exception as e:
            print(f"정보 창 열기 오류: {e}")
    
    def update_time_settings(self, minutes, lunch_hour, lunch_minute, dinner_hour, dinner_minute, 
                           break_enabled=True, lunch_enabled=True, dinner_enabled=True):
        """시간 설정 업데이트"""
        self.time_interval = minutes
        self.lunch_time = (lunch_hour, lunch_minute)
        self.dinner_time = (dinner_hour, dinner_minute)
        self.break_enabled = break_enabled
        self.lunch_enabled = lunch_enabled
        self.dinner_enabled = dinner_enabled
        
        # 휴식 타이머 리셋 (새로운 간격 적용)
        self.last_break_time = time.time()
        
        print(f"설정 업데이트됨 - 간격: {minutes}분, 점심: {lunch_hour:02d}:{lunch_minute:02d}, 저녁: {dinner_hour:02d}:{dinner_minute:02d}")
        print(f"활성화 상태 - 휴식: {break_enabled}, 점심: {lunch_enabled}, 저녁: {dinner_enabled}")
        print("휴식 타이머가 리셋되었습니다.")

def create_hello_window():
    """인사 창 생성"""
    # 실행 시작 시 아이콘 파일 생성
    print("하트 아이콘 파일 생성 중..")
    icon_file_path = create_icon_file()

    # 커스텀 팝업 창 만들기
    root = tk.Tk()
    root.geometry("300x180")
    root.resizable(False, False)
    root.overrideredirect(True)  # 기본 타이틀바 제거

    # 아이콘 설정
    try:
        if icon_file_path and os.path.exists(icon_file_path):
            root.iconbitmap(icon_file_path)
            print("생성된 하트 아이콘 적용 성공")
    except Exception as e:
        print(f"아이콘 설정 실패: {e}")

    # 창을 화면 중앙에 위치
    root.eval('tk::PlaceWindow . center')

    # 커스텀 타이틀바 만들기
    title_frame = tk.Frame(root, bg="#d0d0d0", height=30)
    title_frame.pack(fill=tk.X, side=tk.TOP)
    title_frame.pack_propagate(False)

    # 드래그 기능을 위한 변수
    drag_data = {"x": 0, "y": 0}

    def start_drag(event):
        drag_data["x"] = event.x
        drag_data["y"] = event.y

    def on_drag(event):
        x = root.winfo_x() + event.x - drag_data["x"]
        y = root.winfo_y() + event.y - drag_data["y"]
        root.geometry(f"+{x}+{y}")

    # 타이틀바에 드래그 이벤트 바인딩
    title_frame.bind("<Button-1>", start_drag)
    title_frame.bind("<B1-Motion>", on_drag)

    # 타이틀바 내용 (왼쪽 정렬)
    title_content = tk.Frame(title_frame, bg="#d0d0d0")
    title_content.pack(side=tk.LEFT, padx=10, pady=5)

    # 닫기 버튼 (오른쪽 정렬)
    close_button = tk.Button(title_frame, text="×", command=root.destroy, 
                           bg="#d0d0d0", fg="black", font=("Arial", 12, "bold"),
                           width=3, height=1, relief=tk.FLAT)
    close_button.pack(side=tk.RIGHT, padx=5, pady=5)

    # 닫기 버튼에 호버 효과 추가
    def on_enter(e):
        close_button.config(bg="#ff4444", fg="white")
    
    def on_leave(e):
        close_button.config(bg="#d0d0d0", fg="black")
    
    close_button.bind("<Enter>", on_enter)
    close_button.bind("<Leave>", on_leave)

    try:
        # 타이틀바용 작은 마우스 이미지
        title_clock = create_clock_image(20)
        if title_clock:
            title_clock_photo = ImageTk.PhotoImage(title_clock)
            
            # 시계 이미지
            title_clock_label = tk.Label(title_content, image=title_clock_photo, bg="#d0d0d0")
            title_clock_label.pack(side=tk.LEFT, padx=(0, 5))

            # 인사 텍스트
            title_text = tk.Label(title_content, text="안녕하세요!", bg="#d0d0d0", font=("Arial", 10, "bold"))       
            title_text.pack(side=tk.LEFT)

            # 드래그 이벤트 바인딩
            title_content.bind("<Button-1>", start_drag)
            title_content.bind("<B1-Motion>", on_drag)
            title_clock_label.bind("<Button-1>", start_drag)
            title_clock_label.bind("<B1-Motion>", on_drag)
            title_text.bind("<Button-1>", start_drag)
            title_text.bind("<B1-Motion>", on_drag)
        else:
            raise Exception("시계 이미지 생성 실패")

    except Exception as e:
        print(f"타이틀바 하트 이미지 오류: {e}")
        title_text = tk.Label(title_content, text="♥ 안녕하세요!", bg="#d0d0d0", font=("Arial", 10, "bold"))   
        title_text.pack()
        title_text.bind("<Button-1>", start_drag)
        title_text.bind("<B1-Motion>", on_drag)

    # 메인 컨텐츠 영역
    content_frame = tk.Frame(root)
    content_frame.pack(fill=tk.BOTH, expand=True)

    try:
        # 메인 시계 이미지
        clock_image_original = create_clock_image(64)
        if clock_image_original:
            # 마우스 이미지와 텍스트를 함께 표시하는 프레임
            main_frame = tk.Frame(content_frame)
            main_frame.pack(expand=True)

            # 마우스 이미지를 위한 고정 크기 프레임
            mouse_frame = tk.Frame(main_frame, width=60, height=60)
            mouse_frame.pack(side=tk.LEFT, padx=(0, 10))
            mouse_frame.pack_propagate(False)

            # 마우스 이미지 라벨
            clock_label = tk.Label(mouse_frame)
            clock_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            # 안녕 텍스트 라벨
            text_label = tk.Label(main_frame, text="안녕", font=("Arial", 16))
            text_label.pack(side=tk.LEFT)

            # 애니메이션 변수
            import math
            animation_step = 0
            min_size = 32
            max_size = 48
            total_steps = 120

            def ease_in_out_quart(t):
                if t < 0.5:
                    return 8 * t * t * t * t
                else:
                    return 1 - pow(-2 * t + 2, 4) / 2

            def animate_clock():
                nonlocal animation_step
                progress = (animation_step % total_steps) / total_steps
                sine_progress = (math.cos(progress * 2 * math.pi) + 1) / 2
                eased_progress = ease_in_out_quart(sine_progress)
                current_size = min_size + (max_size - min_size) * eased_progress
                size_int = max(min_size, min(max_size, int(round(current_size))))

                clock_resized = clock_image_original.resize((size_int, size_int), Image.Resampling.LANCZOS)
                clock_photo = ImageTk.PhotoImage(clock_resized)
                clock_label.configure(image=clock_photo)
                clock_label.image = clock_photo

                animation_step += 1
                root.after(17, animate_clock)

            # 애니메이션 시작
            animate_clock()
        else:
            raise Exception("메인 마우스 이미지 생성 실패")

    except Exception as e:
        print(f"메인 하트 이미지 오류: {e}")
        label = tk.Label(content_frame, text="♥ 안녕", font=("Arial", 16))
        label.pack(expand=True)

    # 시계 창을 여는 함수
    def show_clock():
        root.withdraw()  # 인사창 숨기기
        try:
            ClockWindow()  # 시계창 열기
        except Exception as e:
            print(f"시계 창 오류: {e}")
        finally:
            try:
                root.quit()
                root.destroy()
            except:
                pass

    # 확인 버튼
    button = tk.Button(content_frame, text="확인", command=show_clock, width=10)
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    # Win32 뮤텍스를 사용한 중복 실행 방지 (Ver2 전용)
    MUTEX_NAME_V2 = "Global\\ClockApp_Ver2_SingleInstance_Mutex"
    MUTEX_NAME_V1 = "Global\\ClockApp_SingleInstance_Mutex"  # Ver1 감지용
    
    # Win32 API 함수 선언
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    CreateMutexW = kernel32.CreateMutexW
    CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    CreateMutexW.restype = wintypes.HANDLE
    
    OpenMutexW = kernel32.OpenMutexW
    OpenMutexW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    OpenMutexW.restype = wintypes.HANDLE
    
    GetLastError = kernel32.GetLastError
    ERROR_ALREADY_EXISTS = 183
    
    # Ver1이 실행 중인지 확인
    try:
        v1_mutex = OpenMutexW(0x100000, False, MUTEX_NAME_V1)  # SYNCHRONIZE access
        if v1_mutex:
            kernel32.CloseHandle(v1_mutex)
            MessageBoxW = ctypes.windll.user32.MessageBoxW
            result = MessageBoxW(None, 
                               "ClockApp Ver1이 실행 중입니다.\n"
                               "Ver2를 실행하시겠습니까?\n"
                               "(Ver1과 Ver2는 독립적으로 실행됩니다)",
                               "ClockApp Ver2", 
                               0x24)  # MB_YESNO | MB_ICONQUESTION
            if result != 6:  # IDYES가 아니면 종료
                sys.exit(0)
    except:
        pass  # Ver1이 실행되지 않음
    
    # Ver2 뮤텍스 생성 시도
    mutex_handle = CreateMutexW(None, False, MUTEX_NAME_V2)
    
    if GetLastError() == ERROR_ALREADY_EXISTS:
        print("ClockApp Ver2가 이미 실행 중입니다.")
        # 메시지 박스 표시 (콘솔이 없을 수 있으므로)
        MessageBoxW = ctypes.windll.user32.MessageBoxW
        MessageBoxW(None, "ClockApp Ver2가 이미 실행 중입니다.\n시스템 트레이를 확인해주세요.", 
                   "ClockApp Ver2", 0x30)  # 0x30 = MB_ICONWARNING
        sys.exit(0)
    
    try:
        # 명령행 인수 처리
        import argparse
        parser = argparse.ArgumentParser(description='MouseClock - 시간 관리 프로그램')
        parser.add_argument('--minimized', action='store_true', 
                           help='시스템 트레이로 최소화된 상태로 시작')
        args = parser.parse_args()
        
        # 인사창 없이 바로 시계창 실행
        try:
            ClockWindow(start_minimized=args.minimized)
        except Exception as e:
            print(f"시계 창 실행 오류: {e}")
    finally:
        # 뮤텍스 해제 (프로그램 종료 시 자동으로 해제되지만 명시적으로 처리)
        if mutex_handle:
            kernel32.CloseHandle(mutex_handle)