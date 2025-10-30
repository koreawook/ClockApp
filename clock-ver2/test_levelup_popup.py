#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
레벨업 팝업 테스트 - 레벨별 폭죽 강도 테스트
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import random

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
    """레벨업 축하 팝업 클래스 - 레트로 픽셀 아트 스타일"""
    def __init__(self, level):
        self.level = level
        self.popup = tk.Toplevel()
        self.popup.title("Level Up!")
        self.popup.geometry("500x350")
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)
        
        # 하늘색 배경 (레퍼런스 이미지 스타일)
        self.popup.configure(bg="#87CEEB")
        
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

def test_level_sequence():
    """레벨 1부터 10까지 순차적으로 테스트"""
    root = tk.Tk()
    root.withdraw()
    
    current_level = [1]  # 리스트로 감싸서 참조 가능하게
    
    def show_next_level():
        if current_level[0] <= 10:
            print(f"레벨 {current_level[0]} 팝업 표시")
            popup = LevelUpPopup(current_level[0])
            
            # 3초 후 자동으로 다음 레벨
            def auto_next():
                try:
                    popup.close_popup()
                except:
                    pass
                current_level[0] += 1
                if current_level[0] <= 10:
                    root.after(500, show_next_level)  # 0.5초 후 다음 레벨
                else:
                    print("모든 레벨 테스트 완료!")
                    root.quit()
            
            root.after(3000, auto_next)
    
    # 첫 번째 레벨부터 시작
    show_next_level()
    root.mainloop()

def main():
    """테스트용 메인 함수"""
    root = tk.Tk()
    root.withdraw()  # 메인 윈도우 숨기기
    
    print("레벨업 팝업 테스트")
    print("레벨 1-2: 폭죽 없음")
    print("레벨 3: 작은 폭죽 시작")
    print("레벨 10: 최대 화려함")
    print("\n레벨별 순차 테스트를 시작합니다...")
    
    root.after(100, test_level_sequence)
    root.mainloop()

if __name__ == "__main__":
    main()
