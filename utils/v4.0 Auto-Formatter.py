import music21
import os

def v4_auto_formatter(input_midi, output_xml, title="Untitled", author="JAESOO"):
    """
    MuseScore 4 수동 작업을 대체하는 자동화 엔진
    1. 리듬 재정렬 (16분음표 퀀타이즈)
    2. 한 줄에 4마디 고정 레이아웃 주입
    3. 메타데이터(제목/작성자) 자동 입력
    """
    print(f"📂 분석 시작: {input_midi}")
    
    # 1. MIDI 파일 불러오기
    score = music21.converter.parse(input_midi)
    
    # 2. 리듬 재정렬 (Quantization) -
    # quarterLengthDivisors=(4,)는 16분음표(1/4박자의 1/4) 단위로 정렬함을 의미합니다.
    # 지저분한 쉼표들을 제거하고 정박자로 맞춥니다.
    score = score.quantize(quarterLengthDivisors=(4,), processOffsets=True, processDurations=True)
    score = score.makeNotation() # 음표들을 박자에 맞게 묶어주는 리듬 재정렬 실행
    
    # 3. 메타데이터 주입 -
    if score.metadata is None:
        score.metadata = music21.metadata.Metadata()
    score.metadata.title = title
    score.metadata.composer = f"Produced by {author} (SKY Group)"
    
    # 4. 한 줄에 4마디 고정 (Layout Injection) -
    # 모든 파트(보컬, 피아노 등)에 대해 4마디마다 줄바꿈 태그를 삽입합니다.
    for part in score.parts:
        measures = list(part.getElementsByClass(music21.stream.Measure))
        for i, m in enumerate(measures):
            # 4마디마다(4, 8, 12...) 줄바꿈 명령 삽입
            if (i + 1) % 4 == 0 and (i + 1) < len(measures):
                m.insert(0, music21.layout.SystemLayout(isNew=True))
    
    # 5. MusicXML로 저장
    score.write('musicxml', fp=output_xml)
    print(f"✅ 자동 정렬 완료: {output_xml}")

# --- 실전 배치 처리 예시 ---
if __name__ == "__main__":
    # 처리할 MIDI 파일들이 있는 폴더
    input_dir = "./midi_inputs"
    output_dir = "./xml_outputs"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for file in os.listdir(input_dir):
        if file.endswith(".mid") or file.endswith(".midi"):
            target_title = os.path.splitext(file)[0]
            v4_auto_formatter(
                os.path.join(input_dir, file),
                os.path.join(output_dir, f"{target_title}.musicxml"),
                title=target_title,
                author="Park Jae-soo"
            )