import gradio as gr
import os
import shutil
import zipfile
import threading
import time
import argparse
import sys
from voice_trainer import RealVoiceTrainer
from rvc_trainer import VoiceConverter
from vocal_enhancer import VocalEnhancer

# Paths - Automatically detect base directory for local/packaged distribution (v2.3)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TRAIN_DATA_DIR = os.path.join(BASE_DIR, "training_data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

for d in [OUTPUT_DIR, TRAIN_DATA_DIR, MODELS_DIR]:
    os.makedirs(d, exist_ok=True)

# Global instances
trainer = RealVoiceTrainer()
converter = VoiceConverter()
enhancer = VocalEnhancer()

# 디자인: 120% 확대하여 하단/측면 로고 영역을 물리적으로 밀어냄 (v2.3)
unicorn_html = """
<div style="width: 100%; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
    <h1 style="margin: 0; font-size: 28px;">🎙️ MusicSoundLevelUP Station</h1>
    <p style="margin: 5px 0 0 0; opacity: 0.8;">Professional AI Audio Massive Batch System v2.3</p>
</div>
"""

def unzip_data(zip_file):
    target_dir = os.path.join(TRAIN_DATA_DIR, "current_dataset")
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    
    # Gradio 4.x handles file as path string
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(target_dir)
    
    return f"Dataset Extracted to {target_dir}. Ready to train."

def run_training(model_name, epochs, progress=gr.Progress()):
    package_path = os.path.join(TRAIN_DATA_DIR, "current_dataset")
    if not os.path.exists(package_path):
        return "Error: 학습 데이터가 없습니다. 먼저 ZIP 파일을 업로드하고 'Unzip Data' 버튼을 눌러주세요.", None
    
    def progress_wrapper(p, msg):
        progress(p/100, desc=msg)
        
    try:
        model_path = trainer.train(
            package_path=package_path,
            model_name=model_name,
            epochs=int(epochs),
            progress_callback=progress_wrapper
        )
        if model_path:
            return f"Training Complete! Model saved at: {model_path}", model_path
        else:
            return "Training Failed. Check logs.", None
    except Exception as e:
        return f"Error: {str(e)}", None

def run_rvc_conversion(vocal_file, model_file, progress=gr.Progress()):
    if not vocal_file or not model_file:
        return "파일을 업로드해주세요.", None
    try:
        progress(0.1, desc="Loading Model...")
        # Gradio 4.x compatible: direct path string
        success = converter.load_model(model_file)
        if not success:
            return "Failed to load model.", None
            
        output_path = os.path.join(OUTPUT_DIR, f"result_{int(time.time())}.wav")
        progress(0.3, desc="Converting...")
        
        if converter.convert(vocal_file, output_path):
            return "변환 성공!", output_path
        else:
            return "변환 중 오류 발생", None
    except Exception as e:
        return f"에러: {str(e)}", None

def run_mixing(vocal_path, mr_path, vocal_vol, mr_vol, reverb, model_path, use_rvc, progress=gr.Progress()):
    if not vocal_path or not mr_path:
        return "Please upload both Vocal and MR files.", None
    
    try:
        vocal_to_mix = vocal_path
        if use_rvc and model_path:
            progress(0.1, desc="Running RVC Conversion first...")
            rvc_out = os.path.join(OUTPUT_DIR, "temp_rvc_vocal.wav")
            if not converter.load_model(model_path):
                return "RVC Model Load Failed!", None
            if converter.convert(vocal_path, rvc_out):
                vocal_to_mix = rvc_out
            else:
                return "RVC Conversion Failed!", None
        
        output_path = os.path.join(OUTPUT_DIR, f"final_mix_{int(time.time())}.mp3")
        def progress_wrapper(p, msg):
            progress(p/100, desc=msg)
            
        success = enhancer.process(
            vocal_path=vocal_to_mix,
            mr_path=mr_path,
            output_path=output_path,
            vocal_volume=vocal_vol,
            mr_volume=mr_vol,
            reverb_amount=reverb,
            progress_callback=progress_wrapper
        )
        
        if success:
            return "Mixing Complete!", output_path
        else:
            return "Mixing Failed.", None
    except Exception as e:
        return f"Error: {e}", None

def run_massive_batch_job(input_folder, model_path):
    if not os.path.exists(input_folder):
        return f"Error: 입력 폴더를 찾을 수 없습니다: {input_folder}"
    if not os.path.exists(model_path):
        return f"Error: 모델 파일을 찾을 수 없습니다: {model_path}"
    if not converter.load_model(model_path):
        return "Error: AI 모델 로드 실패"
        
    batch_out = os.path.join(OUTPUT_DIR, f"batch_{int(time.time())}")
    os.makedirs(batch_out, exist_ok=True)
    
    files = [f for f in os.listdir(input_folder) if f.endswith(('.wav', '.mp3', '.flac'))]
    files.sort()
    
    print(f"🚀 배치 처리 시작: 총 {len(files)}개 파일 발견")
    success_count = 0
    for i, filename in enumerate(files):
        in_path = os.path.join(input_folder, filename)
        out_path = os.path.join(batch_out, f"ai_{filename}")
        print(f"   [{i+1}/{len(files)}] 변환 중: {filename}...")
        try:
            if converter.convert(in_path, out_path):
                success_count += 1
            else:
                print(f"   ⚠️ 실패: {filename}")
        except Exception as e:
            print(f"   ❌ 오류: {filename} ({e})")
            
    return f"✅ 배치 처리 완료! 성공: {success_count}/{len(files)}\n결과 저장: {batch_out}"

