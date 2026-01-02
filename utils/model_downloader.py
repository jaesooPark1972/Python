#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
📡 RVC 필수 모델 자동 다운로더
==============================
HuBERT, Pretrained G/D 모델 자동 다운로드

Author: Park Jae-soo (SKY Group)
Version: 1.0
"""

import os
import requests
from tqdm import tqdm

class ModelDownloader:
    """
    RVC 필수 모델 자동 다운로더
    - hubert_base.pt (~360MB)
    - Pretrained G/D models (~50MB each)
    """
    
    def __init__(self):
        self.base_url = "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/"
        self.assets_dir = "assets"
        
        # 필요한 폴더 생성
        os.makedirs(os.path.join(self.assets_dir, "hubert"), exist_ok=True)
        os.makedirs(os.path.join(self.assets_dir, "pretrained_v2"), exist_ok=True)
        
        print("📡 모델 다운로더 초기화 완료")
    
    def download_file(self, url, save_path, progress_callback=None):
        """
        파일 다운로드 및 진행률 표시
        
        Args:
            url: 다운로드 URL
            save_path: 저장 경로
            progress_callback: GUI 진행률 콜백 함수(percent)
        """
        if os.path.exists(save_path):
            file_size_mb = os.path.getsize(save_path) / (1024 * 1024)
            print(f"✅ 이미 존재: {os.path.basename(save_path)} ({file_size_mb:.1f} MB)")
            return True
        
        print(f"⬇️ 다운로드 시작: {os.path.basename(save_path)}")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            total_size_mb = total_size / (1024 * 1024)
            
            print(f"   크기: {total_size_mb:.1f} MB")
            
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 진행률 업데이트
                        if progress_callback and total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            progress_callback(percent)
                        
                        # 콘솔 진행률
                        if total_size > 0 and downloaded % (1024 * 1024 * 10) == 0:  # 10MB마다
                            percent = (downloaded / total_size) * 100
                            print(f"   진행: {percent:.1f}% ({downloaded / (1024*1024):.1f}/{total_size_mb:.1f} MB)")
            
            print(f"✨ 다운로드 완료: {os.path.basename(save_path)}")
            return True
            
        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)  # 깨진 파일 삭제
            return False
    
    def check_and_download_all(self, gui_callback=None):
        """
        모든 필수 모델 확인 및 다운로드
        
        Returns:
            bool: 모든 모델이 준비되었는지 여부
        """
        print("=" * 60)
        print("🔍 RVC 필수 모델 확인 중...")
        print("=" * 60)
        
        models_to_download = [
            {
                'name': 'HuBERT Base',
                'url': self.base_url + "hubert_base.pt",
                'path': os.path.join(self.assets_dir, "hubert", "hubert_base.pt"),
                'description': '음성 특징 추출기 (~360MB)'
            },
            {
                'name': 'Pretrained Generator (40k)',
                'url': self.base_url + "pretrained_v2/f0G40k.pth",
                'path': os.path.join(self.assets_dir, "pretrained_v2", "f0G40k.pth"),
                'description': '사전 훈련된 생성기 (~50MB)'
            },
            {
                'name': 'Pretrained Discriminator (40k)',
                'url': self.base_url + "pretrained_v2/f0D40k.pth",
                'path': os.path.join(self.assets_dir, "pretrained_v2", "f0D40k.pth"),
                'description': '사전 훈련된 판별기 (~50MB)'
            }
        ]
        
        all_success = True
        
        for i, model_info in enumerate(models_to_download, 1):
            print(f"\n[{i}/{len(models_to_download)}] {model_info['name']}")
            print(f"    {model_info['description']}")
            
            success = self.download_file(
                model_info['url'],
                model_info['path'],
                gui_callback
            )
            
            if not success:
                all_success = False
                print(f"⚠️ {model_info['name']} 다운로드 실패")
        
        print("\n" + "=" * 60)
        if all_success:
            print("✅ 모든 모델 준비 완료!")
            print("=" * 60)
        else:
            print("❌ 일부 모델 다운로드 실패")
            print("   인터넷 연결을 확인하고 다시 시도해주세요.")
            print("=" * 60)
        
        return all_success
    
    def get_model_paths(self):
        """
        다운로드된 모델 경로 반환
        
        Returns:
            dict: 모델 경로 딕셔너리
        """
        return {
            'hubert': os.path.join(self.assets_dir, "hubert", "hubert_base.pt"),
            'pretrained_G': os.path.join(self.assets_dir, "pretrained_v2", "f0G40k.pth"),
            'pretrained_D': os.path.join(self.assets_dir, "pretrained_v2", "f0D40k.pth")
        }
    
    def verify_models(self):
        """
        모든 모델이 존재하는지 확인
        
        Returns:
            bool: 모든 모델 존재 여부
        """
        paths = self.get_model_paths()
        
        for name, path in paths.items():
            if not os.path.exists(path):
                print(f"❌ 누락: {name} ({path})")
                return False
        
        print("✅ 모든 모델 파일 확인됨")
        return True


# ============================================
# 테스트 코드
# ============================================
if __name__ == "__main__":
    print("RVC 모델 다운로더 테스트")
    print()
    
    downloader = ModelDownloader()
    
    # 모델 다운로드
    success = downloader.check_and_download_all()
    
    if success:
        print("\n📊 다운로드된 모델 정보:")
        paths = downloader.get_model_paths()
        
        for name, path in paths.items():
            if os.path.exists(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                print(f"  - {name}: {size_mb:.1f} MB")
        
        print("\n🎉 모델 준비 완료! 이제 훈련을 시작할 수 있습니다.")
    else:
        print("\n⚠️ 모델 다운로드 실패. 다시 시도해주세요.")
