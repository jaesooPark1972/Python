import subprocess
import os
import sys
import argparse
import time # Import time for timestamp

# Base directory for the entire project
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

OUTPUT_ROOT_DIR = os.path.join(base_dir, "output_result")

def run_ultimate_pipeline(midi_dir, title, author="Park Jae-soo", transposition=0, lyrics=None, output_base_dir=None):
    """
    [v5.1 Refactored] Runs the master score creation pipeline by calling master_score_maker.py.
    """
    try:
        print(f"🔗 [Pipeline v5.1] Starting master score generation for '{title}'...")

        if not os.path.isdir(midi_dir):
            print(f"❌ [Pipeline Error] Input MIDI directory not found: {midi_dir}")
            return False

        # --- Determine the output folder ---
        if output_base_dir:
            # Use provided output_base_dir if specified
            final_output_folder = os.path.join(output_base_dir, f"{title}_MasterScore_{time.strftime('%Y%m%d%H%M%S')}")
        else:
            # Default to output_result/master_scores/TITLE_TIMESTAMP
            master_scores_root = os.path.join(OUTPUT_ROOT_DIR, "master_scores")
            os.makedirs(master_scores_root, exist_ok=True)
            final_output_folder = os.path.join(master_scores_root, f"{title}_MasterScore_{time.strftime('%Y%m%d%H%M%S')}")
        
        os.makedirs(final_output_folder, exist_ok=True)
        print(f"📂 [Pipeline] Output will be saved in: {final_output_folder}")

        # --- Call the master_score_maker.py script ---
        master_script_path = os.path.join(os.path.dirname(__file__), "master_score_maker.py")
        if not os.path.exists(master_script_path):
            print(f"❌ [Pipeline Error] Cannot find master_score_maker.py script!")
            return False
            
        cmd = [
            sys.executable,
            master_script_path,
            midi_dir, # Input MIDI folder
            str(transposition),
        ]
        if lyrics:
            cmd.append(lyrics)
        
        # Add the new output_score_folder argument
        cmd.append(final_output_folder)


        print(f"🎼 [Pipeline] Calling master score maker...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"   > {output.strip()}")

        if process.returncode != 0:
            print(f"❌ [Pipeline Error] master_score_maker.py failed with code {process.returncode}.")
            return False

        # --- Open the output folder ---
        print(f"✅ [Pipeline] Process finished. Opening output directory: {final_output_folder}")
        try:
            os.startfile(final_output_folder)
        except AttributeError:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", final_output_folder])
            else:  # Linux
                subprocess.run(["xdg-open", final_output_folder])
            
        return True

    except Exception as e:
        print(f"❌ [Pipeline Error] An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="[v5.1] Master Score Pipeline Runner")
    parser.add_argument("midi_dir", help="Directory containing the MIDI files to be merged.")
    parser.add_argument("--title", default="Master Score", help="Title of the final score.")
    parser.add_argument("--author", default="Park Jae-soo", help="Author/composer of the score.")
    parser.add_argument("--transpose", type=int, default=0, help="Number of semitones to transpose the score.")
    parser.add_argument("--lyrics", default=None, help="Lyrics text or a Suno URL to fetch lyrics from.")
    parser.add_argument("--output_dir", default=None, help="Optional: Base directory to save the output score. Defaults to output_result/master_scores.")

    args = parser.parse_args()

    run_ultimate_pipeline(
        midi_dir=args.midi_dir,
        title=args.title,
        author=args.author,
        transposition=args.transpose,
        lyrics=args.lyrics,
        output_base_dir=args.output_dir
    )