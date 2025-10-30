#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
휴식 팝업 테스트
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import random
import glob
import time

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

class StretchImageManager:
    """스트레칭 이미지를 랜덤하게 관리하는 클래스"""
    def __init__(self, image_folder="stretchimage"):
        self.image_folder = image_folder
        self.image_history = []
        self.max_history = 5
        self.available_images = self._load_available_images()
    
    def _load_available_images(self):
        """폴더 내의 모든 이미지 파일 로드"""
        try:
            if not os.path.exists(self.image_folder):
                print(f"스트레칭 이미지 폴더가 없습니다: {self.image_folder}")
                return []
            
            image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']
            images = []
            
            for ext in image_extensions:
                pattern = os.path.join(self.image_folder, ext)
                images.extend(glob.glob(pattern))
            
            print(f"스트레칭 이미지 {len(images)}개 발견: {images}")
            return images
        except Exception as e:
            print(f"이미지 로드 오류: {e}")
            return []
    
    def get_random_image(self):
        """랜덤 이미지를 선택"""
        if not self.available_images:
            return None
        
        if len(self.available_images) <= self.max_history:
            return random.choice(self.available_images)
        
        available = [img for img in self.available_images if img not in self.image_history]
        
        if not available:
            self.image_history.clear()
            available = self.available_images.copy()
        
        selected = random.choice(available)
        
        self.image_history.append(selected)
        if len(self.image_history) > self.max_history:
            self.image_history.pop(0)
        
        return selected

stretch_image_manager = StretchImageManager()

class RestPopup:
    """휴식 알림 팝업 클래스"""
    def __init__(self):
        self.popup = tk.Toplevel()
        self.popup.title("ClockApp Ver2 - 휴식 알림")
        
        # 레벨 데이터 로드 (테스트용 간단한 버전)
        self.level_data = {"level": 1, "total_seconds": 0}
        self.initial_total_seconds = self.level_data['total_seconds']
        self.popup_start_time = time.time()
        
        # 초기 레벨 저장 (레벨업 감지용)
        self.initial_level = self.level_data['level']
        self.current_level = self.initial_level
        
        # 스트레칭 이미지 로드
        self.stretch_image = None
        self.stretch_photo = None
        self.load_stretch_image()
        
        # 이미지가 있으면 더 큰 크기로 설정 (세로로 길게)
        if self.stretch_image:
            self.popup.geometry("480x520")
        else:
            self.popup.geometry("400x420")
        
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)
        
        self.center_popup()
        self.remaining_time = 30
        self.create_widgets()
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        
        # 포커스 잃을 때 팝업 닫기 (다른 앱 클릭 시 자동 닫힘)
        self.popup.bind("<FocusOut>", self.on_focus_out)
        
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
                
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                self.stretch_image = img
                print(f"스트레칭 이미지 로드 성공: {image_path}")
            else:
                print("사용 가능한 스트레칭 이미지가 없습니다.")
        except Exception as e:
            print(f"스트레칭 이미지 로드 오류: {e}")
            self.stretch_image = None
    
    def close_popup(self):
        """팝업 닫기"""
        try:
            # 경과 시간 출력 (테스트용)
            elapsed_time = int(time.time() - self.popup_start_time)
            print(f"휴식 팝업 종료 - 경과 시간: {elapsed_time}초")
            self.popup.destroy()
        except:
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
        
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        
        if self.stretch_image:
            popup_width = 480
            popup_height = 520
        else:
            popup_width = 400
            popup_height = 420
        
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2
        
        self.popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
    
    def create_widgets(self):
        """위젯 생성"""
        self.popup.configure(bg="#f0f8ff")
        
        # 상단 헤더
        header_frame = tk.Frame(self.popup, bg="#4a90e2", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        message_label = tk.Label(
            header_frame, 
            text="잠시 휴식하세요", 
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#4a90e2"
        )
        message_label.pack(pady=15)
        
        # 메인 컨텐츠
        content_frame = tk.Frame(self.popup, bg="#f0f8ff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
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
            horizontal_container = tk.Frame(content_frame, bg="#f0f8ff")
            horizontal_container.pack(pady=3)
            
            # 왼쪽: 스트레칭 이미지
            image_frame = tk.Frame(horizontal_container, bg="#f0f8ff")
            image_frame.pack(side=tk.LEFT, padx=(5, 10))
            
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
            # 이미지가 없으면 중앙에 진행바만
            progress_container = tk.Frame(content_frame, bg="#f0f8ff")
            progress_container.pack(pady=10)
        
        self.rest_progress_canvas = tk.Canvas(
            progress_container, 
            width=180, 
            height=180, 
            bg="#f0f8ff",
            highlightthickness=0
        )
        self.rest_progress_canvas.pack()
        
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
        
        self.second_text_id = None
        
        # 스트레칭 이미지 (타이머 아래)
        
        # 하단 버튼
        button_frame = tk.Frame(self.popup, bg="#f0f8ff")
        button_frame.pack(fill=tk.X, padx=15, pady=(5, 12))
        
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
            self.update_rest_progress_bar()
            self.update_level_info()  # 레벨 정보 업데이트
            
            if self.remaining_time <= 10 and self.close_button['state'] == tk.DISABLED:
                self.close_button.config(
                    text="확인", 
                    state=tk.NORMAL,
                    bg="#27ae60",
                    activebackground="#229954"
                )
            
            if self.remaining_time > 10:
                self.close_button.config(text=f"확인 ({self.remaining_time-10}초 후)")
            
            self.remaining_time -= 1
            self.popup.after(1000, self.update_timer)
        else:
            self.update_rest_progress_bar()
            self.update_level_info()  # 마지막 레벨 정보 업데이트
            self.popup.after(500, self.close_popup)
    
    def update_level_info(self):
        """레벨 정보 업데이트"""
        try:
            # 현재까지 경과 시간 계산
            elapsed_time = int(time.time() - self.popup_start_time)
            current_total_seconds = self.initial_total_seconds + elapsed_time
            
            # 현재 레벨 계산
            current_level, accumulated_seconds = calculate_level_from_seconds(current_total_seconds)
            
            # 레벨업 감지 (테스트용 - 콘솔에 출력만)
            if current_level > self.current_level:
                print(f"🎉 휴식 중 레벨업! {self.current_level} → {current_level}")
                self.current_level = current_level
            
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
        """진행바 업데이트"""
        try:
            import math
            
            remaining_ratio = max(0.0, self.remaining_time / 30.0)
            self.rest_progress_canvas.delete("all")
            
            center_x, center_y = 90, 90
            radius = 75
            
            # 배경 원
            self.rest_progress_canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill="#ecf0f1", outline="#bdc3c7", width=2
            )
            
            # 진행 원호
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
            
            # 타이머 텍스트
            timer_text = f"{max(0, self.remaining_time)}"
            
            self.rest_progress_canvas.create_text(
                center_x, center_y - 12,
                text=timer_text,
                font=("Segoe UI", 36, "bold"),
                fill="#4a90e2",
                anchor=tk.CENTER
            )
            
            self.rest_progress_canvas.create_text(
                center_x, center_y + 22,
                text="초",
                font=("Segoe UI", 13),
                fill="#7f8c8d",
                anchor=tk.CENTER
            )
            
        except Exception as e:
            print(f"진행바 업데이트 오류: {e}")

def main():
    root = tk.Tk()
    root.withdraw()  # 메인 윈도우 숨기기
    RestPopup()
    root.mainloop()

if __name__ == "__main__":
    main()
