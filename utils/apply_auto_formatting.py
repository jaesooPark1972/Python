import os
import music21

def batch_process_midis(input_folder, output_folder, author_name):
    # 출력 폴더가 없으면 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 폴더 내 모든 .mid 파일 찾기
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.mid') or file_name.endswith('.midi'):
            input_path = os.path.join(input_folder, file_name)
            title = os.path.splitext(file_name)[0]  # 파일명을 제목으로 사용
            output_path = os.path.join(output_folder, f"{title}_AutoScore.musicxml")
            
            print(f"🚀 처리 중: {title}...")
            # 여기에 기존의 정렬 및 레이아웃 로직(v4.0)을 적용하여 저장
            # (apply_auto_formatting 함수를 여기서 호출하도록 설정)