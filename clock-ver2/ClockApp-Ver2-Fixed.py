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

def get_weather_data():
    """기본 날씨 데이터"""
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
    
    return {
        'current': {
            'temp': current_weather['temp'],
            'humidity': '65%',
            'wind': '2.1m/s',
            'description': current_weather['desc'],
            'icon': current_weather['icon']
        },
        'location': '서울시'
    }

class RestPopup:
    """휴식 알림 팝업 클래스"""
    def __init__(self):
        self.popup = tk.Toplevel()
        self.popup.title("휴식 알림")
        self.popup.geometry("400x300")
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)
        
        # 창을 화면 중앙에 위치
        self.center_popup()
        
        # 30초 타이머
        self.remaining_time = 30
        
        self.create_widgets()
        
        # X 버튼 비활성화
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        
        # 타이머 시작
        self.update_timer()
    
    def center_popup(self):
        """팝업을 화면 중앙에 위치시키기"""
        self.popup.update_idletasks()
        
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        
        popup_width = 400
        popup_height = 300
        
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2
        
        self.popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
    
    def create_widgets(self):
        """위젯 생성"""
        # 헤더
        header_frame = tk.Frame(self.popup, bg="#4a90e2", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # 아이콘
        emoji_label = tk.Label(
            header_frame,
            text="👁️",
            font=("Arial", 36),
            bg="#4a90e2",
            fg="white"
        )
        emoji_label.pack(pady=(10, 5))
        
        # 메시지
        message_label = tk.Label(
            header_frame, 
            text="잠시 휴식하세요!", 
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#4a90e2"
        )
        message_label.pack()
        
        # 내용 영역
        content_frame = tk.Frame(self.popup, bg="#f0f8ff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 부가 메시지
        sub_message = tk.Label(
            content_frame,
            text="눈을 감고 잠시 휴식을 취하세요",
            font=("Arial", 11),
            fg="#5a6c7d",
            bg="#f0f8ff"
        )
        sub_message.pack(pady=(0, 15))
        
        # 타이머 표시
        self.timer_label = tk.Label(
            content_frame,
            text="30",
            font=("Arial", 48, "bold"),
            fg="#4a90e2",
            bg="#f0f8ff"
        )
        self.timer_label.pack(pady=20)
        
        # 버튼 영역
        button_frame = tk.Frame(self.popup, bg="#f0f8ff")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # 닫기 버튼
        self.close_button = tk.Button(
            button_frame,
            text="확인 (10초후)",
            state=tk.DISABLED,
            font=("Arial", 11, "bold"),
            bg="#bdc3c7",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=30,
            pady=12,
            command=self.close_popup
        )
        self.close_button.pack(fill=tk.X)
    
    def update_timer(self):
        """타이머 업데이트"""
        if self.remaining_time >= 0:
            self.timer_label.config(text=str(max(0, self.remaining_time)))
            
            # 마지막 10초에 버튼 활성화
            if self.remaining_time <= 10 and self.close_button['state'] == tk.DISABLED:
                self.close_button.config(
                    text="확인", 
                    state=tk.NORMAL,
                    bg="#27ae60"
                )
            
            if self.remaining_time > 10:
                self.close_button.config(text=f"확인 ({self.remaining_time-10}초후)")
            
            self.remaining_time -= 1
            self.popup.after(1000, self.update_timer)
        else:
            self.popup.after(500, self.close_popup)
    
    def close_popup(self):
        """팝업 닫기"""
        try:
            self.popup.destroy()
        except:
            pass

class ClockApp:
    """메인 시계 앱 클래스"""
    def __init__(self):
        # 설정 로드
        self.settings = load_settings()
        
        # 메인 윈도우 생성
        self.clock_window = tk.Tk()
        self.clock_window.title("시계 앱 v2")
        self.clock_window.geometry("300x200")
        self.clock_window.configure(bg="#f8f9fa")
        
        # 휴식 관련 변수
        self.last_break_time = time.time()
        self.is_meal_time = False
        self.current_popup = None
        
        # 위젯 생성
        self.create_widgets()
        
        # 정기 업데이트 시작
        self.update_clock()
        
        # X 버튼 처리
        self.clock_window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        """메인 위젯 생성"""
        # 시계 프레임
        clock_frame = tk.Frame(self.clock_window, bg="#f8f9fa")
        clock_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 현재 시간
        self.time_label = tk.Label(
            clock_frame,
            text="00:00:00",
            font=("Arial", 24, "bold"),
            fg="#2c3e50",
            bg="#f8f9fa"
        )
        self.time_label.pack(pady=10)
        
        # 날짜
        self.date_label = tk.Label(
            clock_frame,
            text="2024년 10월 22일",
            font=("Arial", 12),
            fg="#7f8c8d",
            bg="#f8f9fa"
        )
        self.date_label.pack()
        
        # 다음 휴식 정보
        self.next_break_label = tk.Label(
            clock_frame,
            text="다음 휴식: 계산 중...",
            font=("Arial", 10),
            fg="#27ae60",
            bg="#f8f9fa"
        )
        self.next_break_label.pack(pady=(20, 5))
        
        # 날씨 정보
        self.weather_label = tk.Label(
            clock_frame,
            text="날씨: 로딩 중...",
            font=("Arial", 10),
            fg="#3498db",
            bg="#f8f9fa"
        )
        self.weather_label.pack(pady=5)
        
        # 버튼 프레임
        button_frame = tk.Frame(clock_frame, bg="#f8f9fa")
        button_frame.pack(pady=10)
        
        # 설정 버튼
        settings_button = tk.Button(
            button_frame,
            text="설정",
            command=self.open_settings,
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=20
        )
        settings_button.pack(side=tk.LEFT, padx=5)
        
        # 날씨 버튼
        weather_button = tk.Button(
            button_frame,
            text="날씨",
            command=self.show_weather,
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            padx=20
        )
        weather_button.pack(side=tk.LEFT, padx=5)
    
    def update_clock(self):
        """시계 업데이트"""
        try:
            # 현재 시간 업데이트
            now = datetime.now()
            time_text = now.strftime("%H:%M:%S")
            date_text = now.strftime("%Y년 %m월 %d일")
            
            self.time_label.config(text=time_text)
            self.date_label.config(text=date_text)
            
            # 다음 휴식 시간 계산
            self.update_next_break_info()
            
            # 휴식 시간 체크
            self.check_break_time()
            
            # 날씨 정보 업데이트 (10분마다)
            if now.minute % 10 == 0 and now.second == 0:
                self.update_weather_info()
            
        except Exception as e:
            print(f"시계 업데이트 오류: {e}")
        
        # 1초 후 다시 호출
        self.clock_window.after(1000, self.update_clock)
    
    def update_next_break_info(self):
        """다음 휴식시간 정보 업데이트"""
        try:
            current_time = time.time()
            time_since_last_break = current_time - self.last_break_time
            interval_seconds = self.settings['time_interval'] * 60
            
            remaining_time = interval_seconds - time_since_last_break
            
            if remaining_time > 0:
                remaining_mins = int(remaining_time // 60)
                remaining_secs = int(remaining_time % 60)
                
                if remaining_mins > 0:
                    self.next_break_label.config(
                        text=f"다음 휴식: {remaining_mins}:{remaining_secs:02d}",
                        fg="#27ae60"
                    )
                elif remaining_secs > 10:
                    self.next_break_label.config(
                        text=f"다음 휴식: {remaining_secs}초",
                        fg="orange"
                    )
                else:
                    self.next_break_label.config(
                        text="휴식시간!",
                        fg="red"
                    )
            else:
                self.next_break_label.config(
                    text="휴식시간!",
                    fg="red"
                )
        except Exception as e:
            print(f"휴식 시간 계산 오류: {e}")
    
    def check_break_time(self):
        """휴식 시간 체크"""
        try:
            if not self.settings.get('break_enabled', True):
                return
            
            current_time = time.time()
            time_since_last_break = current_time - self.last_break_time
            interval_seconds = self.settings['time_interval'] * 60
            
            # 휴식 시간이 되었고 현재 팝업이 없으면
            if time_since_last_break >= interval_seconds and self.current_popup is None:
                self.show_rest_popup()
        except Exception as e:
            print(f"휴식 시간 체크 오류: {e}")
    
    def show_rest_popup(self):
        """휴식 팝업 표시"""
        try:
            self.current_popup = RestPopup()
            self.last_break_time = time.time()
            
            # 팝업이 닫힐 때까지 대기
            self.clock_window.after(100, self.check_popup_closed)
        except Exception as e:
            print(f"휴식 팝업 표시 오류: {e}")
    
    def check_popup_closed(self):
        """팝업이 닫혔는지 확인"""
        try:
            if self.current_popup and hasattr(self.current_popup, 'popup'):
                if self.current_popup.popup.winfo_exists():
                    # 팝업이 아직 있으면 다시 체크
                    self.clock_window.after(100, self.check_popup_closed)
                    return
            # 팝업이 닫혔으면 현재 팝업 초기화
            self.current_popup = None
        except:
            self.current_popup = None
    
    def update_weather_info(self):
        """날씨 정보 업데이트"""
        try:
            weather_data = get_weather_data()
            current = weather_data['current']
            weather_text = f"날씨: {current['icon']} {current['temp']} {current['description']}"
            self.weather_label.config(text=weather_text)
        except Exception as e:
            print(f"날씨 정보 업데이트 오류: {e}")
            self.weather_label.config(text="날씨: 정보 없음")
    
    def show_weather(self):
        """날씨 창 표시"""
        try:
            weather_data = get_weather_data()
            current = weather_data['current']
            
            weather_info = f"""현재 날씨 정보
            
위치: {weather_data['location']}
온도: {current['temp']}
습도: {current['humidity']}
풍속: {current['wind']}
상태: {current['description']} {current['icon']}
"""
            
            messagebox.showinfo("날씨 정보", weather_info)
        except Exception as e:
            print(f"날씨 창 표시 오류: {e}")
            messagebox.showerror("오류", "날씨 정보를 불러올 수 없습니다.")
    
    def open_settings(self):
        """설정 창 열기"""
        try:
            settings_window = tk.Toplevel(self.clock_window)
            settings_window.title("설정")
            settings_window.geometry("300x400")
            settings_window.resizable(False, False)
            settings_window.grab_set()  # 모달 창
            
            # 설정 프레임
            main_frame = tk.Frame(settings_window, padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 휴식 간격 설정
            tk.Label(main_frame, text="휴식 간격 (분):", font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
            interval_var = tk.StringVar(value=str(self.settings['time_interval']))
            interval_entry = tk.Entry(main_frame, textvariable=interval_var, width=10)
            interval_entry.pack(anchor="w", pady=(0, 15))
            
            # 점심 시간 설정
            tk.Label(main_frame, text="점심 시간:", font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
            lunch_frame = tk.Frame(main_frame)
            lunch_frame.pack(anchor="w", pady=(0, 15))
            
            lunch_hour_var = tk.StringVar(value=str(self.settings['lunch_hour']))
            lunch_minute_var = tk.StringVar(value=str(self.settings['lunch_minute']))
            
            tk.Entry(lunch_frame, textvariable=lunch_hour_var, width=5).pack(side=tk.LEFT)
            tk.Label(lunch_frame, text="시").pack(side=tk.LEFT, padx=5)
            tk.Entry(lunch_frame, textvariable=lunch_minute_var, width=5).pack(side=tk.LEFT)
            tk.Label(lunch_frame, text="분").pack(side=tk.LEFT, padx=5)
            
            # 체크박스들
            break_enabled_var = tk.BooleanVar(value=self.settings.get('break_enabled', True))
            lunch_enabled_var = tk.BooleanVar(value=self.settings.get('lunch_enabled', True))
            
            tk.Checkbutton(main_frame, text="휴식 알림 활성화", variable=break_enabled_var).pack(anchor="w", pady=5)
            tk.Checkbutton(main_frame, text="점심 알림 활성화", variable=lunch_enabled_var).pack(anchor="w", pady=5)
            
            # 버튼 프레임
            button_frame = tk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(20, 0))
            
            def save_settings():
                try:
                    # 새 설정 저장
                    new_settings = {
                        'time_interval': int(interval_var.get()),
                        'lunch_hour': int(lunch_hour_var.get()),
                        'lunch_minute': int(lunch_minute_var.get()),
                        'dinner_hour': self.settings.get('dinner_hour', 18),
                        'dinner_minute': self.settings.get('dinner_minute', 0),
                        'break_enabled': break_enabled_var.get(),
                        'lunch_enabled': lunch_enabled_var.get(),
                        'dinner_enabled': self.settings.get('dinner_enabled', False)
                    }
                    
                    if save_settings_to_file(new_settings):
                        self.settings = new_settings
                        messagebox.showinfo("성공", "설정이 저장되었습니다.")
                        settings_window.destroy()
                    else:
                        messagebox.showerror("오류", "설정 저장에 실패했습니다.")
                        
                except ValueError:
                    messagebox.showerror("오류", "올바른 숫자를 입력해주세요.")
                except Exception as e:
                    messagebox.showerror("오류", f"설정 저장 중 오류: {e}")
            
            tk.Button(button_frame, text="저장", command=save_settings, bg="#27ae60", fg="white").pack(side=tk.RIGHT, padx=(5, 0))
            tk.Button(button_frame, text="취소", command=settings_window.destroy, bg="#95a5a6", fg="white").pack(side=tk.RIGHT)
            
        except Exception as e:
            print(f"설정 창 오류: {e}")
            messagebox.showerror("오류", "설정 창을 열 수 없습니다.")
    
    def on_close(self):
        """창 닫기 처리"""
        try:
            # 시스템 트레이로 최소화할지 물어보기
            result = messagebox.askyesnocancel(
                "종료 확인",
                "백그라운드에서 계속 실행하시겠습니까?\n\n예: 백그라운드 실행\n아니오: 완전 종료\n취소: 창 유지"
            )
            
            if result is True:  # 예 - 백그라운드 실행
                self.clock_window.withdraw()  # 창 숨기기
            elif result is False:  # 아니오 - 완전 종료
                self.clock_window.quit()
                sys.exit()
            # 취소인 경우 아무것도 하지 않음
            
        except Exception as e:
            print(f"창 닫기 처리 오류: {e}")
            self.clock_window.quit()
    
    def run(self):
        """앱 실행"""
        try:
            # 초기 날씨 정보 로드
            self.update_weather_info()
            
            # 메인 루프 시작
            self.clock_window.mainloop()
        except Exception as e:
            print(f"앱 실행 오류: {e}")

def main():
    """메인 함수"""
    try:
        # 명령행 인수 처리
        minimized = '--minimized' in sys.argv
        
        # 앱 생성 및 실행
        app = ClockApp()
        
        if minimized:
            # 최소화 상태로 시작
            app.clock_window.withdraw()
        
        app.run()
        
    except Exception as e:
        print(f"메인 함수 오류: {e}")
        messagebox.showerror("오류", f"앱 시작 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()