# -*- coding: utf-8 -*-
"""
Next-Gen AI Audio Workstation - 시스템 통합 테스트
GPU, FFmpeg, LilyPond 등 모든 필수 도구의 설치 및 작동 여부를 검증합니다.
"""

import sys
import os
import subprocess
import tempfile

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_system_resources():
    """시스템 자원(RAM, 디스크 공간) 확인"""
    print_section("0️⃣  시스템 자원 확인")
    
    import shutil
    try:
        import psutil
    except ImportError:
        return False
    
    # 디스크 공간 확인 (현재 폴더 기준)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    total, used, free = shutil.disk_usage(base_dir)
    free_gb = free / (1024**3)
    print(f"{'[OK]' if free_gb > 10 else '[WARNING]'} 여유 디스크 공간: {free_gb:.2f} GB")
    if free_gb < 10:
        print("   [TIP] 모델 다운로드를 위해 최소 10GB 이상의 여유 공간을 권장합니다.")
    
    # 시스템 메모리 확인
    mem = psutil.virtual_memory()
    mem_total_gb = mem.total / (1024**3)
    print(f"{'[OK]' if mem_total_gb > 8 else '[WARNING]'} 시스템 메모리 (RAM): {mem_total_gb:.2f} GB")
    if mem_total_gb < 8:
        print("   [TIP] 대형 AI 모델 처리를 위해 최소 8GB 이상의 RAM을 권장합니다.")
    
    return free_gb > 5 and mem_total_gb > 4


def test_pytorch_cuda():
    """PyTorch 및 CUDA 테스트"""
    print_section("1. PyTorch 및 CUDA 테스트")
    
    try:
        import torch
        print(f"[OK] PyTorch 버전: {torch.__version__}")
        
        # CUDA 사용 가능 여부
        cuda_available = torch.cuda.is_available()
        print(f"\n{'[OK]' if cuda_available else '[WARNING]'} CUDA 사용 가능: {cuda_available}")
        
        if cuda_available:
            # GPU 정보 출력
            gpu_count = torch.cuda.device_count()
            print(f"[OK] 감지된 GPU 개수: {gpu_count}")
            
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_capability = torch.cuda.get_device_capability(i)
                print(f"\n   GPU {i}:")
                print(f"      이름: {gpu_name}")
                print(f"      CUDA Capability: {gpu_capability[0]}.{gpu_capability[1]}")
                
                # GPU 메모리 정보
                try:
                    mem_total = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                    print(f"      총 메모리: {mem_total:.2f} GB")
                except:
                    print("   [INFO] GPU 메모리 정보를 가져올 수 없습니다.")
            
            # 실제 연산 스트레스 테스트
            print("\n[TEST] GPU 가속 성능 테스트 중 (AI 모델 로드 시뮬레이션)...")
            try:
                # 큰 행렬 연산으로 실제 GPU 동작 확인
                size = 4000
                x = torch.randn(size, size, device='cuda')
                y = torch.randn(size, size, device='cuda')
                
                # 시간 측정
                start_event = torch.cuda.Event(enable_timing=True)
                end_event = torch.cuda.Event(enable_timing=True)
                
                start_event.record()
                z = torch.matmul(x, y)
                end_event.record()
                
                torch.cuda.synchronize()
                elapsed_ms = start_event.elapsed_time(end_event)
                
                print(f"[OK] 성능 테스트 완료: {elapsed_ms:.2f} ms")
                
                allocated = torch.cuda.memory_allocated(0) / (1024**2)
                print(f"   현재 사용 중인 VRAM: {allocated:.2f} MB")
                print("[SUCCESS] GPU 가속이 정상 작동합니다!")
                return True
            except Exception as e:
                print(f"[ERROR] GPU 연산 중 오류 발생: {e}")
                print("   [TIP] 드라이버나 CUDA 환경을 다시 확인해 주세요.")
                return False
        else:
            print("\n[WARNING] CUDA를 사용할 수 없습니다.")
            print("\n가능한 원인:")
            print("   1. NVIDIA GPU가 설치되어 있지 않음")
            print("   2. NVIDIA 드라이버가 설치되어 있지 않음")
            print("   3. PyTorch가 CPU 버전으로 설치됨")
            print("\n해결 방법:")
            print("   - NVIDIA 드라이버 설치: https://www.nvidia.com/drivers")
            print("\n[TIP] CPU 모드로도 작동하지만 속도가 느릴 수 있습니다.")
            return False
            
    except ImportError as e:
        if "DLL load failed" in str(e):
            print("\n" + "!"*70)
            print("[ERROR] PyTorch Import Error: DLL load failed")
            print("!"*70)
            print("\n원인: Windows용 Visual C++ Redistributable이 설치되어 있지 않습니다.")
            print("\n해결 방법:")
            print("1. 아래 링크에서 최신 VC++ Redistributable을 다운로드하여 설치하세요:")
            print("   👉 https://aka.ms/vs/17/release/vc_redist.x64.exe")
            print("\n2. [중요] 설치 완료 후 반드시 '컴퓨터 다시 시작(재부팅)'을 해주세요.")
            print("   - 재부팅을 하지 않으면 윈도우가 설치된 라이브러리를 인식하지 못합니다.")
            print("\n3. 재부팅 후 다시 실행해 주세요.")
            print("!"*70 + "\n")
        else:
            print(f"[ERROR] PyTorch를 찾을 수 없습니다: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] PyTorch 테스트 중 오류 발생: {e}")
        return False

