"""
빌드된 앱에서 PIL/ImageTk가 정상적으로 작동하는지 테스트
"""
import sys
import os
from pathlib import Path

def test_pil_imagetn():
    try:
        # PIL 모듈 테스트
        from PIL import Image
        print("✅ PIL.Image import 성공")
        
        from PIL import ImageTk
        print("✅ PIL.ImageTk import 성공")
        
        # 실제 이미지 로드 테스트
        if getattr(sys, 'frozen', False):
            base_path = Path(sys.executable).parent / "_internal"
            stretch_path = base_path / "stretchimage"
        else:
            base_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()
            stretch_path = base_path / "stretchimage"
        
        print(f"이미지 폴더 경로: {stretch_path}")
        print(f"폴더 존재: {stretch_path.exists()}")
        
        if stretch_path.exists():
            image_files = list(stretch_path.glob("*.png")) + list(stretch_path.glob("*.jpg")) + list(stretch_path.glob("*.jpeg"))
            print(f"이미지 파일 개수: {len(image_files)}")
            
            if image_files:
                test_image = image_files[0]
                print(f"테스트 이미지: {test_image}")
                
                # PIL로 이미지 로드
                img = Image.open(test_image)
                print(f"✅ Image.open 성공: {img.size}")
                
                # Tkinter 없이는 ImageTk.PhotoImage를 테스트할 수 없음
                print("⚠️ ImageTk.PhotoImage는 Tkinter 루트 윈도우 필요")
                
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 결과를 파일로 저장
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        test_pil_imagetn()
    
    result = output.getvalue()
    
    with open("pil_test.txt", "w", encoding="utf-8") as f:
        f.write(result)
    
    print("Test completed - check pil_test.txt")