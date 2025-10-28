#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스트레칭 이미지 기능 테스트
"""

import os
import glob
import random

class StretchImageManager:
    """스트레칭 이미지를 랜덤하게 관리하는 클래스"""
    def __init__(self, image_folder="stretchimage"):
        self.image_folder = image_folder
        self.image_history = []  # 최근 표시된 이미지 기록
        self.max_history = 5  # 최근 5개 이미지 기억
        self.available_images = self._load_available_images()
    
    def _load_available_images(self):
        """폴더 내의 모든 이미지 파일 로드"""
        try:
            if not os.path.exists(self.image_folder):
                print(f"❌ 스트레칭 이미지 폴더가 없습니다: {self.image_folder}")
                return []
            
            # 지원하는 이미지 확장자
            image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']
            images = []
            
            for ext in image_extensions:
                pattern = os.path.join(self.image_folder, ext)
                images.extend(glob.glob(pattern))
            
            print(f"✅ 스트레칭 이미지 {len(images)}개 발견")
            for img in images:
                print(f"   - {os.path.basename(img)}")
            return images
        except Exception as e:
            print(f"❌ 이미지 로드 오류: {e}")
            return []
    
    def get_random_image(self):
        """랜덤 이미지를 선택 (최근 이미지는 제외)"""
        if not self.available_images:
            print("❌ 사용 가능한 이미지가 없습니다.")
            return None
        
        # 이미지가 충분하지 않으면 히스토리 무시
        if len(self.available_images) <= self.max_history:
            selected = random.choice(self.available_images)
            print(f"📸 랜덤 선택 (히스토리 무시): {os.path.basename(selected)}")
            return selected
        
        # 히스토리에 없는 이미지 필터링
        available = [img for img in self.available_images if img not in self.image_history]
        
        # 모든 이미지가 히스토리에 있으면 히스토리 초기화
        if not available:
            print("🔄 히스토리 초기화")
            self.image_history.clear()
            available = self.available_images.copy()
        
        # 랜덤 선택
        selected = random.choice(available)
        
        # 히스토리 업데이트
        self.image_history.append(selected)
        if len(self.image_history) > self.max_history:
            self.image_history.pop(0)
        
        print(f"📸 랜덤 선택: {os.path.basename(selected)}")
        print(f"   히스토리: {[os.path.basename(h) for h in self.image_history]}")
        
        return selected

if __name__ == "__main__":
    print("=" * 60)
    print("스트레칭 이미지 매니저 테스트")
    print("=" * 60)
    
    # 이미지 매니저 생성
    manager = StretchImageManager()
    
    print("\n" + "=" * 60)
    print("10회 랜덤 이미지 선택 테스트")
    print("=" * 60)
    
    # 10번 랜덤 선택 테스트
    for i in range(10):
        print(f"\n[{i+1}회]")
        image = manager.get_random_image()
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