def test_tensorflow():
    """TensorFlow GPU 테스트"""
    print_section("2. TensorFlow GPU 테스트")
    
    try:
        import tensorflow as tf
        print(f"[OK] TensorFlow 버전: {tf.__version__}")
        
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"[OK] TensorFlow가 감지한 GPU: {len(gpus)}개")
            for gpu in gpus:
                print(f"   - {gpu.name}")
            return True
        else:
            print("[WARNING] TensorFlow가 GPU를 감지하지 못했습니다.")
            print("   (basic-pitch 악보 생성 시 CPU 사용)")
            return False
    except ImportError:
        print("[WARNING] TensorFlow가 설치되어 있지 않습니다.")
        return False
    except Exception as e:
        print(f"[ERROR] TensorFlow 확인 중 오류: {e}")
        return False

def test_nvidia_driver():
    """NVIDIA 드라이버 테스트"""
    print_section("3. NVIDIA 드라이버 정보")
    
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ nvidia-smi 실행 성공:")
            # 출력 내용 중 중요한 부분만 표시
            lines = result.stdout.split('\n')
            for line in lines[:15]:  # 상위 15줄만 표시
                print(f"   {line}")
            return True
        else:
            print("❌ nvidia-smi 실행 실패")
            return False
    except FileNotFoundError:
        print("⚠️  nvidia-smi를 찾을 수 없습니다.")
        print("   NVIDIA 드라이버가 설치되어 있지 않거나 PATH에 없습니다.")
        return False
    except Exception as e:
        print(f"❌ nvidia-smi 실행 중 오류: {e}")
        return False

