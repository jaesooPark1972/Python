# -*- coding: utf-8 -*-
import os
import sys

# [CRITICAL] TensorFlow legacy Keras setting for TF 2.16+
os.environ["TF_USE_LEGACY_KERAS"] = "1"

# [NEW] Keras 3 Compatibility fix: Force use of tf-keras if available
try:
    import tf_keras as keras
    import sys
    sys.modules['keras'] = keras
except ImportError:
    pass

def main():
    if len(sys.argv) < 3:
        print("Usage: python midi_engine.py <input_audio> <output_midi>")
        sys.exit(1)

    audio_path = sys.argv[1]
    output_midi = sys.argv[2]

    # Try basic-pitch first
    try:
        from basic_pitch.inference import predict
        from basic_pitch import ICASSP_2022_MODEL_PATH
        
        print(f"Predicting MIDI with basic-pitch for {audio_path}...")
        model_output, midi_data, note_events = predict(
            audio_path, 
            model_or_model_path=ICASSP_2022_MODEL_PATH
        )
        
        os.makedirs(os.path.dirname(output_midi), exist_ok=True)
        midi_data.write(output_midi)
        print(f"MIDI Saved successfully: {output_midi}")
        sys.exit(0)
    except ImportError:
        print("basic-pitch not available, using librosa fallback...")
    except Exception as e:
        print(f"basic-pitch failed: {e}, using librosa fallback...")
    
    # Fallback to librosa + pretty_midi
    try:
        import librosa
        import pretty_midi
        import numpy as np
        
        print(f"Loading audio: {audio_path}...")
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        
        print("Extracting pitch information...")
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        
        midi = pretty_midi.PrettyMIDI()
        instrument = pretty_midi.Instrument(program=0)
        
        hop_length = 512
        frame_duration = hop_length / sr
        
        current_note = None
        note_start = 0
        
        for i in range(pitches.shape[1]):
            index = magnitudes[:, i].argmax()
            pitch_hz = pitches[index, i]
            
            if pitch_hz > 0:
                midi_note = int(librosa.hz_to_midi(pitch_hz))
                
                if current_note is None:
                    current_note = midi_note
                    note_start = i * frame_duration
                elif midi_note != current_note:
                    note_end = i * frame_duration
                    if note_end - note_start > 0.1:
                        note = pretty_midi.Note(
                            velocity=100,
                            pitch=current_note,
                            start=note_start,
                            end=note_end
                        )
                        instrument.notes.append(note)
                    current_note = midi_note
                    note_start = i * frame_duration
            else:
                if current_note is not None:
                    note_end = i * frame_duration
                    if note_end - note_start > 0.1:
                        note = pretty_midi.Note(
                            velocity=100,
                            pitch=current_note,
                            start=note_start,
                            end=note_end
                        )
                        instrument.notes.append(note)
                    current_note = None
        
        if current_note is not None:
            note_end = len(y) / sr
            if note_end - note_start > 0.1:
                note = pretty_midi.Note(
                    velocity=100,
                    pitch=current_note,
                    start=note_start,
                    end=note_end
                )
                instrument.notes.append(note)
        
        midi.instruments.append(instrument)
        os.makedirs(os.path.dirname(output_midi), exist_ok=True)
        midi.write(output_midi)
        print(f"MIDI saved successfully: {output_midi} ({len(instrument.notes)} notes)")
        sys.exit(0)
        
    except Exception as e:
        print(f"MIDI Engine Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

