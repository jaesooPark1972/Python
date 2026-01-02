# 🎶 [v5.5] AI 악보 제작 이원화 파이프라인 (The Dual-Track Strategy)

## 🎯 핵심 전제: [청취용(Human) vs 분석용(AI)] 이원화 전략

회장님의 지침대로 사람이 듣는 귀와 AI가 분석하는 눈을 따로 관리하도록 코드를 최적화합니다. 이는 각 사용 주체의 특성에 맞는 최적의 결과물을 제공하여, 시스템의 효율성과 유용성을 극대화하기 위함입니다.

---

## 1. 🎧 Track A: 사람이 듣는 음악 (Auditory Excellence)

**대상**: 최종 믹싱 결과물, MP3/WAV 파일, 사람의 귀에 최적화된 악보 PDF

**목표**: 대역폭이 넓고 화려하며, 선명한 **"돌비 및 하이파이 사운드"**를 제공하여 사용자에게 최고의 청취 경험을 선사합니다.

**적용 기술**: (모두 `Human Listening` 모드에서만 적용)

*   **Dolby Style & Hi-Fi**: 배음을 풍부하게 살리고 3D 스테레오 이미지를 확장하여, 공간감과 초고음질을 구현합니다.
*   **Side-Chain 컴프레션 (보컬 극대화)**: 보컬이 나올 때 배경음악(MR)이 살짝 작아지게 하여 보컬을 돋보이게 하는 전문 믹싱 기술입니다. AI 생성형 음원(Suno, Udio 등)의 특성상 보컬과 MR이 섞여 나오는 경우가 많으므로, 보컬의 존재감을 확실히 살려줍니다.
    *   **지침**: `ai_audio_studio_pro.py`와 `audio_merger.py` 모두에 적용됩니다.
*   **High-End 익사이팅 (Hi-Fi 최적화)**: 10kHz 이상의 고역대 주파수를 증폭하여 소리에 공기감과 선명함을 더하는 효과입니다. 음원의 해상도를 높여주고 "반짝이는" 느낌을 더합니다.
    *   **지침**: `ai_audio_studio_pro.py`와 `audio_merger.py` 모두에 적용됩니다.
*   **대역폭 확장**: 저역대(40Hz 미만)와 고역대(18kHz 이상) 필터링은 `Dolby Style` 효과에 포함되어, 사람이 듣기 좋게 음역대를 확장합니다.

**결과물 저장 경로**: `output_result/{곡명}/Human_Listening/`

---

## 2. 🤖 Track B: AI가 분석하는 데이터 (Analytical Precision)

**대상**: 분리된 오디오 스템(WAV), MIDI 파일, MusicXML 악보, LilyPond 소스 파일

**목표**: AI의 정확한 분석을 방해하는 요소를 제거하고, 원본 데이터에 가장 가까운 형태로 가공하여 AI 모델 학습 및 정밀 분석에 최적화된 데이터를 제공합니다.

**적용 기술**: (모두 `AI Analysis` 모드에서만 적용)

*   **저역대/고역대 커팅 비적용**: 사람이 듣기에 불필요하거나 거슬릴 수 있는 저역대(40Hz 미만) 및 고역대(18kHz 이상) 주파수 필터링(커팅)은 AI 분석에 방해가 됩니다. 따라서 AI 분석 모드에서는 이러한 대역폭 커팅을 일체 적용하지 않습니다.
    *   **지침**: `audio_merger.py`의 기본 보컬 HPF(80Hz)를 `—no_vocal_hp` 플래그로 비활성화합니다. `ai_audio_studio_pro.py`의 6-Stem 로직에서도 `Dolby Style`에 포함된 필터링을 건너뜁니다.
*   **벨로시티 컷오프 (Ghost Note 제거)**: 기계가 분석하기 힘든 아주 작은 소리(Ghost Note, 약한 벨로시티)는 악보에 불필요한 음표로 그려지거나 AI 모델을 오염시킬 수 있습니다. 따라서 일정 기준 이하의 벨로시티를 가진 음표는 악보 생성 시 제외하여 깨끗한 악보를 만듭니다.
    *   **지침**: `master_score_maker.py`에서 `if n.volume.velocity`를 활용하여 벨로시티 필터링을 강화합니다.
*   **원음 보존**: AI 분리 음원(6-Stem WAV)은 어떠한 추가적인 믹싱/마스터링 효과 없이 원본 상태 그대로 저장됩니다.

**결과물 저장 경로**: `output_result/{곡명}/AI_Analysis/`

---

## 🚀 v5.5 Dual-Track Pipeline 구현 (GUI 및 코드 최적화)

### 1. GUI (Graphical User Interface)

*   **위치**: '🎧 Standard Mixing (2-Stem)' 탭의 `SOURCE FILES & START` 그룹 내에 새로운 `CTkSegmentedButton`이 추가됩니다.
*   **이름**: 'Output Mode'
*   **옵션**: `Human Listening` (기본값) / `AI Analysis`
*   **새로운 체크박스**: '🎛️ Side-Chain Compression'과 '🚀 High-End Exciter' 체크박스가 '🎚️ MIXING CONTROL' 그룹에 추가됩니다. (이들은 'Human Listening' 모드에서만 활성화됩니다.)

