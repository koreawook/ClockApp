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

# SSL 인증서 검증 비활성화 (개발용)
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
                
                # 2시간 이내 캐시라면 사용
                if datetime.now() - cache_time < timedelta(seconds=WEATHER_CACHE_DURATION):
                    print(f"날씨 캐시 사용 (저장시각: {cache_time.strftime('%H:%M:%S')})")
                    return cache['data']
                else:
                    print(f"날씨 캐시 만료 (저장시각: {cache_time.strftime('%H:%M:%S')})")
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
        print(f"날씨 캐시 저장완료: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"날씨 캐시 저장실패: {e}")

# 컬러풀한 아이콘 생성 함수 (실제 이미지 파일 사용)
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
    """날씨용 컬러풀한 아이콘 생성 (실제 이미지 파일 사용)"""
    size_num = size[0]  # 첫번째 차원 사용
    return load_icon_image(weather_type, size_num)

def create_system_icon(icon_type, size=(16, 16)):
    """시스템 UI용 컬러풀한 아이콘 (실제 이미지 파일 사용)"""
    size_num = size[0]  # 첫번째 차원 사용
    return load_icon_image(icon_type, size_num)

def get_colorful_break_text(remaining_mins, remaining_secs, is_meal_time=False):
    """휴식 시간 표시용 컬러풀한 텍스트 생성"""
    if is_meal_time:
        return "점심시간 시작 (휴식 알림 일시정지)"
    elif remaining_mins > 0:
        return f"다음 휴식: {remaining_mins}:{remaining_secs:02d}"
    elif remaining_secs > 10:
        return f"다음 휴식: {remaining_secs}초"
    else:
        return "휴식시간!"

def get_weather_type_from_icon(icon_text):
    """이모지 아이콘에서 날씨 타입 추출"""
    weather_map = {
        '☀️': 'sunny',
        '🌞': 'sunny', 
        '☁️': 'cloud',
        '⛅️': 'cloud',
        '🌧️': 'rain',
        '☔️': 'rain',
        '❄️': 'snow',
        '🌨️': 'snow', 
        '⛈️': 'storm',
        '🌩️': 'storm',
        # 추가 매핑
        '🌤': 'sunny',
        '🌥': 'sunny',
        '⛅': 'sunny',
        '☁': 'cloud',
        '🌦': 'rain'
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

        # 시계 중심과 반지름
        center_x, center_y = size // 2, size // 2
        clock_radius = size * 0.4

        # 시계 외곽선 그리기
        draw.ellipse([
            center_x - clock_radius, center_y - clock_radius,
            center_x + clock_radius, center_y + clock_radius
        ], fill=clock_color, outline=clock_dark, width=3)

        # 시계 숫자 12, 3, 6, 9 표시
        import math
        for i, angle in enumerate([0, 90, 180, 270]):  # 12, 3, 6, 9의 위치
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

        # 스크롤휠 (가운데 선)
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
        # PNG 이미지 읽기
        png_image = Image.open(png_path)
        
        # 여러 크기로 리사이즈해서 ICO 파일 생성
        sizes = [16, 32, 48, 64, 128, 256]
        images = []
        
        for size in sizes:
            # 이미지 크기 조정
            resized = png_image.resize((size, size), Image.Resampling.LANCZOS)
            
            # RGB 모드로 변환 (ICO 파일 호환성을 위해)
            if resized.mode == 'RGBA':
                # 투명 배경을 흰색으로 변환
                background = Image.new('RGB', (size, size), (255, 255, 255))
                background.paste(resized, (0, 0), resized)
                resized = background
            elif resized.mode != 'RGB':
                resized = resized.convert('RGB')
                
            images.append(resized)
        
        # ICO 파일로 저장
        if images:
            images[0].save(ico_path, format='ICO', sizes=[(img.size[0], img.size[1]) for img in images])
            print(f"PNG를 ICO로 변환성공: {png_path} -> {ico_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"PNG to ICO 변환실패: {e}")
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

def load_settings():
    """설정 파일에서 설정을 불러오기"""
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
    """설정 파일에서 설정을 로드"""
    try:
        settings_file = os.path.join(os.path.dirname(__file__), "clock_settings.json")
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
        settings_file = os.path.join(os.path.dirname(__file__), "clock_settings.json")
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        print(f"설정 저장성공: {settings}")
        return True
    except Exception as e:
        print(f"설정 저장실패: {e}")
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
            # Python 스크립트로 실행 시
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
    """작업 스케줄러를 사용한 시작 프로그램 등록 (대안방법)"""
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
    """작업 스케줄러에서 시작 프로그램 제거 (대안방법)"""
    try:
        import subprocess
        cmd = 'schtasks /delete /tn "MouseClock" /f'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("작업 스케줄러에서 제거 성공")
            return True
        else:
            print(f"작업 스케줄러 제거 실패: {result.stderr}")
            return True  # 없는 경우도 성공으로 처리
            
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
        return "서울시"

def get_weather_data(location="Seoul", force_refresh=False):
    """실제 날씨 정보 가져오기 (wttr.in API 사용)"""
    # 캐시 확인 (강제 새로고침이 아닌 경우)
    if not force_refresh:
        cached_data = load_weather_cache()
        if cached_data:
            return cached_data
    
    print("날씨 API 호출 중..")
    try:
        # wttr.in API 사용 (무료, API 키 불필요)
        try:
            # ipapi.co에서 좌표 정보를 가져오기
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
                    
                if country and country != 'South Korea':  # 한국이 아닌 경우만 국가 추가
                    location_str = f"{location_str}, {country}"
                
            if lat and lon:
                # wttr.in API ?�용 (무료, API ??불필??
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
                
                # 시간별 예보 정보 처리
                hourly_forecast = []
                if 'weather' in weather_data and weather_data['weather']:
                    today_weather = weather_data['weather'][0]
                    hourly = today_weather.get('hourly', [])
                    
                    for i, hour_data in enumerate(hourly):
                        if i >= 8:  # 8시간까지
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
        return '☁️'
    elif 'rain' in description or '비' in description:
        return '🌧️'
    elif 'snow' in description or '눈' in description:
        return '❄️'
    elif 'storm' in description or '천둥' in description:
        return '⛈️'
    elif 'fog' in description or '안개' in description:
        return '🌫️'
    else:
        return '☀️'

def get_default_weather_data():
    """기본 날씨 데이터 (API 실패 시)"""
    now = datetime.now()
    hour = now.hour
    
    if 6 <= hour < 12:
        current_weather = {"icon": "☀️", "temp": "22°C", "desc": "맑음"}
    elif 12 <= hour < 18:
        current_weather = {"icon": "⛅", "temp": "25°C", "desc": "구름 조금"}
    elif 18 <= hour < 22:
        current_weather = {"icon": "🌙", "temp": "20°C", "desc": "저녁"}
    else:
        current_weather = {"icon": "🌙", "temp": "18°C", "desc": "맑음"}
    
    hourly_forecast = [
        {'time': "00:00", 'icon': "🌙", 'temp': "16°C", 'desc': "맑음"},
        {'time': "03:00", 'icon': "🌙", 'temp': "15°C", 'desc': "맑음"},
        {'time': "06:00", 'icon': "☀️", 'temp': "18°C", 'desc': "맑음"},
        {'time': "09:00", 'icon': "☀️", 'temp': "22°C", 'desc': "맑음"},
        {'time': "12:00", 'icon': "⛅", 'temp': "26°C", 'desc': "구름 조금"},
        {'time': "15:00", 'icon': "⛅", 'temp': "25°C", 'desc': "구름 조금"},
        {'time': "18:00", 'icon': "🌙", 'temp': "21°C", 'desc': "저녁"},
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
        'location': '서울시'
    }

class RestPopup:
    """휴식 알림 팝업 클래스"""
    def __init__(self):
        self.popup = tk.Toplevel()
        self.popup.title("휴식 알림")
        self.popup.geometry("400x380")  # 원형 진행바를 위한 높이 증가
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)  # 항상 위에 표시
        
        # 아이콘 설정 (사용자 PNG 우선, 그다음 기본 시계 아이콘)
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
        
        # X 버튼 비활성화
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        
        # 타이머 시작
        self.update_timer()
        
    def close_popup(self):
        """?�업 ?�기"""
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
        popup_width = 400
        popup_height = 380
        
        # 중앙 위치 계산
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2
        
        self.popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
    
    def create_widgets(self):
        """위젯 생성 - 모던한 디자인"""
        # 팝업 배경색 설정
        self.popup.configure(bg="#f0f8ff")
        
        # 상단 헤더 영역 (그라디언트 효과)
        header_frame = tk.Frame(self.popup, bg="#4a90e2", height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # 눈 이모지
        emoji_label = tk.Label(
            header_frame,
            text="👁️",
            font=("Arial", 36),
            bg="#4a90e2",
            fg="white"
        )
        emoji_label.pack(pady=(15, 5))
        
        # 메인 메시지
        message_label = tk.Label(
            header_frame, 
            text="잠시 휴식하세요!", 
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#4a90e2"
        )
        message_label.pack()
        
        # 메인 컨텐츠 영역
        content_frame = tk.Frame(self.popup, bg="#f0f8ff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 부가 메시지
        sub_message = tk.Label(
            content_frame,
            text="눈을 감고 잠시 휴식을 취하세요",
            font=("Segoe UI", 11),
            fg="#5a6c7d",
            bg="#f0f8ff"
        )
        sub_message.pack(pady=(0, 15))
        
        # 원형 진행 표시 영역 (중앙 정렬을 위한 컨테이너)
        progress_container = tk.Frame(content_frame, bg="#f0f8ff")
        progress_container.pack(pady=10)
        
        # 원형 캔버스 (진행바와 텍스트를 모두 그릴 캔버스)
        self.rest_progress_canvas = tk.Canvas(
            progress_container, 
            width=120, 
            height=120, 
            bg="#f0f8ff",
            highlightthickness=0
        )
        self.rest_progress_canvas.pack()
        
        # 텍스트 요소들을 캔버스에서 관리하기 위한 ID 저장
        self.timer_text_id = None
        self.second_text_id = None
        
        # 하단 버튼 영역
        button_frame = tk.Frame(self.popup, bg="#f0f8ff")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # 닫기 버튼 (모던한 플랫 디자인)
        self.close_button = tk.Button(
            button_frame,
            text="확인 (10초후)",
            state=tk.DISABLED,
            font=("Segoe UI", 11, "bold"),
            bg="#bdc3c7",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.close_popup
        )
        self.close_button.pack(fill=tk.X)
    
    def update_timer(self):
        """타이머 업데이트"""
        if self.remaining_time >= 0:
            # 진행률과 텍스트 업데이트 (30초에서 시작해서 줄어듦)
            self.update_rest_progress_bar()
            
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
                self.close_button.config(text=f"확인 ({self.remaining_time-10}초후)")
            
            # remaining_time 감소
            self.remaining_time -= 1
            
            # 1초 후 다시 호출 (remaining_time이 -1이 될 때까지)
            self.popup.after(1000, self.update_timer)
        else:
            # 시간 종료 (remaining_time이 -1)
            self.update_rest_progress_bar()  # 마지막 진행률 업데이트 (0초 표시)
            # 즉시 팝업 닫기
            self.popup.after(500, self.close_popup)
    
    def update_rest_progress_bar(self):
        """휴식 팝업 원형 진행률과 텍스트 업데이트"""
        try:
            import math
            
            # 남은 시간 비율 계산 (30초 기준)
            remaining_ratio = max(0.0, self.remaining_time / 30.0)
            
            # 캔버스 지우기
            self.rest_progress_canvas.delete("all")
            
            # 원 중심 및 반지름
            center_x, center_y = 60, 60
            radius = 50
            
            # 배경 원 (연한 회색)
            self.rest_progress_canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill="#ecf0f1", outline="#bdc3c7", width=2
            )
            
            # 진행 호선 (시계 방향으로 채워짐)
            if remaining_ratio > 0:
                # 색상 선택 (시간에 따라 변함)
                if remaining_ratio > 0.5:
                    color = "#27ae60"  # 녹색
                elif remaining_ratio > 0.2:
                    color = "#f39c12"  # 주황색
                else:
                    color = "#e74c3c"  # 빨간색
                
                # 각도 계산 (0도가 오른쪽, 시계방향)
                extent = -360 * remaining_ratio
                
                # 호선 그리기
                self.rest_progress_canvas.create_arc(
                    center_x - radius + 5, center_y - radius + 5,
                    center_x + radius - 5, center_y + radius - 5,
                    start=90, extent=extent,
                    fill=color, outline=color, width=10,
                    style=tk.ARC
                )
            
            # 타이머 텍스트를 캔버스 중앙에 직접 그리기 (투명 배경)
            timer_text = f"{max(0, self.remaining_time)}"  # 음수 방지
            
            # 큰 숫자 (메인 타이머)
            self.rest_progress_canvas.create_text(
                center_x, center_y - 8,  # 약간 위로
                text=timer_text,
                font=("Segoe UI", 24, "bold"),
                fill="#4a90e2",
                anchor=tk.CENTER
            )
            
            # "초" 텍스트 (작은 글씨로 아래에)
            self.rest_progress_canvas.create_text(
                center_x, center_y + 15,  # 숫자 아래
                text="초",
                font=("Segoe UI", 10),
                fill="#7f8c8d",
                anchor=tk.CENTER
            )
            
        except Exception as e:
            print(f"휴식 진행률 업데이트 오류: {e}")
    
    def close_popup(self):
        """팝업 닫기"""
        try:
            self.popup.destroy()
        except:
            pass

class MealPopup:
    """식사 알림 팝업 클래스"""
    def __init__(self, meal_type="식사"):
        self.meal_type = meal_type
        self.popup = tk.Toplevel()
        self.popup.title("식사 알림")
        self.popup.geometry("350x200")  # 높이 증가 (진행바 공간)
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)  # 항상 위에 표시
        
        # 아이콘 설정 (사용자 PNG 우선, 그다음 기본 시계 아이콘)
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
        
        # 닫기 버튼 비활성화
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
            text=f"지금은 {self.meal_type} 시간입니다! 🍽️", 
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
            self.update_meal_progress_bar()  # 마지막 진행바 업데이트 (완료 상태)
            # 즉시 팝업 닫기
            self.popup.after(500, self.close_popup)
    
    def update_meal_progress_bar(self):
        """식사 팝업 진행바 업데이트"""
        try:
            # 남은 시간 비율 계산 (3600초 기준, remaining_time이 -1이면 0으로)
            remaining_ratio = max(0.0, self.remaining_time / 3600.0)
            
            # 캔버스 지우기
            self.meal_progress_canvas.delete("all")
            
            # 배경 바 (회색 영역)
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
        self.weather_window.title("날씨 정보")
        self.weather_window.geometry("300x700")  # 여백 최소화로 더 좁게 최적화
        self.weather_window.resizable(True, True)  # 크기 조절 가능하도록 변경
        
        # 날씨 창을 부모창 중앙에 위치
        self.weather_window.transient(parent_clock.clock_window)
        self.weather_window.grab_set()  # 모달 창으로 설정
        
        # 아이콘 설정 (사용자 PNG 우선, 그다음 기본 시계 아이콘)
        try:
            icon_file_path = get_icon_path()
            if icon_file_path and os.path.exists(icon_file_path):
                self.weather_window.iconbitmap(icon_file_path)
        except:
            pass
        
        self.create_widgets()
        self.center_on_parent()
        
        # 초기 위치 설정
        self.current_location = "서울시"
        self.load_weather_info()
        
    def center_on_parent(self):
        """부모창 중앙에 날씨 창 위치시키기"""
        parent = self.parent_clock.clock_window
        parent.update_idletasks()
        
        # 부모창 위치와 크기 가져오기
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
        """날씨 창 위젯 생성 - 메인창과 같은 조화로운 디자인"""
        # 메인 배경색 설정 (메인창과 동일)
        self.weather_window.configure(bg="#f8f9fa")
        
        # 메인 프레임
        main_frame = tk.Frame(self.weather_window, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ?�단: ?�목 ?�역 (카드 ?��???
        header_card = tk.Frame(main_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                              highlightbackground="#e0e0e0", highlightthickness=1)
        header_card.pack(fill=tk.X, pady=(0, 10))
        
        header_content = tk.Frame(header_card, bg="#ffffff")
        header_content.pack(fill=tk.X, padx=15, pady=12)
        
        # ?�목
        title_label = tk.Label(header_content, text="?���??�씨 ?�보", 
                              font=("Segoe UI", 16, "bold"),
                              bg="#ffffff", fg="#2c3e50")
        title_label.pack(side=tk.LEFT)
        
        # ?�로고침 버튼 (메인�??��???
        refresh_btn = tk.Button(header_content, text="?�� ?�로고침", 
                               command=self.refresh_weather,
                               font=("Segoe UI", 9, "bold"),
                               bg="#4fc3f7", fg="white",
                               relief=tk.FLAT, bd=0,
                               padx=12, pady=6,
                               cursor="hand2",
                               activebackground="#29b6f6",
                               activeforeground="white")
        refresh_btn.pack(side=tk.RIGHT)
        
        # ?�로고침 버튼 ?�버 ?�과
        def on_enter_refresh(e):
            refresh_btn['background'] = '#29b6f6'
        def on_leave_refresh(e):
            refresh_btn['background'] = '#4fc3f7'
        refresh_btn.bind("<Enter>", on_enter_refresh)
        refresh_btn.bind("<Leave>", on_leave_refresh)
        
        # ?�씨 ?�보 ?�시 ?�역 (?�크�?가??
        self.weather_frame = tk.Frame(main_frame, bg="#f8f9fa")
        self.weather_frame.pack(fill=tk.BOTH, expand=True)
        
        # 로딩 메시지 (메인�??��???
        self.loading_label = tk.Label(self.weather_frame, text="?�씨 ?�보�?불러?�는 �?..", 
                                     font=("Segoe UI", 11), fg="#7f8c8d", bg="#f8f9fa")
        self.loading_label.pack(expand=True)
        
        # ?�단 버튼 ?�역
        button_frame = tk.Frame(main_frame, bg="#f8f9fa")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # ?�기 버튼 (메인�??��???
        close_btn = tk.Button(button_frame, text="?�기", 
                             command=self.close_weather,
                             font=("Segoe UI", 10, "bold"),
                             bg="#66bb6a", fg="white",
                             relief=tk.FLAT, bd=0,
                             padx=20, pady=10,
                             cursor="hand2",
                             activebackground="#4caf50",
                             activeforeground="white")
        close_btn.pack(fill=tk.X)
        
        # ?�기 버튼 ?�버 ?�과
        def on_enter_close(e):
            close_btn['background'] = '#4caf50'
        def on_leave_close(e):
            close_btn['background'] = '#66bb6a'
        close_btn.bind("<Enter>", on_enter_close)
        close_btn.bind("<Leave>", on_leave_close)
    
    def load_weather_info(self):
        """실제 날씨 정보 로드"""
        def fetch_weather():
            # 백그?�운?�에???�제 ?�씨 ?�이??가?�오�?
            weather_data = get_weather_data()
            # UI ?�레?�에???�데?�트
            self.weather_window.after(0, lambda: self.display_weather_data(weather_data))
        
        # 백그?�운???�레?�에???�씨 ?�보 가?�오�?
        thread = threading.Thread(target=fetch_weather, daemon=True)
        thread.start()
    
    def display_weather_data(self, weather_data):
        """?�씨 ?�이?��? UI???�시 - 메인창과 같�? ?�화로운 ?�자??""
        try:
            # 로딩 ?�벨 ?�거
            if hasattr(self, 'loading_label'):
                self.loading_label.destroy()
            
            # 기존 ?�젯 ?�거 (?�로고침 ??
            for widget in self.weather_frame.winfo_children():
                widget.destroy()
            
            # ?�재 ?�간
            now = datetime.now()
            
            # ?�재 ?�씨 카드 (메인�??��???
            current_card = tk.Frame(self.weather_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                                   highlightbackground="#e0e0e0", highlightthickness=1)
            current_card.pack(fill=tk.X, pady=(0, 10))
            
            # ?�재 ?�씨 ?�더
            current_header = tk.Frame(current_card, bg="#e3f2fd")
            current_header.pack(fill=tk.X)
            
            current_title = tk.Label(current_header, text="?�� ?�재 ?�씨", 
                                   font=("Segoe UI", 12, "bold"), 
                                   bg="#e3f2fd", fg="#1976d2")
            current_title.pack(pady=8)
            
            # ?�치 ?�보
            location = weather_data.get('location', self.current_location)
            location_label = tk.Label(current_card, text=f"�?{location}",
                                    font=("Segoe UI", 11, "bold"), 
                                    bg="#ffffff", fg="#2c3e50")
            location_label.pack(pady=(10, 5))
            
            # ?�재 ?�씨 ?�보
            current_weather = weather_data['current']
            current_info_text = f"{current_weather['icon']} {current_weather['description']} {current_weather['temp']}"
            
            current_info = tk.Label(current_card, text=current_info_text,
                                  font=("Segoe UI", 18, "bold"), 
                                  bg="#ffffff", fg="#2c3e50")
            current_info.pack(pady=8)
            
            # ?�세 ?�보
            detail_info = tk.Label(current_card, 
                                 text=f"?�도: {current_weather['humidity']} | 바람: {current_weather['wind']}",
                                 font=("Segoe UI", 10), 
                                 bg="#ffffff", fg="#7f8c8d")
            detail_info.pack(pady=(0, 12))
            
            # ?�간?��??�보 카드 (메인�??��???
            forecast_card = tk.Frame(self.weather_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                                    highlightbackground="#e0e0e0", highlightthickness=1)
            forecast_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # ?�보 ?�더
            forecast_header = tk.Frame(forecast_card, bg="#e3f2fd")
            forecast_header.pack(fill=tk.X)
            
            forecast_title = tk.Label(forecast_header, text="?�� ?�간?��??�보", 
                                    font=("Segoe UI", 12, "bold"), 
                                    bg="#e3f2fd", fg="#1976d2")
            forecast_title.pack(pady=8)
            
            # ?�크�?가?�한 ?�보 ?�역
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
            
            # ?�간?��??�씨 ?�보 ?�시 (깔끔?????��???
            hourly_data = weather_data['hourly']
            current_hour = now.hour
            current_index = 0  # ?�재 ?�간?� ?�덱??
            
            for i, hour_data in enumerate(hourly_data):
                # ?�재 ?�간�?가까운 ?�간?� 강조
                hour_int = int(hour_data['time'].split(':')[0])
                is_current = abs(hour_int - current_hour) <= 1
                
                if is_current and current_index == 0:
                    current_index = i  # ?�재 ?�간?� ?�덱???�??
                
                bg_color = "#e3f2fd" if is_current else "#ffffff"
                
                slot_frame = tk.Frame(scrollable_frame, bg=bg_color)
                slot_frame.pack(fill=tk.X, pady=1, padx=5)
                
                # 구분??(�?번째 ?�외)
                if i > 0:
                    separator = tk.Frame(scrollable_frame, bg="#e0e0e0", height=1)
                    separator.pack(fill=tk.X, padx=15)
                
                # ?�간
                time_label = tk.Label(slot_frame, text=hour_data['time'], 
                                    font=("Segoe UI", 10, "bold" if is_current else "normal"), 
                                    bg=bg_color, fg="#2c3e50", width=8, anchor="w")
                time_label.pack(side=tk.LEFT, padx=(10, 5), pady=8)
                
                # ?�씨 ?�이�?
                try:
                    weather_type = get_weather_type_from_icon(hour_data['icon'])
                    weather_icon = load_icon_image(weather_type, 24)
                    if weather_icon:
                        weather_label = tk.Label(slot_frame, image=weather_icon, 
                                               bg=bg_color)
                        weather_label.image = weather_icon  # 참조 ?��?
                    else:
                        raise Exception("?�이�?로드 ?�패")
                except Exception as e:
                    # ?��?지 로드 ?�패???�모지 ?�용
                    weather_label = tk.Label(slot_frame, text=hour_data['icon'], 
                                           font=("Segoe UI", 12), 
                                           bg=bg_color)
                weather_label.pack(side=tk.LEFT, padx=5)
                
                # ?�도
                temp_label = tk.Label(slot_frame, text=hour_data['temp'], 
                                    font=("Segoe UI", 10, "bold" if is_current else "normal"), 
                                    bg=bg_color, fg="#e74c3c", width=7, anchor="center")
                temp_label.pack(side=tk.LEFT, padx=3)
                
                # ?�명 (모든 ?�스??명확?�게 ?�시)
                desc_text = hour_data['desc']
                desc_container = tk.Frame(slot_frame, bg=bg_color, width=180)
                desc_container.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
                desc_container.pack_propagate(False)
                
                if len(desc_text) > 12:  # �??�스?�는 ?�크�?
                    # Canvas�??�크�??�과
                    desc_canvas = tk.Canvas(desc_container, bg=bg_color, 
                                          highlightthickness=0, height=25)
                    desc_canvas.pack(fill=tk.BOTH, expand=True)
                    
                    # ?�스???�성 (?????�트, ??진한 ?�상)
                    text_id = desc_canvas.create_text(0, 12, text=desc_text, 
                                                     font=("Segoe UI", 10),
                                                     fill="#5f6c7d", anchor="w")
                    
                    # ?�스???�비 계산
                    bbox = desc_canvas.bbox(text_id)
                    text_width = bbox[2] - bbox[0] if bbox else 0
                    
                    # ?�크�??�니메이??
                    def scroll_text(x_pos=0):
                        if desc_canvas.winfo_exists():
                            desc_canvas.coords(text_id, x_pos, 12)
                            if x_pos < -text_width:
                                x_pos = 180  # 처음?�로
                            desc_canvas.after(50, lambda: scroll_text(x_pos - 2))
                    
                    scroll_text(0)
                else:
                    # 짧�? ?�스?�는 ?�반 ?�벨 (??명확?�게)
                    desc_label = tk.Label(desc_container, text=desc_text, 
                                        font=("Segoe UI", 10), 
                                        bg=bg_color, fg="#5f6c7d", anchor="w")
                    desc_label.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # ?�재 ?�간?�가 중앙???�도�??�크�?조절
            def scroll_to_current():
                # 모든 ?�젯??그려�????�행
                canvas.update_idletasks()
                total_items = len(hourly_data)
                if total_items > 0 and current_index > 0:
                    # ?�재 ?�간?�가 뷰포??중앙???�도�?계산
                    # 중앙 ?�치 = (?�재 ?�덱??/ ?�체 개수) - (뷰포???�이 / ?�체 ?�이 / 2)
                    scroll_position = max(0, min(1, (current_index / total_items) - 0.2))
                    canvas.yview_moveto(scroll_position)
            
            # ?�간??지?????�크�?조절 (?�젯 ?�더�??�료 ?��?
            self.weather_window.after(100, scroll_to_current)
            
            # ?�데?�트 ?�간 (메인�??��???
            update_card = tk.Frame(self.weather_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                                  highlightbackground="#e0e0e0", highlightthickness=1)
            update_card.pack(fill=tk.X)
            
            self.update_label = tk.Label(update_card, 
                                       text=f"?�� 마�?�??�데?�트: {now.strftime('%Y-%m-%d %H:%M:%S')}", 
                                       font=("Segoe UI", 9), 
                                       bg="#ffffff", fg="#7f8c8d")
            self.update_label.pack(pady=8)
            
        except Exception as e:
            print(f"?�씨 ?�이???�시 ?�류: {e}")
            error_label = tk.Label(self.weather_frame, 
                                  text=f"?�씨 ?�보�??�시?????�습?�다.\n{e}",
                                  font=("Segoe UI", 11), 
                                  fg="#e74c3c", 
                                  bg="#f8f9fa",
                                  justify=tk.CENTER)
            error_label.pack(expand=True, pady=20)
    
    def refresh_weather(self):
        """날씨 정보 새로고침 (2시간 캐시 로직 사용)"""
        # 기존 ?�젯 ?�거
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
        
        # 로딩 메시지 ?�시 ?�시 (메인�??��???
        self.loading_label = tk.Label(self.weather_frame, 
                                     text="?�� ?�씨 ?�보�??�인?�는 �?..", 
                                     font=("Segoe UI", 11), 
                                     fg="#7f8c8d",
                                     bg="#f8f9fa")
        self.loading_label.pack(expand=True)
        
        # 캐시 ?�인 ???�요?�에�??�로고침
        def fetch_weather():
            # 캐시 ?�인 (2?�간 ?�내�?캐시 ?�용)
            cached_data = load_weather_cache()
            if cached_data:
                print("??캐시 ?�용 (2?�간 ?�내)")
                weather_data = cached_data
            else:
                print("??캐시 만료, ???�이??가?�오??�?..")
                weather_data = get_weather_data(force_refresh=True)
            
            # UI ?�레?�에???�데?�트
            self.weather_window.after(0, lambda: self.display_weather_data(weather_data))
        
        # 백그?�운???�레?�에???�씨 ?�보 가?�오�?
        thread = threading.Thread(target=fetch_weather, daemon=True)
        thread.start()
    
    def close_weather(self):
        """?�씨 �??�기"""
        try:
            self.weather_window.destroy()
        except:
            pass
    
    def get_weather_type_from_icon(self, icon_text):
        """?�모지 ?�이콘에???�씨 ?�??추출 (?�래??메서??"""
        return get_weather_type_from_icon(icon_text)

class SettingsWindow:
    """?�정 �??�래??""
    def __init__(self, parent_clock):
        self.parent_clock = parent_clock
        self.settings_window = tk.Toplevel(parent_clock.clock_window)
        self.settings_window.title("?�간 ?�정")
        self.settings_window.geometry("350x500")  # ?�이 증�?�?모든 ?�션 ?�시
        self.settings_window.resizable(False, False)
        
        # ?�정 창을 부�?�?중앙???�치
        self.settings_window.transient(parent_clock.clock_window)
        self.settings_window.grab_set()  # 모달 창으�??�정
        
        # ?�이�??�정 (?�용??PNG ?�선, ?�으�?기본 ?�계 ?�이�?
        try:
            icon_file_path = get_icon_path()
            if icon_file_path and os.path.exists(icon_file_path):
                self.settings_window.iconbitmap(icon_file_path)
        except:
            pass
        
        self.create_widgets()
        
        # 창을 부�?�?중앙???�치
        self.center_on_parent()
        
    def center_on_parent(self):
        """부�?�?중앙???�정 �??�치?�키�?""
        parent = self.parent_clock.clock_window
        parent.update_idletasks()
        
        # 부�?�??�치?� ?�기 가?�오�?
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # ?�정 �??�기
        settings_width = 350
        settings_height = 500
        
        # 중앙 ?�치 계산
        x = parent_x + (parent_width - settings_width) // 2
        y = parent_y + (parent_height - settings_height) // 2
        
        self.settings_window.geometry(f"{settings_width}x{settings_height}+{x}+{y}")
    
    def create_widgets(self):
        """?�정 �??�젯 ?�성 - 메인창과 같�? ?�화로운 ?�자??""
        # 메인 배경???�정 (메인창과 ?�일)
        self.settings_window.configure(bg="#f8f9fa")
        
        # 메인 ?�레??
        main_frame = tk.Frame(self.settings_window, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ?�목 카드
        title_card = tk.Frame(main_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                             highlightbackground="#e0e0e0", highlightthickness=1)
        title_card.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_card, text="?�️ ?�간 ?�정", 
                              font=("Segoe UI", 14, "bold"),
                              bg="#ffffff", fg="#2c3e50")
        title_label.pack(pady=12)
        
        # ?�정 카드
        settings_card = tk.Frame(main_frame, bg="#ffffff", relief=tk.FLAT, bd=0,
                                highlightbackground="#e0e0e0", highlightthickness=1)
        settings_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        settings_inner = tk.Frame(settings_card, bg="#ffffff")
        settings_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 1. ?�식 ?�림 ?�정 (?�한 ?��???배경)
        break_section = tk.Frame(settings_inner, bg="#f0f8ff", relief=tk.FLAT, bd=0)
        break_section.pack(pady=5, fill=tk.X)
        
        break_frame = tk.Frame(break_section, bg="#f0f8ff")
        break_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.break_enabled_var = tk.BooleanVar()
        self.break_enabled_var.set(getattr(self.parent_clock, 'break_enabled', True))
        
        break_checkbox = tk.Checkbutton(break_frame, 
                                      text="?�� ?�식 ?�림", 
                                      variable=self.break_enabled_var,
                                      font=("Segoe UI", 10, "bold"),
                                      bg="#f0f8ff", fg="#2c3e50",
                                      activebackground="#f0f8ff")
        break_checkbox.pack(side=tk.LEFT)
        
        time_input_frame = tk.Frame(break_frame, bg="#f0f8ff")
        time_input_frame.pack(side=tk.RIGHT)
        
        tk.Label(time_input_frame, text="간격 (�?:", 
                font=("Segoe UI", 9), bg="#f0f8ff", fg="#7f8c8d").pack(side=tk.LEFT, padx=(10, 5))
        self.minutes_entry = tk.Entry(time_input_frame, width=12, 
                                     font=("Segoe UI", 11), relief=tk.SOLID, bd=1)
        self.minutes_entry.pack(side=tk.LEFT)
        self.minutes_entry.insert(0, str(self.parent_clock.time_interval))
        
        # 구분??
        tk.Frame(settings_inner, bg="#e0e0e0", height=1).pack(fill=tk.X, pady=8)
        
        # 2. ?�심 ?�림 ?�정 (?�한 ?��???배경)
        lunch_section = tk.Frame(settings_inner, bg="#fffef0", relief=tk.FLAT, bd=0)
        lunch_section.pack(pady=5, fill=tk.X)
        
        lunch_frame = tk.Frame(lunch_section, bg="#fffef0")
        lunch_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.lunch_enabled_var = tk.BooleanVar()
        self.lunch_enabled_var.set(getattr(self.parent_clock, 'lunch_enabled', True))
        
        lunch_checkbox = tk.Checkbutton(lunch_frame, 
                                      text="?�� ?�심 ?�림", 
                                      variable=self.lunch_enabled_var,
                                      font=("Segoe UI", 10, "bold"),
                                      bg="#fffef0", fg="#2c3e50",
                                      activebackground="#fffef0")
        lunch_checkbox.pack(side=tk.LEFT)
        
        lunch_time_frame = tk.Frame(lunch_frame, bg="#fffef0")
        lunch_time_frame.pack(side=tk.RIGHT)
        
        tk.Label(lunch_time_frame, text="?�간:", 
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
        
        # 구분??
        tk.Frame(settings_inner, bg="#e0e0e0", height=1).pack(fill=tk.X, pady=8)
        
        # 3. ?�???�림 ?�정 (?�한 주황??배경)
        dinner_section = tk.Frame(settings_inner, bg="#fff5f0", relief=tk.FLAT, bd=0)
        dinner_section.pack(pady=5, fill=tk.X)
        
        dinner_frame = tk.Frame(dinner_section, bg="#fff5f0")
        dinner_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.dinner_enabled_var = tk.BooleanVar()
        self.dinner_enabled_var.set(getattr(self.parent_clock, 'dinner_enabled', True))
        
        dinner_checkbox = tk.Checkbutton(dinner_frame, 
                                       text="?���??�???�림", 
                                       variable=self.dinner_enabled_var,
                                       font=("Segoe UI", 10, "bold"),
                                       bg="#fff5f0", fg="#2c3e50",
                                       activebackground="#fff5f0")
        dinner_checkbox.pack(side=tk.LEFT)
        
        dinner_time_frame = tk.Frame(dinner_frame, bg="#fff5f0")
        dinner_time_frame.pack(side=tk.RIGHT)
        
        tk.Label(dinner_time_frame, text="?�간:", 
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
        
        # 구분??
        tk.Frame(settings_inner, bg="#e0e0e0", height=1).pack(fill=tk.X, pady=8)
        
        # 4. ?�작 ?�로그램 ?�록 (?�한 ?�색 배경)
        startup_section = tk.Frame(settings_inner, bg="#f5f5f5", relief=tk.FLAT, bd=0)
        startup_section.pack(pady=5, fill=tk.X)
        
        startup_frame = tk.Frame(startup_section, bg="#f5f5f5")
        startup_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.startup_var = tk.BooleanVar()
        self.startup_var.set(check_startup_registry())
        
        startup_checkbox = tk.Checkbutton(startup_frame, 
                                        text="?�� ?�도???�작 ???�동 ?�행", 
                                        variable=self.startup_var,
                                        font=("Segoe UI", 10, "bold"),
                                        bg="#f5f5f5", fg="#2c3e50",
                                        activebackground="#f5f5f5")
        startup_checkbox.pack(side=tk.LEFT)
        
        # 버튼 ?�레??(메인�??��???
        button_frame = tk.Frame(main_frame, bg="#f8f9fa")
        button_frame.pack(fill=tk.X)
        
        # ?�??버튼
        save_btn = tk.Button(button_frame, text="?�� ?�??, 
                           command=self.save_settings,
                           font=("Segoe UI", 10, "bold"),
                           bg="#66bb6a", fg="white",
                           relief=tk.FLAT, bd=0,
                           padx=20, pady=10,
                           cursor="hand2",
                           activebackground="#4caf50",
                           activeforeground="white")
        save_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # ?�??버튼 ?�버 ?�과
        def on_enter_save(e):
            save_btn['background'] = '#4caf50'
        def on_leave_save(e):
            save_btn['background'] = '#66bb6a'
        save_btn.bind("<Enter>", on_enter_save)
        save_btn.bind("<Leave>", on_leave_save)
        
        # ?�기 버튼
        close_btn = tk.Button(button_frame, text="?�기", 
                            command=self.settings_window.destroy,
                            font=("Segoe UI", 10, "bold"),
                            bg="#90a4ae", fg="white",
                            relief=tk.FLAT, bd=0,
                            padx=20, pady=10,
                            cursor="hand2",
                            activebackground="#78909c",
                            activeforeground="white")
        close_btn.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # ?�기 버튼 ?�버 ?�과
        def on_enter_close(e):
            close_btn['background'] = '#78909c'
        def on_leave_close(e):
            close_btn['background'] = '#90a4ae'
        close_btn.bind("<Enter>", on_enter_close)
        close_btn.bind("<Leave>", on_leave_close)
    
    def save_settings(self):
        """?�정 ?�??""
        try:
            # ?�력�?검�?�??�??
            minutes = int(self.minutes_entry.get())
            lunch_hour = int(self.lunch_hour_entry.get())
            lunch_minute = int(self.lunch_minute_entry.get())
            dinner_hour = int(self.dinner_hour_entry.get())
            dinner_minute = int(self.dinner_minute_entry.get())
            
            # 체크박스 값들 가?�오�?
            break_enabled = self.break_enabled_var.get()
            lunch_enabled = self.lunch_enabled_var.get()
            dinner_enabled = self.dinner_enabled_var.get()
            
            # ?�효??검??
            if not (1 <= minutes <= 1440):  # 1�?24?�간
                raise ValueError("?�간 간격?� 1~1440�??�이?�야 ?�니??")
            if not (0 <= lunch_hour <= 23):
                raise ValueError("?�심?�간?� 0~23???�이?�야 ?�니??")
            if not (0 <= lunch_minute <= 59):
                raise ValueError("?�심?�간 분�? 0~59�??�이?�야 ?�니??")
            if not (0 <= dinner_hour <= 23):
                raise ValueError("?�?�시간�? 0~23???�이?�야 ?�니??")
            if not (0 <= dinner_minute <= 59):
                raise ValueError("?�?�시�?분�? 0~59�??�이?�야 ?�니??")
            
            # ?�정 ?�??(부�??�래?�에 ?�달)
            self.parent_clock.update_time_settings(minutes, lunch_hour, lunch_minute, dinner_hour, dinner_minute, 
                                                 break_enabled, lunch_enabled, dinner_enabled)
            
            # ?�작 ?�로그램 ?�록/?�제 처리
            startup_enabled = self.startup_var.get()
            startup_success = True
            
            if startup_enabled:
                # ?�작 ?�로그램???�록 (?��??�트�?방법 먼�? ?�도)
                startup_success = add_to_startup()
                if not startup_success:
                    # ?��??�트�?방법 ?�패 ???�업 ?��?줄러 방법 ?�도
                    print("?��??�트�?방법 ?�패, ?�업 ?��?줄러 방법 ?�도...")
                    startup_success = add_to_startup_alternative()
                    if not startup_success:
                        tk.messagebox.showwarning("경고", "?�작 ?�로그램 ?�록???�패?�습?�다.")
                    else:
                        tk.messagebox.showinfo("?�림", "?�업 ?��?줄러�??�해 ?�작 ?�로그램???�록?�었?�니??")
            else:
                # ?�작 ?�로그램?�서 ?�거 (??방법 모두 ?�도)
                reg_success = remove_from_startup()
                sched_success = remove_from_startup_alternative()
                startup_success = reg_success or sched_success
                if not startup_success:
                    tk.messagebox.showwarning("경고", "?�작 ?�로그램 ?�거???�패?�습?�다.")
            
            # ?�일?�도 ?�??
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
                # ?�공 메시지
                tk.messagebox.showinfo("?�???�료", "?�정???�?�되?�습?�다!")
                self.settings_window.destroy()
            else:
                tk.messagebox.showerror("?�???�패", "?�정 ?�일 ?�?�에 ?�패?�습?�다.")
            
        except ValueError as e:
            tk.messagebox.showerror("?�력 ?�류", str(e))
        except Exception as e:
            tk.messagebox.showerror("?�류", f"?�정 ?�??�??�류가 발생?�습?�다: {e}")
    
class ClockWindow:
    """?�계 �??�래??""
    def __init__(self, start_minimized=False):
        # ?�립?�인 루트 �??�성 (Toplevel ?�??Tk ?�용)
        self.clock_window = tk.Tk()
        self.clock_window.title("ClockApp")
        self.clock_window.geometry("320x240")  # ???��? 모던???�기
        self.clock_window.resizable(False, False)
        
        # ?�작 ??최소???��? ?�??
        self.start_minimized = start_minimized
        
        # ?�정 로드
        self.settings = load_settings_from_file() or {}
        
        # ?�이�??�정 (?�용??PNG ?�선, ?�으�?기본 ?�계 ?�이�?
        try:
            icon_file_path = get_icon_path()
            if icon_file_path and os.path.exists(icon_file_path):
                self.clock_window.iconbitmap(icon_file_path)
        except:
            pass
        
        # 모던??메인 ?�레??(부?�러??배경??
        self.clock_window.configure(bg="#f8f9fa")
        main_frame = tk.Frame(self.clock_window, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ?�단: ?�간 ?�시 ?�역 (카드 ?��???
        time_frame = tk.Frame(main_frame, bg="#ffffff", relief=tk.FLAT, bd=0, 
                             highlightbackground="#e0e0e0", highlightthickness=1)
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        # ?�계 ?�이�?(?????�트, 모던???��???
        self.time_label = tk.Label(
            time_frame, 
            text="", 
            font=("Segoe UI", 28, "bold"),
            fg="#2c3e50",
            bg="#ffffff",
            cursor="hand2"
        )
        self.time_label.pack(pady=(15, 5))
        
        # ?�계 ?�릭 ?�벤??바인??
        self.time_label.bind("<Button-1>", self.open_settings)
        
        # ?�짜 ?�이�?(???�련???��???
        self.date_label = tk.Label(
            time_frame, 
            text="", 
            font=("Segoe UI", 10),
            fg="#7f8c8d",
            bg="#ffffff",
            cursor="hand2"
        )
        self.date_label.pack(pady=(0, 15))
        
        # ?�짜 ?�릭 ?�벤??바인??
        self.date_label.bind("<Button-1>", self.open_settings)
        
        # 중단: ?�태 ?�시 ?�역 (카드 ?��??? 부?�러???�상)
        status_frame = tk.Frame(main_frame, bg="#e3f2fd", relief=tk.FLAT, bd=0,
                               highlightbackground="#90caf9", highlightthickness=1)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # ?�음 ?�식?�간 ?�벨 (???�에 ?�게)
        self.next_break_label = tk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 10, "bold"),
            fg="#1976d2",
            bg="#e3f2fd"
        )
        self.next_break_label.pack(pady=12)
        
        # ?�단: 버튼 ?�역 (?�랫 ?�자??
        button_frame = tk.Frame(main_frame, bg="#f8f9fa")
        button_frame.pack(fill=tk.X)
        
        # ?�씨 ?�인 버튼 (모던???�랫 버튼)
        weather_btn = tk.Button(
            button_frame,
            text="?���??�씨",
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
        
        # ?�버 ?�과 추�?
        def on_enter_weather(e):
            weather_btn['background'] = '#29b6f6'
        def on_leave_weather(e):
            weather_btn['background'] = '#4fc3f7'
        weather_btn.bind("<Enter>", on_enter_weather)
        weather_btn.bind("<Leave>", on_leave_weather)
        
        # ?�정 버튼 (모던???�랫 버튼)
        settings_btn = tk.Button(
            button_frame,
            text="?�️ ?�정",
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
        
        # ?�버 ?�과 추�?
        def on_enter_settings(e):
            settings_btn['background'] = '#607d8b'
        def on_leave_settings(e):
            settings_btn['background'] = '#78909c'
        settings_btn.bind("<Enter>", on_enter_settings)
        settings_btn.bind("<Leave>", on_leave_settings)
        
        # ?�?�된 ?�정�?불러?�기
        saved_settings = load_settings()
        self.time_interval = saved_settings["time_interval"]
        self.lunch_time = (saved_settings["lunch_hour"], saved_settings["lunch_minute"])
        self.dinner_time = (saved_settings["dinner_hour"], saved_settings["dinner_minute"])
        self.break_enabled = saved_settings.get("break_enabled", True)
        self.lunch_enabled = saved_settings.get("lunch_enabled", True)
        self.dinner_enabled = saved_settings.get("dinner_enabled", True)
        
        print(f"불러???�정 - 간격: {self.time_interval}�? ?�심: {self.lunch_time[0]:02d}:{self.lunch_time[1]:02d}, ?�?? {self.dinner_time[0]:02d}:{self.dinner_time[1]:02d}")
        print(f"?�성???�태 - ?�식: {self.break_enabled}, ?�심: {self.lunch_enabled}, ?�?? {self.dinner_enabled}")
        
        # ?�식 ?�?�머 관??변??
        self.last_break_time = time.time()  # 마�?�??�식 ?�림 ?�간
        
        # �??�기 ???�리
        self.clock_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # �??�행 ???�작?�로그램???�동 ?�록 (기본 ?�성??
        try:
            if not check_startup_registry():
                add_to_startup()
                print("?�도???�작?�로그램???�동 ?�록?�었?�니??")
        except Exception as e:
            print(f"?�작?�로그램 ?�록 ?�류: {e}")
        
        # ?�작 ??최소??처리
        if self.start_minimized:
            # 창을 ?�기�??�스???�레?�에�??�시
            self.clock_window.withdraw()  # �??�기�?
            self.create_system_tray()     # ?�스???�레???�이�??�성
        else:
            # 창을 ?�면 중앙???�치
            self.clock_window.eval('tk::PlaceWindow . center')
        
        # ?�계 ?�데?�트 ?�작
        self.update_clock()
        
        # ?�계 창의 메인루프 ?�작
        self.clock_window.mainloop()
        
    def update_clock(self):
        """?�계 ?�데?�트"""
        try:
            now = datetime.now()
            
            # ?�간 ?�맷 (HH:MM:SS)
            time_str = now.strftime("%H:%M:%S")
            self.time_label.config(text=time_str)
            
            # ?�짜 ?�맷 (YYYY-MM-DD ?�일)
            date_str = now.strftime("%Y-%m-%d %A")
            self.date_label.config(text=date_str)
            
            # ?�식 ?�?�머 체크
            self.check_break_time()
            
            # ?�사 ?�간 체크
            self.check_meal_time()
            
            # ?�음 ?�식?�간 ?�데?�트
            self.update_next_break_info()
            
            # 1�????�시 ?�데?�트
            self.clock_window.after(1000, self.update_clock)
            
        except Exception as e:
            print(f"?�계 ?�데?�트 ?�류: {e}")
    
    def update_next_break_info(self):
        """?�음 ?�식?�간 ?�보 ?�데?�트"""
        try:
            # ?�사?�간 중이�??�별 메시지 ?�시
            if self.is_meal_time():
                self.next_break_label.config(text="?���??�사?�간 (?�식 ?�림 ?�시?��?)", fg="orange")
                return
            
            current_time = time.time()
            elapsed_minutes = (current_time - self.last_break_time) / 60
            
            # ?�음 ?�식까�? ?��? ?�간 계산
            remaining_minutes = max(0, self.time_interval - elapsed_minutes)
            
            if remaining_minutes >= 1:
                remaining_mins = int(remaining_minutes)
                remaining_secs = int((remaining_minutes - remaining_mins) * 60)
                self.next_break_label.config(text=f"???�음 ?�식: {remaining_mins}:{remaining_secs:02d}", fg="green")
            else:
                remaining_secs = int(remaining_minutes * 60)
                if remaining_secs > 0:
                    self.next_break_label.config(text=f"???�음 ?�식: {remaining_secs}�?, fg="orange")
                else:
                    self.next_break_label.config(text="???�식?�간!", fg="red")
            
        except Exception as e:
            print(f"?�음 ?�식?�간 ?�보 ?�데?�트 ?�류: {e}")
    
    def is_meal_time(self):
        """?�재 ?�사?�간?��? ?�인 (?�사 ?�림???�성?�된 경우?�만)"""
        try:
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            current_time_minutes = current_hour * 60 + current_minute
            
            is_meal = False
            
            # ?�심?�간 체크 (?�심 ?�림???�성?�된 경우?�만)
            if getattr(self, 'lunch_enabled', True):
                lunch_start = self.lunch_time[0] * 60 + self.lunch_time[1]
                lunch_end = lunch_start + 60  # 1?�간 ??
                if lunch_start <= current_time_minutes < lunch_end:
                    is_meal = True
            
            # ?�?�시�?체크 (?�???�림???�성?�된 경우?�만)
            if getattr(self, 'dinner_enabled', True):
                dinner_start = self.dinner_time[0] * 60 + self.dinner_time[1]
                dinner_end = dinner_start + 60  # 1?�간 ??
                if dinner_start <= current_time_minutes < dinner_end:
                    is_meal = True
            
            return is_meal
            
        except Exception as e:
            print(f"?�사?�간 ?�인 ?�류: {e}")
            return False
    
    def check_break_time(self):
        """?�식 ?�간 체크"""
        try:
            # ?�식 ?�림??비활?�화?�어 ?�으�?건너?�기
            if not getattr(self, 'break_enabled', True):
                return
            
            # ?�사?�간 중이�??�식 ?�업 건너?�기
            if self.is_meal_time():
                print("?�사?�간 중이므�??�식 ?�림??건너?�니??")
                return
            
            current_time = time.time()
            elapsed_minutes = (current_time - self.last_break_time) / 60
            
            # ?�정???�간 간격??지?�으�??�식 ?�림
            if elapsed_minutes >= self.time_interval:
                print(f"?�식 ?�간! {self.time_interval}분이 지?�습?�다.")
                self.show_break_popup()
                self.last_break_time = current_time  # 마�?�??�식 ?�간 ?�데?�트
                
        except Exception as e:
            print(f"?�식 ?�간 체크 ?�류: {e}")
    
    def show_break_popup(self):
        """?�식 ?�업 ?�시"""
        try:
            RestPopup()
        except Exception as e:
            print(f"?�식 ?�업 ?�시 ?�류: {e}")
    
    def check_meal_time(self):
        """?�사 ?�간 체크"""
        try:
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            current_date = now.strftime("%Y-%m-%d")
            
            # ?�심 ?�간 체크 (?�확???�간?�만)
            if (getattr(self, 'lunch_enabled', True) and 
                current_hour == self.lunch_time[0] and current_minute == self.lunch_time[1] and 
                (not hasattr(self, 'lunch_shown_today') or 
                getattr(self, 'lunch_shown_today', '') != current_date)):
                print("?�심 ?�간?�니??")
                self.show_meal_popup("?�심")
                self.lunch_shown_today = current_date
            
            # ?�???�간 체크 (?�확???�간?�만)
            if (getattr(self, 'dinner_enabled', True) and
                current_hour == self.dinner_time[0] and current_minute == self.dinner_time[1] and
                (not hasattr(self, 'dinner_shown_today') or 
                getattr(self, 'dinner_shown_today', '') != current_date)):
                print("?�???�간?�니??")
                self.show_meal_popup("?�??)
                self.dinner_shown_today = current_date
                
        except Exception as e:
            print(f"?�사 ?�간 체크 ?�류: {e}")
    
    def show_meal_popup(self, meal_type):
        """?�사 ?�업 ?�시"""
        try:
            MealPopup(meal_type)
        except Exception as e:
            print(f"?�사 ?�업 ?�시 ?�류: {e}")
    
    def on_closing(self):
        """�??�기 처리 - X 버튼 ?�릭 ??백그?�운?�로 ?�동"""
        try:
            # 창을 ?�전???�기�?
            self.clock_window.withdraw()
            
            # ?�업?�시줄에?�도 ?�기�?
            self.clock_window.attributes('-toolwindow', True)
            
            # ?�스???�레???�이�??�성 (?�으�?
            if not hasattr(self, 'system_tray') or not self.system_tray:
                self.create_system_tray()
            
            # 기존 ?�레??창이 ?�으�??�거
            if hasattr(self, 'tray_window') and self.tray_window:
                try:
                    self.tray_window.destroy()
                    self.tray_window = None
                except:
                    pass
            
            # ?�용?�에�?백그?�운???�행 ?�림
            self.show_background_notification()
            
        except Exception as e:
            print(f"백그?�운???�동 ?�류: {e}")
            # ?�류 발생 ???�전 종료
            self.exit_application()
    
    def show_background_notification(self):
        """백그?�운???�행 ?�림 ?�시"""
        try:
            # 간단???�림 ?�업 (?�동?�로 ?�라�?
            notification = tk.Toplevel()
            notification.title("ClockApp")
            notification.geometry("300x100")
            notification.resizable(False, False)
            notification.attributes('-topmost', True)
            notification.attributes('-toolwindow', True)  # ?�업?�시줄에???��?
            
            # ?�면 ?�하?�에 ?�치
            notification.update_idletasks()
            screen_width = notification.winfo_screenwidth()
            screen_height = notification.winfo_screenheight()
            x = screen_width - 320
            y = screen_height - 150
            notification.geometry(f"300x100+{x}+{y}")
            
            # ?�림 ?�용
            frame = tk.Frame(notification, bg="#f0f0f0")
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            tk.Label(frame, text="?�� ClockApp", font=("Arial", 12, "bold"), bg="#f0f0f0").pack()
            tk.Label(frame, text="백그?�운?�에???�행 중입?�다", font=("Arial", 9), bg="#f0f0f0").pack()
            tk.Label(frame, text="?�레???�이콘을 ?�인?�세??, font=("Arial", 8), fg="gray", bg="#f0f0f0").pack()
            
            # 3�????�동?�로 ?�힘
            notification.after(3000, notification.destroy)
            
        except Exception as e:
            print(f"?�림 ?�시 ?�류: {e}")
    
    def create_system_tray(self):
        """?�스???�레??기능 구현 (간단??버전)"""
        try:
            # ?�클�?메뉴 ?�성
            self.tray_menu = tk.Menu(self.clock_window, tearoff=0)
            self.tray_menu.add_command(label="?�계 �??�기", command=self.show_window)
            self.tray_menu.add_command(label="?�정", command=self.open_settings)
            self.tray_menu.add_command(label="?�씨", command=self.open_weather)
            self.tray_menu.add_separator()
            self.tray_menu.add_command(label="종료", command=self.exit_application)
            
            # ?�스???�레???�이�??��??�이??(?��? �?
            self.create_tray_icon()
            
        except Exception as e:
            print(f"?�스???�레???�성 ?�류: {e}")
    
    def create_tray_icon(self):
        """?�레???�이�?�??�성"""
        try:
            self.tray_window = tk.Toplevel(self.clock_window)
            self.tray_window.title("ClockApp - ?�레??)
            
            # ?�면 ?�하?�에 ?�치
            self.tray_window.update_idletasks()
            screen_width = self.tray_window.winfo_screenwidth()
            screen_height = self.tray_window.winfo_screenheight()
            
            tray_width = 200
            tray_height = 120
            x = screen_width - tray_width - 10
            y = screen_height - tray_height - 50  # ?�업?�시�??�에
            
            self.tray_window.geometry(f"{tray_width}x{tray_height}+{x}+{y}")
            self.tray_window.resizable(False, False)
            self.tray_window.attributes('-topmost', True)  # ??�� ?�에
            self.tray_window.attributes('-toolwindow', True)  # ?�업?�시줄에???��?
            
            # ?�이�??�정 (?�용??PNG ?�선, ?�으�?기본 ?�계 ?�이�?
            try:
                icon_file_path = get_icon_path()
                if icon_file_path and os.path.exists(icon_file_path):
                    self.tray_window.iconbitmap(icon_file_path)
            except:
                pass
            
            # ?�레???�용 (???�에 ???�게)
            tray_frame = tk.Frame(self.tray_window, bg="#2c3e50", relief=tk.RAISED, bd=2)
            tray_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            tk.Label(tray_frame, text="�?ClockApp", font=("Arial", 10, "bold"), bg="#f0f0f0").pack()
            tk.Label(tray_frame, text="?�레??모드", font=("Arial", 8), fg="gray", bg="#f0f0f0").pack()
            
            btn_frame = tk.Frame(tray_frame, bg="#f0f0f0")
            btn_frame.pack(pady=3)
            
            tk.Button(btn_frame, text="?�기", command=self.show_window, width=5, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
            tk.Button(btn_frame, text="종료", command=self.exit_application, width=5, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
            
            # ?�클�?메뉴 바인??
            self.tray_window.bind("<Button-3>", self.show_tray_menu)
            tray_frame.bind("<Button-3>", self.show_tray_menu)
            
        except Exception as e:
            print(f"?�레???�이�??�성 ?�류: {e}")
    
    def update_tray_time(self):
        """?�레??창의 ?�간 ?�데?�트"""
        try:
            if hasattr(self, 'tray_time_label') and self.tray_time_label.winfo_exists():
                current_time = datetime.now().strftime("%H:%M:%S")
                self.tray_time_label.config(text=current_time)
                # 1�????�시 ?�행
                self.root.after(1000, self.update_tray_time)
        except Exception as e:
            print(f"?�레???�간 ?�데?�트 ?�류: {e}")
    
    def show_tray_menu(self, event):
        """?�레??메뉴 ?�시"""
        try:
            self.tray_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"?�레??메뉴 ?�시 ?�류: {e}")
    
    def show_window(self):
        """�??�시 ?�시"""
        try:
            self.clock_window.deiconify()  # �??�시 ?�시
            self.clock_window.lift()       # 창을 �??�으�?
            if hasattr(self, 'tray_window'):
                self.tray_window.destroy()  # ?�레??�??�기
        except Exception as e:
            print(f"�??�시 ?�류: {e}")
    
    def create_system_tray(self):
        """?�제 Windows ?�스???�레???�이�??�성"""
        try:
            # ?�레???�이�??��?지 가?�오�?
            icon_image = self.get_tray_icon_image()
            
            # ?�레??메뉴 ?�성
            menu = Menu(
                MenuItem("?�기", self.show_window_from_tray, default=True),
                MenuItem("?�정", self.open_settings_from_tray),
                Menu.SEPARATOR,
                MenuItem("종료", self.quit_from_tray)
            )
            
            # ?�스???�레???�이�??�성
            self.system_tray = pystray.Icon(
                "ClockApp",
                icon_image,
                "ClockApp - ?�간 관�??�구",
                menu
            )
            
            # 별도 ?�레?�에???�레???�행
            self.tray_thread = threading.Thread(target=self.system_tray.run, daemon=True)
            self.tray_thread.start()
            
            print("Windows ?�스???�레???�이콘이 ?�성?�었?�니??")
            
        except Exception as e:
            print(f"?�스???�레???�이�??�성 ?�류: {e}")
    
    def get_tray_icon_image(self):
        """?�레?�에 ?�용???�이�??��?지 가?�오�?""
        try:
            # 1. clock_app.ico ?�이콘이 ?�으�??�선 ?�용
            clock_app_ico = os.path.join(os.path.dirname(__file__), "clock_app.ico")
            if os.path.exists(clock_app_ico):
                image = Image.open(clock_app_ico)
                # ?�절???�기�?리사?�즈 (32x32가 ?�스???�레?�에 ?�합)
                image = image.resize((32, 32), Image.Resampling.LANCZOS)
                return image
            
            # 2. clock_icon.ico ?�이콘이 ?�으�??�용 (fallback)
            clock_icon_ico = os.path.join(os.path.dirname(__file__), "clock_icon.ico")
            if os.path.exists(clock_icon_ico):
                image = Image.open(clock_icon_ico)
                # ?�절???�기�?리사?�즈 (32x32가 ?�스???�레?�에 ?�합)
                image = image.resize((32, 32), Image.Resampling.LANCZOS)
                return image
            else:
                # 3. 기본 ?�계 ?�이�??�성 (마�?�?fallback)
                return create_clock_image(32)
        except Exception as e:
            print(f"?�레???�이�??��?지 ?�성 ?�류: {e}")
            # ?�류 ??기본 ?�이�?반환
            return create_clock_image(32)
    
    def show_window_from_tray(self, icon=None, item=None):
        """?�레?�에??�??�기"""
        self.clock_window.after(0, self.show_window)
    
    def open_settings_from_tray(self, icon=None, item=None):
        """?�레?�에???�정 ?�기"""
        self.clock_window.after(0, self.open_settings)
    
    def quit_from_tray(self, icon=None, item=None):
        """?�레?�에???�플리�??�션 종료"""
        try:
            # ?�스???�레???�이�??�리
            if hasattr(self, 'system_tray') and self.system_tray:
                self.system_tray.stop()
        except:
            pass
        self.clock_window.after(0, self.exit_application)
    
    def exit_application(self):
        """?�플리�??�션 ?�전 종료"""
        try:
            # ?�스???�레???�리
            if hasattr(self, 'system_tray') and self.system_tray:
                try:
                    self.system_tray.stop()
                except:
                    pass
            
            # 기존 ?�레??�??�리
            if hasattr(self, 'tray_window') and self.tray_window:
                try:
                    self.tray_window.destroy()
                except:
                    pass
            
            # 메인 �?종료
            self.clock_window.quit()
            self.clock_window.destroy()
        except:
            pass
    
    def open_settings(self, event=None):
        """?�정 �??�기"""
        try:
            SettingsWindow(self)
        except Exception as e:
            print(f"?�정 �??�기 ?�류: {e}")
    
    def open_weather(self):
        """?�씨 �??�기"""
        try:
            WeatherWindow(self)
        except Exception as e:
            print(f"?�씨 �??�기 ?�류: {e}")
    
    def update_time_settings(self, minutes, lunch_hour, lunch_minute, dinner_hour, dinner_minute, 
                           break_enabled=True, lunch_enabled=True, dinner_enabled=True):
        """?�간 ?�정 ?�데?�트"""
        self.time_interval = minutes
        self.lunch_time = (lunch_hour, lunch_minute)
        self.dinner_time = (dinner_hour, dinner_minute)
        self.break_enabled = break_enabled
        self.lunch_enabled = lunch_enabled
        self.dinner_enabled = dinner_enabled
        
        # ?�식 ?�?�머 리셋 (?�로??간격 ?�용)
        self.last_break_time = time.time()
        
        print(f"?�정 ?�데?�트??- 간격: {minutes}�? ?�심: {lunch_hour:02d}:{lunch_minute:02d}, ?�?? {dinner_hour:02d}:{dinner_minute:02d}")
        print(f"?�성???�태 - ?�식: {break_enabled}, ?�심: {lunch_enabled}, ?�?? {dinner_enabled}")
        print("?�식 ?�?�머가 리셋?�었?�니??")

def create_hello_window():
    """?�사 �??�성"""
    # ?�행 ?�작 ???�이�??�일 ?�성
    print("?�트 ?�이�??�일 ?�성 �?.")
    icon_file_path = create_icon_file()

    # 커스?� ?�업 �?만들�?
    root = tk.Tk()
    root.geometry("300x180")
    root.resizable(False, False)
    root.overrideredirect(True)  # 기본 ?�?��?�??�거

    # ?�이�??�정
    try:
        if icon_file_path and os.path.exists(icon_file_path):
            root.iconbitmap(icon_file_path)
            print("?�성???�트 ?�이�??�용 ?�공")
    except Exception as e:
        print(f"?�이�??�정 ?�패: {e}")

    # 창을 ?�면 중앙???�치
    root.eval('tk::PlaceWindow . center')

    # 커스?� ?�?��?�?만들�?
    title_frame = tk.Frame(root, bg="#d0d0d0", height=30)
    title_frame.pack(fill=tk.X, side=tk.TOP)
    title_frame.pack_propagate(False)

    # ?�래�?기능???�한 변??
    drag_data = {"x": 0, "y": 0}

    def start_drag(event):
        drag_data["x"] = event.x
        drag_data["y"] = event.y

    def on_drag(event):
        x = root.winfo_x() + event.x - drag_data["x"]
        y = root.winfo_y() + event.y - drag_data["y"]
        root.geometry(f"+{x}+{y}")

    # ?�?��?바에 ?�래�??�벤??바인??
    title_frame.bind("<Button-1>", start_drag)
    title_frame.bind("<B1-Motion>", on_drag)

    # ?�?��?�??�용 (?�쪽 ?�렬)
    title_content = tk.Frame(title_frame, bg="#d0d0d0")
    title_content.pack(side=tk.LEFT, padx=10, pady=5)

    # ?�기 버튼 (?�른�??�렬)
    close_button = tk.Button(title_frame, text="×", command=root.destroy, 
                           bg="#d0d0d0", fg="black", font=("Arial", 12, "bold"),
                           width=3, height=1, relief=tk.FLAT)
    close_button.pack(side=tk.RIGHT, padx=5, pady=5)

    # ?�기 버튼???�버 ?�과 추�?
    def on_enter(e):
        close_button.config(bg="#ff4444", fg="white")
    
    def on_leave(e):
        close_button.config(bg="#d0d0d0", fg="black")
    
    close_button.bind("<Enter>", on_enter)
    close_button.bind("<Leave>", on_leave)

    try:
        # ?�?��?바용 ?��? 마우???��?지
        title_clock = create_clock_image(20)
        if title_clock:
            title_clock_photo = ImageTk.PhotoImage(title_clock)
            
            # ?�계 ?��?지
            title_clock_label = tk.Label(title_content, image=title_clock_photo, bg="#d0d0d0")
            title_clock_label.pack(side=tk.LEFT, padx=(0, 5))

            # ?�사 ?�스??
            title_text = tk.Label(title_content, text="?�녕?�세??", bg="#d0d0d0", font=("Arial", 10, "bold"))       
            title_text.pack(side=tk.LEFT)

            # ?�래�??�벤??바인??
            title_content.bind("<Button-1>", start_drag)
            title_content.bind("<B1-Motion>", on_drag)
            title_clock_label.bind("<Button-1>", start_drag)
            title_clock_label.bind("<B1-Motion>", on_drag)
            title_text.bind("<Button-1>", start_drag)
            title_text.bind("<B1-Motion>", on_drag)
        else:
            raise Exception("?�계 ?��?지 ?�성 ?�패")

    except Exception as e:
        print(f"?�?��?�??�트 ?��?지 ?�류: {e}")
        title_text = tk.Label(title_content, text="???�녕?�세??", bg="#d0d0d0", font=("Arial", 10, "bold"))   
        title_text.pack()
        title_text.bind("<Button-1>", start_drag)
        title_text.bind("<B1-Motion>", on_drag)

    # 메인 컨텐�??�역
    content_frame = tk.Frame(root)
    content_frame.pack(fill=tk.BOTH, expand=True)

    try:
        # 메인 ?�계 ?��?지
        clock_image_original = create_clock_image(64)
        if clock_image_original:
            # 마우???��?지?� ?�스?��? ?�께 ?�시?�는 ?�레??
            main_frame = tk.Frame(content_frame)
            main_frame.pack(expand=True)

            # 마우???��?지�??�한 고정 ?�기 ?�레??
            mouse_frame = tk.Frame(main_frame, width=60, height=60)
            mouse_frame.pack(side=tk.LEFT, padx=(0, 10))
            mouse_frame.pack_propagate(False)

            # 마우???��?지 ?�벨
            clock_label = tk.Label(mouse_frame)
            clock_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            # ?�녕 ?�스???�벨
            text_label = tk.Label(main_frame, text="?�녕", font=("Arial", 16))
            text_label.pack(side=tk.LEFT)

            # ?�니메이??변??
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

            # ?�니메이???�작
            animate_clock()
        else:
            raise Exception("메인 마우???��?지 ?�성 ?�패")

    except Exception as e:
        print(f"메인 ?�트 ?��?지 ?�류: {e}")
        label = tk.Label(content_frame, text="???�녕", font=("Arial", 16))
        label.pack(expand=True)

    # ?�계 창을 ?�는 ?�수
    def show_clock():
        root.withdraw()  # ?�사�??�기�?
        try:
            ClockWindow()  # ?�계�??�기
        except Exception as e:
            print(f"?�계 �??�류: {e}")
        finally:
            try:
                root.quit()
                root.destroy()
            except:
                pass

    # ?�인 버튼
    button = tk.Button(content_frame, text="?�인", command=show_clock, width=10)
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    # Win32 뮤텍?��? ?�용??중복 ?�행 방�?
    MUTEX_NAME = "Global\\ClockApp_SingleInstance_Mutex"
    
    # Win32 API ?�수 ?�언
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    CreateMutexW = kernel32.CreateMutexW
    CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    CreateMutexW.restype = wintypes.HANDLE
    
    GetLastError = kernel32.GetLastError
    ERROR_ALREADY_EXISTS = 183
    
    # 뮤텍???�성 ?�도
    mutex_handle = CreateMutexW(None, False, MUTEX_NAME)
    
    if GetLastError() == ERROR_ALREADY_EXISTS:
        print("ClockApp???��? ?�행 중입?�다.")
        # 메시지 박스 ?�시 (콘솔???�을 ???�으므�?
        MessageBoxW = ctypes.windll.user32.MessageBoxW
        MessageBoxW(None, "ClockApp???��? ?�행 중입?�다.\n?�스???�레?��? ?�인?�주?�요.", 
                   "ClockApp", 0x30)  # 0x30 = MB_ICONWARNING
        sys.exit(0)
    
    try:
        # 명령???�수 처리
        import argparse
        parser = argparse.ArgumentParser(description='MouseClock - ?�간 관�??�로그램')
        parser.add_argument('--minimized', action='store_true', 
                           help='?�스???�레?�로 최소?�된 ?�태�??�작')
        args = parser.parse_args()
        
        # ?�사�??�이 바로 ?�계�??�행
        try:
            ClockWindow(start_minimized=args.minimized)
        except Exception as e:
            print(f"?�계 �??�행 ?�류: {e}")
    finally:
        # 뮤텍???�제 (?�로그램 종료 ???�동?�로 ?�제?��?�?명시?�으�?처리)
        if mutex_handle:
            kernel32.CloseHandle(mutex_handle)
