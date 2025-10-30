"""
휴식 팝업 단독 테스트 스크립트
"""
import sys
import os
from pathlib import Path

# 현재 경로를 sys.path에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# ClockApp-ver2.py에서 필요한 것들 import
try:
    from ClockApp_ver2 import RestPopup
    import tkinter as tk
    
    # 테스트용 메인 윈도우 생성
    root = tk.Tk()
    root.withdraw()  # 메인 윈도우 숨기기
    
    print("휴식 팝업 테스트 시작...")
    
    # 휴식 팝업 생성
    popup = RestPopup()
    
    # 메인루프 실행
    root.mainloop()
    
except ImportError as e:
    print(f"Import 오류: {e}")
    print("ClockApp-ver2.py 파일에서 모듈을 찾을 수 없습니다.")
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()