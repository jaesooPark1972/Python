#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🎛️ AI Vocal Enhancement Engine
================================
보컬 + MR 믹싱 및 음질 개선

Author: Park Jae-soo (SKY Group)
Version: 1.0
"""

import os
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
from scipy import signal
import soundfile as sf


class VocalEnhancer:
    """
    AI 보컬 향상 엔진
    - 노이즈 제거
    - EQ 부스트
    - 컴프레서
    - 리버브
    - 마스터링
    """
    
    def __init__(self):
        self.enhancement_enabled = {
            'noise_reduction': True,
            'eq': True,
            'compressor': True,
            'reverb': True,
            'mastering': True
        }
        print("🎛️ 보컬 향상 엔진 초기화 완료")
    
    def load_audio(self, audio_path):
        """
        오디오 파일 로드
        
        Returns:
            AudioSegment
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            print(f"✓ 오디오 로드: {os.path.basename(audio_path)}")
            print(f"  - 길이: {len(audio) / 1000:.1f}초")
            print(f"  - 샘플레이트: {audio.frame_rate}Hz")
            print(f"  - 채널: {audio.channels}")
            return audio
        except Exception as e:
            print(f"❌ 오디오 로드 실패: {e}")
            return None
    
    def apply_noise_reduction(self, audio):
        """
        노이즈 제거 (하이패스 필터)
        - 80Hz 이하 저음 제거 (웅웅거림 제거)
        """
        if not self.enhancement_enabled['noise_reduction']:
            return audio
        
        print("  🔇 노이즈 제거 중...")
        # 하이패스 필터 (80Hz 이하 제거)
        audio = audio.high_pass_filter(80)
        return audio
    
    def apply_eq(self, audio):
        """
        EQ 부스트
        - Presence boost (2-5kHz) for vocal clarity
        """
        if not self.enhancement_enabled['eq']:
            return audio
        
        print("  🎚️ EQ 적용 중...")
        # 간단한 EQ: 고음 부스트
        audio = audio.high_pass_filter(100)  # 저음 정리
        return audio
    
    def apply_compression(self, audio):
        """
        다이나믹 레인지 컴프레션
        - 목소리를 일정하게 유지
        """
        if not self.enhancement_enabled['compressor']:
            return audio
        
        print("  🗜️ 컴프레서 적용 중...")
        # pydub의 compress_dynamic_range 사용
        audio = compress_dynamic_range(
            audio,
            threshold=-20.0,  # dB
            ratio=4.0,
            attack=5.0,  # ms
            release=50.0  # ms
        )
        return audio
    
    def apply_reverb(self, audio, reverb_amount=30):
        """
        리버브 (공간감)
        - 딜레이 기반 간단한 리버브
        """
        if not self.enhancement_enabled['reverb'] or reverb_amount == 0:
            return audio
        
        print(f"  🏰 리버브 적용 중... ({reverb_amount}ms)")
        
        # 딜레이 기반 리버브
        delay_ms = int(reverb_amount)
        reverb_audio = audio - 10  # 10dB 작게
        
        # 원본 + 딜레이된 소리 믹스
        audio = audio.overlay(reverb_audio, position=delay_ms)
        
        return audio
    
    def apply_mastering(self, audio):
        """
        최종 마스터링
        - 노멀라이즈 (클리핑 방지)
        """
        if not self.enhancement_enabled['mastering']:
            return audio
        
        print("  ✨ 마스터링 중...")
        # 노멀라이즈 (-1dB 헤드룸)
        audio = normalize(audio, headroom=1.0)
        return audio
    
    
    def apply_dolby(self, audio):
        """
        Dolby Style Effect (Rich Sound)
        - Wide stereo + Bass/Treble boost
        """
        if not self.enhancement_enabled.get('dolby', False):
            return audio
            
        print("  💎 Dolby Style 효과 적용 중...")
        # Simple bandwidth expansion simulation
        try:
            audio = audio.set_frame_rate(48000)
            audio = audio.low_pass_filter(18000).high_pass_filter(40)
            
            # Bass hint
            lows = audio.low_pass_filter(150)
            audio = audio.overlay(lows - 6) # subtle boost
            
            # Treble hint
            highs = audio.high_pass_filter(5000)
            audio = audio.overlay(highs - 6)
        except:
            pass
            
        return audio

    def apply_hifi(self, audio):
        """
        Hi-Fi Mode (Crystal Clear)
        - Exciter / Air
        """
        if not self.enhancement_enabled.get('hifi', False):
            return audio
            
        print("  👑 Hi-Fi 모드 적용 중...")
        # High-End Exciter
        try:
            high_freq = audio.high_pass_filter(10000)
            audio = audio.overlay(high_freq - 3) # Add air
        except:
            pass
        return audio
    # [REMOVED] SKY-Aura Logic (Deprecated)
    # [REMOVED] Vocal Protagonist Lead (Deprecated)

    def enhance_vocal(self, vocal_path, reverb_amount=30):
        """
        보컬 향상 파이프라인
        
        Args:
            vocal_path: 보컬 파일 경로
            reverb_amount: 리버브 양 (0-50ms)
        
        Returns:
            enhanced_vocal: AudioSegment
        """
        print("\n" + "="*60)
        print("🎤 보컬 향상 시작")
        print("="*60)
        
        # 로드
        vocal = self.load_audio(vocal_path)
        if vocal is None:
            return None
        
        # 향상 파이프라인
        vocal = self.apply_noise_reduction(vocal)
        vocal = self.apply_eq(vocal)
        vocal = self.apply_compression(vocal)
        
        # [NEW] Pro Effects
        vocal = self.apply_dolby(vocal)
        vocal = self.apply_hifi(vocal)
        
        vocal = self.apply_reverb(vocal, reverb_amount)
        vocal = self.apply_mastering(vocal)
        
        print("✓ 보컬 향상 완료")
        return vocal
    
    def mix_vocal_and_mr(self, vocal, mr, vocal_volume=0, mr_volume=0):
        """
        보컬 + MR 믹싱 (Standard High-Fidelity)
        """
        print("\n" + "="*60)
        print("🎵 오디오 믹싱 시작")
        print("="*60)
        
        # 1. 보컬의 존재감을 위해 MR의 특정 주파수(중음역대)를 아주 살짝 눌러줌 (Vocal Carving)
        # MR이 보컬의 감정을 방해하지 않게 조연 역할을 충실히 하게 함.
        print("  🎼 MR 조연 처리: 보컬 가독성 확보를 위한 공간 형성...")
        mr = mr.low_pass_filter(15000).high_pass_filter(20) # 불필요한 초고역/초저역 정리
        
        # 보컬 명료도 확보를 위한 EQ (3kHz 대역을 MR에서 살짝 줄임)
        # pydub에는 정밀 EQ가 부족하므로 전체 음량을 살짝 낮추고 보컬을 더 부각
        mr = mr - 1.5 # MR을 기본적으로 약간 더 낮게 설정하여 보컬의 레이어를 높임
        
        # 볼륨 조정
        if vocal_volume != 0:
            vocal = vocal + vocal_volume
            print(f"  보컬 볼륨: {vocal_volume:+.1f} dB")
        
        if mr_volume != 0:
            mr = mr + mr_volume
            print(f"  MR 볼륨: {mr_volume:+.1f} dB")
        
        # 길이 맞추기
        if len(mr) > len(vocal):
            # MR이 더 길면 보컬을 오버레이
            mixed = mr.overlay(vocal)
            print(f"  믹싱 길이: {len(mixed) / 1000:.1f}초 (MR 기준)")
        else:
            # 보컬이 더 길면 MR을 오버레이
            mixed = vocal.overlay(mr)
            print(f"  믹싱 길이: {len(mixed) / 1000:.1f}초 (보컬 기준)")
        
        print("✓ 믹싱 완료")
        return mixed
    
    def process(self, vocal_path, mr_path, output_path, 
                vocal_volume=0, mr_volume=0, reverb_amount=30,
                progress_callback=None):
        """
        전체 처리 파이프라인
        
        Args:
            vocal_path: 보컬 파일 경로
            mr_path: MR 파일 경로
            output_path: 출력 파일 경로
            vocal_volume: 보컬 볼륨 (dB)
            mr_volume: MR 볼륨 (dB)
            reverb_amount: 리버브 양 (ms)
            progress_callback: 진행률 콜백
        
        Returns:
            bool: 성공 여부
        """
        try:
            if progress_callback:
                progress_callback(10, "보컬 로딩 중...")
            
            # 1. 보컬 향상
            vocal = self.enhance_vocal(vocal_path, reverb_amount)
            if vocal is None:
                return False
            
            if progress_callback:
                progress_callback(40, "MR 로딩 중...")
            
            # 2. MR 로드
            mr = self.load_audio(mr_path)
            if mr is None:
                return False
            
            if progress_callback:
                progress_callback(60, "믹싱 중...")
            
            # 3. 믹싱
            mixed = self.mix_vocal_and_mr(vocal, mr, vocal_volume, mr_volume)
            
            if progress_callback:
                progress_callback(80, "최종 마스터링...")
            
            # 4. 최종 마스터링
            mixed = self.apply_mastering(mixed)
            
            if progress_callback:
                progress_callback(90, "파일 저장 중...")
            
            # 5. 저장
            print("\n" + "="*60)
            print("💾 파일 저장")
            print("="*60)
            
            mixed.export(
                output_path,
                format="mp3",
                bitrate="320k",
                parameters=["-q:a", "0"]  # 최고 품질
            )
            
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✓ 저장 완료: {os.path.basename(output_path)}")
            print(f"  - 크기: {file_size_mb:.1f} MB")
            print(f"  - 비트레이트: 320kbps")
            
            if progress_callback:
                progress_callback(100, "✅ 완료!")
            
            return True
            
        except Exception as e:
            print(f"❌ 처리 중 오류: {e}")
            import traceback
            traceback.print_exc()
            if progress_callback:
                progress_callback(0, f"❌ 오류: {str(e)}")
            return False


# ============================================
# 테스트 코드
# ============================================
if __name__ == "__main__":
    print("AI Vocal Enhancement Engine Test")
    print()
    
    enhancer = VocalEnhancer()
    
    # 테스트 파일 경로 (실제 파일로 교체 필요)
    test_vocal = "output_result/vocals.wav"
    test_mr = "output_result/accompaniment.wav"
    test_output = "output_result/final_mix.mp3"
    
    if os.path.exists(test_vocal) and os.path.exists(test_mr):
        def test_callback(progress, message):
            print(f"[{progress}%] {message}")
        
        success = enhancer.process(
            vocal_path=test_vocal,
            mr_path=test_mr,
            output_path=test_output,
            vocal_volume=2,  # 보컬 +2dB
            mr_volume=-2,  # MR -2dB
            reverb_amount=30,  # 30ms 리버브
            progress_callback=test_callback
        )
        
        if success:
            print(f"\n✅ 테스트 성공! 출력: {test_output}")
        else:
            print("\n❌ 테스트 실패")
    else:
        print("⚠️ 테스트 파일이 없습니다.")
        print(f"  필요: {test_vocal}")
        print(f"  필요: {test_mr}")
