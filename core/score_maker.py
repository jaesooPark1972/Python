import os
import music21
from PIL import Image, PsdImagePlugin
import sys
import subprocess
import shutil
import re
import glob

# [FIX] Force ASCII output for console
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='ascii', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='ascii', errors='replace')

class LilyScoreMaker:
    def __init__(self):
        # [Configuration] Load from config.json
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        try:
            import json
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except:
            self.config = {}

        # LilyPond path (User config first, then System, then portable, then fallback)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        user_lily_path = self.config.get("lilypond_path", "")
        if user_lily_path and not user_lily_path.endswith("bin"):
             user_lily_path = os.path.join(user_lily_path, "bin")

        system_path = r"C:\lilypond-2.24.4\bin"
        portable_path = os.path.join(current_dir, "lilypond-2.24.4", "bin")
        fallback_path = r"D:\Util\lilypond-2.24.4\bin"
        
        if user_lily_path and os.path.exists(os.path.join(user_lily_path, "lilypond.exe")):
            self.lilypond_dir = user_lily_path
        elif os.path.exists(os.path.join(system_path, "lilypond.exe")):
            self.lilypond_dir = system_path
        elif os.path.exists(os.path.join(portable_path, "lilypond.exe")):
            self.lilypond_dir = portable_path
        else:
            self.lilypond_dir = fallback_path

        self.lilypond_exe = os.path.join(self.lilypond_dir, "lilypond.exe")
        self.musicxml2ly = os.path.join(self.lilypond_dir, "musicxml2ly.py")
        
        # Determine Python for LilyPond (prefer system python if configured, else portable python next to lilypond)
        if self.config.get("system_python_path") and os.path.exists(os.path.join(self.config.get("system_python_path"), "python.exe")):
             self.python_exe = os.path.join(self.config.get("system_python_path"), "python.exe")
        else:
             self.python_exe = os.path.join(self.lilypond_dir, "python.exe") 
        
        # [사용자 요청] 수정 가능한 작성자 이름
        self.author_name = "Music Revolutionary JAESOO"
        
        # [FIX] music21 환경 설정에 LilyPond 및 MuseScore 경로 등록
        try:
            from music21 import environment
            us = environment.UserSettings()
            us['lilypondPath'] = self.lilypond_exe
            
            musescore_path = self.config.get("musescore_path")
            if musescore_path and os.path.exists(musescore_path):
                 us['musescoreDirectPath'] = os.path.join(musescore_path, "MuseScore4.exe")
            
            print(f"music21 LilyPond path set: {self.lilypond_exe}")
            if musescore_path: print(f"music21 MuseScore path set: {us['musescoreDirectPath']}")
        except Exception as e:
            print(f"music21 environment setup warning: {e}")
        
        if os.path.exists(self.lilypond_exe):
            print(f"LilyPond detected: {self.lilypond_exe}")
        else:
            print(f"LilyPond not found at {self.lilypond_exe}")

    def clean_filename(self, filename):
        """파일명에서 영문/숫자만 남기고 특수문자 및 공백을 모두 제거합니다."""
        return "".join([c for c in filename if c.isalnum()])

    def patch_lilypond_layout(self, ly_path):
        """LilyPond 파일에 레이아웃 최적화 코드를 추가하여 가독성을 높입니다."""
        try:
            with open(ly_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # [사용자 요청] 악보 배치 및 여백 조정 (화면 안으로 들어오게)
            layout_settings = f"""
#(set-global-staff-size 18) % 6S 가독성 향상
\\paper {{
  #(set-paper-size "a4")
  indent = 1.0\\cm
  short-indent = 0.5\\cm
  left-margin = 1.5\\cm
  right-margin = 1.5\\cm
  top-margin = 1.5\\cm
  bottom-margin = 1.5\\cm
  line-width = 18.0\\cm
  ragged-last-bottom = ##f
  system-system-spacing.basic-distance = #15
}}
"""
            new_content = layout_settings + content
            with open(ly_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            print(f"   WARNING: Layout patch failed: {e}")

    def run_command_safe(self, cmd, cwd):
        """안전하게 외부 명령어를 실행합니다."""
        try:
            env = os.environ.copy()
            env["PATH"] = self.lilypond_dir + os.pathsep + env.get("PATH", "")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding='utf-8',
                errors='replace',
                check=False,
                cwd=cwd,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result
        except Exception as e:
            print(f"   ERROR: Execution error: {str(e)}")
            return None

    def generate_score_files(self, midi_folder_path, specific_midi_name=None):
        """
        LilyPond를 사용하여 MIDI -> MusicXML -> LY -> PDF + 고화질 PNG 순서로 변환합니다.
        specific_midi_name이 제공되면 해당 파일만 처리합니다.
        """
        if not os.path.exists(midi_folder_path):
            print(f"ERROR: Folder not found: {midi_folder_path}")
            return

        if not os.path.exists(self.lilypond_exe):
            print("ERROR: LilyPond engine missing. Aborting score generation.")
            return

        if specific_midi_name:
            midi_files = [specific_midi_name]
            print(f"[LilyPond] Starting conversion for 1 file...")
        else:
            print(f"[LilyPond Engine] Starting score generation (PDF + High-Res Image)...")
            print(f"Working folder: {midi_folder_path}")
            midi_files = [f for f in os.listdir(midi_folder_path) if f.lower().endswith('.mid')]
        
        # 프로젝트 내 임시 폴더
        safe_temp_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_scores"))
        if not os.path.exists(safe_temp_dir): os.makedirs(safe_temp_dir, exist_ok=True)

        if not os.path.exists(safe_temp_dir): os.makedirs(safe_temp_dir, exist_ok=True)

        # [OPTIMIZATION] Parallel Processing for "Maximal Advantage"
        # Using ThreadPoolExecutor because we are mostly waiting on Subprocess (IO Bound)
        import concurrent.futures
        
        print(f"🚀 [Performance] Starting Parallel Processing (Max Workers: {os.cpu_count()})")
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Create a partial function or wrapper if needed, but here we can just map
            # We need to pass self, so we'll use a wrapper lambda or internal function
            # However, self methods are fine in ThreadPool.
            
            future_to_file = {executor.submit(self.process_single_midi, midi_file, midi_folder_path, safe_temp_dir): midi_file for midi_file in midi_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                midi_file = future_to_file[future]
                try:
                    future.result()
                except Exception as exc:
                    print(f"   ❌ {midi_file} generated an exception: {exc}")

    def process_single_midi(self, midi_file, midi_folder_path, safe_temp_dir):
        """Worker function for a single MIDI file"""
        full_midi_path = os.path.join(midi_folder_path, midi_file)
        if not os.path.exists(full_midi_path): return

        base_name_raw = os.path.splitext(midi_file)[0]
        safe_base = self.clean_filename(base_name_raw)
        if not safe_base: safe_base = "score"
        
        import time
        import random
        # Unique timestamp for threads
        ts = int(time.time() * 1000) + random.randint(0, 9999) 
        
        temp_xml = os.path.join(safe_temp_dir, f"temp_{ts}.musicxml")
        temp_ly = os.path.join(safe_temp_dir, f"temp_{ts}.ly")
        
        final_pdf = os.path.join(midi_folder_path, f"{safe_base}.pdf")
        final_png = os.path.join(midi_folder_path, f"{safe_base}.png")

        print(f"   ▶️ Processing: {midi_file}")

        try:
            # 1. MIDI -> MusicXML (music21)
            # print(f"      To XML...", flush=True) 
            # (Reduce noise in parallel output)
            
            try:
                score = music21.converter.parse(full_midi_path)
            except:
                print(f"      ⚠️ Parse Failed: {midi_file}")
                return

            # [Clean Parse] Simplify stream and MIDI filtering
            score = score.flatten().notesAndRests.stream()
            
            # [Filter Noise]
            filtered_score = music21.stream.Stream()
            for n in score:
                if n.isNote:
                    vol = getattr(n, 'volume', None)
                    if vol and vol.velocity is not None and vol.velocity < 20: continue
                    if n.duration.quarterLength < 0.1: continue
                    filtered_score.insert(n.offset, n)
                else:
                    filtered_score.insert(n.offset, n)
            score = filtered_score
            
            # [Pitch Normalization]
            pitches = [n.pitch.ps for n in score.recurse().notes if n.isNote]
            if pitches:
                avg_ps = sum(pitches) / len(pitches)
                if avg_ps > 84: score = score.transpose(-12)
                elif avg_ps < 36: score = score.transpose(12)

            # [Clef Assignment]
            if "bass" in midi_file.lower() or "drums" in midi_file.lower():
                score.insert(0, music21.clef.BassClef())
            else:
                score.insert(0, music21.clef.TrebleClef())

            # [Robust Quantization]
            score.quantize([4, 3], processOffsets=True, processDurations=True, inPlace=True)
            
            # [Final Assembly]
            score.makeMeasures(inPlace=True)
            score.makeRests(fillGaps=True, inPlace=True)
            if not score.recurse().getElementsByClass(music21.meter.TimeSignature):
                score.measure(1).insert(0, music21.meter.TimeSignature('4/4'))
            
            # Metadata
            if not score.metadata:
                score.insert(0, music21.metadata.Metadata())
            
            score.metadata.title = "" 
            score.metadata.composer = self.author_name
            
            score.write('musicxml', fp=temp_xml)
            
            if os.path.exists(temp_xml):
                # 2. MusicXML -> LilyPond (.ly)
                cmd_ly = [self.python_exe, self.musicxml2ly, "-o", temp_ly, temp_xml]
                self.run_command_safe(cmd_ly, safe_temp_dir)
                
                if os.path.exists(temp_ly):
                    # [Layout Patch]
                    self.patch_lilypond_layout(temp_ly)
                    
                    # 3. LilyPond -> PDF + PNG
                    out_prefix = os.path.join(safe_temp_dir, f"temp_{ts}")
                    cmd_lily = [self.lilypond_exe, "--pdf", "--png", "-dresolution=300", "-o", out_prefix, temp_ly]
                    self.run_command_safe(cmd_lily, safe_temp_dir)
                    
                    # Copy Results
                    generated_pdf = out_prefix + ".pdf"
                    if os.path.exists(generated_pdf):
                        if os.path.exists(final_pdf): os.remove(final_pdf)
                        shutil.copy2(generated_pdf, final_pdf)
                        # print(f"      ✅ PDF: {midi_file}")
                    
                    png_files = glob.glob(out_prefix + "*.png")
                    if png_files:
                        png_files.sort()
                        real_png = png_files[0]
                        if os.path.exists(final_png): os.remove(final_png)
                        shutil.copy2(real_png, final_png)
                        print(f"   ✅ Done: {midi_file} (PDF+PNG)")
                    
                    if not os.path.exists(generated_pdf) and not png_files:
                         print(f"      ❌ Failed Gen: {midi_file}")
                else:
                    print(f"      ❌ Failed XML->LY: {midi_file}")
            else:
                print(f"      ❌ Failed MIDI->XML: {midi_file}")
            
            # Cleanup
            for f in os.listdir(safe_temp_dir):
                if f.startswith(f"temp_{ts}"):
                    try: os.remove(os.path.join(safe_temp_dir, f))
                    except: pass
                    
        except Exception as e:
            print(f"   🔥 Error {midi_file}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        target_folder = sys.argv[1]
        specific_file = sys.argv[2]
        maker = LilyScoreMaker()
        maker.generate_score_files(target_folder, specific_file)
    elif len(sys.argv) > 1:
        target_folder = sys.argv[1]
        maker = LilyScoreMaker()
        maker.generate_score_files(target_folder)
    else:
        # 단독 실행 시 테스트 로직 (사용자 코드 스타일 반영)
        maker = LilyScoreMaker()
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_result")
        if os.path.exists(base_dir):
            all_subdirs = [os.path.join(base_dir, d) for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
            if all_subdirs:
                latest_folder = max(all_subdirs, key=os.path.getmtime)
                midi_folder = os.path.join(latest_folder, "미디분리")
                maker.generate_score_files(midi_folder)
            else:
                print("ERROR: No folders found in output_result.")
        else:
            print(f"ERROR: Path not found: {base_dir}")
