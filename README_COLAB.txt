
[Google Colab 사용 가이드]

1. 폴더 업로드
   - 이 'colab_setup' 폴더를 통째로 Google Drive에 업로드하세요.
   - 예: '내 드라이브/music_ai' 폴더 안에 업로드

2. 노트북 열기
   - 구글 코랩(https://colab.research.google.com/)에 접속합니다.
   - '업로드' 탭을 선택하고 'Run_on_Colab.ipynb' 파일을 엽니다.
   - 또는 드라이브에서 'Run_on_Colab.ipynb' 우클릭 -> 연결 프로그램 -> Google Colaboratory 선택.

3. 실행 순서
   - 노트북의 상단 메뉴 [런타임] -> [런타임 유형 변경] -> 하드웨어 가속기 'GPU' 선택 (필수!)
   - 노트북의 셀을 순서대로 실행하세요 (Shift + Enter).
   - 1번부터 4번까지 실행하여 환경을 설정합니다.
   - 5번 셀을 실행하면 웹 UI(Gradio)가 실행됩니다.
   - "Running on public URL: https://....gradio.live" 링크를 클릭하세요.

4. 기능 사용
   - Voice Training: 목소리 녹음 파일들(ZIP)을 올리고 모델을 훈련합니다.
   - RVC Conversion: 훈련된 모델(.pth)로 목소리를 변환합니다.
   - Mixing: 보컬과 MR을 믹싱하고 효과를 적용합니다.

[주의사항]
- 구글 코랩 무료 버전은 사용 시간에 제한이 있습니다.
- 훈련 데이터는 너무 길지 않게(총 10~30분 내외) 준비하는 것이 좋습니다.
- GPU가 연결되지 않으면 훈련 속도가 매우 느립니다.
