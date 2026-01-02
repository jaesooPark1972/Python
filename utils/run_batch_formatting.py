import os
import glob
from auto_formatter import apply_auto_formatting

def run_batch():
    # List of specific files to process (picked from search results)
    # Using relative paths from c:\INSTALLER_PACKAGE
    targets = [
        ("output_result/3. 다시 돌아갈 수 없는 그 시절 (The Days We Can't Return To)/미디분리/3. 다시 돌아갈 수 없는 그 시절 (The Days We Can't Return To)_piano.mid", "다시 돌아갈 수 없는 그 시절 (Piano)", "JAESOO"),
        ("output_result/시간의 다리 아래/미디분리/시간의 다리 아래_piano.mid", "시간의 다리 아래 (Piano)", "JAESOO"),
        ("output_result/20 Years Later, You/미디분리/20 Years Later, You_vocals.mid", "20 Years Later, You (Vocals)", "JAESOO")
    ]

    base_dir = os.getcwd()
    print(f"Base Directory: {base_dir}")

    for rel_path, title, author in targets:
        full_path = os.path.join(base_dir, rel_path.replace("/", os.sep))
        
        if not os.path.exists(full_path):
            print(f"⚠️ File not found, skipping: {full_path}")
            continue
            
        output_path = full_path.replace(".mid", "_formatted.musicxml")
        
        print(f"Processing: {title}...")
        try:
            apply_auto_formatting(full_path, output_path, title, author)
        except Exception as e:
            print(f"❌ Failed to process {title}: {e}")

if __name__ == "__main__":
    run_batch()
