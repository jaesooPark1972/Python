# -*- coding: utf-8 -*-
# VER: 20251226_1730_FULL_FIX
import os
import sys
import music21
import json
import time

# [DEBUG] Ensure we are running the correct script
print(f"--- [Master Score Engine v5.1 PRO] Starting from: {__file__} ---")

def create_master_score(midi_folder, transposition=0, lyrics=None, output_folder=None):
    """
    [v5.1 Pro] Master Score Creation Pipeline
    Merges all MIDI files from separated stems into a single high-quality conductor's score.
    """
    # ... (rest of the logic I wrote before)
    from score_maker import LilyScoreMaker
    from auto_formatter import apply_auto_formatting

    print(f"\n[Master Score Engine] Phase 1: Merging MIDI tracks...")
    master_score = music21.stream.Score()
    
    # Check folder
    if not os.path.isdir(midi_folder):
         print(f"❌ Error: {midi_folder} is not a directory.")
         return False

    # 1. MIDI 파일 목록 확보
    midi_files = [f for f in os.listdir(midi_folder) if f.lower().endswith('.mid')]
    if not midi_files:
        print(f"❌ No MIDI files found in {midi_folder}")
        return False

    # 2. 트랙 병합 (Vocal, Bass, Piano, Guitar, Others, Drums 순서 선호)
    preferred_order = ["vocal", "piano", "guitar", "bass", "others", "drums"]
    midi_files.sort(key=lambda x: next((i for i, name in enumerate(preferred_order) if name in x.lower()), 99))

    for midi_file in midi_files:
        try:
            path = os.path.join(midi_folder, midi_file)
            part = music21.converter.parse(path)
            # 트랙 이름 설정
            part_name = os.path.splitext(midi_file)[0].replace("_", " ").title()
            
            p = part.parts[0]
            p.id = part_name
            p.partName = part_name
            
            # 조옮김 적용
            if transposition != 0:
                p = p.transpose(transposition)
            
            master_score.insert(0, p)
            print(f"   + Added track: {part_name}")
        except Exception as e:
            print(f"   ⚠️ Failed to add track {midi_file}: {e}")

    # 3. 메타데이터 설정
    master_score.insert(0, music21.metadata.Metadata())
    master_score.metadata.title = "Master Conductor Score"
    master_score.metadata.composer = "Park Jae-soo"

    # 4. 출력 경로 설정 (Ultimate Pipeline에서 전달받은 폴더 우선)
    if not output_folder:
        output_folder = midi_folder # Fallback
    
    os.makedirs(output_folder, exist_ok=True)
    
    output_filename_base = "Master_Score_Full"
    xml_path = os.path.join(output_folder, f"{output_filename_base}_raw.musicxml")
    final_xml_path = os.path.join(output_folder, f"{output_filename_base}.musicxml")

    try:
        # A. 기본 XML 생성
        print(f"[Master Score Engine] Phase 2: Generating raw MusicXML...")
        master_score.write('musicxml', fp=xml_path)
        
        # B. Auto-Formatter 연동 (정밀 레이아웃 정렬)
        print(f"[Master Score Engine] Phase 3: Applying Professional Auto-Formatting...")
        folder_name = os.path.basename(output_folder)
        apply_auto_formatting(xml_path, final_xml_path, folder_name, "Park Jae-soo")
        
        # C. 임시 파일 삭제 후 PDF 생성 시도
        if os.path.exists(xml_path):
            os.remove(xml_path)
            
        # D. LilyPond PDF 생성 (score_maker 활용)
        print(f"[Master Score Engine] Phase 4: Finalizing PDF Engineering...")
        maker = LilyScoreMaker()
        maker.generate_score_files(output_folder, os.path.basename(final_xml_path))
        
        print(f"\n✅ [SUCCESS] Master Score completed: {final_xml_path}")
        return True
        
    except Exception as e:
        print(f"❌ [Master Score Engine Error] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python master_score_maker.py <midi_dir> [transpose] [lyrics] [output_folder]")
        sys.exit(1)
        
    midi_dir = sys.argv[1]
    transpose = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    lyrics = sys.argv[3] if len(sys.argv) > 3 else None
    out_folder = sys.argv[4] if len(sys.argv) > 4 else None
    
    success = create_master_score(midi_dir, transpose, lyrics, out_folder)
    sys.exit(0 if success else 1)