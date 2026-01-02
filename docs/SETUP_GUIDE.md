# 🎵 Next-Gen AI Audio Workstation - 설치 가이드

## 📦 패키지 내용

이 포터블 패키지에는 AI 기반 음원 분리 및 악보 생성을 위한 모든 도구가 포함되어 있습니다.

## ⚡ 빠른 시작

### 1단계: 초기 설치

```batch
setup.bat
```

**`setup.bat`** 를 더블클릭하여 실행하면:

- ✅ Python 가상환경 자동 생성
- ✅ 필수 AI 라이브러리 설치 (PyTorch, Demucs, TensorFlow 등)
- ✅ FFmpeg 자동 다운로드 및 설치
- ✅ LilyPond (악보 생성 엔진) 자동 다운로드
- ✅ GPU 인식 테스트 (선택 사항)

**소요 시간**: 약 5-10분 (인터넷 속도에 따라 다름)

### 2단계: 시스템 검증 (권장)

```batch
test_gpu.bat
```

설치가 완료되면 **`test_gpu.bat`**를 실행하여:

- 🔍 GPU/CUDA 인식 상태 확인
- 🔍 FFmpeg 작동 여부 확인
- 🔍 LilyPond 설치 확인
- 🔍 Dolby & Hi-Fi 오디오 효과 테스트
- 🔍 필수 라이브러리 점검

### 3단계: 프로그램 실행

```batch
run_gui.bat
```

**`run_gui.bat`**를 실행하면 GUI 프로그램이 시작됩니다!

## 🎯 주요 기능

### 🎚️ Standard Mixing (2-Stem)

- **보컬/반주 분리**: AI가 자동으로 보컬과 반주를 분리
- **장르별 프리셋**: YouTube, Pop, Rock, Ballad, R&B, HipHop, Trot 등
- **💎 Dolby Style**: 3D Surround + Crystalizer 효과
- **👑 Hi-Fi Mode**: 무손실 WAV 출력 + 고해상도 처리

### 🎸 Pro Extraction (6-Stem)

- **6개 채널 분리**: Vocals, Drums, Bass, Guitar, Piano, Others
- **Master Polish**: Vocal Air, Drum Punch, Deep Bass, Wall of Sound
- **MIDI 변환**: 각 악기를 MIDI 파일로 자동 변환
- **악보 생성**: PDF 형식의 밴드 스코어 자동 생성

## 💻 시스템 요구사항

### 필수 사항

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.10 이상
- **RAM**: 최소 8GB (16GB 권장)
- **저장 공간**: 최소 5GB

### 권장 사항 (GPU 가속)

- **GPU**: NVIDIA GPU (CUDA 지원)
- **VRAM**: 4GB 이상
- **드라이버**: 최신 NVIDIA 드라이버

> **💡 참고**: GPU가 없어도 CPU 모드로 작동합니다. (처리 속도가 느릴 수 있음)

## 문제 해결

### GPU가 인식되지 않습니다

1. NVIDIA 드라이버 최신 버전 설치: <https://www.nvidia.com/drivers>
2. `test_gpu.bat` 실행하여 상태 확인
3. PyTorch가 CUDA 버전으로 설치되었는지 확인

### FFmpeg 오류

1. `setup.bat` 다시 실행
2. 또는 수동으로 FFmpeg 다운로드: <https://ffmpeg.org>
3. `ffmpeg.exe`를 `ffmpeg` 폴더에 복사

### LilyPond 미설치

1. `setup.bat` 다시 실행 (자동 다운로드 시도)
2. 또는 수동 다운로드: <https://lilypond.org/download.html>
3. **참고**: 악보 생성 기능을 사용하지 않으면 필수 아님

### Dolby/Hi-Fi 효과가 작동하지 않습니다

- FFmpeg가 제대로 설치되지 않았을 수 있습니다
- `test_gpu.bat`의 "오디오 효과 테스트" 결과 확인
- FFmpeg를 재설치하세요

## 📂 출력 폴더 구조

처리가 완료되면 `output_result` 폴더에 다음과 같이 저장됩니다:

```
output_result/
└── [곡_제목]/
    ├── 음원분리/
    │   ├── [곡_제목]_[프리셋].mp3 (또는 .wav)
    │   ├── 6S_vocals_[곡_제목].wav
    │   ├── 6S_drums_[곡_제목].wav
    │   ├── 6S_bass_[곡_제목].wav
    │   ├── 6S_guitar_[곡_제목].wav
    │   ├── 6S_piano_[곡_제목].wav
    │   └── 6S_other_[곡_제목].wav
    └── 미디분리/
        ├── [곡_제목]_vocals.mid
        ├── [곡_제목]_drums.mid
        ├── [곡_제목]_bass.mid
        └── ... (기타 MIDI 파일)
```

## 🛠️ 고급 설정

### GPU 메모리 부족 시

- 2-Stem 모드 사용 (메모리 사용량이 적음)
- 다른 프로그램 종료
- Shift 값 줄이기 (코드 수정 필요)

### 처리 속도 향상

- GPU 사용 (NVIDIA GTX 1060 이상 권장)
- SSD 사용
- RAM 16GB 이상 사용

## 📞 지원

문의사항이나 버그 리포트는 개발자에게 문의하세요.

**Developed by Music Revolutionary JAESOO**

---

## 🔄 업데이트 이력

### v3.1 Pro

- ✨ GPU 자동 감지 및 가속
- ✨ Dolby Style & Hi-Fi Mode 추가
- ✨ 6-Stem 프로 믹싱 콘솔
- ✨ MIDI 자동 변환 및 악보 생성
- ✨ 통합 시스템 테스트 (`test_gpu.bat`)
- ✨ FFmpeg & LilyPond 자동 다운로드

---

**🎵 Enjoy Your Music Revolution! 🎵**
