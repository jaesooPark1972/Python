# 🏠 집에서 반드시 해야 할 작업 가이드 (TO-DO)

회장님, 현재 사무실 PC에서 GPU 및 악보 엔진 관련 핵심 오류 수정을 마쳤으나, **PyTorch(CUDA) 설치가 용량 문제로 지연**되었습니다. 집에 가셔서 아래 순서대로 실행하시면 모든 기능이 완벽하게 작동할 것입니다.

---

## 1. 🚀 필수 실행 패키지 (가장 먼저 수행)

가장 중요한 PyTorch CUDA 버전을 재설치해야 GPU가 인식됩니다. (사무실에서 공간 부족으로 중단된 작업)

1. **터미널(PowerShell)**을 열고 프로젝트 폴더(`d:\Music_Sound_Level_UP_setup`)로 이동합니다.
2. 아래 명령어를 **복사해서 붙여넣기** 하세요:

   ```powershell
   .venv\Scripts\pip.exe install torch==2.4.1 torchaudio==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall
   ```

   > [!IMPORTANT]
   > 설치 시 인터넷 속도에 따라 5~10분 정도 소요될 수 있습니다.

---

## 2. 🎼 악보 엔진(LilyPond) 최종 연결

LilyPond 경로는 이미 제가 코드와 설정을 수정해두었습니다.
