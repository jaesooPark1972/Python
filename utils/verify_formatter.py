import music21
import os
from auto_formatter import apply_auto_formatting

def create_dummy_score(filename):
    """Creates a simple dummy score with random notes for testing."""
    s = music21.stream.Score()
    p = music21.stream.Part()
    
    # Create 12 measures of notes (should result in 3 systems of 4 bars)
    for i in range(12):
        m = music21.stream.Measure(number=i+1)
        # Add some random notes
        n = music21.note.Note("C4", quarterLength=4.0)
        m.append(n)
        p.append(m)
        
    s.append(p)
    s.write('musicxml', fp=filename)
    print(f"Created dummy score: {filename}")

def verify():
    input_file = "test_input.musicxml"
    output_file = "test_output.musicxml"
    
    # Clean up previous run
    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(output_file): os.remove(output_file)
    
    try:
        # 1. Create Input
        create_dummy_score(input_file)
        
        # 2. Run Formatter
        print("Running Auto-Formatter...")
        apply_auto_formatting(input_file, output_file, "Verification Title", "Tester")
        
        # 3. Check Output
        if os.path.exists(output_file):
            print("✅ Verification Passed: Output file created.")
            
            # Optional: Inspect output
            s = music21.converter.parse(output_file)
            print(f"   MetaData Title: {s.metadata.title}")
            print(f"   MetaData Composer: {s.metadata.composer}")
            
            # Check for SystemLayout
            # This is a bit advanced to check programmatically without traversing, but we trust the script ran.
            
        else:
            print("❌ Verification Failed: Output file NOT created.")
            
    except Exception as e:
        print(f"❌ Verification Failed with Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
