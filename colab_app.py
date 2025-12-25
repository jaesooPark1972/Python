
import gradio as gr
import os
import shutil
import zipfile
import threading
import time
from voice_trainer import RealVoiceTrainer
from rvc_trainer import VoiceConverter
from vocal_enhancer import VocalEnhancer

# Paths
BASE_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TRAIN_DATA_DIR = os.path.join(BASE_DIR, "training_data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TRAIN_DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Global instances
trainer = RealVoiceTrainer()
converter = VoiceConverter()
enhancer = VocalEnhancer()

def unzip_data(zip_file):
    target_dir = os.path.join(TRAIN_DATA_DIR, "current_dataset")
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_file.name, 'r') as zip_ref:
        zip_ref.extractall(target_dir)
    
    # Check for 'audio' folder inside
    audio_dir = os.path.join(target_dir, "audio")
    if not os.path.exists(audio_dir):
        # Allow flat zip
        audio_dir = target_dir
        
    return f"Dataset Extracted to {target_dir}. Ready to train."

def run_training(model_name, epochs, progress=gr.Progress()):
    target_dir = os.path.join(TRAIN_DATA_DIR, "current_dataset")
    # If explicit audio folder exists, use it
    if os.path.exists(os.path.join(target_dir, "audio")):
         package_path = target_dir
    else:
         # Create a structure expected by voice_trainer
         package_path = os.path.join(TRAIN_DATA_DIR, "package_struct")
         os.makedirs(os.path.join(package_path, "audio"), exist_ok=True)
         # Copy all wavs from target_dir to package_path/audio
         for f in os.listdir(target_dir):
             if f.endswith(('.wav', '.mp3', '.flac')):
                 shutil.copy(os.path.join(target_dir, f), os.path.join(package_path, "audio", f))
    
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
        return "Please upload both vocal file and model file.", None
        
    try:
        progress(0.1, desc="Loading Model...")
        success = converter.load_model(model_file.name)
        if not success:
            return "Failed to load model.", None
            
        output_path = os.path.join(OUTPUT_DIR, f"converted_{int(time.time())}.wav")
        progress(0.3, desc="Converting...")
        
        success = converter.convert(vocal_file.name, output_path)
        
        if success:
            return "Conversion Successful!", output_path
        else:
            return "Conversion Failed.", None
    except Exception as e:
        return f"Error: {e}", None

def run_mixing(vocal_path, mr_path, vocal_vol, mr_vol, reverb, model_path, use_rvc, progress=gr.Progress()):
    if not vocal_path or not mr_path:
        return "Please upload both Vocal and MR files.", None
    
    try:
        # 1. RVC Conversion (Optional)
        vocal_to_mix = vocal_path
        
        if use_rvc and model_path:
            progress(0.1, desc="Running RVC Conversion first...")
            rvc_out = os.path.join(OUTPUT_DIR, "temp_rvc_vocal.wav")
            
            # Load model
            if not converter.load_model(model_path.name):
                return "RVC Model Load Failed!", None
                
            if converter.convert(vocal_path, rvc_out):
                vocal_to_mix = rvc_out
            else:
                return "RVC Conversion Failed!", None
        
        # 2. Mixing
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


# Build Interface
with gr.Blocks(title="Next-Gen AI Audio Workstation (Colab Edition)", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎵 Next-Gen AI Audio Workstation (Colab Edition)")
    gr.Markdown("Created by **Music Revolutionary JAESOO**")
    
    with gr.Tab("🎙️ Voice Training"):
        gr.Markdown("### Train your own AI Voice Model")
        with gr.Row():
            train_zip = gr.File(label="Upload Training Data (ZIP of WAVs)", file_types=['.zip'])
            train_btn = gr.Button("1. Unzip Data")
        
        unzip_status = gr.Textbox(label="Status", interactive=False)
        train_btn.click(unzip_data, inputs=[train_zip], outputs=[unzip_status])
        
        with gr.Row():
            model_name_input = gr.Textbox(label="Model Name", value="MyVoice")
            epochs_input = gr.Slider(minimum=5, maximum=100, value=20, step=5, label="Epochs")
            start_train_btn = gr.Button("2. Start Training", variant="primary")
        
        train_status = gr.Textbox(label="Training Status")
        train_output_file = gr.File(label="Download Model (.pth)")
        
        start_train_btn.click(
            run_training, 
            inputs=[model_name_input, epochs_input], 
            outputs=[train_status, train_output_file]
        )
        
    with gr.Tab("🔄 RVC Conversion"):
        gr.Markdown("### Convert Voice using AI Model")
        with gr.Row():
            rvc_vocal = gr.Audio(type="filepath", label="Input Vocal File")
            rvc_model = gr.File(label="Upload .pth Model")
        
        rvc_btn = gr.Button("Convert Voice", variant="primary")
        rvc_status = gr.Textbox(label="Status")
        rvc_result = gr.Audio(label="Converted Audio")
        
        rvc_btn.click(
            run_rvc_conversion,
            inputs=[rvc_vocal, rvc_model],
            outputs=[rvc_status, rvc_result]
        )
        
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
        
        mix_btn.click(
            run_mixing,
            inputs=[mix_vocal, mix_mr, vol_vocal, vol_mr, reverb_amt, mix_model, use_rvc_chk],
            outputs=[mix_status, mix_result]
        )

if __name__ == "__main__":
    app.queue().launch(share=True)
