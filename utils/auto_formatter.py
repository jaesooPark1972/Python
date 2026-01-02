import music21
import os

def apply_auto_formatting(xml_path, output_path, title, author):
    """
    MusicXML 파일을 로드하여 다음 처리를 수행합니다:
    1. Flatten & Quantize: 전체를 평탄화한 후 16분음표 단위로 정렬
    2. Re-measure: 시간표/조표에 맞춰 마디를 다시 생성 (makeMeasures)
    3. Make Ties & Notation: 마디를 넘어가는 음표를 붙임줄로 처리하고, 기보법 정리
    4. 메타데이터 주입 (Title, Composer)
    5. 4마디 System Break 삽입
    """
    print(f"🔄 Processing (v4.1 Robust): {xml_path}")
    
    try:
        # 1. MusicXML 파일 불러오기
        score = music21.converter.parse(xml_path)
        
        # 2. 각 파트별로 정밀 정렬 수행
        new_parts = []
        is_score_changed = False
        
        for part in score.parts:
            try:
                # A. 안전 장치: 원본 메타데이터/악기 정보 보존 시도
                original_instrument = part.getInstrument()
                
                # B. Flatten (마디 구조 해제)
                # Recurse and flatten to get all notes/rests/events in a single timeline
                flat_part = part.flatten()
                
                # C. Quantize (16분음표 = 0.25 on Quarter-based system)
                # inPlace=False returns a new stream
                # processOffsets=True: 노트 시작 위치 보정
                # processDurations=True: 노트 길이 보정
                quantized_part = flat_part.quantize((4,), processOffsets=True, processDurations=True, inPlace=False)
                
                # D. Re-measure (마디 다시 나누기)
                # makeMeasures()를 호출하여 TimeSignature에 맞게 마디를 재구성함.
                # 이는 퀀타이징으로 인해 삐져나간 노트들을 올바른 마디로 재배치할 준비를 함.
                remeasured_part = quantized_part.makeMeasures()
                
                # E. Make Ties (붙임줄 처리)
                # 마디 경계에 걸친 노트를 [노트]-[붙임줄]-[노트]로 쪼갬.
                remeasured_part.makeTies(inPlace=True)
                
                # F. Make Notation (기보법 정리)
                # 빔(Beaming), 쉼표 채우기(Rest-filling) 등을 수행하여 'Incomplete measure' 방지
                # makeRests=True, makeBeams=True 등 포함됨.
                # 에러 방지를 위해 bestScheme 사용
                remeasured_part.makeNotation(inPlace=True)
                
                # G. 악기 정보 복구 (if lost)
                if original_instrument:
                    remeasured_part.insert(0, original_instrument)
                    
                new_parts.append(remeasured_part)
                is_score_changed = True
                
            except Exception as e:
                print(f"⚠️ Failed to process a part, keeping original: {e}")
                import traceback
                traceback.print_exc()
                new_parts.append(part) # 실패 시 원본 유지

        # 스코어가 변경되었으면 파트 교체
        if is_score_changed:
            # 기존 파트 제거 후 새 파트 추가 (단, 메타데이터 등 스코어 레벨 속성은 유지)
            # score.parts는 튜플일 수 있으므로 stream 조작 필요
            # 가장 안전한 방법: 새 스코어 생성 혹은 remove/append
            
            # 메타데이터 보존
            original_metadata = score.metadata
            
            # 새 스코어 생성
            new_score = music21.stream.Score()
            new_score.metadata = original_metadata
            for p in new_parts:
                new_score.append(p)
            
            score = new_score

        # 3. 메타데이터 업데이트
        if score.metadata is None:
            score.metadata = music21.metadata.Metadata()
        score.metadata.title = title
        score.metadata.composer = f"Produced by {author}"
        
        # 4. System Break (4마디 고정)
        # 이제 마디가 확실히 재구성되었으므로 SystemLayout 적용
        for part in score.parts:
            measures = part.getElementsByClass(music21.stream.Measure)
            for i, m in enumerate(measures):
                # 기존 레이아웃 정리
                m.removeByClass(music21.layout.SystemLayout)
                
                # 0, 4, 8, 12... (1, 5, 9, 13마디) 에 New System 걸기
                # 단, 첫 마디(0)는 이미 새 시스템이므로 5번째 마디(index 4)부터 적용
                if i > 0 and i % 4 == 0:
                    sl = music21.layout.SystemLayout(isNew=True)
                    m.insert(0, sl)

    except Exception as e:
        print(f"⚠️ Critical Error: {e}")
        import traceback
        traceback.print_exc()
        # 원본이라도 저장 시도 (변수 scope 주의)
        pass

    # 5. 결과물 저장
    try:
        score.write('musicxml', fp=output_path)
        print(f"✅ {title} (v4.1) 악보 자동 정렬 완료: {output_path}")
    except Exception as e:
        print(f"❌ Save failed: {e}")

if __name__ == "__main__":
    pass
