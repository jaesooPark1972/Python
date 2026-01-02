#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GPT-SoVITS Training Engine Integration
=======================================
Full professional-grade voice training system
Optimized for GTX 1060 3GB / GTX 1070

Author: Park Jae-soo (SKY Group)
Version: 1.0
"""

import os
import sys
import subprocess
import json
import shutil
import time
from pathlib import Path
import requests
from tqdm import tqdm

class GPTSoVITSTrainer:
    """
    Complete GPT-SoVITS training pipeline
    
    3-Stage Training:
    1. Data Preprocessing (1-2 min)
    2. SoVITS Training - Voice Tone (20-40 min)
    3. GPT Training - Prosody/Rhythm (15-30 min)
    """
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.engine_dir = os.path.join(base_dir, "GPT_SoVITS_Engine")
        self.pretrained_dir = os.path.join(self.engine_dir, "pretrained_models")
        self.output_dir = os.path.join(base_dir, "output_result")
        
        # VRAM optimization settings (GTX 1060 3GB)
        self.vram_optimized_config = {
            "batch_size": 2,
            "fp16": True,
            "gradient_accumulation_steps": 4,
            "gradient_checkpointing": True,
            "max_audio_length": 10.0,  # seconds
        }
        
    def check_installation(self):
        """
        Verify GPT-SoVITS engine is installed
        Returns: (bool, str) - (is_ready, message)
        """
        if not os.path.exists(self.engine_dir):
            return False, "GPT-SoVITS engine not found. Click 'Install Engine' first."
        
        required_files = [
            "GPT_SoVITS/s1_train.py",
            "GPT_SoVITS/s2_train.py",
            "GPT_SoVITS/prepare_datasets/1-get-text.py",
            "GPT_SoVITS/prepare_datasets/2-get-hubert-wav32k.py",
            "GPT_SoVITS/prepare_datasets/3-get-semantic.py",
        ]
        
        for file in required_files:
            full_path = os.path.join(self.engine_dir, file)
            if not os.path.exists(full_path):
                return False, f"Missing: {file}"
        
        # Check pretrained models
        pretrained_models = [
            "s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt",
            "s2G488k.pth",
            "s2D488k.pth"
        ]
        
        for model in pretrained_models:
            model_path = os.path.join(self.pretrained_dir, model)
            if not os.path.exists(model_path):
                return False, f"Missing pretrained model: {model}"
        
        return True, "GPT-SoVITS engine ready!"
    
    def install_engine(self, progress_callback=None):
        """
        Download and install GPT-SoVITS engine
        
        Args:
            progress_callback: function(message, progress) for UI updates
        """
        try:
            if progress_callback:
                progress_callback("📥 Downloading GPT-SoVITS...", 0.1)
            
            # Clone repository
            if not os.path.exists(self.engine_dir):
                subprocess.run([
                    "git", "clone",
                    "https://github.com/RVC-Boss/GPT-SoVITS.git",
                    self.engine_dir
                ], check=True)
            
            if progress_callback:
                progress_callback("📦 Installing dependencies...", 0.3)
            
            # Install requirements
            req_file = os.path.join(self.engine_dir, "requirements.txt")
            if os.path.exists(req_file):
                subprocess.run([
                    sys.executable, "-m", "pip", "install",
                    "-r", req_file
                ], check=True)
            
            if progress_callback:
                progress_callback("⬇️ Downloading pretrained models...", 0.5)
            
            # Download pretrained models
            self.download_pretrained_models(progress_callback)
            
            if progress_callback:
                progress_callback("✅ Installation complete!", 1.0)
            
            return True, "GPT-SoVITS installed successfully!"
            
        except Exception as e:
            return False, f"Installation failed: {str(e)}"
    
    def download_pretrained_models(self, progress_callback=None):
        """Download required pretrained models from HuggingFace"""
        os.makedirs(self.pretrained_dir, exist_ok=True)
        
        # HuggingFace model URLs
        models = {
            "s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt": 
                "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s1bert25hz-2kh-longer-epoch%3D68e-step%3D50232.ckpt",
            "s2G488k.pth": 
                "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2G488k.pth",
            "s2D488k.pth": 
                "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2D488k.pth",
        }
        
        for i, (filename, url) in enumerate(models.items()):
            output_path = os.path.join(self.pretrained_dir, filename)
            
            if os.path.exists(output_path):
                print(f"✓ {filename} already exists")
                continue
            
            if progress_callback:
                progress = 0.5 + (i / len(models)) * 0.4
                progress_callback(f"Downloading {filename}...", progress)
            
            self._download_file(url, output_path)
    
    def _download_file(self, url, output_path):
        """Download file with progress bar"""
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
    
    def preprocess_training_data(self, package_dir, progress_callback=None):
        """
        Stage 1: Data Preprocessing
        
        Input: GPT_SoVITS_Training_{timestamp}/
               ├── audio/*.wav
               └── cleaned_lyrics.txt
        
        Output: formatted_data/
                ├── wavs/ (32kHz resampled)
                ├── text/
                └── metadata.csv
        """
        try:
            if progress_callback:
                progress_callback("Stage 1/3: Preprocessing data...", 0.1)
            
            # Create output directory
            formatted_dir = os.path.join(package_dir, "formatted_data")
            os.makedirs(formatted_dir, exist_ok=True)
            os.makedirs(os.path.join(formatted_dir, "wavs"), exist_ok=True)
            os.makedirs(os.path.join(formatted_dir, "text"), exist_ok=True)
            
            # Get audio files
            audio_dir = os.path.join(package_dir, "audio")
            audio_files = [f for f in os.listdir(audio_dir) if f.endswith(('.wav', '.mp3'))]
            
            # Read lyrics
            lyrics_path = os.path.join(package_dir, "cleaned_lyrics.txt")
            with open(lyrics_path, 'r', encoding='utf-8') as f:
                lyrics = f.read().strip()
            
            # Split lyrics into sentences
            sentences = [s.strip() for s in lyrics.split('\n') if s.strip()]
            
            # Process each audio file
            metadata = []
            for i, audio_file in enumerate(audio_files):
                src_path = os.path.join(audio_dir, audio_file)
                dst_name = f"sample_{i+1:03d}.wav"
                dst_path = os.path.join(formatted_dir, "wavs", dst_name)
                
                # Resample to 32kHz (GPT-SoVITS requirement)
                self._resample_audio(src_path, dst_path, 32000)
                
                # Assign lyrics (cycle through sentences)
                text = sentences[i % len(sentences)] if sentences else ""
                
                # Save text file
                text_path = os.path.join(formatted_dir, "text", f"sample_{i+1:03d}.txt")
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                # Add to metadata
                metadata.append(f"{dst_name}|{text}")
            
            # Save metadata.csv
            metadata_path = os.path.join(formatted_dir, "metadata.csv")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(metadata))
            
            if progress_callback:
                progress_callback(f"✓ Preprocessed {len(audio_files)} files", 0.15)
            
            return formatted_dir
            
        except Exception as e:
            raise Exception(f"Preprocessing failed: {str(e)}")
    
    def _resample_audio(self, input_path, output_path, target_sr=32000):
        """Resample audio to target sample rate using ffmpeg"""
        try:
            import torchaudio
            waveform, sr = torchaudio.load(input_path)
            
            if sr != target_sr:
                resampler = torchaudio.transforms.Resample(sr, target_sr)
                waveform = resampler(waveform)
            
            torchaudio.save(output_path, waveform, target_sr)
            
        except Exception as e:
            # Fallback to ffmpeg
            subprocess.run([
                "ffmpeg", "-i", input_path,
                "-ar", str(target_sr),
                "-ac", "1",
                "-y", output_path
            ], check=True, capture_output=True)
    
    def train_sovits(self, data_dir, model_name, config, progress_callback=None):
        """
        Stage 2: SoVITS Training (Voice Tone/Timbre)
        
        Generates: {model_name}/sovits_model/G_{epoch}.pth
        """
        try:
            if progress_callback:
                progress_callback("Stage 2/3: Training SoVITS (Voice Tone)...", 0.2)
            
            # Prepare config
            sovits_config = {
                "exp_name": model_name,
                "batch_size": config.get("batch_size", 2),
                "total_epoch": config.get("sovits_epochs", 8),
                "save_every_epoch": 2,
                "learning_rate": 0.0001,
                "fp16": config.get("fp16", True),
                "data_dir": data_dir,
                "gpu": "0"
            }
            
            # Save config
            config_path = os.path.join(self.output_dir, f"{model_name}_sovits_config.json")
            with open(config_path, 'w') as f:
                json.dump(sovits_config, f, indent=2)
            
            # Run training script
            train_script = os.path.join(self.engine_dir, "GPT_SoVITS", "s2_train.py")
            
            cmd = [
                sys.executable, train_script,
                "--config", config_path
            ]
            
            # Execute training
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Monitor progress
            for line in process.stdout:
                print(line.strip())
                if progress_callback and "Epoch" in line:
                    # Parse epoch progress
                    try:
                        epoch = int(line.split("Epoch")[1].split("/")[0].strip())
                        total_epochs = sovits_config["total_epoch"]
                        progress = 0.2 + (epoch / total_epochs) * 0.4
                        progress_callback(f"SoVITS Epoch {epoch}/{total_epochs}", progress)
                    except:
                        pass
            
            process.wait()
            
            if process.returncode != 0:
                raise Exception("SoVITS training failed")
            
            if progress_callback:
                progress_callback("✓ SoVITS training complete", 0.6)
            
        except Exception as e:
            raise Exception(f"SoVITS training failed: {str(e)}")
    
    def train_gpt(self, data_dir, model_name, config, progress_callback=None):
        """
        Stage 3: GPT Training (Prosody/Rhythm)
        
        Generates: {model_name}/gpt_model/s1_{epoch}.ckpt
        """
        try:
            if progress_callback:
                progress_callback("Stage 3/3: Training GPT (Prosody)...", 0.65)
            
            # Prepare config
            gpt_config = {
                "exp_name": model_name,
                "batch_size": config.get("batch_size", 2),
                "total_epoch": config.get("gpt_epochs", 10),
                "save_every_epoch": 2,
                "learning_rate": 0.0001,
                "data_dir": data_dir,
                "gpu": "0"
            }
            
            # Save config
            config_path = os.path.join(self.output_dir, f"{model_name}_gpt_config.json")
            with open(config_path, 'w') as f:
                json.dump(gpt_config, f, indent=2)
            
            # Run training script
            train_script = os.path.join(self.engine_dir, "GPT_SoVITS", "s1_train.py")
            
            cmd = [
                sys.executable, train_script,
                "--config", config_path
            ]
            
            # Execute training
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Monitor progress
            for line in process.stdout:
                print(line.strip())
                if progress_callback and "Epoch" in line:
                    try:
                        epoch = int(line.split("Epoch")[1].split("/")[0].strip())
                        total_epochs = gpt_config["total_epoch"]
                        progress = 0.65 + (epoch / total_epochs) * 0.3
                        progress_callback(f"GPT Epoch {epoch}/{total_epochs}", progress)
                    except:
                        pass
            
            process.wait()
            
            if process.returncode != 0:
                raise Exception("GPT training failed")
            
            if progress_callback:
                progress_callback("✓ GPT training complete", 0.95)
            
        except Exception as e:
            raise Exception(f"GPT training failed: {str(e)}")
    
    def finalize_model(self, model_name):
        """
        Finalize training and organize output files
        
        Returns: path to final model directory
        """
        model_dir = os.path.join(self.output_dir, f"{model_name}_GPT_SoVITS")
        os.makedirs(model_dir, exist_ok=True)
        
        # Create README
        readme_path = os.path.join(model_dir, "README.txt")
        readme_content = f"""
GPT-SoVITS Voice Model: {model_name}
=====================================

Training completed: {time.strftime("%Y-%m-%d %H:%M:%S")}
Created by: Next-Gen AI Audio Workstation

📁 Model Files:
--------------
sovits_model/ - Voice tone/timbre model (.pth)
gpt_model/    - Prosody/rhythm model (.ckpt)

🎤 How to Use:
-------------
1. Install GPT-SoVITS inference tool
2. Load both SoVITS and GPT models
3. Enter text to synthesize
4. Adjust parameters as needed

💡 Recommended Settings:
-----------------------
- Speed: 1.0 (normal)
- Pitch: 0 (no change)
- Prosody strength: 1.0

📧 Support:
----------
Created by Park Jae-soo (SKY Group)
Next-Gen AI Audio Workstation v3.1
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return model_dir


if __name__ == "__main__":
    # Test installation
    trainer = GPTSoVITSTrainer(os.getcwd())
    is_ready, msg = trainer.check_installation()
    print(f"Status: {msg}")
