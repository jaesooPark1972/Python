@echo off
:: 한글 인코딩 설정 및 현재 경로 강제 고정 (드라이브 무관)
chcp 65001 > nul
setlocal
cd /d "%~dp0"

:: [상대 경로 설정] 부모(..) 및 현재(.) 폴더의 venv 경로 탐색
set "PARENT_VENV=..\venv\Scripts\activate.bat"
set "LOCAL_VENV=.\venv\Scripts\activate.bat"

:main_menu
cls
echo ======================================================
echo    MusicSoundLevelUP 통합 워크스테이션 (드라이브 무관)
echo ======================================================
echo  현재 위치: %cd%
echo ======================================================
echo  1. [실행] AI 워크스테이션 시작 (로컬 GPU/CUDA 사용)
echo  2. [설치/수리] 가상환경(venv) 및 라이브러리 구축
echo  3. [도움말] 구글 코랩(Colab) 가이드 열기
echo  4. 프로그램 종료
echo ======================================================
set /p choice="번호를 입력하세요 (1-4): "

if "%choice%"=="1" goto check_venv
if "%choice%"=="2" goto install_env
if "%choice%"=="3" goto run_colab
if "%choice%"=="4" exit
goto main_menu

:check_venv
cls
echo [정보] 가상환경(venv) 탐색 중...
:: 상위 폴더 venv 우선 확인
if exist "%PARENT_VENV%" (
    echo [확인] 상위 폴더의 venv를 발견했습니다. 연동합니다.
    call "%PARENT_VENV%"
    goto start_app
)
:: 현재 폴더 venv 확인
if exist "%LOCAL_VENV%" (
    echo [확인] 현재 폴더의 venv를 발견했습니다. 연동합니다.
    call "%LOCAL_VENV%"
    goto start_app
)
echo [알림] venv를 찾을 수 없습니다. 2번 메뉴를 통해 설치를 진행해 주세요.
pause
goto main_menu

:start_app
cls
echo [정보] GPU 및 CUDA 환경 체크 중...
:: CUDA 인식 성공 여부 확인 [cite: 14]
python -c "import torch; print('✓ NVIDIA GPU(CUDA) 인식 성공' if torch.cuda.is_available() else '⚠️ CPU 모드 실행')"
echo [진행] 앱을 실행합니다. 잠시만 기다려 주세요... [cite: 15]
python colab_app.py
pause
goto main_menu

:install_env
cls
echo [설치] 현재 폴더에 가상환경을 구성합니다. [cite: 16]
if not exist "venv" (
    python -m venv venv
)
call .\venv\Scripts\activate
echo [진행] 필수 라이브러리 및 CUDA 전용 Torch 설치 중...
pip install --upgrade pip
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
echo [완료] 모든 라이브러리 구성이 완료되었습니다! [cite: 17]
pause
goto main_menu

:run_colab
start https://colab.research.google.com/
goto main_menu