# UI Build
with gr.Blocks(title="Next-Gen AI Audio Workstation (Massive Edition)", theme=gr.themes.Soft()) as app:
    gr.HTML(unicorn_html)
    gr.Markdown("# 🎵 Next-Gen AI Audio Workstation (v2.3)")
    gr.Markdown("Created by **Music Revolutionary JAESOO (SKY Group)**")
    
    with gr.Tab("🎙️ Voice Training"):
        gr.Markdown("### Train your own AI Voice Model")
        with gr.Row():
            train_zip = gr.File(label="Upload Training Data (ZIP of WAVs)", file_types=['.zip'])
            train_btn = gr.Button("1. Unzip Data")
        unzip_status = gr.Textbox(label="Status", interactive=False)
        train_btn.click(unzip_data, inputs=[train_zip], outputs=[unzip_status])
        with gr.Row():
            model_name_input = gr.Textbox(label="Model Name", value="MyVoice")
            epochs_input = gr.Slider(minimum=5, maximum=200, value=20, step=5, label="Epochs")
            start_train_btn = gr.Button("2. Start Training", variant="primary")
        train_status = gr.Textbox(label="Training Status")
        train_output_file = gr.File(label="Download Model (.pth)")
        start_train_btn.click(run_training, inputs=[model_name_input, epochs_input], outputs=[train_status, train_output_file])
        
    with gr.Tab("🔄 RVC Conversion"):
        gr.Markdown("### Convert Voice using AI Model")
        with gr.Row():
            rvc_vocal = gr.Audio(type="filepath", label="Input Vocal File")
            rvc_model = gr.File(label="Upload .pth Model")
        rvc_btn = gr.Button("Convert Voice", variant="primary")
        rvc_status = gr.Textbox(label="Status")
        rvc_result = gr.Audio(label="Converted Audio")
        rvc_btn.click(run_rvc_conversion, inputs=[rvc_vocal, rvc_model], outputs=[rvc_status, rvc_result])
        
    with gr.Tab("🎛️ AI Studio Mixing"):
        gr.Markdown("### Mix Vocals + MR (with optional AI Conversion)")
        with gr.Row():
            mix_vocal = gr.Audio(type="filepath", label="Vocal Track")
            mix_mr = gr.Audio(type="filepath", label="MR / Instrumental")
        with gr.Accordion("AI Voice Conversion Settings (Optional)", open=False):
            use_rvc_chk = gr.Checkbox(label="Enable RVC Conversion before Mixing", value=False)
            mix_model = gr.File(label="Select RVC Model (.pth)")
        with gr.Row():
            vol_vocal = gr.Slider(-10, 10, value=0, label="Vocal Volume (dB)")
            vol_mr = gr.Slider(-10, 10, value=0, label="MR Volume (dB)")
            reverb_amt = gr.Slider(0, 100, value=30, label="Reverb (ms)")
        mix_btn = gr.Button("Start AI Mixing", variant="primary")
        mix_status = gr.Textbox(label="Status")
        mix_result = gr.Audio(label="Final Mix")
        mix_btn.click(run_mixing, inputs=[mix_vocal, mix_mr, vol_vocal, vol_mr, reverb_amt, mix_model, use_rvc_chk], outputs=[mix_status, mix_result])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Next-Gen AI Audio Workstation")
    parser.add_argument("--batch_mode", action="store_true", help="Run in batch mode without UI")
    args = parser.parse_args()

    if args.batch_mode:
        print("\n" + "="*60)
        print("🚀 BATCH MODE ACTIVE (Massive Overnight Processing)")
        print("="*60)
        batch_input = os.path.join(BASE_DIR, "batch_input")
        os.makedirs(batch_input, exist_ok=True)
        model_list = [f for f in os.listdir(MODELS_DIR) if f.endswith('.pth')]
        if not model_list:
            print("❌ [ERROR] 'models' 폴더에 .pth 파일이 없습니다.")
            sys.exit(1)
        target_model = os.path.join(MODELS_DIR, model_list[0])
        print(f"[INFO] 모델: {target_model}")
        print(f"[INFO] 입력 폴더: {batch_input}")
        result = run_massive_batch_job(batch_input, target_model)
        print(f"\n{result}")
        print("======================================================\n")
        time.sleep(2) 
    else:
        app.queue().launch(share=True)