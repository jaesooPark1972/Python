import os
import argparse
import sys

# Try to import pedalboard
try:
    from pedalboard import Pedalboard, NoiseGate, Compressor, HighPassFilter, Gain
    from pedalboard.io import AudioFile
    import numpy as np
except ImportError:
    print("❌ ERROR: 'pedalboard' library missing.")
    print("👉 Please run: pip install pedalboard")
    sys.exit(1)

def process_file_to_dry(input_path, output_path, threshold_db=-30, ratio=4.0):
    """
    Applies a chain of effects to simulate FL Studio's 'Dry' vocal processing.
    1. HighPassFilter (80Hz): Remove low-end rumble (EQ 2)
    2. NoiseGate: Remove silence/background hiss (Fruity Limiter)
    3. Compressor: Even out dynamics (optional but recommended)
    4. Gain: Normalize slightly
    """
    print(f"🔄 Processing: {os.path.basename(input_path)}")
    
    try:
        # Load Audio
        with AudioFile(input_path) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate

        # Create Effect Chain (Virtual MCP Logic)
        board = Pedalboard([
            # 1. EQ: Cut Mud (< 80Hz)
            HighPassFilter(cutoff_frequency_hz=80),
            
            # 2. Gate: Remove Noise (Simulating Fruity Limiter Gate)
            # threshold_db: Volume below this is muted
            # ratio: How hard to mute (inf = complete silence)
            NoiseGate(threshold_db=threshold_db, ratio=10, release_ms=200),
            
            # 3. Dynamic Control (Optional)
            Compressor(threshold_db=-20, ratio=ratio),
            
            # 4. Makeup Gain
            Gain(gain_db=2.0) 
        ])

        # Run Effect
        effected = board(audio, samplerate)

        # [RVC Optimization] Peak Normalization to -1.0 dB
        # This ensures the training data has consistent volume without clipping.
        max_peak = np.max(np.abs(effected))
        if max_peak > 0:
            target_peak = 10 ** (-1.0 / 20)  # -1.0 dB
            normalization_factor = target_peak / max_peak
            effected = effected * normalization_factor
            
        # Ensure data type is correct for 16-bit/24-bit saving (float32 is standard in pedalboard)
        
        # Save Output
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with AudioFile(output_path, 'w', samplerate, effected.shape[0]) as f:
            f.write(effected)
            
        print(f"✅ [RVC Ready] Saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dry Audio Processor (Virtual MCP)")
    parser.add_argument("--input", "-i", required=True, help="Input file or folder path")
    parser.add_argument("--output", "-o", default="output_dry", help="Output folder")
    parser.add_argument("--threshold", "-t", type=float, default=-40.0, help="Noise Gate Threshold (dB)")
    
    args = parser.parse_args()
    
    input_path = args.input
    output_base = args.output
    
    if os.path.isfile(input_path):
        # Single file mode
        fname = os.path.basename(input_path)
        out_path = os.path.join(output_base, f"dry_{fname}")
        process_file_to_dry(input_path, out_path, args.threshold)
        
    elif os.path.isdir(input_path):
        # Batch mode
        files = [f for f in os.listdir(input_path) if f.lower().endswith(('.wav', '.mp3', '.flac'))]
        print(f"🚀 Found {len(files)} audio files in '{input_path}'")
        
        success_count = 0
        for f in files:
            full_in = os.path.join(input_path, f)
            full_out = os.path.join(output_base, f"dry_{f}")
            if process_file_to_dry(full_in, full_out, args.threshold):
                success_count += 1
                
        print(f"\n🎉 Batch Complete! ({success_count}/{len(files)})")
        print(f"📂 Results in: {os.path.abspath(output_base)}")
    else:
        print("❌ Invalid input path.")
