# -*- coding: utf-8 -*-
import os
import sys

# [CRITICAL FIX] DLL 로딩 문제 해결을 위한 환경 변수 설정
# PyTorch와 다른 라이브러리들의 DLL 경로를 명시적으로 추가
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 경우
    base_dir = os.path.dirname(sys.executable)
else:
    # 개발 환경
    base_dir = os.path.dirname(os.path.abspath(__file__))

# [MODULAR] 모듈 로딩을 위해 core 및 utils 폴더를 시스템 경로에 추가
sys.path.append(os.path.join(base_dir, 'core'))
sys.path.append(os.path.join(base_dir, 'utils'))

# DLL 검색 경로에 venv의 DLL들을 추가
venv_dir = os.path.join(base_dir, ".venv")
if os.path.exists(venv_dir):
    dll_paths = [
        os.path.join(venv_dir, "Lib", "site-packages", "torch", "lib"),
        os.path.join(venv_dir, "Scripts"),
        os.path.join(venv_dir, "Library", "bin"),
    ]
    
    # PATH에 추가
    for dll_path in dll_paths:
        if os.path.exists(dll_path):
            os.environ["PATH"] = dll_path + os.pathsep + os.environ.get("PATH", "")
    
    # Windows DLL 검색 경로에도 추가 (Python 3.8+)
    if hasattr(os, 'add_dll_directory'):
        for dll_path in dll_paths:
            if os.path.exists(dll_path):
                try:
                    os.add_dll_directory(dll_path)
                except:
                    pass

# 기본 imports
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import random
import shutil
import re
import subprocess
import requests

# PyTorch import with better error handling
try:
    import torch
    import torchaudio
except ImportError as e:
    error_msg = f"""
PyTorch Import Error: {e}

해결 방법:
1. Visual C++ Redistributable 설치
   https://aka.ms/vs/17/release/vc_redist.x64.exe
   
2. PyTorch 재설치:
   pip uninstall torch torchaudio
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

3. 시스템 재부팅 후 재시도
"""
    print(error_msg)
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    tk.messagebox.showerror("PyTorch Error", error_msg)
    sys.exit(1)
except Exception as e:
    error_msg = f"""
PyTorch DLL Loading Error: {e}

이것은 보통 다음 중 하나가 원인입니다:
1. Visual C++ Redistributable 미설치
2. GPU 드라이버가 오래됨
3. CUDA 라이브러리 충돌

해결:
1. Visual C++ Redistributable 최신 버전 설치
2. NVIDIA 드라이버 업데이트
3. 시스템 재부팅
"""
    print(error_msg)
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    tk.messagebox.showerror("DLL Loading Error", error_msg)
    sys.exit(1)

import webbrowser # [NEW] 링크 열기용

# basic-pitch imports for Phase 2 (Localized inside methods)
BASIC_PITCH_AVAILABLE = True # Assume available, handle errors during local import
from pydub import AudioSegment, effects
import numpy as np
import ctypes
import io

# [NEW] Chord Remover for Voice Training
from chord_remover import ChordRemover

# [NEW] Voice Training Engine
from voice_trainer import RealVoiceTrainer
from training_scripts import TRAINING_SCRIPTS

# [NEW] Official RVC Engine Integration
try:
    from official_rvc_converter import OfficialRVCConverter
except ImportError:
    OfficialRVCConverter = None

# [윈도우 작업 표시줄 아이콘 분리 설정]
try:
    myappid = 'nextgenaudioworkstation.gui.pro.v3.1' # 임의의 고유 식별자
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# =================================================================
# 디자인 설정 (LUXURY DARK & GOLD)
# =================================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#050505"
COLOR_FRAME_BG = "#1A1A1A"
COLOR_GOLD = "#D4AF37"
COLOR_GOLD_DIM = "#8A7129"
COLOR_TEXT = "#F0F0F0"
COLOR_TEXT_DIM = "#AAAAAA"

# 폰트 설정
# 폰트 설정 (가독성 UP: 크고 굵은 폰트 적용)
FONT_TITLE = ("Arial Black", 30)
FONT_SUBTITLE = ("Malgun Gothic", 14, "bold")
FONT_BOLD = ("Malgun Gothic", 16, "bold")   # Presets 등 주요 헤더
FONT_NORMAL = ("Malgun Gothic", 14, "bold") # 일반 텍스트도 선명하게
FONT_SMALL = ("Malgun Gothic", 12)

# =================================================================
# 환경 설정
# =================================================================
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# [기본 경로 설정] 실행 파일 또는 스크립트 위치 기준
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# [ffmpeg 설정]
# 우선순위: 1. ffmpeg 폴더 내부, 2. 루트 폴더
if os.path.exists(os.path.join(base_dir, "ffmpeg", "ffmpeg.exe")):
    ffmpeg_exe = os.path.join(base_dir, "ffmpeg", "ffmpeg.exe")
    ffprobe_exe = os.path.join(base_dir, "ffmpeg", "ffprobe.exe")
else:
    ffmpeg_exe = os.path.join(base_dir, "ffmpeg.exe")
    ffprobe_exe = os.path.join(base_dir, "ffprobe.exe")

if os.path.exists(ffmpeg_exe):
    # PATH에 추가 (다른 라이브러리 지원용)
    os.environ["PATH"] = base_dir + os.pathsep + os.environ.get("PATH", "")
    # pydub 명시적 설정
    AudioSegment.converter = ffmpeg_exe
    AudioSegment.ffmpeg = ffmpeg_exe
    AudioSegment.ffprobe = ffprobe_exe

# [폴더 경로 설정] 절대 경로 사용
# [수정] WinError 32 (PermissionError) 방지를 위해 TEMP 환경변수를 강제로 변경하지 않습니다.
# 대신 프로그램 내부에서 사용하는 임시 폴더만 별도로 관리합니다.
# temp_base = os.path.join(base_dir, "temp_base")
# os.makedirs(temp_base, exist_ok=True)
# os.environ['TEMP'] = os.environ['TMP'] = os.environ['TMPDIR'] = temp_base

OUTPUT_DIR = os.path.join(base_dir, "output_result")
TEMP_DIR = os.path.join(base_dir, "temp_work")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

def clean_name(name):
    # [수정] 한글 및 공백 등을 보존하면서 윈도우 예약 문자만 제거
    name = os.path.splitext(os.path.basename(name))[0]
    # 윈도우에서 금지된 문자들: \ / : * ? " < > |
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    # 양끝 공백 제거 및 마침표 제거 (시스템 예약어 방지용)
    return name.strip().rstrip('.') or "song"

def separate(file_path, use_gpu, mode, progress_callback):
    """
    Demucs AI 분리 실행 (실시간 진행률 파싱 포함)
    """
    model_name = "htdemucs_ft" if mode == "2-Stem" else "htdemucs_6s"
    str_mode = "Standard 2-Stem" if mode == "2-Stem" else "Pro 6-Stem"
    
    progress_callback(f"AI Engine Starting... ({mode})", 0.05)
    
    progress_callback(f"AI Engine Starting... ({mode})", 0.05)
    
    # [수정] 실행 환경에 따른 명령어 분기 처리 (Frozen vs Script)
    if getattr(sys, 'frozen', False):
        # ■ EXE 배포 상태: 별도로 빌드된 'demucs_runner.exe'를 호출
        executable_dir = os.path.dirname(sys.executable)
        runner_path = os.path.join(executable_dir, "demucs_runner.exe")
        
        # 만약 runner가 없으면 내부(_internal)에 있을 수도 있음 (onedir 구조에 따라 다름)
        if not os.path.exists(runner_path):
             runner_path = os.path.join(sys._MEIPASS, "demucs_runner.exe") if hasattr(sys, '_MEIPASS') else runner_path
             
        # [추가] 여전히 못찾으면 현재 작업 디렉토리에서도 확인
        if not os.path.exists(runner_path):
            runner_path = os.path.join(os.getcwd(), "demucs_runner.exe")
             
        cmd = [runner_path, "-n", model_name, "--shifts=2", "--overlap=0.25", "--mp3-bitrate", "320", "--out", TEMP_DIR, file_path]
    else:
        # ■ 개발/스크립트 상태: 'python -m demucs' 사용
        cmd = [sys.executable, "-m", "demucs", "-n", model_name, "--shifts=2", "--overlap=0.25", "--mp3-bitrate", "320", "--out", TEMP_DIR, file_path]
    
    # [중요] 2-Stem 모드일 때만 반주를 하나로 뭉침 (no_vocals 생성)
    if "2-Stem" in str_mode or mode == "2-Stem":
        cmd.append("--two-stems=vocals")
    
    if use_gpu:
        cmd.append("-d")
        cmd.append("cuda")
    else:
        cmd.append("-d")
        cmd.append("cpu")
        
    # 콘솔 창 숨기기 설정
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    # [FIX] torchcodec 이슈 해결을 위한 환경 변수 설정
    env = os.environ.copy()
    env["TORCHAUDIO_BACKEND"] = "soundfile"
    
    # [핵심] 실시간 로그 캡처
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True, 
        encoding='utf-8', 
        errors='replace',
        startupinfo=startupinfo,
        env=env,
        bufsize=1,
        universal_newlines=True
    )
    
    # 진행률 파싱용 정규식
    progress_pattern = re.compile(r"(\d+)%")
    
    error_logs = [] # 에러 내용 수집
    
    while True:
        output = process.stderr.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            if "Error" in output or "Traceback" in output or "out of memory" in output:
                error_logs.append(output.strip())
                
            match = progress_pattern.search(output)
            if match:
                percent = int(match.group(1))
                normalized_p = 0.1 + (percent * 0.8 / 100)
                progress_callback(f"Analyzing... {percent}%", normalized_p)

    process.wait()

    if process.returncode != 0:
        err_msg = "\n".join(error_logs[-5:])
        raise Exception(f"AI 엔진 오류 발생 (코드 {process.returncode}):\n{err_msg}")

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    # AI 결과는 이제 TEMP_DIR 안에 있음
    target_dir = os.path.join(TEMP_DIR, model_name)
    expected_path = os.path.join(target_dir, base_name)
    
    final_path = expected_path

    # [강력한 폴더 찾기 로직]
    if os.path.exists(expected_path):
        final_path = expected_path
    else:
        if os.path.exists(target_dir):
            try:
                subdirs = [os.path.join(target_dir, d) for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
                if subdirs:
                    latest_folder = max(subdirs, key=os.path.getmtime)
                    final_path = latest_folder
            except: pass

    # [최종 검증]
    check_file = "vocals.wav" if mode == "2-Stem" else "drums.wav"
    if not os.path.exists(os.path.join(final_path, check_file)):
         raise Exception(f"결과 파일을 찾을 수 없습니다.\n경로: {final_path}")
    
    return final_path, model_name


class GlassFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=15, border_width=1, border_color=COLOR_GOLD_DIM,
                         fg_color=COLOR_FRAME_BG, **kwargs)

class AudioStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NEXT-GEN AI AUDIO - Music Revolutionary JAESOO (GPU Accelerated)")
        
        # [화면 맞춤 1단계] 기본 크기 설정
        self.geometry("1000x750")
        
        # [화면 맞춤 2단계] 시작 시 자동 최대화 (Windows 전용)
        try:
            self.state("zoomed")
        except:
            pass
            
        self.configure(fg_color=COLOR_BG)
        self.title("NEXT-GEN AI AUDIO v3.1 Pro - JAESOO")
        self.geometry("1400x980") # [수정] 박재수 님 요청: 모든 버튼이 시원하게 보이도록 높이 복구
        self.configure(bg="black")
        
        # [NEW] 아이콘 설정 (윈도우 타이틀바 & 작업 표시줄)
        icon_path = os.path.join(base_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Icon Error: {e}")
        
        self.resizable(True, True) # [수정] 창 크기 조절 허용
        self.file_path = None
        self.effect_path = None
        self.is_processing = False
        self.slider_labels = {} 
        self.sliders = {}
        self.current_preset = "Manual"  # 프리셋 이름 저장 변수 추가
        self.midi_vars = {} # [NEW] 각 줄기별 MIDI 추출 여부 저장
        self.active_midi_tasks = set() # [NEW] 현재 변환 중인 트랙 추적 (중복 방지)
        self.status_glow_step = 0 # [NEW] 상태바 애니메이션용
        
        # [NEW] Voice Training Tab Variables
        self.training_files = []  # 훈련용 오디오 파일 목록
        self.chord_remover = ChordRemover()  # 코드 제거 엔진
        self.cleaned_lyrics = ""  # 정제된 가사 저장
        self.is_training = False  # 훈련 진행 중 플래그
        
        # [NEW] Official RVC Initializer
        if OfficialRVCConverter:
            self.official_rvc = OfficialRVCConverter()
        else:
            self.official_rvc = None
            print("WARNING: RVC library not found.")
        
        # [NEW] 상단 파형 애니메이션용 고정 데이터 생성
        import random
        self.waveform_data = [random.randint(5, 25) for _ in range(250)]

        self.setup_ui()
        
        # [GPU 감지] UI 로딩 후 0.5초 뒤에 체크 (정확도 향상)
        self.after(500, self.check_gpu_status)

    def check_gpu_status(self):
        try:
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                self.gpu_status_lbl.configure(text=f"⚡ SYSTEM: {gpu_name} (GPU MODE)", text_color="#00FF00")
                self.gpu_var.set(True)
            else:
                self.gpu_status_lbl.configure(text="⚠️ SYSTEM: GPU NOT FOUND (CPU MODE)", text_color="#FF5555")
                self.gpu_var.set(False)
        except:
             self.gpu_status_lbl.configure(text="⚠️ SYSTEM: CHECK FAILED", text_color="gray")
    
        # [FIX] UI 애니메이션 트리거 (GPU 체크 직후 실행)
        self.after(100, self.draw_initial_waveform)
        self.after(200, self.animate_status)
        self.after(300, self.animate_wave)

    def setup_ui(self):
        # 전체 컨테이너 (좌우 여백 확대)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=40, pady=(10, 5))
        
        # 1. 헤더 (여백 축소)
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # 메인 타이틀 변경
        ctk.CTkLabel(header_frame, text="NEXT-GEN AI AUDIO", font=FONT_TITLE, text_color="white").pack(side="left")
        ctk.CTkLabel(header_frame, text="WORKSTATION", font=FONT_TITLE, text_color=COLOR_GOLD).pack(side="left", padx=(5,0))
        
        # [REVISED] GPU Status & Toggle on the extreme right
        gpu_control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        gpu_control_frame.pack(side="right", padx=10)

        # [REVISED] Author moved NEXT to GPU status for collective branding
        self.author_lbl = ctk.CTkLabel(gpu_control_frame, text="Music Revolutionary JAESOO", 
                                       font=("Arial", 10, "italic"), text_color="#888")
        self.author_lbl.pack(side="top", anchor="e")

        self.gpu_status_lbl = ctk.CTkLabel(gpu_control_frame, text="Checking System...", font=("Arial", 11, "bold"))
        self.gpu_status_lbl.pack(side="top", anchor="e")

        self.gpu_var = ctk.BooleanVar(value=True)
        self.gpu_chk = ctk.CTkCheckBox(gpu_control_frame, text="⚡ GPU ACCELERATION", variable=self.gpu_var, 
                                       font=("Arial", 9, "bold"), fg_color=COLOR_GOLD, hover_color=COLOR_GOLD,
                                       text_color=COLOR_GOLD_DIM, width=20, height=20)
        self.gpu_chk.pack(side="top", pady=(2, 0), anchor="e")

        # [NEW] System Diagnosis Button
        self.diag_btn = ctk.CTkButton(gpu_control_frame, text="🔍 DIAGNOSIS", width=80, height=22, 
                                      font=("Arial", 8, "bold"), fg_color="#333", border_width=1, border_color="#555",
                                      command=self.run_system_diagnosis)
        self.diag_btn.pack(side="top", pady=(5, 0), anchor="e")

        # 2. 파형 (높이 100 -> 70으로 축소)
        self.viz_frame = GlassFrame(self.main_container, height=70)
        self.viz_frame.pack(fill="x", pady=(0, 15))
        self.viz_canvas = tk.Canvas(self.viz_frame, bg=COLOR_FRAME_BG, height=70, highlightthickness=0)
        self.viz_canvas.pack(fill="both", expand=True, padx=2, pady=2)
        self.draw_initial_waveform(0)
        
        # [UPLIFTED] 4. 상태 표시 및 프로그레스 (파형 바로 아래로 이동하여 가시성 극대화)
        self.footer = ctk.CTkFrame(self.main_container, fg_color="#121212", corner_radius=12, border_width=1, border_color="#333")
        self.footer.pack(fill="x", pady=(0, 10))
        
        self.status_lbl = ctk.CTkLabel(self.footer, text="Ready for Project", font=("Arial", 13, "bold"), text_color=COLOR_GOLD)
        self.status_lbl.pack(anchor="w", padx=20, pady=(10, 0))

        self.progress = ctk.CTkProgressBar(self.footer, height=16, progress_color=COLOR_GOLD, fg_color="#222", corner_radius=8)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=20, pady=(6, 15))
        self.animate_status()

        # 3. 중앙 콘텐츠 (Tabview 도입 - 탭 버튼 크기 확대)
        self.tabview = ctk.CTkTabview(self.main_container, fg_color=COLOR_FRAME_BG, segmented_button_fg_color="#222", 
                                      segmented_button_selected_color=COLOR_GOLD, segmented_button_selected_hover_color="#D4AF37",
                                      segmented_button_unselected_hover_color="#333", text_color="white",
                                      height=50)  # 탭 버튼 높이 증가
        self.tabview.pack(fill="both", expand=True, pady=(0, 10))
        
        # 탭 버튼 폰트 크기 증가
        self.tabview._segmented_button.configure(font=("Arial", 14, "bold"))
        
        self.tab_mix = self.tabview.add("🎧 Standard Mixing (2-Stem)")
        self.tab_pro = self.tabview.add("🎸 Pro Extraction (6-Stem)")
        self.tab_voice = self.tabview.add("🎙️ Voice Training (GPT-SoVITS)")  # [NEW] 음성 훈련 탭
        self.tab_rvc = self.tabview.add("🎤 AI Cover & Mixing (RVC)")
        
        self.setup_standard_mix_tab()
        self.setup_pro_extraction_tab()
        self.setup_voice_training_tab()
        self.setup_rvc_tab()

    def setup_standard_mix_tab(self):
        """Standard Mixing (2-Stem) 탭 UI 구성"""
        self.tab_mix.grid_columnconfigure(0, weight=4)
        self.tab_mix.grid_columnconfigure(1, weight=6)

        # Tab 1 - 왼쪽 (파일 + 믹싱)
        mix_left = ctk.CTkFrame(self.tab_mix, fg_color="transparent")
        mix_left.grid(row=0, column=0, sticky="nsew", padx=(10, 15), pady=10)

        files_group = GlassFrame(mix_left)
        files_group.pack(fill="x", pady=(0, 15), ipady=5)
        ctk.CTkLabel(files_group, text="📁 SOURCE FILES & START", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(10, 5))

        # [START BUTTON NEXT TO UPLOAD]
        mix_file_row = ctk.CTkFrame(files_group, fg_color="transparent")
        mix_file_row.pack(fill="x", padx=15, pady=5)
        
        self.file_btn = self.create_file_btn(mix_file_row, "📂 Select Main Audio", self.select_file)
        self.file_btn.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        # New score_row for the full score button
        score_row = ctk.CTkFrame(files_group, fg_color="transparent")
        score_row.pack(fill="x", padx=15, pady=5)

        self.full_score_btn = ctk.CTkButton(score_row, text="✨ Generate Full Band Score (XML/PDF)", font=("Arial", 14, "bold"),
                                         height=45, fg_color="#00FF7F", text_color="black", hover_color="#00CC66",
                                         command=self.generate_full_score_request)
        self.full_score_btn.pack(fill="x", expand=True, padx=5)

        self.run_btn_1 = ctk.CTkButton(mix_file_row, text="✨ START MIXING", font=("Arial", 13, "bold"),
                                     width=160, height=42, fg_color=COLOR_GOLD, text_color="black", hover_color="#E5C158",
                                     command=self.start_thread)
        self.run_btn_1.pack(side="right", padx=5)

        self.file_label = ctk.CTkLabel(files_group, text="선택안함", font=FONT_SMALL, text_color=COLOR_TEXT_DIM)
        self.file_label.pack(anchor="w", padx=25, pady=(0, 5))

        self.eff_btn = self.create_file_btn(files_group, "🔔 Add Effect (Optional)", self.select_effect)
        self.eff_btn.pack(fill="x", padx=20, pady=5)
        
        mix_group = GlassFrame(mix_left)
        mix_group.pack(fill="x", expand=False, ipady=5)
        ctk.CTkLabel(mix_group, text="🎚️ MIXING CONTROL", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.create_slider_row(mix_group, "vocal", "🎤 Vocals (보컬)", 0)
        self.create_slider_row(mix_group, "mr", "🎹 Inst (반주)", 0)
        self.create_slider_row(mix_group, "sfx", "🔔 Effects (효과음)", -10)
        
        # [NEW] Dolby 스타일 효과 체크박스
        self.dolby_var = ctk.BooleanVar(value=True)
        self.dolby_chk = ctk.CTkCheckBox(mix_group, text=" 💎 Dolby Style (3D Surround + Crystalizer)", variable=self.dolby_var,
                                         font=("Arial", 12, "bold"), text_color=COLOR_GOLD, fg_color=COLOR_GOLD, hover_color=COLOR_GOLD)
        self.dolby_chk.pack(anchor="w", padx=20, pady=(5, 5))
        
        # [NEW] Hi-Fi 모드 체크박스 (무손실)
        self.hifi_var = ctk.BooleanVar(value=False)
        self.hifi_chk = ctk.CTkCheckBox(mix_group, text=" 👑 Hi-Fi Mode (Lossless WAV + Resolution Up)", variable=self.hifi_var,
                                         font=("Arial", 12, "bold"), text_color="#00FFAA", fg_color="#00FFAA", hover_color="#00FFAA")
        self.hifi_chk.pack(anchor="w", padx=20, pady=(0, 10))

        # [RE-DESIGN] 2-Stem Output Quick Access
        out_box_1 = ctk.CTkFrame(mix_left, fg_color="#111", border_color=COLOR_GOLD_DIM, border_width=1)
        out_box_1.pack(fill="x", pady=(5, 0))
        self.last_output_lbl_1 = ctk.CTkLabel(out_box_1, text="📂 READY FOR NEW PROJECT", font=("Arial", 11, "bold"), text_color=COLOR_GOLD)
        self.last_output_lbl_1.pack(pady=12)
        
        # Click to open last folder (UX touch)
        out_box_1.bind("<Button-1>", lambda e: self.open_last_output())
        self.last_output_lbl_1.bind("<Button-1>", lambda e: self.open_last_output())

        # Tab 1 - 오른쪽 (프리셋)
        mix_right = GlassFrame(self.tab_mix)
        mix_right.grid(row=0, column=1, sticky="nsew", padx=(15, 10), pady=10)
        ctk.CTkLabel(mix_right, text="🛢️ GENRE PRESETS", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(10, 5))
        
        presets_grid = ctk.CTkFrame(mix_right, fg_color="transparent")
        presets_grid.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        for i in range(2): presets_grid.grid_columnconfigure(i, weight=1)

        self.presets = [
            ("YouTube", 4, -2, "▶️"), ("Standard (표준)", 0, 0, "⚖️"),
            ("Pop (팝)", 3, -1, "🎤"), ("Rock (락)", 5, 1, "🎸"),
            ("Ballad (발라드)", 5, -3, "💝"), ("R&B", 4, -1, "🎵"),
            ("HipHop (힙합)", 6, 0, "🎧"), ("Trot (트로트)", 6, -2, "🎺")
        ]

        for i, (name, v, m, icon) in enumerate(self.presets):
            btn = ctk.CTkButton(presets_grid, text=f"{icon} {name}\n(V:{v}/M:{m})", 
                                font=("Arial", 12, "bold"), fg_color="#222", hover_color="#333", 
                                border_color="#444", border_width=1, height=55,
                                command=lambda v=v, m=m, n=name: self.apply_preset(v, m, n))
            btn.grid(row=i//2, column=i%2, padx=6, pady=6, sticky="nsew")

        # [NEW] Usage Guide Box in the empty space
        guide_box = GlassFrame(mix_right)
        guide_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        ctk.CTkLabel(guide_box, text="💡 AI STUDIO USAGE GUIDE", font=FONT_BOLD, text_color=COLOR_GOLD).pack(pady=(15, 10))
        
        guide_text = (
            "1. 'Select Main Audio'를 클릭해 파일을 불러옵니다.\n"
            "2. 'GENRE PRESETS'로 최적의 믹싱값을 설정하세요.\n"
            "3. 'Dolby Style'은 공간감, 'Hi-Fi'는 초고음질을 제공합니다.\n"
            "4. 하단의 '📂 OPEN LAST'로 최근 폴더를 확인하세요.\n"
            "5. 설정 완료 후 'START MIXING' 클릭!"
        )
        ctk.CTkLabel(guide_box, text=guide_text, font=("Malgun Gothic", 14), text_color="#F0F0F0", justify="left").pack(padx=20, pady=(0, 15))

    def setup_pro_extraction_tab(self):
        """Pro HQ Mastering (6-Stem) 탭 UI 구성"""
        self.tab_pro.grid_columnconfigure(0, weight=1)
        
        # [Console Header]
        pro_header = ctk.CTkFrame(self.tab_pro, fg_color="transparent")
        pro_header.pack(fill="x", padx=30, pady=(15, 0))
        ctk.CTkLabel(pro_header, text="🎚️ 6-STEM REVOLUTION MIXER", font=("Montserrat", 22, "bold"), text_color=COLOR_GOLD).pack(side="left")
        
        # [Console Main Layout]
        console_body = ctk.CTkFrame(self.tab_pro, fg_color="transparent")
        console_body.pack(fill="both", expand=True, padx=30, pady=5)
        console_body.grid_columnconfigure(0, weight=6) # Mixer Sliders (Adjusted for balance)
        console_body.grid_columnconfigure(1, weight=4) # Mastering Panel (Widened)
        
        # --- [Mixer Section] ---
        mixer_frame = GlassFrame(console_body)
        mixer_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        
        ctk.CTkLabel(mixer_frame, text="STEM CONTROL CHANNELS", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(10, 5))
        
        # 6-Stem Sliders
        self.pro_sliders = {}
        self.pro_slider_labels = {}
        pro_stems = [
            ("vocals", "🎤 VOCALS (보컬)", 0), ("drums", "🥁 DRUMS (드럼)", 0),
            ("bass", "🎸 BASS (베이스)", 0), ("guitar", "🎸 GUITAR (기타)", 0),
            ("piano", "🎹 PIANO (피아노)", 0), ("other", "🎼 OTHERS (기타악기)", 0)
        ]
        
        mixer_grid = ctk.CTkFrame(mixer_frame, fg_color="transparent")
        mixer_grid.pack(fill="x", expand=False, padx=10, pady=5)
        
        for name, label, default in pro_stems:
            self.create_pro_slider_row(mixer_grid, name, label, default)

        # [REPOSITIONED] MASTER POLISH (Now in 2 columns for balance)
        ctk.CTkLabel(mixer_frame, text="💎 MASTER POLISH", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(10, 5))
        
        # Grid frame for Master Polish for horizontal balance
        fx_grid = ctk.CTkFrame(mixer_frame, fg_color="transparent")
        fx_grid.pack(fill="x", padx=15, pady=2)
        fx_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.fx_vocal_air = ctk.BooleanVar(value=True)
        chk1 = ctk.CTkCheckBox(fx_grid, text="✨ Vocal Air", variable=self.fx_vocal_air, font=("Arial", 11),
                                text_color="#CCC", fg_color=COLOR_GOLD, hover_color=COLOR_GOLD)
        chk1.grid(row=0, column=0, sticky="w", pady=5)
        
        self.fx_drum_punch = ctk.BooleanVar(value=True)
        chk2 = ctk.CTkCheckBox(fx_grid, text="🥊 Drum Punch", variable=self.fx_drum_punch, font=("Arial", 11),
                                text_color="#CCC", fg_color=COLOR_GOLD, hover_color=COLOR_GOLD)
        chk2.grid(row=0, column=1, sticky="w", pady=5)
        
        self.fx_bass_warmth = ctk.BooleanVar(value=True)
        chk3 = ctk.CTkCheckBox(fx_grid, text="🔥 Deep Bass", variable=self.fx_bass_warmth, font=("Arial", 11),
                                text_color="#CCC", fg_color=COLOR_GOLD, hover_color=COLOR_GOLD)
        chk3.grid(row=0, column=2, sticky="w", pady=5)
        
        self.fx_stereo_wall = ctk.BooleanVar(value=True)
        chk4 = ctk.CTkCheckBox(fx_grid, text="↔️ Wall of Sound", variable=self.fx_stereo_wall, font=("Arial", 11),
                                text_color="#CCC", fg_color=COLOR_GOLD, hover_color=COLOR_GOLD)
        chk4.grid(row=0, column=3, sticky="w", pady=5)

        # [REPOSITIONED] MIDI LOAD PRESET (Now on the left)
        ctk.CTkLabel(mixer_frame, text="🎹 MIDI LOAD PRESET", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(10, 5))
        
        midi_preset_frame = ctk.CTkFrame(mixer_frame, fg_color="transparent")
        midi_preset_frame.pack(fill="x", padx=15, pady=(0, 5))

        self.midi_load_mode = ctk.StringVar(value="Light")
        self.midi_preset_btn = ctk.CTkSegmentedButton(midi_preset_frame, values=["Light", "Balanced", "Full"],
                                                      variable=self.midi_load_mode, command=self.apply_midi_preset,
                                                      font=("Arial", 11, "bold"), fg_color="#222", selected_color=COLOR_GOLD,
                                                      selected_hover_color="#E5C158", unselected_color="#333", unselected_hover_color="#444")
        self.midi_preset_btn.pack(fill="x", padx=10, pady=(0, 5))
        
        self.batch_midi_btn = ctk.CTkButton(midi_preset_frame, text="✨ Convert All to MIDI & Scores",
                                           font=("Arial", 11, "bold"), fg_color=COLOR_GOLD, hover_color="#E5C158",
                                           text_color="#000", command=self.convert_all_to_midi_request)
        self.batch_midi_btn.pack(fill="x", padx=10, pady=(0, 5))
        

        # [NEW] 6-Stem Presets Grid
        ctk.CTkLabel(mixer_frame, text="🎸 PRO MIX PRESETS", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(5, 5))
        
        pro_presets_frame = ctk.CTkFrame(mixer_frame, fg_color="transparent")
        pro_presets_frame.pack(fill="x", padx=15, pady=(0, 10))
        for i in range(6): pro_presets_frame.grid_columnconfigure(i, weight=1)

        self.pro_presets_data = [
            ("Band Live", {"vocals":0, "drums":2, "bass":1, "guitar":1, "piano":0, "other":0}, {"v":1,"d":1,"b":1,"s":0}),
            ("Vocal Focus", {"vocals":4, "drums":-2, "bass":-2, "guitar":-1, "piano":-1, "other":-2}, {"v":1,"d":0,"b":0,"s":0}),
            ("Power Rhythm", {"vocals":-1, "drums":4, "bass":3, "guitar":0, "piano":0, "other":0}, {"v":0,"d":1,"b":1,"s":0}),
            ("Acoustic", {"vocals":2, "drums":-4, "bass":-3, "guitar":3, "piano":3, "other":-2}, {"v":1,"d":0,"b":0,"s":1}),
            ("Cinematic", {"vocals":0, "drums":1, "bass":2, "guitar":0, "piano":2, "other":3}, {"v":0,"d":1,"b":1,"s":1}),
            ("Revolution", {"vocals":1, "drums":1, "bass":1, "guitar":1, "piano":1, "other":1}, {"v":1,"d":1,"b":1,"s":1}),
        ]

        for i, (p_name, gains, fxs) in enumerate(self.pro_presets_data):
            btn = ctk.CTkButton(pro_presets_frame, text=p_name, font=("Arial", 9, "bold"), 
                                 fg_color="#222", hover_color="#333", border_color="#444", border_width=1, height=28,
                                 command=lambda g=gains, f=fxs, n=p_name: self.apply_pro_preset(g, f, n))
            btn.grid(row=0, column=i, padx=2, pady=3, sticky="nsew")


        # --- [Mastering Panel - NO SCROLL] ---
        # [수정] 스크롤을 제거하고 콤팩트하게 배치하여 가시성 확보
        master_panel = GlassFrame(console_body)
        master_panel.grid(row=0, column=1, sticky="nsew", pady=(10, 5))
        
        # [BAND SCORE SETTINGS] Header with Start Button
        header_frame_right = ctk.CTkFrame(master_panel, fg_color="transparent")
        header_frame_right.pack(fill="x", padx=10, pady=(15, 10))
        
        ctk.CTkLabel(header_frame_right, text="🎼 BAND SCORE SETTINGS", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(side="left")
        
        self.run_btn_2 = ctk.CTkButton(header_frame_right, text="🚀 START PRO MIX", font=("Arial", 12, "bold"),
                                     height=38, width=150, fg_color=COLOR_GOLD, text_color="black", hover_color="#E5C158",
                                     border_width=2, border_color="#AA8A2E",
                                     command=self.start_thread)
        self.run_btn_2.pack(side="right", padx=(10, 0))

        band_score_frame = ctk.CTkFrame(master_panel, fg_color="transparent")
        band_score_frame.pack(fill="x", padx=5, pady=0)

        # Transposition
        trans_frame = ctk.CTkFrame(band_score_frame, fg_color="transparent")
        trans_frame.pack(fill="x", padx=5, pady=(0, 15))
        ctk.CTkLabel(trans_frame, text="Key Transpose:", font=("Arial", 11, "bold"), text_color="white").pack(side="left", padx=(0, 10))
        self.score_trans_var = ctk.IntVar(value=0)
        self.score_trans_btn = ctk.CTkSegmentedButton(trans_frame, values=["-2", "-1", "0", "+1", "+2"],
                                                     variable=self.score_trans_var, font=("Arial", 11, "bold"),
                                                     height=32, fg_color="#222", selected_color=COLOR_GOLD)
        self.score_trans_btn.pack(side="right", expand=True, fill="x")

        # [NEW] Suno Link & Lyrics Fetch
        suno_frame = ctk.CTkFrame(band_score_frame, fg_color="transparent")
        suno_frame.pack(fill="x", padx=5, pady=(5, 10))
        
        self.suno_url_entry = ctk.CTkEntry(suno_frame, placeholder_text="🔗 Suno Song URL (https://suno.com/song/...)", 
                                           font=("Arial", 11), height=35, fg_color="#111", border_color="#333")
        self.suno_url_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.fetch_lyrics_btn = ctk.CTkButton(suno_frame, text="⚡ Get Lyrics", width=100, height=35,
                                              font=("Arial", 11, "bold"), fg_color=COLOR_GOLD, text_color="#000",
                                              command=self.fetch_suno_lyrics_action)
        self.fetch_lyrics_btn.pack(side="right")

        # Lyrics Entry
        ctk.CTkLabel(band_score_frame, text="Lyrics (Suno style):", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=5, pady=(5, 2))
        self.lyrics_entry = ctk.CTkTextbox(band_score_frame, height=140, font=("Arial", 11), fg_color="#111", border_color="#333", border_width=1)
        self.lyrics_entry.pack(fill="x", padx=5, pady=(2, 8))
        self.lyrics_entry.insert("1.0", "어둠 속을 걷다가 빛을 만났어\n너의 손을 잡고서 다시 일어 서\n우리 함께 라면 두렵지 않아\n영원히 너를 사랑해")

        # [NEW] External MIDI Option
        midi_opt_frame = ctk.CTkFrame(band_score_frame, fg_color="transparent")
        midi_opt_frame.pack(fill="x", padx=5, pady=(5, 5))
        
        self.external_midi_path = None
        self.midi_select_btn = ctk.CTkButton(midi_opt_frame, text="📁 Select MIDI Folder (Optional)", 
                                            font=("Arial", 11, "bold"), height=30, fg_color="#333", border_color="#555", border_width=1,
                                            command=self.select_external_midi_folder)
        self.midi_select_btn.pack(fill="x")

        # Generate Button
        self.full_score_btn = ctk.CTkButton(master_panel, text="🎼 Generate Full Band Score (PDF)", font=("Arial", 14, "bold"),
                                           fg_color="#00EE76", hover_color="#00CD66", border_width=2, border_color="#008B45",
                                           text_color="#000", height=42, command=self.generate_full_score_request)
        self.full_score_btn.pack(fill="x", padx=10, pady=(5, 10))
        
        # [RE-DESIGNED] Files Section
        pro_btn_row = ctk.CTkFrame(master_panel, fg_color="transparent")
        pro_btn_row.pack(fill="x", pady=(10, 5), padx=10)
        
        self.pro_file_btn = self.create_file_btn(pro_btn_row, "📂 Select Main Audio File", self.select_file)
        self.pro_file_btn.pack(fill="x", expand=True)
        self.pro_file_btn.configure(fg_color="#333", border_color=COLOR_GOLD, border_width=1)
        
        self.pro_file_label = ctk.CTkLabel(master_panel, text="선택안함 (파일을 불러오세요)", font=("Arial", 12, "bold"), text_color=COLOR_GOLD_DIM)
        self.pro_file_label.pack(pady=(2, 2))

        # [RE-DESIGN] 6-Stem Output Quick Access
        out_box_2 = ctk.CTkFrame(master_panel, fg_color="#111", border_color=COLOR_GOLD_DIM, border_width=1)
        out_box_2.pack(fill="x", padx=10, pady=(5, 10))
        self.last_output_lbl_2 = ctk.CTkLabel(out_box_2, text="📂 READY FOR NEW PROJECT", font=("Arial", 11, "bold"), text_color=COLOR_GOLD)
        self.last_output_lbl_2.pack(pady=6)

        # 클릭 이벤트 바인딩 (이제 정의된 후이므로 에러 없음)
        out_box_2.bind("<Button-1>", lambda e: self.open_last_output())
        self.last_output_lbl_2.bind("<Button-1>", lambda e: self.open_last_output())

    def setup_voice_training_tab(self):
        """Voice Training (GPT-SoVITS) 탭 UI 구성"""
        self.tab_voice.grid_columnconfigure(0, weight=3)  # Left: Lyrics
        self.tab_voice.grid_columnconfigure(1, weight=3)  # Center: Audio Files
        self.tab_voice.grid_columnconfigure(2, weight=4)  # Right: Export
        
        # --- [Left Panel: Lyrics Cleaning] ---
        lyrics_panel = GlassFrame(self.tab_voice)
        lyrics_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        ctk.CTkLabel(lyrics_panel, text="📝 LYRICS CLEANING", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(15, 5))
        
        # [NEW] Script Preset Selector
        preset_frame = ctk.CTkFrame(lyrics_panel, fg_color="transparent")
        preset_frame.pack(fill="x", padx=20, pady=(10, 5))
        ctk.CTkLabel(preset_frame, text="📜 Script Presets:", font=("Arial", 10, "bold"), text_color=COLOR_GOLD).pack(side="left", padx=(0, 10))
        
        self.script_preset = ctk.StringVar(value="Custom")
        preset_selector = ctk.CTkSegmentedButton(
            preset_frame,
            values=["CEO 모드", "내레이션", "유튜버", "Custom"],
            variable=self.script_preset,
            command=self.load_script_preset,
            font=("Arial", 9),
            height=26,
            fg_color="#222",
            selected_color=COLOR_GOLD
        )
        preset_selector.pack(side="left", fill="x", expand=True)
        
        # Raw Lyrics Input
        ctk.CTkLabel(lyrics_panel, text="Raw Lyrics (with chords):", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=20, pady=(5, 2))
        self.raw_lyrics_text = ctk.CTkTextbox(lyrics_panel, height=180, font=("Arial", 11), fg_color="#111", border_color="#333", border_width=1)
        self.raw_lyrics_text.pack(fill="x", padx=20, pady=(2, 10))
        self.raw_lyrics_text.insert("1.0", "[Intro]\nC  G  Am  F\n\n(Verse 1)\n학교종이 땡땡땡\n어서 모이자")
        
        # Clean Button
        self.clean_lyrics_btn = ctk.CTkButton(lyrics_panel, text="✨ Clean Lyrics (Remove Chords)", 
                                             font=("Arial", 13, "bold"), height=40, fg_color=COLOR_GOLD, 
                                             text_color="black", hover_color="#E5C158",
                                             command=self.clean_lyrics_action)
        self.clean_lyrics_btn.pack(fill="x", padx=20, pady=(0, 10))
        
        # Cleaned Lyrics Output
        ctk.CTkLabel(lyrics_panel, text="Cleaned Lyrics:", font=("Arial", 11, "bold"), text_color="#00FF7F").pack(anchor="w", padx=20, pady=(5, 2))
        self.clean_lyrics_text = ctk.CTkTextbox(lyrics_panel, height=200, font=("Arial", 11), fg_color="#0A1A0A", border_color="#00FF7F", border_width=1)
        self.clean_lyrics_text.pack(fill="x", padx=20, pady=(2, 10))
        
        # Save Cleaned Lyrics Button
        self.save_lyrics_btn = ctk.CTkButton(lyrics_panel, text="💾 Save Cleaned Lyrics", 
                                            font=("Arial", 11, "bold"), height=35, fg_color="#333", 
                                            border_color=COLOR_GOLD, border_width=1,
                                            command=self.save_cleaned_lyrics)
        self.save_lyrics_btn.pack(fill="x", padx=20, pady=(0, 15))
        
        # --- [Center Panel: Audio Files] ---
        audio_panel = GlassFrame(self.tab_voice)
        audio_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        
        ctk.CTkLabel(audio_panel, text="🎤 TRAINING AUDIO FILES", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(15, 5))
        
        # File List
        ctk.CTkLabel(audio_panel, text="Selected Files (WAV recommended):", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w", padx=20, pady=(10, 2))
        
        # Listbox with Scrollbar
        list_frame = ctk.CTkFrame(audio_panel, fg_color="#111", border_color="#333", border_width=1)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(2, 10))
        
        self.training_listbox = tk.Listbox(list_frame, bg="#111", fg="white", font=("Consolas", 10), 
                                          selectmode=tk.MULTIPLE, highlightthickness=0, borderwidth=0)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.training_listbox.yview)
        self.training_listbox.config(yscrollcommand=scrollbar.set)
        
        self.training_listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=2, pady=2)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File Management Buttons
        btn_frame = ctk.CTkFrame(audio_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.add_files_btn = ctk.CTkButton(btn_frame, text="➕ Add Audio Files", 
                                          font=("Arial", 12, "bold"), height=38, fg_color="#00AA00", 
                                          hover_color="#008800", command=self.add_training_files)
        self.add_files_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.remove_files_btn = ctk.CTkButton(btn_frame, text="➖ Remove Selected", 
                                             font=("Arial", 12, "bold"), height=38, fg_color="#AA0000", 
                                             hover_color="#880000", command=self.remove_training_files)
        self.remove_files_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # File Count Info
        self.file_count_lbl = ctk.CTkLabel(audio_panel, text="Files: 0", font=("Arial", 11, "bold"), text_color=COLOR_GOLD)
        self.file_count_lbl.pack(pady=(5, 15))
        
        # --- [Right Panel: Export & Guide] ---
        export_panel = GlassFrame(self.tab_voice)
        export_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        
        ctk.CTkLabel(export_panel, text="📦 EXPORT TRAINING PACKAGE", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(15, 5))
        
        # Export Button
        self.export_btn = ctk.CTkButton(export_panel, text="🚀 Generate Training Package", 
                                       font=("Arial", 14, "bold"), height=50, fg_color="#00EE76", 
                                       hover_color="#00CD66", border_width=2, border_color="#008B45",
                                       text_color="#000", command=self.export_training_package)
        self.export_btn.pack(fill="x", padx=20, pady=(10, 15))
        
        # [NEW] Training Configuration
        training_config_frame = ctk.CTkFrame(export_panel, fg_color="#1A1A2E", border_color="#444", border_width=1)
        training_config_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(training_config_frame, text="🎓 TRAINING SETTINGS", font=("Arial", 11, "bold"), text_color=COLOR_GOLD).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Model Name Input
        name_frame = ctk.CTkFrame(training_config_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=(5, 5))
        ctk.CTkLabel(name_frame, text="Model Name:", font=("Arial", 10), text_color="white").pack(side="left", padx=(0, 10))
        self.training_model_name = ctk.CTkEntry(name_frame, placeholder_text="JaeSoo_Voice", font=("Arial", 11), height=30)
        self.training_model_name.pack(side="left", fill="x", expand=True)
        
        # Quality Preset
        quality_frame = ctk.CTkFrame(training_config_frame, fg_color="transparent")
        quality_frame.pack(fill="x", padx=15, pady=(5, 10))
        ctk.CTkLabel(quality_frame, text="Quality:", font=("Arial", 10), text_color="white").pack(side="left", padx=(0, 10))
        self.training_quality = ctk.StringVar(value="Balanced")
        quality_selector = ctk.CTkSegmentedButton(
            quality_frame,
            values=["Fast (5 epochs)", "Balanced (15 epochs)", "Best (30 epochs)"],
            variable=self.training_quality,
            font=("Arial", 9),
            height=28,
            fg_color="#222",
            selected_color=COLOR_GOLD
        )
        quality_selector.pack(side="left", fill="x", expand=True)
        
        # Start Training Button
        self.start_training_btn = ctk.CTkButton(
            export_panel,
            text="🔥 START TRAINING (Generate .pth Model)",
            font=("Arial", 14, "bold"),
            height=50,
            fg_color="#FF6B35",
            hover_color="#FF5722",
            border_width=2,
            border_color="#CC4A1C",
            text_color="#000",
            command=self.start_voice_training
        )
        self.start_training_btn.pack(fill="x", padx=20, pady=(0, 10))
        
        # Training Status
        self.training_status_lbl = ctk.CTkLabel(
            export_panel,
            text="Ready to train",
            font=("Arial", 10, "bold"),
            text_color="#888"
        )
        self.training_status_lbl.pack(pady=(0, 10))
        
        # Export Info
        export_info = ctk.CTkFrame(export_panel, fg_color="#0A0A1A", border_color="#333", border_width=1)
        export_info.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(export_info, text="📂 Export Structure:", font=("Arial", 11, "bold"), text_color=COLOR_GOLD).pack(anchor="w", padx=15, pady=(10, 5))
        
        structure_text = (
            "GPT_SoVITS_Training_{time}/\n"
            "├── cleaned_lyrics.txt\n"
            "├── audio/\n"
            "│   ├── sample_001.wav\n"
            "│   ├── sample_002.wav\n"
            "│   └── ...\n"
            "└── README.txt"
        )
        ctk.CTkLabel(export_info, text=structure_text, font=("Consolas", 9), text_color="#AAA", justify="left").pack(anchor="w", padx=15, pady=(0, 10))
        
        # Usage Guide
        guide_frame = GlassFrame(export_panel)
        guide_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        ctk.CTkLabel(guide_frame, text="💡 USAGE GUIDE", font=FONT_BOLD, text_color=COLOR_GOLD).pack(pady=(15, 10))
        
        guide_text = (
            "1. 가사 입력 후 'Clean Lyrics' 클릭\n"
            "   → 코드(C, Am, G7 등) 자동 제거\n\n"
            "2. 'Add Audio Files'로 훈련 음성 추가\n"
            "   → WAV 형식 권장 (고음질)\n\n"
            "3. 'Generate Training Package' 클릭\n"
            "   → output_result에 폴더 생성\n\n"
            "4. 생성된 폴더를 GPT-SoVITS에서 사용\n"
            "   → 음성 합성 훈련 시작!"
        )
        ctk.CTkLabel(guide_frame, text=guide_text, font=("Malgun Gothic", 11), text_color="#F0F0F0", justify="left").pack(padx=20, pady=(0, 15))


    def apply_midi_preset(self, value):
        """[NEW] 프리셋에 따라 MIDI 체크박스 상태 일괄 변경 + UI 피드백"""
        presets = {
            "Light": ["vocals", "drums", "bass"],
            "Balanced": ["vocals", "drums", "bass", "guitar", "piano"],
            "Full": ["vocals", "drums", "bass", "guitar", "piano", "other"]
        }
        active_stems = presets.get(value, [])
        for k, v in self.midi_vars.items():
            v.set(k in active_stems)
        
        # [수정] 자동 변환 시작 제거 (사용자 요청: 피로감 감소를 위해 개별/명시적 실행으로 변경)
        self.safe_status(f"🎯 MIDI Preset: {value} Mode Selected. Click 'START SELECTED' to begin.", COLOR_GOLD)

    def convert_all_to_midi_request(self):
        """[NEW] 선택된 악기들에 대해 MIDI 변환 순차적(Sequential) 실행"""
        if not hasattr(self, 'last_output_dir') or not self.last_output_dir:
            self.safe_status("❌ Error: 6-Stem 분석을 먼저 실행해주세요.", "#FF5555")
            return
        
        targets = [s for s in ["vocals", "drums", "bass", "guitar", "piano", "other"] if self.midi_vars[s].get()]
        if not targets:
            self.safe_status("⚠️ MIDI 변환할 악기가 선택되지 않았습니다.", COLOR_GOLD)
            return

        self.batch_midi_btn.configure(state="disabled", text="⏳ MIDI Processing...")
        self.progress.set(0)

        # 순차적 처리를 위한 워커 스레드 생성
        def sequential_worker():
            try:
                stems = ["vocals", "drums", "bass", "guitar", "piano", "other"]
                targets = [s for s in stems if self.midi_vars.get(s) and self.midi_vars[s].get()]
                
                if not targets:
                    self.safe_status("⚠️ 선택된 MIDI 트랙이 없습니다.", "#FFAA00")
                    return

                self.safe_status(f"🎹 Batch MIDI Start (0/{len(targets)})", COLOR_GOLD)
            
                for i, s in enumerate(targets):
                    if s in self.active_midi_tasks: continue # 이미 작업 중이면 건너뜀
                    self.active_midi_tasks.add(s)
                    
                    # 오디오 파일 찾기
                    audio_dir = os.path.join(self.last_output_dir, "음원분리")
                    clean_basename = clean_name(self.file_path)
                    target_file = os.path.join(audio_dir, f"6S_{s}_{clean_basename}.wav")
                    
                    if not os.path.exists(target_file):
                        if s == "vocals": target_file = os.path.join(audio_dir, f"Vocals_{clean_basename}.wav")
                        elif s == "mr": target_file = os.path.join(audio_dir, f"Inst_{clean_basename}.wav")

                    if os.path.exists(target_file):
                        # 1. MIDI 변환
                        msg_midi = f"🎹 Converting MIDI: {s.upper()} ({i+1}/{len(targets)})..."
                        self.safe_status(msg_midi, "#00CCFF")
                        self.run_midi_conversion_logic(target_file, s)
                        
                        # 2. 악보 자동 생성 (LilyPond) - 각 파일 변환 직후 실행하여 피드백 강화
                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        lily_exe = os.path.join(base_dir, "lilypond-2.24.4", "bin", "lilypond.exe")
                        if not os.path.exists(lily_exe):
                            lily_exe = r"C:\lilypond-2.24.4\bin\lilypond.exe"
                            
                        if os.path.exists(lily_exe):
                            msg_score = f"📄 Generating Score: {s.upper()}..."
                            self.safe_status(msg_score, "#00FF7F")
                            
                            score_maker_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "score_maker.py")
                            midi_dir_path = os.path.join(self.last_output_dir, "미디분리")
                            
                            if os.path.exists(score_maker_script) and os.path.exists(midi_dir_path):
                                 # [FIX] LilyPond 엔진을 직접 호출하지 않고 score_maker.py를 통해 통제
                                 midi_filename = f"{clean_basename}_{s}.mid"
                                 subprocess.run([sys.executable, score_maker_script, midi_dir_path, midi_filename], check=False)

                        if s in self.active_midi_tasks: self.active_midi_tasks.remove(s)
                        
                    # 진행 바 업데이트 (하단 공통 바 동기화)
                    progress_val = (i + 1) / len(targets)
                    self.safe_update(self.progress.set, progress_val)
                    
                self.safe_status("✅ All Done! MIDI & Scores Created.", "#00FF7F")
                self.safe_update(self.progress.set, 1.0)
            except Exception as e:
                print(f"Batch Processing Error: {e}")
                self.safe_status(f"❌ Batch Error: {str(e)}", "#FF5555")
            finally:
                self.safe_update(self.batch_midi_btn.configure, {"state": "normal", "text": "✨ Convert All to MIDI & Scores"})

        threading.Thread(target=sequential_worker, daemon=True).start()

    def convert_to_midi_request(self, stem_name):
        """[NEW] 개별 MIDI 변환 요청 (비동기)"""
        if not hasattr(self, 'last_output_dir') or not self.last_output_dir:
            self.status_lbl.configure(text="❌ Error: 6-Stem 분석을 먼저 실행해주세요.", text_color="#FF5555")
            return
        
        audio_dir = os.path.join(self.last_output_dir, "음원분리")
        clean_basename = clean_name(self.file_path)
        target_file = os.path.join(audio_dir, f"6S_{stem_name}_{clean_basename}.wav")
             
        if not os.path.exists(target_file):
            if stem_name == "vocals": target_file = os.path.join(audio_dir, f"Vocals_{clean_basename}.wav")
            elif stem_name == "mr": target_file = os.path.join(audio_dir, f"Inst_{clean_basename}.wav")

        if not os.path.exists(target_file): return

        # 중복 실행 방지
        if stem_name in self.active_midi_tasks:
            self.safe_status(f"⏳ {stem_name.upper()} is already processing...", COLOR_GOLD)
            return
        
        self.active_midi_tasks.add(stem_name)

        # 개별 요청은 즉시 스레드 실행
        msg = f"🎹 Starting MIDI: {stem_name.upper()}..."
        self.safe_status(msg, "#00CCFF")
        self.safe_update(self.progress.set, 0.1) # 초기 진행 표시
        threading.Thread(target=self.run_midi_conversion_logic, args=(target_file, stem_name, True), daemon=True).start()

    def run_midi_conversion_logic(self, audio_path, stem_name, is_individual=False):
        """[FIX] 독립 프로세스(midi_engine.py)를 통한 MIDI 변환 - 환경 충돌 완벽 차단"""
        try:
            midi_dir = os.path.join(self.last_output_dir, "미디분리")
            os.makedirs(midi_dir, exist_ok=True)
            clean_basename = clean_name(self.file_path)
            output_midi = os.path.join(midi_dir, f"{clean_basename}_{stem_name}.mid")
            
            # [FIX] 별도의 프로세스로 midi_engine.py 실행
            # GUI가 아닌 별도의 Python 인터프리터를 사용하여 TensorFlow 환경을 격리합니다.
            executable = sys.executable
            engine_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core", "midi_engine.py")
            
            if not os.path.exists(engine_path):
                print(f"Error: {engine_path} not found")
                return

            cmd = [executable, engine_path, audio_path, output_midi]
            
            # 콘솔 창 숨기기
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # 작업을 수행하고 완료될 때까지 대기 (순차적 처리를 위해)
            process = subprocess.Popen(cmd, startupinfo=startupinfo)
            process.wait()

            if process.returncode == 0:
                print(f"MIDI Success ({stem_name}): {output_midi}")
                if is_individual:
                    self.safe_status(f"✅ MIDI Done: {stem_name.upper()}", "#00FF7F")
                    self.safe_update(self.progress.set, 1.0)
            else:
                print(f"MIDI Engine Failed for {stem_name} with code {process.returncode}")
                if is_individual:
                    self.safe_status(f"❌ MIDI Error: {stem_name.upper()}", "#FF5555")
        except Exception as e:
            print(f"MIDI Outer Error ({stem_name}): {e}")
            if is_individual:
                self.safe_status(f"❌ MIDI Error: {stem_name.upper()}", "#FF5555")
        finally:
            # 작업 완료 후 태스크 세트에서 확실히 제거
            if stem_name in self.active_midi_tasks:
                self.active_midi_tasks.remove(stem_name)

    def fetch_suno_lyrics_action(self):
        """[NEW] Suno URL에서 가사 가져오기"""
        url = self.suno_url_entry.get().strip().rstrip(':').rstrip('/')
        if not url:
            return messagebox.showwarning("No URL", "Suno 노래 링크를 입력해주세요.")
        
        def worker():
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            try:
                self.safe_status("🔍 Fetching lyrics from Suno...", COLOR_GOLD)
                
                # URL 형식 대응 (Alphanumeric ID 지원)
                song_id_match = re.search(r"(?:song/|s/|playlist/)([a-zA-Z0-9\-]+)", url)
                if not song_id_match:
                    song_id_match = re.search(r"/([a-zA-Z0-9\-]+)$", url.split('?')[0])
                
                if not song_id_match:
                    self.safe_status("❌ Invalid Suno URL", "#FF5555")
                    return
                
                song_id = song_id_match.group(1)
                
                # [추가] Short ID인 경우 redirect를 통해 실제 UUID 확보 시도
                if len(song_id) < 30:
                    try:
                        r = requests.get(url, headers=headers, allow_redirects=True, timeout=5)
                        id_match = re.search(r"song/([a-f0-9\-]{32,})", r.url)
                        if id_match: song_id = id_match.group(1)
                    except: pass

                api_url = f"https://studio-api.suno.ai/api/feed/?ids={song_id}"
                response = requests.get(api_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        metadata = data[0].get('metadata', {})
                        lyrics = metadata.get('prompt', '')
                        if lyrics:
                            self.safe_update(self.lyrics_entry.delete, "1.0", "end")
                            self.safe_update(self.lyrics_entry.insert, "1.0", lyrics)
                            self.safe_status("✅ Lyrics fetched successfully!", "#00FF7F")
                        else:
                            self.safe_status("⚠️ No lyrics found in metadata", COLOR_GOLD)
                    else:
                        self.safe_status("⚠️ Song not found or private", COLOR_GOLD)
                else:
                    self.safe_status(f"❌ Server error: {response.status_code}", "#FF5555")
            except Exception as e:
                self.safe_status(f"❌ Lyrics error: {str(e)}", "#FF5555")

        threading.Thread(target=worker, daemon=True).start()

    def generate_full_score_request(self):
        """[NEW] 통합 총보(Master Score) 생성 요청"""
        # [수정] 외부 미디 폴더가 선택되어 있으면 우선 사용
        if hasattr(self, 'external_midi_path') and self.external_midi_path:
            midi_dir = self.external_midi_path
        elif hasattr(self, 'last_output_dir') and self.last_output_dir:
            midi_dir = os.path.join(self.last_output_dir, "미디분리")
        else:
            self.status_lbl.configure(text="❌ Error: MIDI 폴더를 선택하거나 6-Stem 분석을 먼저 실행하세요.", text_color="#FF5555")
            return

        if not os.path.exists(midi_dir) or not os.listdir(midi_dir):
            self.status_lbl.configure(text="❌ Error: 선택한 폴더에 MIDI 파일이 없습니다.", text_color="#FF5555")
            return

        def score_worker():
            try:
                self.safe_status("🎼 Generating Master Full Score...", "#00FF7F")
                
                trans = self.score_trans_var.get()
                lyrics = self.lyrics_entry.get("1.0", "end-1c")
                
                master_maker_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core", "master_score_maker.py")
                
                if os.path.exists(master_maker_script):
                    # arg order: [midi_folder] [transposition] [lyrics_text]
                    cmd = [sys.executable, master_maker_script, midi_dir, str(trans), lyrics]
                    
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    # [수정] 결과 캡처 및 에러 처리 강화 (STDOUT/STDERR 통합 및 인코딩 대응)
                    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                           startupinfo=startupinfo)
                    
                    # 한국어 윈도우 인코딩(CP949)과 UTF-8 대응
                    try:
                        out_msg = process.stdout.decode('utf-8')
                    except:
                        out_msg = process.stdout.decode('cp949', errors='replace')

                    if process.returncode == 0:
                        self.safe_status("✅ Hybrid XML/PDF Created! (Tip: Open XML in MuseScore 4)", "#00FF7F")
                        # 자동 열기 시도 (PDF 선택)
                        try:
                            # Open the directory to show both XML and PDF
                            os.startfile(midi_dir)
                        except: pass
                    else:
                        print(f"Master Score Error Log:\n{out_msg}")
                        self.safe_status("❌ PDF Engine Error: Check Rhythm/Path", "#FF5555")
                        messagebox.showerror("Hybrid Score Error", 
                                          f"악보 생성 중 오류가 발생했습니다.\n\n"
                                          f"1. LilyPond 엔진 설치 여부를 확인하세요.\n"
                                          f"2. MIDI 박자가 너무 복잡하면 발생할 수 있습니다.\n\n"
                                          f"로그 요약:\n{out_msg[:500]}")
            except Exception as e:
                print(f"Master Score Thread Error: {e}")
                self.safe_status(f"❌ Thread Error: {str(e)}", "#FF5555")

        threading.Thread(target=score_worker, daemon=True).start()

    def select_external_midi_folder(self):
        """[NEW] 외부 미디 파일이 있는 폴더 선택"""
        d = filedialog.askdirectory(title="MIDI 파일들이 있는 폴더를 선택하세요")
        if d:
            self.external_midi_path = d
            self.midi_select_btn.configure(text=f"✅ Folder: {os.path.basename(d)}", fg_color="#F59E0B")
            self.safe_status(f"📂 External MIDI Folder Selected: {d}", COLOR_GOLD)

    def show_engine_alert(self):
        """[NEW] 악보 엔진 미설치 시 알림 및 가이드"""
        if messagebox.askyesno("LilyPond Required", 
                               "🎹 고품질 악보(PDF)와 이미지(PSD)를 생성하려면 'LilyPond' 엔진이 필요합니다.\n\n지금 설치 안내 페이지를 보시겠습니까?"):
            # webbrowser.open("https://lilypond.org/download.html")
            # Local setup guide is better
            messagebox.showinfo("Instructions", "setup.bat를 실행하면 LilyPond가 자동으로 설치됩니다.\n또는 INSTALL_MANUAL.md 파일을 확인해 주세요.")

    def create_file_btn(self, parent, text, cmd):
        return ctk.CTkButton(parent, text=text, command=cmd, font=FONT_NORMAL, height=40, 
                             fg_color="#222", hover_color="#333", border_color=COLOR_GOLD_DIM, border_width=1)

    def create_slider_row(self, parent, key, label, default_val):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=2)
        h = ctk.CTkFrame(f, fg_color="transparent")
        h.pack(fill="x")
        ctk.CTkLabel(h, text=label, font=FONT_BOLD, text_color="white").pack(side="left")
        v_lbl = ctk.CTkLabel(h, text=f"{default_val} dB", font=FONT_BOLD, text_color=COLOR_GOLD)
        v_lbl.pack(side="right")
        s = ctk.CTkSlider(f, from_=-20, to=10, number_of_steps=30, progress_color=COLOR_GOLD, button_color="white", height=16)
        s.set(default_val)
        s.pack(fill="x", pady=(2, 8))
        s.configure(command=lambda v, k=key: self.update_slider_text(k, v))
        self.sliders[key] = slider = s
        self.slider_labels[key] = v_lbl

    def create_pro_slider_row(self, parent, key, label, default_val):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=10, pady=0)
        
        h = ctk.CTkFrame(f, fg_color="transparent")
        h.pack(fill="x")
        
        ctk.CTkLabel(h, text=label, font=("Arial", 11, "bold"), text_color="white").pack(side="left")
        v_lbl = ctk.CTkLabel(h, text=f"{default_val} dB", font=("Arial", 10, "bold"), text_color=COLOR_GOLD)
        v_lbl.pack(side="right")
        
        s = ctk.CTkSlider(f, from_=-20, to=10, number_of_steps=30, progress_color=COLOR_GOLD, button_color="white", height=12)
        s.set(default_val)
        s.pack(fill="x", pady=(0, 2))
        s.configure(command=lambda v, k=key: self.update_pro_slider_text(k, v))
        
        # [NEW] MIDI Conversion Toggle & Button
        # 기본값: Vocals, Drums, Bass는 True / 나머지는 False
        is_default_on = key in ["vocals", "drums", "bass"]
        mv = ctk.BooleanVar(value=is_default_on)
        self.midi_vars[key] = mv
        
        chk = ctk.CTkCheckBox(h, text="", variable=mv, width=20, height=20, corner_radius=5,
                               fg_color=COLOR_GOLD, hover_color=COLOR_GOLD, border_color=COLOR_GOLD_DIM)
        chk.pack(side="right", padx=(5, 0))

        midi_btn = ctk.CTkButton(h, text="🎹 MIDI", width=60, height=22, font=("Arial", 10, "bold"),
                                 fg_color="#333", hover_color=COLOR_GOLD, text_color=COLOR_GOLD,
                                 border_color=COLOR_GOLD_DIM, border_width=1,
                                 command=lambda k=key: self.convert_to_midi_request(k))
        midi_btn.pack(side="right", padx=(5, 10))
        
        self.pro_sliders[key] = s
        self.pro_slider_labels[key] = v_lbl

    def apply_pro_preset(self, gains, fxs, name):
        # Apply Gains
        for k, v in gains.items():
            if k in self.pro_sliders:
                self.pro_sliders[k].set(v)
                self.update_pro_slider_text(k, v)
        
        # Apply FX Toggles
        self.fx_vocal_air.set(bool(fxs['v']))
        self.fx_drum_punch.set(bool(fxs['d']))
        self.fx_bass_warmth.set(bool(fxs['b']))
        self.fx_stereo_wall.set(bool(fxs['s']))
        
        self.current_preset = f"Pro:{name}"
        self.status_lbl.configure(text=f"Pro Preset Applied: [{name}]", text_color=COLOR_GOLD)

    def update_pro_slider_text(self, key, value):
        self.pro_slider_labels[key].configure(text=f"{int(value)} dB")

    def create_fx_toggle(self, parent, text, variable):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=5)
        
        chk = ctk.CTkCheckBox(f, text=text, variable=variable, font=("Arial", 12),
                              text_color="#CCC", fg_color=COLOR_GOLD, hover_color=COLOR_GOLD)
        chk.pack(side="left")

    def update_slider_text(self, key, value):
        self.slider_labels[key].configure(text=f"{int(value)} dB")

    def apply_preset(self, v, m, name=None):
        self.sliders['vocal'].set(v)
        self.sliders['mr'].set(m)
        self.update_slider_text('vocal', v)
        self.update_slider_text('mr', m)
        if name:
            self.current_preset = name
            self.status_lbl.configure(text=f"Preset Applied: [{name}] - Vocals {v}dB / MR {m}dB")
        else:
            self.current_preset = "Custom"
            self.status_lbl.configure(text=f"Applied: Vocal {v}dB / MR {m}dB")

    # --- 스레드 안전성 처리를 위한 메서드 ---
    def safe_update(self, func, *args, **kwargs):
        """메인 스레드에서 UI 업데이트 실행 (kwargs 지원)"""
        self.after(0, lambda: func(*args, **kwargs))

    def safe_status(self, msg, color=None):
        """스레드 안전하게 하단 상태바 텍스트와 색상 업데이트"""
        def update():
            self.status_lbl.configure(text=msg)
            if color: self.status_lbl.configure(text_color=color)
        self.after(0, update)

    def select_file(self):
        f = filedialog.askopenfilename(filetypes=[("Audio", "*.mp3 *.wav *.flac")])
        if f: 
            self.file_path = f
            short_name = os.path.basename(f)
            
            # [수정] 양쪽 탭 모두에 파일 정보 업데이트
            self.file_btn.configure(text=f"📄 {short_name}")
            self.file_label.configure(text=f"✅ {short_name}", text_color=COLOR_GOLD)
            
            if hasattr(self, 'pro_file_btn'):
                self.pro_file_btn.configure(text=f"📄 {short_name}", fg_color="#F59E0B")
            if hasattr(self, 'pro_file_label'):
                self.pro_file_label.configure(text=f"✅ LOADED: {short_name}", text_color="#00FFAA", font=("Arial", 13, "bold"))
                
            self.status_lbl.configure(text=f"Ready: {short_name}", text_color=COLOR_GOLD_DIM)
            
            # 파형 분석 스레드 시작
            threading.Thread(target=self.analyze_waveform_thread, args=(f,), daemon=True).start()

    def select_effect(self):
        f = filedialog.askopenfilename()
        if f:
            self.effect_path = f
            self.eff_btn.configure(text=f"🔔 {os.path.basename(f)}")

    def draw_initial_waveform(self, p=0):
        """[UI] 상단 시각화 바 업데이트 (진행도 p 반영)"""
        if not hasattr(self, 'waveform_data'):
            import random
            self.waveform_data = [random.randint(5, 25) for _ in range(250)]
            
        self.viz_canvas.delete("all")
        # 캔버스 실제 크기 확인
        w = self.viz_canvas.winfo_width()
        h = self.viz_canvas.winfo_height()
        if w <= 1 or w > 5000: w = 1200 # 초기 로딩 시 보정 (충분히 넓게)
        if h <= 1: h = 70
        
        mid = h / 2
        num_bars = len(self.waveform_data)
        prog_index = int(p * num_bars)
        
        # 배경 중심선
        self.viz_canvas.create_line(0, mid, w, mid, fill="#222", width=1)
        
        for i, height in enumerate(self.waveform_data):
            x = i * (w / num_bars)
            # 진행도에 따라 색상 변경 (진행된 부분: GOLD, 남은 부분: DARK)
            if i < prog_index:
                color = COLOR_GOLD
            elif i == prog_index:
                color = "white" # 현재 진행 헤드 시각화
            else:
                color = "#444"
            
            self.viz_canvas.create_line(x, mid - height, x, mid + height, fill=color, width=2)

    def analyze_waveform_thread(self, path):
        """[스레드] 오디오 데이터 로딩만 수행"""
        if not LIBROSA_AVAILABLE: return
        try:
            # 무거운 작업
            y, sr = librosa.load(path, sr=8000, duration=60)
            # UI 그리기는 메인 스레드로 넘김
            self.safe_update(self.draw_waveform_ui, y)
        except Exception as e:
            print(f"Waveform Error: {e}")

    def draw_waveform_ui(self, y):
        """[메인] 춤추는 비주얼라이저 그리기"""
        self.viz_canvas.delete("all")
        self.wave_lines = [] # 애니메이션용 라인 ID 저장
        self.wave_amps = []  # 원본 진폭 데이터 저장
        
        w = self.viz_canvas.winfo_width()
        h = self.viz_canvas.winfo_height()
        if w < 10: w = 1000
        
        # 성능과 디자인을 위해 막대 수를 줄이고 두껍게 (Bar Style)
        bar_count = 60 # 막대 개수
        step = w / bar_count
        audio_step = len(y) // bar_count
        
        for i in range(bar_count):
            idx = i * audio_step
            if idx < len(y):
                # 해당 구간의 평균 진폭 구하기
                chunk = y[idx:idx+audio_step]
                if len(chunk) > 0:
                    amp = np.mean(np.abs(chunk)) * (h) * 1.5 
                else: 
                    amp = 5
                
                x = i * step + (step/2)
                mid = h/2
                
                # 색상: 중앙부는 골드, 사이드는 어둡게
                dist = abs(i - bar_count/2) / (bar_count/2)
                if dist < 0.5: color = COLOR_GOLD
                else: color = "#555"
                
                # 라인 생성 (초기 상태)
                line = self.viz_canvas.create_line(x, mid-amp, x, mid+amp, fill=color, width=8, capstyle="round")
                self.wave_lines.append(line)
                self.wave_amps.append(amp)
        
        # 애니메이션 시작 (기존 루프 제거 후 시작)
        if hasattr(self, 'anim_id'):
            self.after_cancel(self.anim_id)
        self.animate_wave()

    def animate_status(self):
        """[UI] 하단 상태바 글로우 애니메이션 (숨쉬기 효과)"""
        try:
            # 럭셔리 골드 & 시안 그라데이션 사이클
            colors = [COLOR_GOLD, "#E5C158", "#F59E0B", "#00F2FF", "#00D2FF", "#00FFAA"]
            self.status_glow_step = (self.status_glow_step + 1) % len(colors)
            self.status_lbl.configure(text_color=colors[self.status_glow_step])
            self.after(500, self.animate_status)
        except:
            pass

    def animate_wave(self):
        """막대들을 춤추게 만드는 함수"""
        if not hasattr(self, 'wave_lines') or not self.wave_lines:
            # [FIX] 파일이 없을 때도 기본 파형이 둠칫둠칫하게 유지
            self.draw_initial_waveform(0)
            self.anim_id = self.after(100, self.animate_wave)
            return
        
        h = self.viz_canvas.winfo_height()
        mid = h/2
        
        for i, line in enumerate(self.wave_lines):
            base_amp = self.wave_amps[i]
            
            # 랜덤하게 춤추는 효과 (둠칫둠칫)
            # base_amp를 기준으로 0.8 ~ 1.2배 크기로 진동
            scale = random.uniform(0.7, 1.3)
            current_amp = base_amp * scale
            
            # 최소 높이 보장
            if current_amp < 2: current_amp = 2
            
            # 좌표 업데이트
            coords = self.viz_canvas.coords(line)
            if coords:
                x = coords[0]
                self.viz_canvas.coords(line, x, mid-current_amp, x, mid+current_amp)
        
        # 50ms마다 반복 (초당 20프레임)
        self.anim_id = self.after(50, self.animate_wave)

    # --- UI 업데이트용 메서드 (메인 스레드에서 실행됨) ---
    def update_progress_ui(self, msg, p):
        # [수정] 폰트 크기 최적화 (16 -> 14) 및 여백 확보로 잘림 방지
        self.status_lbl.configure(text=msg, font=("Arial", 14, "bold"), text_color="white")
        self.progress.set(p)
        
        # [NEW] 상단 파형 시각화 업데이트
        self.draw_initial_waveform(p)
        
        # [NEW] 실시간 오디오 파형(분석 후) 색상 업데이트
        if hasattr(self, 'wave_lines') and self.wave_lines:
            num_bars = len(self.wave_lines)
            prog_index = int(p * num_bars)
            for i, line in enumerate(self.wave_lines):
                color = COLOR_GOLD if i < prog_index else "#444"
                self.viz_canvas.itemconfig(line, fill=color)

    def finish_process_ui(self, save_path):
        self._set_run_btns_state("normal")
        self._update_run_btns(None, COLOR_GOLD, "black") # None means use default text
        self.is_processing = False
        
        # [NEW] 최근 출력 폴더 라벨 업데이트 (고급 피드백)
        self.last_out_path = save_path
        folder_display = os.path.basename(save_path)
        
        msg = f"📂 OPEN LAST: {folder_display}"
        if hasattr(self, 'last_output_lbl_1'):
            self.last_output_lbl_1.configure(text=msg, text_color="#00FFAA")
        if hasattr(self, 'last_output_lbl_2'):
            self.last_output_lbl_2.configure(text=msg, text_color="#00FFAA")
            
        if messagebox.askyesno("Done", f"Processing Complete!\n\nFolder: {folder_display}\nOpen output folder now?"):
            try:
                os.startfile(save_path)
            except Exception as e:
                messagebox.showwarning("Folder Open Error", f"Could not open folder automatically.\nPlease open manually:\n{save_path}")

    def _update_run_btns(self, text, fg_color, text_color):
        """[UX] 양쪽 탭의 실행 버튼 디자인 통합 업데이트"""
        if hasattr(self, 'run_btn_1'):
            txt1 = text if text else "✨ START MIXING"
            self.run_btn_1.configure(text=txt1, fg_color=fg_color, text_color=text_color)
        if hasattr(self, 'run_btn_2'):
            txt2 = text if text else "✨ START PRO MIX"
            self.run_btn_2.configure(text=txt2, fg_color=fg_color, text_color=text_color)

    def _set_run_btns_state(self, state):
        """[UX] 버튼 활성/비활성 제어"""
        for btn_attr in ['run_btn_1', 'run_btn_2']:
            if hasattr(self, btn_attr):
                getattr(self, btn_attr).configure(state=state)

    def open_last_output(self):
        """[UX] 최근 출력 폴더 열기 (라벨 클릭 시 동작)"""
        try:
            if hasattr(self, 'last_out_path') and os.path.exists(self.last_out_path):
                os.startfile(self.last_out_path)
            else:
                # 아직 처리가 안 되었거나 경로가 없으면 전체 결과 폴더 열기
                if os.path.exists(OUTPUT_DIR):
                    os.startfile(OUTPUT_DIR)
        except Exception as e:
            messagebox.showwarning("Folder Open Error", f"Could not open folder.\nPath: {getattr(self, 'last_out_path', OUTPUT_DIR)}")

    def error_process_ui(self, error_msg):
        self.status_lbl.configure(text="Error!", text_color="red")
        self._set_run_btns_state("normal")
        self._update_run_btns(None, COLOR_GOLD, "black")
        self.is_processing = False
        messagebox.showerror("Error", error_msg)

    def start_thread(self):
        if self.is_processing: return # 중복 실행 방지
        if not self.file_path: return messagebox.showwarning("No File", "Please select a file!")
        
        # [NEW] 현재 선택된 탭 감지
        current_tab = self.tabview.get()
        mode = "6-Stem" if "6-Stem" in current_tab else "2-Stem"
        
        # [중요] 스레드 시작 전 필요한 값을 미리 읽어옴
        params = {
            'v_val': self.sliders['vocal'].get(),
            'm_val': self.sliders['mr'].get(),
            'e_val': self.sliders['sfx'].get(),
            'gpu': self.gpu_var.get(),
            'mode': mode,
            'dolby': self.dolby_var.get() if hasattr(self, 'dolby_var') else False,
            'hifi': self.hifi_var.get() if hasattr(self, 'hifi_var') else False,
            # 6-Stem 전용 파라미터 추가
            'pro_mixer': {k: v.get() for k, v in self.pro_sliders.items()} if hasattr(self, 'pro_sliders') else {},
            'pro_fx': {
                'vocal_air': self.fx_vocal_air.get(),
                'drum_punch': self.fx_drum_punch.get(),
                'bass_warmth': self.fx_bass_warmth.get(),
                'stereo_wall': self.fx_stereo_wall.get()
            } if hasattr(self, 'fx_vocal_air') else {}
        }
        
        self.is_processing = True
        # 현재 프리셋 이름을 파라미터로 넘김
        params['preset_name'] = self.current_preset
        
        # 버튼 디자인 업데이트
        self._set_run_btns_state("disabled")
        self._update_run_btns("⏳ Processing...", "#F59E0B", "black")
        threading.Thread(target=self.process, args=(params,), daemon=True).start()

    def process(self, params):
        """[스레드] 무거운 AI 작업 수행 (Safe Temp File 방식 적용)"""
        from pydub import AudioSegment, effects
        try:
            def cb(msg, p):
                self.safe_update(self.update_progress_ui, msg, p)
            
            # [Step 1] 안전해제: 복잡한 파일명 에러 방지를 위해 임시 파일로 복사
            if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
            
            ext = os.path.splitext(self.file_path)[1]
            safe_input = os.path.join(TEMP_DIR, f"temp_input{ext}")
            shutil.copyfile(self.file_path, safe_input)
            
            # [Step 2] 분리 (이제 safe_input을 사용하므로 에러 없음)
            # separate 함수는 폴더 경로와 모델명을 반환함
            res_dir, model_name = separate(safe_input, params['gpu'], params['mode'], cb)
            
            # [Step 3] 결과 저장 (output_result 바로 아래에 저장)
            base_filename = clean_name(self.file_path)
            
            # [수정] 폴더 생성하지 않고 바로 OUTPUT_DIR 사용
            save_path = OUTPUT_DIR 
            if not os.path.exists(save_path): os.makedirs(save_path)
            
            final_output = ""

            # --- 6-Stem 혁명적 믹싱 모드 처리 ---
            if params['mode'] == "6-Stem":
                cb("Loading 6-Stem Channels...", 0.6)
                stems_data = {}
                stem_files = ["vocals.wav", "drums.wav", "bass.wav", "guitar.wav", "piano.wav", "other.wav"]
                
                # [1] 모든 줄기 로드 및 기본 게인 적용
                for s in stem_files:
                    src = os.path.join(res_dir, s)
                    if os.path.exists(src):
                        name = s.replace(".wav", "")
                        gain = params['pro_mixer'].get(name, 0)
                        audio = AudioSegment.from_file(src) + gain
                        stems_data[name] = audio
                
                # [2] 개별 줄기별 혁명적 프로세싱 (Advanced FX)
                pro_fx = params.get('pro_fx', {})
                
                # 🎤 Vocal Air: 고음역대 선명도와 공기감 추가
                if pro_fx.get('vocal_air') and 'vocals' in stems_data:
                    cb("Polishing Vocals (Air)...", 0.7)
                    try:
                        import io
                        raw = stems_data['vocals'].export(format="wav").read()
                        cmd = ["ffmpeg", "-i", "pipe:0", "-af", "firequalizer=gain='if(gt(f,10000), 4, 0)'", "-f", "wav", "pipe:1"]
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                        out, _ = proc.communicate(input=raw)
                        if proc.returncode == 0: stems_data['vocals'] = AudioSegment.from_wav(io.BytesIO(out))
                    except: pass

                # 🥁 Drum Punch: 타격감 및 어택 강화
                if pro_fx.get('drum_punch') and 'drums' in stems_data:
                    cb("Powering Up Drums...", 0.75)
                    stems_data['drums'] = effects.compress_dynamic_range(stems_data['drums'], threshold=-15, ratio=3.0, attack=5, release=100)

                # 🔥 Bass Warmth: 저음의 깊이와 따뜻함
                if pro_fx.get('bass_warmth') and 'bass' in stems_data:
                    cb("Deeper Bass Processing...", 0.8)
                    stems_data['bass'] = stems_data['bass'].low_pass_filter(500) + 2 # 압도적 중저음

                # ↔️ Stereo Wall (Guitar/Piano): 스테레오 이미지 확장
                if pro_fx.get('stereo_wall'):
                    cb("Widening Soundstage...", 0.85)
                    for k in ['guitar', 'piano']:
                        if k in stems_data:
                            try:
                                import io
                                raw = stems_data[k].export(format="wav").read()
                                cmd = ["ffmpeg", "-i", "pipe:0", "-af", "stereowidener=level_in=1:level_out=1:crossfeed=0.4:drymix=0.6", "-f", "wav", "pipe:1"]
                                startupinfo = subprocess.STARTUPINFO()
                                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                                out, _ = proc.communicate(input=raw)
                                if proc.returncode == 0: stems_data[k] = AudioSegment.from_wav(io.BytesIO(out))
                            except: pass

                # [3] 최종 융합 (Revolution Fusion)
                cb("Master Fusion in Progress...", 0.9)
                final = None
                for name in stems_data:
                    audio = stems_data[name]
                    if final is None: 
                        final = audio
                    else: 
                        final = final.overlay(audio)
                
                # [안전장치] 만약 어떤 이유로든 데이터가 없다면 빈 오디오 생성
                if final is None:
                    final = AudioSegment.silent(duration=1000)

                # [4] 마스터 글루 컴프레션 및 노멀라이즈
                final = effects.compress_dynamic_range(final, threshold=-12.0, ratio=2.5)
                
                # Dolby Style (6-Stem Revolution Mix 적용)
                if params.get('dolby', False):
                    cb("Applying Dolby Effect...", 0.94)
                    try:
                        raw = final.export(format="wav").read()
                        cmd = [
                            "ffmpeg", "-i", "pipe:0",
                            "-af", "stereotools=mlev=1:slev=1.4,bass=g=3:f=100,treble=g=3:f=10000",
                            "-f", "wav", "pipe:1"
                        ]
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                        out, _ = proc.communicate(input=raw)
                        if proc.returncode == 0: final = AudioSegment.from_wav(io.BytesIO(out))
                    except: pass

                # Hi-Fi Polishing (6-Stem Revolution Mix 적용)
                if params.get('hifi', False):
                    cb("Optimizing Hi-Fi Quality...", 0.96)
                    try:
                        raw = final.export(format="wav").read()
                        cmd = ["ffmpeg", "-i", "pipe:0", "-af", "treble=g=4:f=14000", "-f", "wav", "pipe:1"]
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                        out, _ = proc.communicate(input=raw)
                        if proc.returncode == 0: final = AudioSegment.from_wav(io.BytesIO(out))
                    except: pass

                final = effects.normalize(final, headroom=0.1)
                
                # [5] 결과 저장 및 개별 줄기 백업
                # [수정] 노래 제목 폴더 내부에 '음원분리' 및 '미디분리' 서브 폴더 생성
                song_folder = os.path.join(save_path, base_filename)
                audio_dir = os.path.join(song_folder, "음원분리")
                os.makedirs(audio_dir, exist_ok=True)
                os.makedirs(os.path.join(song_folder, "미디분리"), exist_ok=True)
                
                preset_suffix = params.get('preset_name', 'Revolution').replace("Pro:", "")
                final_name = f"{base_filename}_{preset_suffix}"
                
                if params.get('hifi', False):
                    final_output_file = os.path.join(audio_dir, f"{final_name}.wav")
                    final.export(final_output_file, format="wav")
                else:
                    final_output_file = os.path.join(audio_dir, f"{final_name}.mp3")
                    final.export(final_output_file, format="mp3", bitrate="320k")
                
                # 개별 줄기도 해당 폴더에 보관
                for name, audio in stems_data.items():
                    audio.export(os.path.join(audio_dir, f"6S_{name}_{base_filename}.wav"), format="wav")
                
                final_output = song_folder # 결과 폴더를 리턴
                self.last_output_dir = song_folder # [추가] MIDI 변환을 위해 경로 저장
            
            # --- 2-Stem 모드 처리 ---
            else:
                v_path = os.path.join(res_dir, "vocals.wav")
                m_path = os.path.join(res_dir, "no_vocals.wav")
                
                if not os.path.exists(v_path):
                     raise Exception(f"결과 파일 없음: {v_path}")

                cb("Mixing Vocals & Inst...", 0.85)
                v = AudioSegment.from_file(v_path).high_pass_filter(80) + params['v_val']
                m = AudioSegment.from_file(m_path) + params['m_val']
                final = v.overlay(m)
                
                if self.effect_path:
                    try: final = final.overlay(AudioSegment.from_file(self.effect_path) + params['e_val'])
                    except: pass
                
                cb("Mastering Audio...", 0.9)
                final = effects.compress_dynamic_range(final, threshold=-12.0, ratio=2.0)
                
                # Dolby Style
                if params.get('dolby', False):
                    cb("Applying Dolby Effect...", 0.95)
                    try:
                        import io
                        raw = final.export(format="wav").read()
                        cmd = [
                            "ffmpeg", "-i", "pipe:0",
                            "-af", "stereotools=mlev=1:slev=1.4,bass=g=3:f=100,treble=g=3:f=10000",
                            "-f", "wav", "pipe:1"
                        ]
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                        out, _ = proc.communicate(input=raw)
                        if proc.returncode == 0:
                            final = AudioSegment.from_wav(io.BytesIO(out))
                    except: pass

                # Hi-Fi Polishing
                if params.get('hifi', False):
                    cb("Optimizing Hi-Fi Quality...", 0.98)
                    try:
                        import io
                        raw = final.export(format="wav").read()
                        cmd = [
                            "ffmpeg", "-i", "pipe:0",
                            "-af", "treble=g=4:f=14000",
                            "-f", "wav", "pipe:1"
                        ]
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                        out, _ = proc.communicate(input=raw)
                        if proc.returncode == 0:
                            final = AudioSegment.from_wav(io.BytesIO(out))
                    except: pass

                # 최종 노멀라이즈 및 저장
                final = effects.normalize(final, headroom=0.1)
                
                # [수정] 파일명 폴더 내부에 서브 폴더 구성
                song_folder = os.path.join(save_path, base_filename)
                audio_dir = os.path.join(song_folder, "음원분리")
                os.makedirs(audio_dir, exist_ok=True)
                os.makedirs(os.path.join(song_folder, "미디분리"), exist_ok=True)

                preset_prefix = params.get('preset_name', 'Custom')
                final_name = f"{base_filename}_{preset_prefix}"
                
                if params.get('hifi', False):
                    final_output_file = os.path.join(audio_dir, f"{final_name}_HiFi.wav")
                    final.export(final_output_file, format="wav")
                else:
                    final_output_file = os.path.join(audio_dir, f"{final_name}.mp3")
                    final.export(final_output_file, format="mp3", bitrate="320k")

                v.export(os.path.join(audio_dir, f"Vocals_{base_filename}.wav"), format="wav")
                m.export(os.path.join(audio_dir, f"Inst_{base_filename}.wav"), format="wav")
                
                final_output = song_folder
                self.last_output_dir = song_folder # [추가] MIDI 변환을 위해 경로 저장

            cb("Done!", 1.0)
            self.safe_update(self.finish_process_ui, final_output)
            
            # [청소] 임시 폴더 삭제 (output_result는 건드리지 않음)
            try: shutil.rmtree(TEMP_DIR, ignore_errors=True)
            except: pass

        except Exception as e:
            self.safe_update(self.error_process_ui, str(e))
    
    # ============================================================
    # [NEW] Voice Enhancement Tab (RVC Integration)
    # ============================================================
    
    def setup_rvc_tab(self):
        """AI Vocal Enhancement (RVC) 탭 UI 구성"""
        self.tab_rvc.grid_columnconfigure(0, weight=1)
        
        # [Header]
        rvc_header = ctk.CTkFrame(self.tab_rvc, fg_color="transparent")
        rvc_header.pack(fill="x", padx=30, pady=(15, 0))
        ctk.CTkLabel(rvc_header, text="🎤 AI VOCAL ENHANCEMENT & COVER", font=("Montserrat", 22, "bold"), text_color=COLOR_GOLD).pack(side="left")
        
        # [Main Content]
        rvc_body = ctk.CTkFrame(self.tab_rvc, fg_color="transparent")
        rvc_body.pack(fill="both", expand=True, padx=30, pady=5)
        rvc_body.grid_columnconfigure(0, weight=6)
        rvc_body.grid_columnconfigure(1, weight=4)
        
        # 1. 파일 설정 (왼쪽)
        rvc_file_frame = GlassFrame(rvc_body)
        rvc_file_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        
        ctk.CTkLabel(rvc_file_frame, text="📁 SOURCE SELECTION", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(10, 5))
        
        # 보컬 선택
        self.rvc_vocal_btn = self.create_file_btn(rvc_file_frame, "🎤 Select Vocal Audio (WAV/MP3)", self.select_enhance_vocal)
        self.rvc_vocal_btn.pack(fill="x", padx=20, pady=5)
        self.rvc_vocal_label = ctk.CTkLabel(rvc_file_frame, text="선택안함", font=FONT_SMALL, text_color=COLOR_TEXT_DIM)
        self.rvc_vocal_label.pack(anchor="w", padx=25, pady=(0, 5))
        
        # MR 선택
        self.rvc_mr_btn = self.create_file_btn(rvc_file_frame, "🎹 Select Inst (Optional)", self.select_enhance_mr)
        self.rvc_mr_btn.pack(fill="x", padx=20, pady=5)
        self.rvc_mr_label = ctk.CTkLabel(rvc_file_frame, text="선택안함", font=FONT_SMALL, text_color=COLOR_TEXT_DIM)
        self.rvc_mr_label.pack(anchor="w", padx=25, pady=(0, 5))
        
        # RVC 모델 선택
        self.rvc_model_btn = self.create_file_btn(rvc_file_frame, "🧠 Select RVC Model (.pth)", self.select_enhance_model)
        self.rvc_model_btn.pack(fill="x", padx=20, pady=5)
        self.rvc_model_label = ctk.CTkLabel(rvc_file_frame, text="선택안함", font=FONT_SMALL, text_color=COLOR_TEXT_DIM)
        self.rvc_model_label.pack(anchor="w", padx=25, pady=(0, 5))
        
        # [NEW] RVC Index 파일 선택
        self.rvc_index_btn = self.create_file_btn(rvc_file_frame, "🔍 Select Index File (.index)", self.select_enhance_index)
        self.rvc_index_btn.pack(fill="x", padx=20, pady=5)
        self.rvc_index_label = ctk.CTkLabel(rvc_file_frame, text="선택안함 (권장사항)", font=FONT_SMALL, text_color=COLOR_TEXT_DIM)
        self.rvc_index_label.pack(anchor="w", padx=25, pady=(0, 5))
        
        # 실행 버튼
        self.enhance_start_btn = ctk.CTkButton(rvc_file_frame, text="🚀 START VOCAL ENHANCEMENT", font=("Arial", 16, "bold"),
                                               height=50, fg_color=COLOR_GOLD, text_color="black", hover_color="#E5C158",
                                               command=self.start_voice_enhancement)
        self.enhance_start_btn.pack(fill="x", padx=20, pady=20)
        
        # 2. 고급 설정 (오른쪽)
        rvc_settings_frame = GlassFrame(rvc_body)
        rvc_settings_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        
        ctk.CTkLabel(rvc_settings_frame, text="⚙️ NEURAL VOICE SETTINGS", font=FONT_BOLD, text_color=COLOR_GOLD_DIM).pack(anchor="w", padx=20, pady=(10, 10))
        
        # F0 Algorithm
        ctk.CTkLabel(rvc_settings_frame, text="F0 추출 알고리즘:", font=FONT_SMALL, text_color="white").pack(anchor="w", padx=20)
        self.f0_method_var = ctk.StringVar(value="rmvpe")
        self.f0_method_menu = ctk.CTkOptionMenu(rvc_settings_frame, values=["rmvpe", "pm", "harvest"], 
                                                variable=self.f0_method_var, fg_color="#222", button_color=COLOR_GOLD, 
                                                button_hover_color="#D4AF37", text_color="white")
        self.f0_method_menu.pack(fill="x", padx=20, pady=(5, 15))
        
        # Index Rate Slider
        ctk.CTkLabel(rvc_settings_frame, text="Index Rate (검색 강도):", font=FONT_SMALL, text_color="white").pack(anchor="w", padx=20)
        self.index_rate_var = ctk.DoubleVar(value=0.75)
        self.index_rate_slider = ctk.CTkSlider(rvc_settings_frame, from_=0, to=1, variable=self.index_rate_var,
                                               button_color=COLOR_GOLD, button_hover_color="#D4AF37", progress_color=COLOR_GOLD)
        self.index_rate_slider.pack(fill="x", padx=20, pady=(5, 15))
        
        # Protect Slider
        ctk.CTkLabel(rvc_settings_frame, text="Protect (무자각 보호):", font=FONT_SMALL, text_color="white").pack(anchor="w", padx=20)
        self.protect_var = ctk.DoubleVar(value=0.33)
        self.protect_slider = ctk.CTkSlider(rvc_settings_frame, from_=0, to=0.5, variable=self.protect_var,
                                            button_color=COLOR_GOLD, button_hover_color="#D4AF37", progress_color=COLOR_GOLD)
        self.protect_slider.pack(fill="x", padx=20, pady=(5, 15))
        
        # Filter Radius
        ctk.CTkLabel(rvc_settings_frame, text="Filter Radius (노이즈 제거):", font=FONT_SMALL, text_color="white").pack(anchor="w", padx=20)
        self.filter_radius_var = ctk.IntVar(value=3)
        self.filter_radius_slider = ctk.CTkSlider(rvc_settings_frame, from_=0, to=7, number_of_steps=7, variable=self.filter_radius_var,
                                                  button_color=COLOR_GOLD, button_hover_color="#D4AF37", progress_color=COLOR_GOLD)
        self.filter_radius_slider.pack(fill="x", padx=20, pady=(5, 15))

        # [NEW] Pitch Shift Slider
        ctk.CTkLabel(rvc_settings_frame, text="Pitch Shift (음정 조절):", font=FONT_SMALL, text_color="white").pack(anchor="w", padx=20)
        self.rvc_pitch_var = ctk.IntVar(value=0)
        h_frame = ctk.CTkFrame(rvc_settings_frame, fg_color="transparent")
        h_frame.pack(fill="x", padx=20)
        self.rvc_pitch_lbl = ctk.CTkLabel(h_frame, text="0", font=("Arial", 12, "bold"), text_color=COLOR_GOLD)
        self.rvc_pitch_lbl.pack(side="right")
        self.rvc_pitch_slider = ctk.CTkSlider(rvc_settings_frame, from_=-12, to=12, number_of_steps=24, variable=self.rvc_pitch_var,
                                                button_color="#00FFAA", button_hover_color="#00D2FF", progress_color="#00FFAA",
                                                command=lambda v: self.rvc_pitch_lbl.configure(text=f"{int(v):+d} semitones"))
        self.rvc_pitch_slider.pack(fill="x", padx=20, pady=(5, 15))

    def select_enhance_vocal(self):
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.wav *.mp3 *.flac *.m4a")])
        if path:
            self.rvc_vocal_path = path
            self.rvc_vocal_label.configure(text=os.path.basename(path), text_color=COLOR_GOLD)

    def select_enhance_mr(self):
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.wav *.mp3 *.flac *.m4a")])
        if path:
            self.rvc_mr_path = path
            self.rvc_mr_label.configure(text=os.path.basename(path), text_color=COLOR_GOLD)

    def select_enhance_model(self):
        path = filedialog.askopenfilename(filetypes=[("RVC Model", "*.pth")])
        if path:
            self.rvc_model_path = path
            self.rvc_model_label.configure(text=os.path.basename(path), text_color=COLOR_GOLD)

    def select_enhance_index(self):
        path = filedialog.askopenfilename(filetypes=[("RVC Index", "*.index")])
        if path:
            self.rvc_index_path = path
            self.rvc_index_label.configure(text=os.path.basename(path), text_color=COLOR_GOLD)

    def start_voice_enhancement(self):
        if not hasattr(self, 'rvc_vocal_path') or not hasattr(self, 'rvc_model_path'):
            messagebox.showwarning("Warning", "Vocal audio and RVC model must be selected.")
            return
        
        if not self.official_rvc:
            messagebox.showerror("Error", "RVC engine not initialized. Please check dependencies.")
            return
            
        self.enhance_start_btn.configure(state="disabled", text="⏳ Processing...")
        threading.Thread(target=self.run_voice_enhancement_process, daemon=True).start()

    def run_voice_enhancement_process(self):
        try:
            self.safe_status("🔥 AI Voice Conversion Started...", COLOR_GOLD)
            output_file = self.official_rvc.convert(
                self.rvc_vocal_path,
                self.rvc_model_path,
                index_path=getattr(self, 'rvc_index_path', None),
                f0_method=self.f0_method_var.get(),
                index_rate=self.index_rate_var.get(),
                protect=self.protect_var.get(),
                filter_radius=self.filter_radius_var.get(),
                pitch_shift=self.rvc_pitch_var.get()
            )
            
            if output_file and os.path.exists(output_file):
                self.safe_status("✅ RVC Enhancement Complete!", "#00FF7F")
                
                # [NEW] Professional Post-Processing (Vocal Air & Bass)
                try:
                    self.safe_status("💎 Diamond Mastering in Progress...", COLOR_GOLD)
                    vocal = AudioSegment.from_file(output_file)
                    
                    # 1. Vocal Air (High shelf boost simulation)
                    vocal = vocal.set_frame_rate(48000)
                    highs = vocal.high_pass_filter(10000)
                    vocal = vocal.overlay(highs - 3) # +3dB air
                    
                    # 2. Bass Warmth (Subtle low-end boost)
                    lows = vocal.low_pass_filter(250)
                    vocal = vocal.overlay(lows - 6) # subtle warmth
                    
                    vocal = effects.normalize(vocal, headroom=0.1)
                    vocal.export(output_file, format="wav")
                    print("✓ AI Voice Diamond Post-Processing applied.")
                except Exception as ex:
                    print(f"Post-processing failed: {ex}")

                # MR과 병합 처리 (있는 경우)
                if hasattr(self, 'rvc_mr_path') and self.rvc_mr_path:
                    self.safe_status("🎹 Merging with Instrument...", COLOR_GOLD)
                    vocal = AudioSegment.from_file(output_file)
                    inst = AudioSegment.from_file(self.rvc_mr_path)
                    final = vocal.overlay(inst)
                    final_path = output_file.replace(".wav", "_mixed.wav")
                    final.export(final_path, format="wav")
                    output_file = final_path
                
                self.safe_status("✅ RVC Enhancement Complete!", "#00FF7F")
                self.after(0, lambda: messagebox.showinfo("Success", f"Conversion complete!\nSaved to: {output_file}"))
                os.startfile(os.path.dirname(output_file))
            else:
                raise Exception("RVC conversion failed or returned no file.")
                
        except Exception as e:
            self.safe_status(f"❌ RVC Error: {str(e)}", "#FF5555")
            self.after(0, lambda e=e: messagebox.showerror("RVC Error", str(e)))
        finally:
            self.after(0, lambda: self.enhance_start_btn.configure(state="normal", text="🚀 START VOCAL ENHANCEMENT"))

    # ============================================================
    # [Restored] Core Process Logic
    # ============================================================
    
    def clean_lyrics_action(self):
        """가사에서 코드 제거 (ChordRemover 사용)"""
        try:
            raw_text = self.raw_lyrics_text.get("1.0", "end-1c")
            
            if not raw_text.strip():
                self.safe_status("⚠️ 가사를 입력해주세요.", "#FFAA00")
                return
            
            # ChordRemover로 처리
            self.safe_status("🎵 Cleaning lyrics...", COLOR_GOLD)
            cleaned = self.chord_remover.process(raw_text)
            
            # 결과 표시
            self.clean_lyrics_text.delete("1.0", "end")
            self.clean_lyrics_text.insert("1.0", cleaned)
            
            # 저장
            self.cleaned_lyrics = cleaned
            
            # 통계 표시
            original_len = len(raw_text)
            cleaned_len = len(cleaned)
            reduction = int((1 - cleaned_len / original_len) * 100) if original_len > 0 else 0
            
            self.safe_status(f"✅ Lyrics cleaned! ({original_len} → {cleaned_len} chars, {reduction}% reduced)", "#00FF7F")
            
        except Exception as e:
            self.safe_status(f"❌ Error: {str(e)}", "#FF5555")
    
    def load_script_preset(self, value):
        """
        훈련용 대본 프리셋 로드
        
        Args:
            value: 선택된 프리셋 ("CEO 모드", "내레이션", "유튜버", "Custom")
        """
        if value == "Custom":
            return  # Custom은 사용자가 직접 입력
        
        # 프리셋 매핑
        preset_map = {
            "CEO 모드": "CEO 모드 (비전 선포형)",
            "내레이션": "내레이션 모드 (감성 에세이형)",
            "유튜버": "유튜버 모드 (튜토리얼 설명형)"
        }
        
        script_key = preset_map.get(value)
        if script_key and script_key in TRAINING_SCRIPTS:
            script = TRAINING_SCRIPTS[script_key]
            
            # 텍스트박스에 로드
            self.raw_lyrics_text.delete("1.0", "end")
            self.raw_lyrics_text.insert("1.0", script)
            
            self.safe_status(f"📜 Loaded: {value} script ({len(script)} chars)", COLOR_GOLD)
    
    def save_cleaned_lyrics(self):
        """정제된 가사를 파일로 저장"""
        try:
            if not self.cleaned_lyrics:
                messagebox.showwarning("Warning", "먼저 'Clean Lyrics'를 실행해주세요.")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile="cleaned_lyrics.txt"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.cleaned_lyrics)
                
                self.safe_status(f"💾 Saved: {os.path.basename(file_path)}", "#00FF7F")
                messagebox.showinfo("Success", f"가사가 저장되었습니다:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"저장 실패:\n{str(e)}")
    
    def add_training_files(self):
        """훈련용 오디오 파일 추가"""
        try:
            files = filedialog.askopenfilenames(
                title="Select Training Audio Files",
                filetypes=[
                    ("Audio files", "*.wav *.mp3 *.flac *.ogg"),
                    ("WAV files", "*.wav"),
                    ("All files", "*.*")
                ]
            )
            
            if files:
                for file in files:
                    if file not in self.training_files:
                        self.training_files.append(file)
                        self.training_listbox.insert(tk.END, os.path.basename(file))
                
                self.update_file_count()
                self.safe_status(f"➕ Added {len(files)} file(s)", "#00FF7F")
        
        except Exception as e:
            messagebox.showerror("Error", f"파일 추가 실패:\n{str(e)}")
    
    def remove_training_files(self):
        """선택된 파일 제거"""
        try:
            selected_indices = self.training_listbox.curselection()
            
            if not selected_indices:
                messagebox.showwarning("Warning", "제거할 파일을 선택해주세요.")
                return
            
            # 역순으로 제거 (인덱스 변경 방지)
            for index in reversed(selected_indices):
                self.training_listbox.delete(index)
                del self.training_files[index]
            
            self.update_file_count()
            self.safe_status(f"➖ Removed {len(selected_indices)} file(s)", COLOR_GOLD)
        
        except Exception as e:
            messagebox.showerror("Error", f"파일 제거 실패:\n{str(e)}")
    
    def update_file_count(self):
        """파일 개수 업데이트"""
        count = len(self.training_files)
        self.file_count_lbl.configure(text=f"Files: {count}")
    
    def export_training_package(self):
        """GPT-SoVITS 훈련 패키지 생성"""
        try:
            # 검증
            if not self.cleaned_lyrics:
                messagebox.showwarning("Warning", "먼저 가사를 정제해주세요 (Clean Lyrics).")
                return
            
            if len(self.training_files) == 0:
                messagebox.showwarning("Warning", "훈련용 오디오 파일을 추가해주세요.")
                return
            
            # 폴더 생성
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            package_name = f"GPT_SoVITS_Training_{timestamp}"
            package_dir = os.path.join(OUTPUT_DIR, package_name)
            audio_dir = os.path.join(package_dir, "audio")
            
            os.makedirs(audio_dir, exist_ok=True)
            
            self.safe_status("📦 Creating training package...", COLOR_GOLD)
            self.progress.set(0.1)
            
            # 1. 가사 저장
            lyrics_path = os.path.join(package_dir, "cleaned_lyrics.txt")
            with open(lyrics_path, 'w', encoding='utf-8') as f:
                f.write(self.cleaned_lyrics)
            
            self.progress.set(0.3)
            
            # 2. 오디오 파일 복사
            total_files = len(self.training_files)
            for i, src_file in enumerate(self.training_files):
                # 파일명 정리 (001, 002, 003 형식)
                ext = os.path.splitext(src_file)[1]
                dst_name = f"sample_{i+1:03d}{ext}"
                dst_path = os.path.join(audio_dir, dst_name)
                
                shutil.copy2(src_file, dst_path)
                
                # 진행률 업데이트
                progress = 0.3 + (0.5 * (i + 1) / total_files)
                self.progress.set(progress)
            
            self.progress.set(0.8)
            
            # 3. README 생성
            readme_path = os.path.join(package_dir, "README.txt")
            readme_content = f"""
GPT-SoVITS Training Package
===========================

Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}
Created by: Next-Gen AI Audio Workstation

📁 Package Contents:
-------------------
- cleaned_lyrics.txt : 정제된 가사 (코드 제거됨)
- audio/ : 훈련용 오디오 파일 ({total_files}개)

🎯 Usage Instructions:
----------------------
1. GPT-SoVITS 프로그램을 실행하세요
2. 'audio' 폴더의 파일들을 훈련 데이터로 사용하세요
3. 'cleaned_lyrics.txt'의 가사를 참고하세요
4. 음성 합성 모델 훈련을 시작하세요!

💡 Tips:
--------
- WAV 형식이 가장 좋은 품질을 제공합니다
- 최소 10개 이상의 샘플을 권장합니다
- 각 샘플은 3-10초 길이가 적당합니다
- 배경 소음이 적은 깨끗한 음성을 사용하세요

📧 Support:
-----------
Created by Park Jae-soo (SKY Group)
Next-Gen AI Audio Workstation v3.1
"""
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            self.progress.set(1.0)
            
            # 완료 메시지
            self.safe_status(f"✅ Package created: {package_name}", "#00FF7F")
            
            # 폴더 열기
            result = messagebox.askyesno(
                "Success", 
                f"훈련 패키지가 생성되었습니다!\n\n"
                f"위치: {package_dir}\n\n"
                f"파일: {total_files}개\n"
                f"가사: {len(self.cleaned_lyrics)} 글자\n\n"
                f"폴더를 열까요?"
            )
            
            if result:
                os.startfile(package_dir)
            
            self.progress.set(0)
        
        except Exception as e:
            self.safe_status(f"❌ Export failed: {str(e)}", "#FF5555")
            messagebox.showerror("Error", f"패키지 생성 실패:\n{str(e)}")
            self.progress.set(0)
    
    def start_voice_training(self):
        """
        실전 음성 훈련 시작 (스레드 사용)
        """
        try:
            # 검증
            if self.is_training:
                messagebox.showwarning("Warning", "이미 훈련이 진행 중입니다!")
                return
            
            model_name = self.training_model_name.get().strip()
            if not model_name:
                model_name = "JaeSoo_Voice"
            
            # 최신 패키지 찾기
            package_dir = self.get_latest_training_package()
            if not package_dir:
                messagebox.showwarning(
                    "Warning",
                    "훈련 패키지를 찾을 수 없습니다!\n\n"
                    "먼저 'Generate Training Package'를 실행해주세요."
                )
                return
            
            # Quality preset to epochs mapping
            quality_map = {
                "Fast (5 epochs)": 5,
                "Balanced (15 epochs)": 15,
                "Best (30 epochs)": 30
            }
            epochs = quality_map.get(self.training_quality.get(), 15)
            
            # 확인 대화상자
            result = messagebox.askyesno(
                "Start Training",
                f"음성 훈련을 시작하시겠습니까?\n\n"
                f"모델 이름: {model_name}\n"
                f"품질: {self.training_quality.get()}\n"
                f"예상 시간: {epochs * 0.5:.0f}-{epochs * 1:.0f}분\n\n"
                f"훈련 중에는 다른 작업을 하실 수 있습니다."
            )
            
            if not result:
                return
            
            # UI 상태 변경
            self.is_training = True
            self.start_training_btn.configure(state="disabled", text="⏳ Training in Progress...")
            self.training_status_lbl.configure(text="Initializing...", text_color=COLOR_GOLD)
            self.progress.set(0)
            
            # 스레드로 훈련 시작
            training_thread = threading.Thread(
                target=self.training_worker,
                args=(package_dir, model_name, epochs),
                daemon=True
            )
            training_thread.start()
            
        except Exception as e:
            self.safe_status(f"❌ Training start failed: {str(e)}", "#FF5555")
            messagebox.showerror("Error", f"훈련 시작 실패:\n{str(e)}")
    
    def get_latest_training_package(self):
        """최신 훈련 패키지 폴더 찾기"""
        try:
            packages = [
                os.path.join(OUTPUT_DIR, d)
                for d in os.listdir(OUTPUT_DIR)
                if d.startswith("GPT_SoVITS_Training_") and os.path.isdir(os.path.join(OUTPUT_DIR, d))
            ]
            
            if packages:
                return max(packages, key=os.path.getmtime)
            return None
        except:
            return None
    
    def training_worker(self, package_dir, model_name, epochs):
        """
        훈련 워커 스레드 (백그라운드 실행)
        """
        try:
            self.safe_status(f"🔥 Training started: {model_name}", COLOR_GOLD)
            
            # 훈련 실행
            result_path = self.voice_trainer.train(
                package_path=package_dir,
                model_name=model_name,
                epochs=epochs,
                progress_callback=self.training_progress_callback
            )
            
            # 완료 처리
            if result_path:
                self.safe_status(f"✅ Training complete! Model: {model_name}.pth", "#00FF7F")
                
                # 완료 대화상자 (메인 스레드에서 실행)
                self.after(100, lambda: self.show_training_complete(result_path, model_name))
            else:
                self.safe_status("❌ Training failed", "#FF5555")
                self.after(100, lambda: messagebox.showerror("Error", "훈련이 실패했습니다. 로그를 확인해주세요."))
            
        except Exception as e:
            self.safe_status(f"❌ Training error: {str(e)}", "#FF5555")
            self.after(100, lambda: messagebox.showerror("Training Error", f"훈련 중 오류:\n{str(e)}"))
        
        finally:
            # UI 복구
            self.is_training = False
            self.safe_update(self.start_training_btn.configure, state="normal", text="🔥 START TRAINING (Generate .pth Model)")
            self.safe_update(self.training_status_lbl.configure, text="Ready to train", text_color="#888")
            self.safe_update(self.progress.set, 0)
    
    def training_progress_callback(self, progress, message):
        """
        훈련 진행률 콜백 (스레드 안전)
        
        Args:
            progress: 0-100 정수
            message: 상태 메시지
        """
        # 진행률 업데이트
        progress_value = progress / 100.0
        self.safe_update(self.progress.set, progress_value)
        
        # 상태 메시지 업데이트
        self.safe_update(self.training_status_lbl.configure, text=message, text_color=COLOR_GOLD)
        self.safe_status(message, COLOR_GOLD)
    
    def show_training_complete(self, model_path, model_name):
        """훈련 완료 대화상자"""
        model_dir = os.path.dirname(model_path)
        
        result = messagebox.askyesno(
            "Training Complete!",
            f"🎉 음성 모델 훈련이 완료되었습니다!\n\n"
            f"모델: {model_name}.pth\n"
            f"위치: {model_dir}\n\n"
            f"폴더를 열까요?"
        )
        
        if result:
            os.startfile(model_dir)

    def run_system_diagnosis(self):
        """[NEW] 시스템 자가 진단 기능 (GPU, FFmpeg, 패키지 확인)"""
        def worker():
            results = []
            results.append("🔍 NEXT-GEN AI SYSTEM DIAGNOSIS")
            results.append("-" * 40)
            
            # 1. GPU Check
            try:
                import torch
                cuda_avail = torch.cuda.is_available()
                results.append(f"• PyTorch CUDA: {'✅ OK' if cuda_avail else '❌ FAILED'}")
                if cuda_avail:
                    results.append(f"  - Device: {torch.cuda.get_device_name(0)}")
                    results.append(f"  - Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            except Exception as e:
                results.append(f"• PyTorch Trace: {str(e)}")

            # 2. FFmpeg Check
            ffmpeg_ok = os.path.exists(ffmpeg_exe)
            results.append(f"• FFmpeg Engine: {'✅ OK' if ffmpeg_ok else '❌ MISSING (run setup.bat)'}")

            # 3. RVC Assets Check
            rvc_asset = r"C:\INSTALLER_PACKAGE\assets\hubert\hubert_base.pt"
            results.append(f"• RVC Base Model: {'✅ OK' if os.path.exists(rvc_asset) else '⚠️ MISSING (Fallback active)'}")

            # 4. LilyPond Check
            lily_path = r"C:\INSTALLER_PACKAGE\lilypond-2.24.4\bin\lilypond.exe"
            lily_ok = os.path.exists(lily_path)
            results.append(f"• Score Engine: {'✅ OK' if lily_ok else '⚠️ MISSING (Check C:Installer_Package)'}")

            self.after(0, lambda: self.show_diagnosis_window("\n".join(results)))

        threading.Thread(target=worker, daemon=True).start()

    def show_diagnosis_window(self, text):
        win = ctk.CTkToplevel(self)
        win.title("System Diagnosis Results")
        win.geometry("500x400")
        win.attributes("-topmost", True)
        
        textbox = ctk.CTkTextbox(win, font=("Consolas", 12), fg_color="#000", text_color="#00FF00")
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")
        
        ctk.CTkButton(win, text="CLOSE", command=win.destroy, fg_color="#333", hover_color="#444").pack(pady=10)

if __name__ == "__main__":
    app = AudioStudioApp()
    app.mainloop()