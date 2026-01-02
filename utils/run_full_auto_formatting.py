
import music21
import os
import traceback
import logging

# music21 라이브러리에서 발생하는 경고(WARNING) 메시지를 숨깁니다.
# 라이브러리가 내부적으로 처리하는 문제에 대한 로그가 많아 사용자에게 혼란을 줄 수 있으므로
# CRITICAL 이상의 심각한 에러만 표시하도록 설정합니다.
logging.getLogger('music21').setLevel(logging.CRITICAL)

def run_full_auto_formatting(midi_path, output_path, title, author):
    """
    (v4.1 Hybrid) MIDI 파일을 로드하여 MusicXML으로 변환하고 자동 서식을 적용합니다.
    1. MIDI 로드 -> MusicXML 변환
    2. Flatten & Quantize
    3. Re-measure & Make Ties
    4. 메타데이터 주입
    5. 4마디 System Break 삽입
    """
    print(f"🔄 Processing (v4.1 Hybrid): {midi_path}")
    
    try:
        # 1. MIDI 파일 불러오기 (v4.0 로직)
        score = music21.converter.parse(midi_path)
        
        # --- v4.1 Robust 로직 시작 (auto_formatter.py에서 가져와 MIDI -> Score 객체에 맞게 수정) ---
        new_parts = []
        is_score_changed = False
        
        for part in score.parts:
            try:
                original_instrument = part.getInstrument()
                
                flat_part = part.flatten()
                
                # 16분음표로 퀀타이즈
                quantized_part = flat_part.quantize((4,), processOffsets=True, processDurations=True, inPlace=False)
                
                remeasured_part = quantized_part.makeMeasures()
                remeasured_part.makeTies(inPlace=True)
                remeasured_part.makeNotation(inPlace=True)
                
                if original_instrument:
                    remeasured_part.insert(0, original_instrument)
                    
                new_parts.append(remeasured_part)
                is_score_changed = True
                
            except Exception as e:
                print(f"⚠️ 파트 처리 중 오류 발생, 원본 파트를 유지합니다: {e}")
                traceback.print_exc()
                new_parts.append(part)

        if is_score_changed:
            original_metadata = score.metadata
            new_score = music21.stream.Score()
            if original_metadata:
                new_score.metadata = original_metadata
            
            for p in new_parts:
                new_score.append(p)
            score = new_score

        # 3. 메타데이터 업데이트
        if score.metadata is None:
            score.metadata = music21.metadata.Metadata()
        score.metadata.title = title
        score.metadata.composer = f"Produced by {author}"
        
        # 4. 4마디마다 줄바꿈 적용
        for part in score.parts:
            measures = part.getElementsByClass(music21.stream.Measure)
            for i, m in enumerate(measures):
                m.removeByClass(music21.layout.SystemLayout)
                if i > 0 and i % 4 == 0:
                    sl = music21.layout.SystemLayout(isNew=True)
                    m.insert(0, sl)

    except Exception as e:
        print(f"CRITICAL: Cannot process file {midi_path}. Error: {e}")
        traceback.print_exc()
        return

    # 5. 결과물 저장
    try:
        score.write('musicxml', fp=output_path)
        print(f"✅ (v4.1) 자동 서식 적용 완료: {output_path}")
    except Exception as e:
        print(f"❌ 저장 실패: {e}")

if __name__ == "__main__":
    # 처리할 MIDI 파일이 있는 루트 폴더
    root_dir = "./output_result"
    author_name = "JAESOO"
    
    print("="*50)
    print("Starting Full Auto-Formatting Process (MIDI -> MusicXML v4.1)")
    print(f"Target directory: {os.path.abspath(root_dir)}")
    print("="*50)

    # 지정된 폴더와 그 하위 폴더까지 모두 탐색
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith((".mid", ".midi")):
                midi_file_path = os.path.join(dirpath, filename)
                
                # 제목은 파일명에서 확장자를 제거하여 사용
                base_name = os.path.splitext(filename)[0]
                
                # 출력 파일명 (기존 파일명에 .musicxml 확장자만 붙임)
                output_xml_path = os.path.join(dirpath, f"{base_name}.musicxml")
                
                run_full_auto_formatting(
                    midi_path=midi_file_path,
                    output_path=output_xml_path,
                    title=base_name,
                    author=author_name
                )

    print("="*50)
    print("All MIDI files have been processed.")
    print("="*50)
