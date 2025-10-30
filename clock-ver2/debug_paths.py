"""
PyInstaller 빌드 버전 디버그를 위한 임시 테스트 스크립트
"""
import os
import sys
from pathlib import Path

def debug_paths():
    """경로 정보 디버그"""
    debug_info = []
    
    debug_info.append(f"sys.frozen: {getattr(sys, 'frozen', False)}")
    debug_info.append(f"sys.executable: {sys.executable}")
    debug_info.append(f"__file__ exists: {'__file__' in globals()}")
    
    if getattr(sys, 'frozen', False):
        # PyInstaller 환경
        base_path = Path(sys.executable).parent
        internal_path = base_path / "_internal"
        stretch_path = internal_path / "stretchimage"
    else:
        # 개발 환경
        if '__file__' in globals():
            base_path = Path(__file__).parent
        else:
            base_path = Path.cwd()
        stretch_path = base_path / "stretchimage"
    
    debug_info.append(f"Base path: {base_path}")
    debug_info.append(f"Stretch path: {stretch_path}")
    debug_info.append(f"Stretch path exists: {stretch_path.exists()}")
    
    if stretch_path.exists():
        files = list(stretch_path.glob("*"))
        debug_info.append(f"Files in stretch folder: {len(files)}")
        for file in files:
            debug_info.append(f"  - {file.name}")
    
    return "\n".join(debug_info)

if __name__ == "__main__":
    with open("path_debug.txt", "w", encoding="utf-8") as f:
        f.write(debug_paths())
    print("Debug info written to path_debug.txt")