def test_ffmpeg():
    """FFmpeg 설치 및 작동 테스트"""
    print_section("4️⃣  FFmpeg 테스트")
    
    # 현재 디렉토리 기준으로 ffmpeg 찾기
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_paths = [
        os.path.join(base_dir, "ffmpeg", "ffmpeg.exe"),
        os.path.join(base_dir, "ffmpeg.exe"),
        "ffmpeg"  # PATH에서 찾기
    ]
    
    ffmpeg_found = None
    for path in ffmpeg_paths:
        try:
            result = subprocess.run([path, '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                ffmpeg_found = path
                break
        except:
            continue
    
    if ffmpeg_found:
        print(f"✅ FFmpeg 발견: {ffmpeg_found}")
        # 버전 정보 추출
        try:
            result = subprocess.run([ffmpeg_found, '-version'], capture_output=True, text=True, timeout=5)
            version_line = result.stdout.split('\n')[0]
            print(f"   {version_line}")
            
            # 간단한 변환 테스트
            print("\n✅ FFmpeg 변환 테스트 중...")
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                test_output = tmp.name
            
            # 1초짜리 무음 파일 생성 테스트
            cmd = [ffmpeg_found, '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', 
                   '-t', '1', '-y', test_output]
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(test_output):
                print("✅ FFmpeg 변환 테스트 성공!")
                os.remove(test_output)
                return True
            else:
                print("⚠️  FFmpeg 변환 테스트 실패")
                return False
        except Exception as e:
            print(f"⚠️  FFmpeg 테스트 중 오류: {e}")
            return False
    else:
        print("❌ FFmpeg를 찾을 수 없습니다.")
        print("\n해결 방법:")
        print("   1. setup.bat를 다시 실행하여 자동 다운로드")
        print("   2. 수동 다운로드: https://ffmpeg.org")
        print("   3. ffmpeg.exe를 'ffmpeg' 폴더에 복사")
        return False

def test_lilypond():
    """LilyPond 설치 및 작동 테스트"""
    print_section("5️⃣  LilyPond 테스트 (악보 생성 엔진)")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    lilypond_paths = [
        os.path.join(base_dir, "lilypond-2.24.4", "bin", "lilypond.exe"),
        r"C:\lilypond-2.24.4\bin\lilypond.exe",
        "lilypond"  # PATH에서 찾기
    ]
    
    lilypond_found = None
    for path in lilypond_paths:
        if os.path.exists(path) or path == "lilypond":
            try:
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lilypond_found = path
                    break
            except:
                continue
    
    if lilypond_found:
        print(f"✅ LilyPond 발견: {lilypond_found}")
        try:
            result = subprocess.run([lilypond_found, '--version'], capture_output=True, text=True, timeout=5)
            version_line = result.stdout.split('\n')[0]
            print(f"   {version_line}")
            
            # 간단한 악보 생성 테스트
            print("\n✅ LilyPond 악보 생성 테스트 중...")
            
            # 임시 .ly 파일 생성
            test_ly_content = r'''
\version "2.24.0"
\score {
  \new Staff {
    \clef treble
    \time 4/4
    c'4 d' e' f' g'1
  }
  \layout { }
}
'''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ly', delete=False, encoding='utf-8') as tmp:
                tmp.write(test_ly_content)
                test_ly_file = tmp.name
            
            try:
                # PDF 생성 시도
                result = subprocess.run([lilypond_found, '-o', tempfile.gettempdir(), test_ly_file], 
                                      capture_output=True, timeout=30)
                
                # 생성된 PDF 파일 확인
                pdf_file = test_ly_file.replace('.ly', '.pdf')
                
                if result.returncode == 0:
                    print("✅ LilyPond 악보 생성 테스트 성공!")
                    # 테스트 파일들 정리
                    try:
                        os.remove(test_ly_file)
                        if os.path.exists(pdf_file):
                            os.remove(pdf_file)
                    except:
                        pass
                    return True
                else:
                    print("⚠️  LilyPond 실행은 되지만 악보 생성 실패")
                    print(f"   Error: {result.stderr[:200]}")
                    return False
            except subprocess.TimeoutExpired:
                print("⚠️  LilyPond 실행 시간 초과")
                return False
            except Exception as e:
                print(f"⚠️  LilyPond 테스트 중 오류: {e}")
                return False
            finally:
                # 정리
                try:
                    if os.path.exists(test_ly_file):
                        os.remove(test_ly_file)
                except:
                    pass
        except Exception as e:
            print(f"⚠️  LilyPond 버전 확인 중 오류: {e}")
            return False
    else:
        print("❌ LilyPond를 찾을 수 없습니다.")
        print("\n해결 방법:")
        print("   1. setup.bat를 다시 실행하여 자동 다운로드")
        print("   2. 수동 다운로드: https://lilypond.org/download.html")
        print("\n💡 LilyPond가 없어도 음원 분리는 가능하지만,")
        print("   악보(PDF) 생성 기능은 사용할 수 없습니다.")
        return False

def test_essential_libraries():
    """필수 라이브러리 테스트"""
    print_section("6️⃣  필수 Python 라이브러리 테스트")
    
    libraries = {
        'demucs': 'Demucs (AI 음원 분리)',
        'librosa': 'Librosa (오디오 분석)',
        'basic_pitch': 'Basic Pitch (MIDI 변환)',
        'music21': 'Music21 (악보 처리)',
        'customtkinter': 'CustomTkinter (GUI)',
        'pydub': 'Pydub (오디오 편집)',
        'gradio': 'Gradio (웹 인터페이스)'
    }
    
    results = {}
    for lib, description in libraries.items():
        try:
            __import__(lib)
            print(f"✅ {description}")
            results[lib] = True
        except ImportError:
            print(f"❌ {description} - 설치되지 않음")
            results[lib] = False
    
    return all(results.values())

def test_audio_effects():
    """Dolby & Hi-Fi 오디오 효과 테스트"""
    print_section("7️⃣  오디오 효과 테스트 (Dolby & Hi-Fi)")
    
    # FFmpeg 찾기
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_paths = [
        os.path.join(base_dir, "ffmpeg", "ffmpeg.exe"),
        os.path.join(base_dir, "ffmpeg.exe"),
        "ffmpeg"
    ]
    
    ffmpeg_exe = None
    for path in ffmpeg_paths:
        try:
            result = subprocess.run([path, '-version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                ffmpeg_exe = path
                break
        except:
            continue
    
    if not ffmpeg_exe:
        print("⚠️  FFmpeg를 찾을 수 없어 효과 테스트를 건너뜁니다.")
        return False
    
    # 테스트용 무음 오디오 생성 (1초)
    print("   테스트용 오디오 생성 중...")
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_input:
        input_file = tmp_input.name
    
    cmd_gen = [
        ffmpeg_exe, '-f', 'lavfi', '-i', 'sine=frequency=440:duration=1',
        '-ar', '44100', '-ac', '2', '-y', input_file
    ]
    
    try:
        subprocess.run(cmd_gen, capture_output=True, timeout=10, check=True)
    except:
        print("   ⚠️  테스트 파일 생성 실패")
        return False
    
    # Dolby 효과 테스트
    print("   [1/2] Dolby Style 테스트...")
    with tempfile.NamedTemporaryFile(suffix='_dolby.wav', delete=False) as tmp_dolby:
        output_dolby = tmp_dolby.name
    
    dolby_filter = "stereotools=mlev=1:slev=1.4,bass=g=3:f=100,treble=g=3:f=10000"
    cmd_dolby = [ffmpeg_exe, '-i', input_file, '-af', dolby_filter, '-y', output_dolby]
    
    dolby_ok = False
    try:
        result = subprocess.run(cmd_dolby, capture_output=True, timeout=10)
        if result.returncode == 0 and os.path.exists(output_dolby) and os.path.getsize(output_dolby) > 1000:
            print("   ✅ Dolby Style 효과 정상 작동")
            dolby_ok = True
        else:
            print("   ⚠️  Dolby Style 효과 적용 실패")
    except:
        print("   ⚠️  Dolby Style 테스트 중 오류")
    finally:
        try:
            if os.path.exists(output_dolby):
                os.remove(output_dolby)
        except:
            pass
    
    # Hi-Fi 효과 테스트
    print("   [2/2] Hi-Fi Mode 테스트...")
    with tempfile.NamedTemporaryFile(suffix='_hifi.wav', delete=False) as tmp_hifi:
        output_hifi = tmp_hifi.name
    
    hifi_filter = "treble=g=4:f=14000"
    cmd_hifi = [ffmpeg_exe, '-i', input_file, '-af', hifi_filter, '-y', output_hifi]
    
    hifi_ok = False
    try:
        result = subprocess.run(cmd_hifi, capture_output=True, timeout=10)
        if result.returncode == 0 and os.path.exists(output_hifi) and os.path.getsize(output_hifi) > 1000:
            print("   ✅ Hi-Fi Mode 효과 정상 작동")
            hifi_ok = True
        else:
            print("   ⚠️  Hi-Fi Mode 효과 적용 실패")
    except:
        print("   ⚠️  Hi-Fi Mode 테스트 중 오류")
    finally:
        try:
            if os.path.exists(output_hifi):
                os.remove(output_hifi)
        except:
            pass
    
    # 정리
    try:
        if os.path.exists(input_file):
            os.remove(input_file)
    except:
        pass
    
    if dolby_ok and hifi_ok:
        print("\n✅ 모든 오디오 효과가 정상 작동합니다!")
        return True
    else:
        print("\n⚠️  일부 오디오 효과가 작동하지 않습니다.")
        print("   (음원 분리는 가능하지만 고급 효과가 제한될 수 있습니다)")
        return False

def main():
    print("="*70)
    print("  🎵 AI Audio Workstation - Professional System Readiness Check")
    print("="*70)
    print("\n최적의 AI 경험을 위해 환경을 정밀 분석합니다...\n")
    
    # psutil이 필요한 경우를 위해 설치 확인
    try:
        import psutil
    except ImportError:
        print("   📦 시스템 파라미터 분석을 위한 모듈(psutil) 설치 중...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil", "--quiet"])
        import psutil

    results = {
        'Resources': test_system_resources(),
        'PyTorch/CUDA': test_pytorch_cuda(),
        'TensorFlow': test_tensorflow(),
        'NVIDIA Driver': test_nvidia_driver(),
        'FFmpeg': test_ffmpeg(),
        'LilyPond': test_lilypond(),
        'Libraries': test_essential_libraries(),
        'Audio Effects': test_audio_effects()
    }
    
    # 최종 결과 요약
    print_section("📊 최종 테스트 결과")
    
    print("\n핵심 기능:")
    print(f"  {'✅' if results['PyTorch/CUDA'] else '⚠️ '} AI 음원 분리 (GPU 가속): {'사용 가능' if results['PyTorch/CUDA'] else 'CPU 모드'}")
    print(f"  {'✅' if results['FFmpeg'] else '❌'} 오디오 변환: {'정상' if results['FFmpeg'] else '설치 필요'}")
    print(f"  {'✅' if results['Audio Effects'] else '⚠️ '} 오디오 효과 (Dolby/Hi-Fi): {'사용 가능' if results['Audio Effects'] else '일부 제한'}")
    print(f"  {'✅' if results['LilyPond'] else '⚠️ '} 악보 생성: {'사용 가능' if results['LilyPond'] else '선택 기능'}")
    print(f"  {'✅' if results['Libraries'] else '❌'} Python 라이브러리: {'모두 설치됨' if results['Libraries'] else '일부 누락'}")
    
    print("\n추가 정보:")
    if results['PyTorch/CUDA']:
        print("  🚀 GPU 가속이 활성화되어 최고 성능으로 작동합니다!")
    else:
        print("  💡 CPU 모드로 작동합니다. GPU가 있다면 드라이버를 확인하세요.")
    
    if not results['FFmpeg']:
        print("  ⚠️  FFmpeg가 필요합니다. setup.bat를 다시 실행하세요.")
    
    if not results['Audio Effects']:
        print("  💡 Dolby/Hi-Fi 효과가 제한됩니다. FFmpeg 필터를 확인하세요.")
    
    if not results['LilyPond']:
        print("  💡 LilyPond는 선택 사항입니다. 악보가 필요하면 설치하세요.")
    
    # 전체 성공 여부
    critical_tests = ['PyTorch/CUDA', 'FFmpeg', 'Libraries']
    all_critical_passed = all(results.get(test, False) or test == 'PyTorch/CUDA' for test in critical_tests)
    
    print("\n" + "="*70)
    if results['FFmpeg'] and results['Libraries']:
        print("  ✅ 시스템이 정상적으로 작동할 준비가 되었습니다!")
        print("  👉 'run_gui.bat'를 실행하여 프로그램을 시작하세요.")
    else:
        print("  ⚠️  일부 구성 요소가 누락되었습니다.")
        print("  👉 setup.bat를 다시 실행하거나 수동으로 설치하세요.")
    print("="*70)
    
    return all_critical_passed

if __name__ == "__main__":
    try:
        success = main()
        print("\n")
        input("아무 키나 눌러 종료...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        input("\n아무 키나 눌러 종료...")
        sys.exit(1)
