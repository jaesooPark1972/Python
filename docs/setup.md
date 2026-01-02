# 🎵 Next-Gen AI Audio Workstation - 설치 및 사용 가이드

## 1. 소개
이 프로그램은 최신 AI 기술을 활용하여 음악에서 목소리, 드럼, 베이스, 기타, 피아노 등을 분리하고, 이를 바탕으로 악보를 생성하거나 다른 목소리로 변환(AI 커버)할 수 있는 통합 오디오 워크스테이션입니다.

## 2. 설치 방법 (One-Click Setup)

가장 간편한 설치 방법을 제공합니다.

1.  **`setup.bat`** 파일을 더블 클릭하세요.
2.  검은색 창이 열리고 자동으로 다음 작업이 진행됩니다:
    *   Python 가상환경 생성
    *   필수 AI 라이브러리(PyTorch, Demucs 등) 설치
    *   FFmpeg (오디오 변환 도구) 자동 다운로드 및 설정
    *   LilyPond (악보 생성 엔진) 확인 및 설치
    *   필수 폴더 구조 생성
3.  "Setup Complete!" 메시지가 나오면 창을 닫으셔도 됩니다.

## 3. 실행 방법

1.  **`run_gui.bat`** 파일을 더블 클릭하세요.
2.  잠시 후 프로그램 메인 화면이 실행됩니다.

---

## 4. 주요 기능 상세 가이드

### 🎧 1. Standard Mixing (2-Stem)
보컬과 반주(MR)를 빠르고 깔끔하게 분리합니다.
*   **사용법**: 오디오 파일을 드래그하여 넣고 'Start Processing'을 누르세요.
*   **기능**:
    *   **Dolby Style**: 입체감 있는 사운드로 변환합니다.
    *   **Hi-Fi Mode**: 고음질로 업스케일링합니다.

### 🎸 2. Pro Extraction (6-Stem & Score)
전문가를 위한 기능으로, 6가지 악기(보컬, 드럼, 베이스, 기타, 피아노, 기타)로 분리하고 악보를 만듭니다.
*   **사용법**: 파일을 선택하고 'Generate Full Band Score'를 클릭하세요.
*   **결과물**:
    *   각 악기별 분리된 오디오 파일 (.wav)
    *   각 악기별 MIDI 파일 (.mid)
    *   **악보 파일 (PDF & PNG)**: `output_result` 폴더 내에 생성됩니다.

### 🎙️ 3. Voice Training & Covering
나만의 AI 목소리 모델을 만들거나, 기존 노래를 다른 목소리로 바꿉니다.
*   **Voice Training**: 내 목소리 녹음 파일(WAV) 폴더를 선택하여 학습시킵니다.
*   **AI Cover**: 분리된 보컬 파일과 학습된 모델(.pth)을 선택하여 목소리를 변환합니다.

---

## 5. 문제 해결 (Troubleshooting)

### Q: 설치 중 빨간색 에러가 뜹니다.
*   인터넷 연결을 확인하세요 (대용량 AI 모델을 다운로드합니다).
*   Visual C++ Redistributable이 없으면 에러가 날 수 있습니다. [여기](https://aka.ms/vs/17/release/vc_redist.x64.exe)에서 다운로드하여 설치하고 재부팅하세요.

### Q: 악보가 생성되지 않습니다.
*   LilyPond가 설치되지 않았을 수 있습니다. `setup.bat`를 다시 실행하거나 [LilyPond 공식 홈페이지](https://lilypond.org/download.html)에서 직접 설치하세요.
*   기본 경로: `C:\lilypond-2.24.4\bin` 또는 프로그램 폴더 내 `lilypond-2.24.4`

### Q: 실행 속도가 너무 느립니다.
*   이 프로그램은 NVIDIA GPU(그래픽카드)가 있으면 훨씬 빠릅니다.
*   GPU가 없다면 CPU 모드로 작동하며, 속도가 느릴 수 있습니다.

---
**Developed by Music Revolutionary JAESOO**
