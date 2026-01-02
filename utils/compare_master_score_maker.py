import os
# master_score_maker.py 상단에 추가
from auto_formatter import apply_auto_formatting 

# ... 기존 코드 생략 ...

# 5. 출력 파일명 결정 부분 수정
xml_path = os.path.join(midi_folder, f"{output_filename_base}_raw.musicxml")
final_xml_path = os.path.join(midi_folder, f"{output_filename_base}.musicxml")

try:
    # A. 일단 기본 XML 생성
    master_score.write('musicxml', fp=xml_path)
    
    # B. [연결 핵심] 생성된 XML을 auto_formatter로 다시 정밀 정렬
    apply_auto_formatting(xml_path, final_xml_path, folder_name, "Park Jae-soo")
    
    # C. 임시 파일 삭제
    os.remove(xml_path)
    print(f"\n[OK] [V4.1 정밀 정렬 완료] {os.path.basename(final_xml_path)}")
except Exception as e:
    print(f"[ERROR] 연결 공정 실패: {e}")