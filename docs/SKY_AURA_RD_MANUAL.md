# 🧪 SKY Audio Studio: 연구개발(R&D) 핵심 기술 매뉴얼

## 1. 개요
본 매뉴얼은 SKY Audio Studio의 독자적인 오디오 처리 엔진인 **SKY-Aura** 및 **SKY-Protagonist** 기술의 핵심 이론과 구현 방식을 정의합니다. 본 기술들은 오디오를 단순한 파형이 아닌 '성분'과 '위계'로 분석하여 최상의 음악적 결과물을 만드는 것을 목표로 합니다.

---

## 2. SKY-Aura: 신경망 기반 오디오 DNA 정제 (Neural Purification)

### 2.1 핵심 철학: DNA 기반 분리
*   **배경**: 기존의 오디오 분리는 주파수 대역을 단순히 나누는 방식이었으나, SKY-Aura는 목소리의 DNA(음색, 발음, 피치, 에너지)를 분석하여 다른 악기 성분과 완벽히 격리합니다.
*   **기술명**: SKY-Aura (정제) / SKY-Titan (분리)

### 2.2 주요 기능
1.  **Aura Deep Clean (고순도 정제)**:
    *   `librosa` 및 신경망 기반 노이즈 제거 알고리즘을 사용하여 목소리 외의 모든 불필요 성분을 제거.
    *   RVC 학습 전 데이터 정제에 최적화되어, AI가 잡음을 음색으로 오해하는 현상을 원천 차단.
2.  **Titan Separator (HTDemucs v4)**:
    *   Hybrid Transformer를 사용한 6-Stem 분리로 보컬, 드럼, 베이스, 기타, 피아노, 기타 악기를 고해상도로 추출.
3.  **Aura Resonance (AI Super-Resolution)**:
    *   고주파 대역(10kHz 이상)의 손실된 성분을 AI로 예측하여 복원함으로써 소리에 '공기감(Air)'과 '생동감'을 부여.

---

## 3. SKY-Protagonist: 보컬 주연 중심 위계 믹싱

### 3.1 핵심 철학: 보컬은 주연, MR은 조연
*   **배경**: 노래는 인간의 감정(기쁨, 슬픔, 분노, 슬픔 등)을 전달하는 예술이며, 그 감정의 90%는 목소리에 담겨 있습니다. 따라서 보컬과 MR은 같은 급의 레이어가 아니며, 보컬이 모든 악기 위에서 곡을 지휘해야 합니다.

### 3.2 구현 전략
1.  **Emotional Frequency Boost (감정 대역 강화)**:
    *   인간의 감정이 가장 밀도 있게 표현되는 **2kHz ~ 5kHz 대역**을 정밀 타격하여 강화.
    *   음색의 떨림과 미세한 감정 표현(Vibrato)이 악기에 묻히지 않게 함.
2.  **Vocal Carving (조연의 미덕)**:
    *   보컬의 주파수 자리를 확보하기 위해 MR의 중음역대를 미세하게 깎아냄(Side-chain EQ 효과).
    *   MR은 보컬을 받쳐주는 완벽한 배경막 역할을 수행.
3.  **Harmonic Soul Layering (배음 적층)**:
    *   목소리의 배음 구조를 분석하여 '두툼한' 질감을 형성. 목소리가 반주 위에서 겉돌지 않고 입체적으로 자리 잡게 함.

---

## 4. 참조 코드 구조
*   `sky_aura_engine.py`: 정제 및 분리 원천 기술.
*   `vocal_enhancer.py`: Protagonist 믹싱 및 레이어링 로직 탑재.
*   `ai_audio_studio_pro.py`: 전체 엔진 제어 및 UI 인터페이스.

---

## 5. 향후 연구 과제
*   목소리의 감정 상태를 자동 감지하여 리버브/컴프레서 값을 초정밀 튜닝하는 'Auto-Emotion Mixing'.
*   성도의 길이를 조절하는 Formant Shifting을 통한 실시간 디에이징 기술 고도화.

---
**작성일**: 2025년 12월 25일
**책임 연구원**: Music Revolutionary JAESOO (SKY Group)
