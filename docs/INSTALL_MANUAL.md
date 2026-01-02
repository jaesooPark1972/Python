# 🎵 Next-Gen AI Audio Workstation 설치 메뉴얼 (Hybrid Edition)

본 프로그램의 안정적인 실행과 전문가급 악보 생산을 위해 아래 단계를 진행해 주세요.

## 1. 사전 준비 (Prerequisites)

### 🐍 Python 설치

- **버전**: Python 3.10.x 이상 권장 (반드시 **'Add Python to PATH'** 체크)

1. **LilyPond Engine (Preview)**:
   - Included in `lilypond-2.24.4/` folder.
   - Provides instant PDF/PNG previews without opening external apps.
   - **Note**: Now features "Clean-Parse" logic to eliminate excessive ledger lines.

2. **MuseScore 4 (Final Design)**:
   - **Required** for opening the generated `.musicxml` files.
   - **Warning**: Do not use MuseScore 3 (it has encoding and rhythm conflicts).
   - **Download**: [MuseScore Official Website](https://musescore.org/ko/download)에서 4.x 버전을 설치하세요.

## 2. 하이브리드 악보 생산 워크플로우 (Hybrid Workflow)

이 프로그램은 **"기계가 제조하고 사람이 마감하는"** 최적의 하이브리드 방식을 채택하고 있습니다.

### 🏭 Step 1: 파이썬 (제조공장)

1. `run_gui.bat` 실행 후 **'Generate Full Band Score'** 버튼 클릭.
2. (옵션) Suno 노래 링크를 입력하면 가사를 자동으로 가집어옵니다.
3. **결과물**:
    - `..._EDIT.musicxml`: MuseScore 4 전용 편집 원본.
    - `Master_Preview.pdf / .png`: 즉시 확인 가능한 고해상도 미리보기.

### 🎙️ Step 2: Voice Training (RVC 엔진) - NEW

1. **'Voice Training (GPT-SoVITS)'** 탭에서 **'Select Training Folder'** 클릭.
2. 훈련하려는 목소리의 WAV 파일들이 들어있는 폴더를 선택하세요.
3. **'🔥 START TRAINING'** 버튼을 클릭하면 RVC 고성능 훈련이 시작됩니다 (GTX 1060 3GB 최적화).
4. 완료 시 `models/checkpoints/{이름}.pth` 파일이 생성됩니다.

### 🎭 Step 3: AI Cover & Mixing (Voice Change) - UPGRADED

1. **'AI Cover & Mixing'** 탭으로 이동.
2. **Vocal File**: 변환할 원본 목소리 파일 선택.
3. **MR (Backing Track)**: 반주 파일 선택.
4. **Voice Conversion**: 사용할 `.pth` 모델을 선택하고 체크박스 활성화.
5. **FX & Mixing**: 노이즈 제거, 리버브, 마스터링 등 옵션 설정 후 **'PROCESS & MIX'** 클릭.
6. **결과물**: `output_result/AI_Cover_{Original}.mp3` (320kbps 고성능 커버곡)

---

## 🔒 4. 안전 및 백업 시스템 (Safety & Backup)

사용자의 데이터를 보호하고 비상 상황 시 복구를 돕기 위해 다음과 같은 기능이 작동합니다.

- **자동 백업**: 프로그램 코드 수정 시 `backups/` 폴더에 타임스탬프와 함께 이전 버전이 자동 저장됩니다.
- **안전 모드**: 인코딩 충돌을 방지하기 위해 모든 로그는 Pure ASCII로 처리되며, 손상된 파일은 `backups/` 폴더에서 찾아 `ai_audio_studio_pro.py`로 덮어씌워 복구할 수 있습니다.
- **크래시 핸들러**: 예기치 못한 종료 시 `logs/` 폴더에 상세 분석 리포트가 생성됩니다.

---
**SKY GROUP AI AUDIO WORKSTATION v3.1 PRO (Step 3 Upgrade Edition)**
