#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실시간 레벨업 테스트 - 레벨 1에서 29초 누적으로 시작 (1초 후 레벨업)
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import random
import glob
import time
import json

def get_level_data_file_path():
    """레벨 데이터 파일 경로 반환"""
    appdata_dir = os.path.join(os.getenv('APPDATA'), 'ClockApp-Ver2')
    os.makedirs(appdata_dir, exist_ok=True)
    return os.path.join(appdata_dir, 'rest_level_data.json')

def load_level_data():
    """레벨 데이터 로드"""
    try:
        file_path = get_level_data_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"레벨 데이터 로드: 레벨 {data['level']}, 누적시간 {data['total_seconds']}초")
                return data
    except Exception as e:
        print(f"레벨 데이터 로드 오류: {e}")
    
    return {"level": 1, "total_seconds": 0}

def save_level_data(level, total_seconds):
    """레벨 데이터 저장"""
    try:
        file_path = get_level_data_file_path()
        data = {"level": level, "total_seconds": total_seconds}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"레벨 데이터 저장: 레벨 {level}, 누적시간 {total_seconds}초")
    except Exception as e:
        print(f"레벨 데이터 저장 오류: {e}")

def calculate_level_from_seconds(total_seconds):
    """누적 시간으로 레벨 계산"""
    level = 1
    required_seconds = 30
    accumulated_seconds = 0
    
    while accumulated_seconds + required_seconds <= total_seconds:
        accumulated_seconds += required_seconds
        level += 1
        required_seconds *= 2
    
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

class LevelUpPopup:
    """레벨업 축하 팝업 클래스"""
    def __init__(self, level):
        self.level = level
        self.popup = tk.Toplevel()
        self.popup.title("Level Up!")
        self.popup.geometry("500x350")
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)
        
        self.popup.configure(bg="#87CEEB")
        self.center_popup()
        self.create_widgets()
        
        # 포커스 잃으면 닫기 (다른 앱 클릭 시 자동 닫힘)
        self.popup.bind("<FocusOut>", self.on_focus_out)
        
        # 추가 이벤트 바인딩 (더 안정적인 작동을 위해)
        self.popup.bind("<Deactivate>", self.on_focus_out)  # 창이 비활성화될 때
        
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        
        if self.level >= 3:
            self.firework_particles = []
            self.animate_fireworks()
    
    def center_popup(self):
        self.popup.update_idletasks()
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 350) // 2
        self.popup.geometry(f"500x350+{x}+{y}")
    
    def create_widgets(self):
        main_frame = tk.Frame(self.popup, bg="#87CEEB")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if self.level >= 3:
            self.firework_canvas = tk.Canvas(
                main_frame, width=460, height=310,
                bg="#87CEEB", highlightthickness=0
            )
            self.firework_canvas.place(x=0, y=0)
        
        level_up_frame = tk.Frame(main_frame, bg="#FF6B8A", relief=tk.RAISED, bd=3)
        level_up_frame.pack(pady=(30, 15))
        
        level_up_label = tk.Label(
            level_up_frame, text="Level Up",
            font=("Arial Black", 28, "bold"),
            fg="#FFEB3B", bg="#FF6B8A", padx=30, pady=10
        )
        level_up_label.pack()
        
        level_number_label = tk.Label(
            main_frame, text=f"레벨 {self.level}",
            font=("맑은 고딕", 36, "bold"),
            fg="#2C3E50", bg="#87CEEB"
        )
        level_number_label.pack(pady=(10, 15))
        
        message = get_level_up_message(self.level)
        message_label = tk.Label(
            main_frame, text=message,
            font=("맑은 고딕", 12, "bold"),
            fg="#34495E", bg="#87CEEB",
            wraplength=400, justify=tk.CENTER
        )
        message_label.pack(pady=(5, 25))
        
        close_button = tk.Button(
            main_frame, text="계속하기",
            font=("맑은 고딕", 11, "bold"),
            bg="#FF6B8A", fg="white",
            relief=tk.RAISED, bd=3,
            padx=35, pady=8, cursor="hand2",
            command=self.close_popup
        )
        close_button.pack()
    
    def get_firework_intensity(self):
        if self.level < 3:
            return 0, 0, 0.0
        elif self.level == 3:
            return 8, 3, 0.15
        elif self.level <= 5:
            return 12, 4, 0.25
        elif self.level <= 7:
            return 18, 5, 0.35
        elif self.level <= 9:
            return 25, 6, 0.45
        else:
            return 35, 7, 0.60
    
    def animate_fireworks(self):
        try:
            particle_count, max_size, spawn_rate = self.get_firework_intensity()
            
            if random.random() < spawn_rate:
                x = random.randint(50, 410)
                y = random.randint(50, 260)
                self.create_firework(x, y, particle_count, max_size)
            
            for particle in self.firework_particles[:]:
                particle['life'] -= 1
                if particle['life'] <= 0:
                    self.firework_canvas.delete(particle['id'])
                    self.firework_particles.remove(particle)
                else:
                    self.firework_canvas.move(
                        particle['id'],
                        particle['vx'],
                        particle['vy']
                    )
                    particle['vy'] += 0.2
            
            if self.popup.winfo_exists():
                self.popup.after(50, self.animate_fireworks)
        except:
            pass
    
    def create_firework(self, x, y, particle_count, max_size):
        colors = ["#FFD700", "#FF6B8A", "#00FF00", "#00FFFF", "#FF69B4", "#FFA500"]
        
        for _ in range(particle_count):
            speed = random.uniform(2, 7)
            vx = speed * random.uniform(-1, 1)
            vy = speed * random.uniform(-1, 1)
            color = random.choice(colors)
            size = random.randint(max(2, max_size - 2), max_size)
            
            particle_id = self.firework_canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill=color, outline=""
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
        try:
            self.popup.destroy()
        except:
            pass

