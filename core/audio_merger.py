
import argparse
import os
import sys
from pydub import AudioSegment, effects
import traceback
import math

def safe_print(message):
    """Prints messages safely regardless of the console's encoding."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback for environments that cannot handle the default encoding
        encoded_message = message.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
        print(encoded_message)

def _apply_sidechain_compression(vocal_track, instrumental_track, threshold_db=-25.0, ratio=2.5):
    """
    Applies side-chain compression to the instrumental track, triggered by the vocal track.
    Makes the instrumental track duck slightly when vocals are present.
    """
    safe_print("Applying Side-Chain Compression (Vocal Priority)...")
    compressed_instrumental = instrumental_track.empty() # Create an empty segment for compressed audio

    # Parameters for compression
    samplerate = instrumental_track.frame_rate
    chunk_size = int(samplerate * 0.05) # 50ms chunk for smoother analysis (increased from 20ms)

    # Ensure tracks are same length for iteration
    min_length = min(len(vocal_track), len(instrumental_track))
    vocal_track_sliced = vocal_track[:min_length]
    instrumental_track_sliced = instrumental_track[:min_length]

    for i in range(0, min_length, chunk_size):
        vocal_chunk = vocal_track_sliced[i : i + chunk_size]
        instrumental_chunk = instrumental_track_sliced[i : i + chunk_size]

        if not vocal_chunk.duration_seconds > 0: 
            compressed_instrumental += instrumental_chunk
            continue

        # Calculate vocal RMS level
        vocal_rms_db = vocal_chunk.dBFS if vocal_chunk.duration_seconds > 0 else -float('inf')

        # Determine gain reduction
        gain_reduction_db = 0.0
        if vocal_rms_db > threshold_db:
             # More aggressive ratio for clearer vocals
            gain_reduction_db = (threshold_db - vocal_rms_db) / ratio
        
        # Apply gain reduction to instrumental chunk
        # Limit max reduction to Avoid pumping effect too much
        processed_chunk = instrumental_chunk.apply_gain(max(gain_reduction_db, -6.0)) 

        compressed_instrumental += processed_chunk
    
    # Handle remaining part if any
    if len(instrumental_track) > min_length:
        compressed_instrumental += instrumental_track[min_length:]
        
    return compressed_instrumental


def _apply_high_end_exciter(audio_segment, boost_db=4.0, cutoff_hz=10000):
    """
    Applies a high-end exciter effect by boosting high frequencies.
    """
    safe_print(f"Applying High-End Exciter (boosting {cutoff_hz}Hz+ by {boost_db}dB)...")
    
    # Isolate high frequencies (e.g., above 10kHz)
    high_freq_content = audio_segment.high_pass_filter(cutoff_hz)
    
    # Boost the high frequencies
    boosted_high_freq = high_freq_content + boost_db
    
    # Overlay the boosted high frequencies back onto the original audio
    # This simulates adding "air" without making the original sound thin
    excited_audio = audio_segment.overlay(boosted_high_freq)
    
    return excited_audio

def main():
    parser = argparse.ArgumentParser(description="v5.5 Audio Merger - Mixes vocal, instrumental, and effects tracks with advanced processing.")
    parser.add_argument("--vocal_path", required=True, help="Path to the vocal audio file.")
    parser.add_argument("--instrumental_path", required=True, help="Path to the instrumental (MR) audio file.")
    parser.add_argument("--output_path", required=True, help="Path to save the final mixed audio file.")
    parser.add_argument("--effect_path", default=None, help="Optional: Path to an effect audio file.")
    parser.add_argument("--vocal_gain", type=float, default=0.0, help="Gain for the vocal track in dB.")
    parser.add_argument("--instrumental_gain", type=float, default=0.0, help="Gain for the instrumental track in dB.")
    parser.add_argument("--effect_gain", type=float, default=0.0, help="Gain for the effect track in dB.")
    parser.add_argument("--apply_dolby", action='store_true', help="Apply 'Dolby Style' effect.")
    parser.add_argument("--apply_hifi", action='store_true', help="Apply 'Hi-Fi' mode for WAV output and treble boost.")
    parser.add_argument("--apply_sidechain", action='store_true', help="Apply side-chain compression for vocals.")
    parser.add_argument("--apply_exciter", action='store_true', help="Apply high-end exciter effect.")
    parser.add_argument("--no_vocal_hp", action='store_true', help="Do NOT apply high-pass filter to vocal track (for AI Analysis mode).")
    
    args = parser.parse_args()

    try:
        safe_print("AudioMerger (v5.5) - Starting process...")

        # 1. Load audio files
        safe_print(f"🎤 Loading Vocal: {args.vocal_path}")
        vocal_track = AudioSegment.from_file(args.vocal_path)
        if not args.no_vocal_hp:
            vocal_track = vocal_track.high_pass_filter(80) # Apply HPF unless explicitly told not to
        vocal_track += args.vocal_gain
        
        safe_print(f"🎹 Loading Instrumental: {args.instrumental_path}")
        instrumental_track = AudioSegment.from_file(args.instrumental_path) + args.instrumental_gain
        
        # 2. Apply Side-Chain Compression (if enabled)
        if args.apply_sidechain:
            safe_print("🔄 Applying Vocal Priority (Side-chain + Exciter)...")
            # 1. Boost Vocal Presence
            vocal_track = _apply_high_end_exciter(vocal_track, boost_db=5.0) 
            
            # 2. Side-chain instrumental based on vocal presence
            instrumental_track = _apply_sidechain_compression(vocal_track, instrumental_track)

        # 3. Overlay vocal and instrumental
        safe_print("🔄 Overlaying tracks...")
        final_mix = instrumental_track.overlay(vocal_track) # Overlay vocal onto (potentially side-chained) instrumental
        
        # 4. Add optional effect
        if args.effect_path and os.path.exists(args.effect_path):
            safe_print(f"🔔 Adding Effect: {args.effect_path}")
            try:
                effect_track = AudioSegment.from_file(args.effect_path) + args.effect_gain
                final_mix = final_mix.overlay(effect_track)
            except Exception as e:
                safe_print(f"⚠️ Could not add effect: {e}")

        # 5. Apply mastering effects
        safe_print("🎚️ Applying master compressor...")
        final_mix = effects.compress_dynamic_range(final_mix, threshold=-12.0, ratio=2.0)
        
        if args.apply_dolby:
            safe_print("💎 Applying Dolby Style effect...")
            final_mix = final_mix.set_frame_rate(48000)
            final_mix = effects.normalize(final_mix)
            final_mix = final_mix.low_pass_filter(18000).high_pass_filter(40) # Simulate bandwidth expansion
            # Note: Full Dolby effect requires complex multi-band processing and spatialization.
            # This is a pydub-based approximation using frequency shaping.


        if args.apply_hifi:
            safe_print("👑 Applying Hi-Fi effect...")
            final_mix = effects.normalize(final_mix)
            # Treble boost is one component. High-End Exciter adds more 'air'.
        
        # 6. Apply High-End Exciter (if enabled) - done after other mastering to affect the whole mix
        if args.apply_exciter:
            final_mix = _apply_high_end_exciter(final_mix)

        # 7. Normalize final output
        safe_print("✨ Normalizing final mix...")
        final_mix = effects.normalize(final_mix, headroom=0.1)

        # 8. Export file
        output_format = "wav" if args.apply_hifi else "mp3"
        bitrate = "320k" if output_format == "mp3" else None
        
        safe_print(f"💾 Exporting to {args.output_path} (Format: {output_format.upper()})")
        
        final_mix.export(
            args.output_path,
            format=output_format,
            bitrate=bitrate
        )
        
        safe_print("✅ Process complete!")

    except Exception as e:
        safe_print(f"❌ An error occurred in audio_merger.py: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
