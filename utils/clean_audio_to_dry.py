import pedalboard
from pedalboard.io import AudioFile
from pedalboard import NoiseGate, Compressor, HighPassFilter

# AI가 이 함수를 MCP 도구로 호출하게 함
def clean_audio_to_dry(input_path, output_path):
    with AudioFile(input_path) as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate

    # FL Studio의 이펙트 체인을 코드로 구현
    board = pedalboard.Pedalboard([
        HighPassFilter(cutoff_frequency_hz=80), # 저역대 웅웅거림 제거
        NoiseGate(threshold_db=-30),           # 화이트 노이즈 제거 (Gate)
        Compressor(threshold_db=-20)           # 소리 크기 평탄화
    ])

    effected = board(audio, samplerate)

    with AudioFile(output_path, 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)