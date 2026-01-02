# 변환 프로세스 완료 후 자동 실행
try:
    merge_vocal_and_piano(
        vocal_midi_path, 
        piano_midi_path, 
        output_xml_path, 
        title="바람처럼 춤추는", 
        author="Park Jae-soo"
    )
    print("🚀 [System] 총보 작성이 자동으로 완료되었습니다!")
except Exception as e:
    print(f"❌ [System] 악보 생성 중 오류 발생: {e}")