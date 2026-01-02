# -*- coding: utf-8 -*-
"""
Alternative MIDI Engine using librosa + pretty_midi
Fallback solution for basic-pitch compatibility issues
"""
import os
import sys
import numpy as np

def main():
    if len(sys.argv) < 3:
        print("Usage: python midi_engine_alt.py <input_audio> <output_midi>")
        sys.exit(1)

    audio_path = sys.argv[1]
    output_midi = sys.argv[2]

    try:
        import librosa
        import pretty_midi
        
        print(f"Loading audio: {audio_path}...")
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        
        print("Extracting pitch information...")
        # Use librosa's piptrack for pitch detection
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        
        # Create MIDI object
        midi = pretty_midi.PrettyMIDI()
        instrument = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano
        
        # Extract notes from pitch tracking
        hop_length = 512
        frame_duration = hop_length / sr
        
        current_note = None
        note_start = 0
        
        for i in range(pitches.shape[1]):
            # Get the pitch with highest magnitude
            index = magnitudes[:, i].argmax()
            pitch_hz = pitches[index, i]
            
            if pitch_hz > 0:
                # Convert Hz to MIDI note number
                midi_note = int(librosa.hz_to_midi(pitch_hz))
                
                if current_note is None:
                    # Start new note
                    current_note = midi_note
                    note_start = i * frame_duration
                elif midi_note != current_note:
                    # Note changed, save previous note
                    note_end = i * frame_duration
                    if note_end - note_start > 0.1:  # Minimum note duration
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
                # Silence, end current note if exists
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
        
        # Add final note if exists
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
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_midi), exist_ok=True)
        
        # Save MIDI file
        midi.write(output_midi)
        print(f"MIDI saved successfully: {output_midi}")
        print(f"Extracted {len(instrument.notes)} notes")
        sys.exit(0)
        
    except Exception as e:
        print(f"MIDI Engine Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
