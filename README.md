# 🎵 MusicSoundLevelUP (Version 2.3)
### Massive AI Audio Workstation (Hybrid Edition)
**Created by Music Revolutionary JAESOO (SKY Group)**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jaesooPark1972/MusicSoundLevelUP/blob/main/Run_on_Colab.ipynb)

본 프로젝트는 200페이지 분량, 1,200개 이상의 대규모 오디오 작업을 위해 설계된 전문가용 AI 워크스테이션입니다. 드라이브 경로에 상관없이 로컬 PC와 구글 코랩(Colab) 환경을 모두 지원합니다.

---

## 🚀 바로 시작하기 (One-Click Start)

### 1. Cloud 환경 (Google Colab)
위의 배지를 클릭하여 노트북을 열고 GPU 런타임에서 실행하세요.
*   **Fix**: `str object has no attribute 'name'` 에러가 수정된 최신 버전을 제공합니다.

### 2. Local PC 환경 (Windows)
*   **드라이브 독립성**: C:, D:, E: 등 어떤 드라이브에 설치해도 실행 파일 위치를 기준으로 가상환경(`venv`)을 자동 탐색합니다.
*   **GPU 가속**: NVIDIA CUDA를 자동으로 감지하여 AI 연산 속도를 극대화합니다.

---

## 💻 로컬 설치 및 실행 가이드

### STEP 1. 환경 구축
1. `start_station.bat`을 실행합니다.
2. **2번(설치/수리)** 메뉴를 선택하세요.
3. 이미 설치된 Python과 CUDA를 찾아 가상환경을 구성합니다.
   - *Tip: 부모 폴더에 venv가 있다면 자동으로 연동하여 중복 설치를 방지합니다.*

### STEP 2. 앱 실행
1. `start_station.bat`에서 **1번(실행)**을 선택하세요.
2. 자동으로 GPU 인식 여부를 체크하고 Gradio 웹 UI를 띄웁니다.
3. **Unicorn Studio 디자인**: UI 상단에 120% 확대된 화려한 비주얼이 적용되며, 하단 로고는 물리적으로 제거되어 더욱 전문적인 느낌을 줍니다.

---

## 📁 프로젝트 구조 (Folder Structure)

```text
MusicSoundLevelUP/
├── venv/                 # [자동탐색] 상위 또는 현재 폴더의 가상환경
└── colab_setup/          # 작업 메인 폴더
    ├── colab_app.py      # 메인 코드 (Gradio UI 및 경로 자동화 적용)
    ├── start_station.bat  # [최종] 드라이브 무관 통합 실행기
    ├── models/           # AI 음성 모델(.pth) 저장소
    ├── output/           # 최종 변환 결과물 저장소
    └── requirements.txt  # 필수 라이브러리 목록
```

---

## 🛠️ 주요 업데이트 사항 (v2.3)

1.  **지능형 경로 인식**: 드라이브 문자가 바뀌거나 폴더를 이동해도 `%~dp0` 기반의 상대 경로를 통해 부모 폴더의 `venv`를 정확히 찾아냅니다.
2.  **Gradio 4.x 완벽 대응**: 파일 업로드 시 발생하던 `'str' object has no attribute 'name'` 오류를 내부 로직 수정을 통해 완벽히 해결했습니다.
3.  **디자인 최적화**: Unicorn Studio 캔버스를 컨테이너보다 크게 설정(120% 확대)하여 워터마크 로고를 화면 밖으로 밀어냈습니다.
4.  **대규모 자동화 준비**: 1,200개 컷의 오버나이트 배치를 위한 파일명 규칙(`page_001_cut_01.wav`) 관리가 용이하도록 결과물 저장 로직을 개선했습니다.

---

## ⚠️ FAQ

**Q: 실행 시 검은 창에 'GPU 인식 실패'라고 뜹니다.**
*   NVIDIA 드라이버와 CUDA Toolkit(11.8 권장)이 설치되어 있는지 확인 후 2번 메뉴로 재설치하세요.

**Q: 상위 폴더의 venv를 인식하지 못합니다.**
*   `colab_setup` 폴더와 `venv` 폴더가 동일한 부모 폴더 안에 위치해 있는지 확인하세요.

---

**Repository**: [jaesooPark1972/MusicSoundLevelUP](https://github.com/jaesooPark1972/MusicSoundLevelUP)
**Author**: Park Jae-soo (SKY Group)
**Version**: 2.3 (Stable)