class TestRestPopup:
    """레벨업 직전 상태로 시작하는 휴식 팝업"""
    def __init__(self):
        self.popup = tk.Toplevel()
        self.popup.title("실시간 레벨업 테스트")
        
        # 레벨 1, 29초로 시작 (1초 후 레벨 2로 올라감)
        self.level_data = {"level": 1, "total_seconds": 29}
        self.initial_total_seconds = self.level_data['total_seconds']
        self.popup_start_time = time.time()
        
        # 초기 레벨 저장
        self.initial_level = self.level_data['level']
        self.current_level = self.initial_level
        
        self.popup.geometry("400x420")
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)
        
        self.center_popup()
        self.remaining_time = 30
        self.create_widgets()
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        
        self.update_timer()
    
    def close_popup(self):
        try:
            elapsed_time = int(time.time() - self.popup_start_time)
            print(f"테스트 종료 - 경과 시간: {elapsed_time}초")
            self.popup.destroy()
        except:
            pass
    
    def center_popup(self):
        self.popup.update_idletasks()
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 420) // 2
        self.popup.geometry(f"400x420+{x}+{y}")
    
    def create_widgets(self):
        self.popup.configure(bg="#f0f8ff")
        
        header_frame = tk.Frame(self.popup, bg="#4a90e2", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        message_label = tk.Label(
            header_frame, text="실시간 레벨업 테스트", 
            font=("맑은 고딕", 16, "bold"),
            fg="white", bg="#4a90e2"
        )
        message_label.pack(pady=15)
        
        content_frame = tk.Frame(self.popup, bg="#f0f8ff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        sub_message = tk.Label(
            content_frame,
            text="눈을 감고 잠시 휴식을 취하세요",
            font=("맑은 고딕", 11),
            fg="#5a6c7d", bg="#f0f8ff"
        )
        sub_message.pack(pady=(0, 15))
        
        progress_container = tk.Frame(content_frame, bg="#f0f8ff")
        progress_container.pack(pady=10)
        
        self.rest_progress_canvas = tk.Canvas(
            progress_container, width=180, height=180,
            bg="#f0f8ff", highlightthickness=0
        )
        self.rest_progress_canvas.pack()
        
        self.timer_text_id = None
        self.second_text_id = None
        
        level_info_frame = tk.Frame(content_frame, bg="#f0f8ff")
        level_info_frame.pack(pady=(10, 5))
        
        self.accumulated_time_label = tk.Label(
            level_info_frame, text="누적시간: 0분 29초",
            font=("맑은 고딕", 10, "bold"),
            fg="#2980b9", bg="#f0f8ff"
        )
        self.accumulated_time_label.pack()
        
        self.level_label = tk.Label(
            level_info_frame, text="레벨: 1",
            font=("맑은 고딕", 16, "bold"),
            fg="#27ae60", bg="#f0f8ff"
        )
        self.level_label.pack(pady=(5, 3))
        
        self.next_level_label = tk.Label(
            level_info_frame,
            text="다음 레벨까지 남은 시간: 0분 1초",
            font=("맑은 고딕", 10),
            fg="#7f8c8d", bg="#f0f8ff"
        )
        self.next_level_label.pack(pady=(3, 0))
        
        button_frame = tk.Frame(self.popup, bg="#f0f8ff")
        button_frame.pack(fill=tk.X, padx=15, pady=(5, 12))
        
        self.close_button = tk.Button(
            button_frame, text="닫기",
            state=tk.NORMAL,
            font=("맑은 고딕", 9, "bold"),
            bg="#27ae60", fg="white",
            relief=tk.FLAT, bd=0,
            padx=20, pady=8, cursor="hand2",
            command=self.close_popup
        )
        self.close_button.pack(fill=tk.X)
    
    def update_timer(self):
        if self.remaining_time >= 0:
            self.update_rest_progress_bar()
            self.update_level_info()
            self.remaining_time -= 1
            self.popup.after(1000, self.update_timer)
        else:
            self.update_rest_progress_bar()
            self.update_level_info()
            self.popup.after(500, self.close_popup)
    
    def update_level_info(self):
        try:
            elapsed_time = int(time.time() - self.popup_start_time)
            current_total_seconds = self.initial_total_seconds + elapsed_time
            
            current_level, accumulated_seconds = calculate_level_from_seconds(current_total_seconds)
            
            # 레벨업 감지!
            if current_level > self.current_level:
                print(f"🎉 휴식 중 레벨업 감지! {self.current_level} → {current_level}")
                self.current_level = current_level
                
                # 레벨업 팝업 표시
                try:
                    LevelUpPopup(current_level)
                except Exception as e:
                    print(f"레벨업 팝업 표시 오류: {e}")
            
            next_level_required = get_next_level_required_seconds(current_level)
            time_to_next_level = next_level_required - (current_total_seconds - accumulated_seconds)
            
            time_display = format_time_display(current_total_seconds)
            self.accumulated_time_label.config(text=f"누적시간: {time_display}")
            
            self.level_label.config(text=f"레벨: {current_level}")
            
            remaining_time_display = format_time_display(time_to_next_level)
            self.next_level_label.config(text=f"다음 레벨까지 남은 시간: {remaining_time_display}")
            
        except Exception as e:
            print(f"레벨 정보 업데이트 오류: {e}")
    
    def update_rest_progress_bar(self):
        try:
            remaining_ratio = max(0.0, self.remaining_time / 30.0)
            self.rest_progress_canvas.delete("all")
            
            center_x, center_y = 90, 90
            radius = 75
            
            self.rest_progress_canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill="#ecf0f1", outline="#bdc3c7", width=2
            )
            
            if remaining_ratio > 0:
                if remaining_ratio > 0.5:
                    color = "#27ae60"
                elif remaining_ratio > 0.2:
                    color = "#f39c12"
                else:
                    color = "#e74c3c"
                
                extent = -360 * remaining_ratio
                
                self.rest_progress_canvas.create_arc(
                    center_x - radius + 8, center_y - radius + 8,
                    center_x + radius - 8, center_y + radius - 8,
                    start=90, extent=extent,
                    fill=color, outline=color, width=14,
                    style=tk.ARC
                )
            
            timer_value = max(0, self.remaining_time)
            self.timer_text_id = self.rest_progress_canvas.create_text(
                center_x, center_y,
                text=str(timer_value),
                font=("Arial", 48, "bold"),
                fill="#2c3e50"
            )
            
            self.second_text_id = self.rest_progress_canvas.create_text(
                center_x, center_y + 40,
                text="초",
                font=("맑은 고딕", 14),
                fill="#7f8c8d"
            )
            
        except Exception as e:
            print(f"진행바 업데이트 오류: {e}")

def main():
    root = tk.Tk()
    root.withdraw()
    
    print("=" * 60)
    print("실시간 레벨업 테스트")
    print("=" * 60)
    print("초기 상태: 레벨 1, 누적시간 29초")
    print("1초 후 레벨 2로 올라가면서 레벨업 팝업이 나타나야 합니다!")
    print("=" * 60)
    
    TestRestPopup()
    root.mainloop()

if __name__ == "__main__":
    main()