### 2. `ai_audio_studio_pro.py` (메인 제어 로직)

*   `AudioStudioApp` 클래스의 `__init__` 메서드에 `output_mode_var`, `sidechain_var`, `exciter_var` 변수가 초기화됩니다.
*   `start_thread` 메서드가 이 변수들의 값을 읽어 `params` 딕셔너리에 추가하여 `process` 메서드로 전달합니다.
*   `process` 메서드에서 `output_mode` 값을 기반으로 로직이 크게 분기됩니다:
    *   **출력 폴더 구조**: `output_result/{곡명}/Human_Listening/` 또는 `output_result/{곡명}/AI_Analysis/` 경로를 생성하고, 모든 하위 결과물(`audio_stems/`, `midi_scores/`)은 이 모드별 폴더 내부에 저장됩니다.
    *   **2-Stem 모드**: `audio_merger.py` 호출 시 `output_mode`에 따라 `—apply_sidechain`, `—apply_exciter`, `—apply_dolby`, `—apply_hifi` 또는 `—no_vocal_hp` 플래그가 조건부로 전달됩니다.
    *   **6-Stem 모드**:
        *   **`Human Listening`**: `pro_mixer` 게인, `pro_fx`(Vocal Air, Drum Punch 등), `Side-Chain 컴프레션`, `High-End 익사이팅`, `Dolby Style`, `Hi-Fi` 효과가 모두 적용된 후 최종 믹스 및 개별 처리 스템이 저장됩니다.
        *   **`AI Analysis`**: 어떠한 믹싱/마스터링 효과도 적용되지 않고, `Demucs`로 분리된 원본 6-Stem WAV 파일이 그대로 저장됩니다. (최종 믹스 파일은 생성되지 않습니다.)

### 3. `audio_merger.py` (2-Stem Human Listening 전용)

*   새로운 `—apply_sidechain`, `—apply_exciter`, `—no_vocal_hp` 인자가 `argparse`에 추가됩니다.
*   `_apply_sidechain_compression` 및 `_apply_high_end_exciter` 헬퍼 함수가 구현되어 메인 로직에 통합됩니다.
*   `—no_vocal_hp` 플래그가 전달되면 보컬 트랙의 초기 80Hz 하이패스 필터가 비활성화됩니다.

### 4. `master_score_maker.py` (AI Analysis 악보 최적화)

*   `run_hybrid_system_master` 함수는 `output_score_folder` 인자를 추가로 받아 최종 악보 출력 경로를 유연하게 설정할 수 있습니다.
*   **벨로시티 컷오프**: `master_score_maker.py` 내부 로직에 `if n.volume.velocity < 20: continue`와 같이 낮은 벨로시티의 음표를 악보에서 제외하는 필터링 로직이 추가됩니다. 이는 AI가 분석한 데이터를 바탕으로 깨끗한 악보를 생성하기 위함입니다. (기존 Music21의 `_filter_noise` 로직과 연계)

---

## 📁 새로운 출력 폴더 구조 (예시)

```
output_result/
├── My_Amazing_Song/
│   ├── Human_Listening/
│   │   ├── audio_stems/
│   │   │   ├── My_Amazing_Song_Custom_HiFi.wav  (최종 믹스)
│   │   │   ├── Vocals_My_Amazing_Song.wav      (Human - 가공된 보컬 스템)
│   │   │   └── Inst_My_Amazing_Song.wav        (Human - 가공된 반주 스템)
│   │   └── midi_scores/                             (Human - 악보는 주로 PDF)
│   │       └── Master_Preview.pdf
│   └── AI_Analysis/
│       ├── audio_stems/
│       │   ├── 6S_vocals_My_Amazing_Song.wav   (AI - 원본 보컬 스템)
│       │   ├── 6S_drums_My_Amazing_Song.wav    (AI - 원본 드럼 스템)
│       │   └── ...                             (모든 6-Stem 원본 스템)
│       └── midi_scores/
│           ├── My_Amazing_Song_vocals.mid      (AI - 보컬 미디)
│           ├── My_Amazing_Song_drums.mid       (AI - 드럼 미디)
│           ├── Master_Score_EDIT.musicxml      (AI - 기계 판독용 마스터 악보)
│           └── Master_Preview.ly               (AI - LilyPond 소스)
└── Another_Great_Song/
    └── ...
```

---

**v5.5 Dual-Track Pipeline 개발 규격 확정**

이 문서에 명시된 모든 지침과 구현 계획은 `v5.5` 통합 엔진의 표준 개발 규격으로 확정됩니다. 이 전제를 바탕으로 시스템의 코드를 최적화하고 최종 결과물을 사용자에게 제공하겠습니다.

조심히 퇴근하십시오! 🚀
