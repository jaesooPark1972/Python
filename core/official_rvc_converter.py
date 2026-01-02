import torch
import os
import time
from scipy.io.wavfile import write
try:
    from rvc.modules.vc.modules import VC
except ImportError:
    VC = None

# Fallback Engine
try:
    from rvc_trainer import VoiceConverter
except ImportError:
    VoiceConverter = None

class OfficialRVCConverter:
    def __init__(self, device=None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.vc = None
        self.rvc_available = False
        self.is_fallback = False

        if VC:
            try:
                self.vc = VC()
                self.rvc_available = True
                print(f"🚀 Official RVC Engine Initialized (Device: {self.device})")
            except Exception as e:
                print(f"⚠️ Official RVC Engine failed to initialize: {e}")
                self.rvc_available = False
        
        # Professional Fallback logic
        if not self.rvc_available and VoiceConverter:
            try:
                print("🔄 Official RVC module missing. Switching to HQ Fallback Engine...")
                self.vc = VoiceConverter()
                self.rvc_available = True
                self.is_fallback = True
                print(f"✅ HQ Fallback Engine Initialized (Device: {self.device})")
            except Exception as e:
                print(f"❌ HQ Fallback Engine failed: {e}")
                self.rvc_available = False

        if not self.rvc_available:
             print("❌ All RVC Engines failed to initialize. RVC functionality will be disabled.")

    def convert(self, input_path, model_path, index_path=None,
                f0_method="rmvpe",    # RMVPE is highly recommended
                index_rate=0.4,       # 0.3~0.5 suggested
                protect=0.33,         # Protects high frequencies
                filter_radius=3,      # Smooths out breathiness
                pitch_shift=0,        # Transposition
                output_path=None):
        
        if not self.rvc_available:
            print("Error: RVC converter not available due to missing dependencies or initialization failure.")
            return None

        if not self.vc:
            print("❌ Converter not initialized properly.")
            return None

        if output_path is None:
            os.makedirs("output_result", exist_ok=True)
            output_path = os.path.join("output_result", f"rvc_{int(time.time())}.wav")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            # Load the model
            print(f"   [Model] Loading: {os.path.basename(model_path)}")
            
            if self.is_fallback:
                # Fallback engine (rvc_trainer.py) has a simple load_model method
                success = self.vc.load_model(model_path)
                if not success:
                    raise Exception("Fallback model load failed.")
                
                # Inference via fallback
                # mapping parameters to fallback convert signature
                success = self.vc.convert(
                    in_path=input_path, 
                    out_path=output_path,
                    f0_method=f0_method,
                    index_rate=index_rate,
                    protect=protect,
                    filter_radius=filter_radius
                )
                if not success:
                    raise Exception("Fallback conversion failed.")
            else:
                # Official RVC inference call
                self.vc.get_vc(model_path)
                tgt_sr, audio_opt, times, _ = self.vc.vc_inference(
                    f0_up_key=pitch_shift,
                    f0_method=f0_method,
                    file_index=index_path or "",
                    index_rate=index_rate,
                    filter_radius=filter_radius,
                    resample_sr=0,
                    rms_mix_rate=0.25,
                    protect=protect
                )
                # Save the result
                write(output_path, tgt_sr, audio_opt)
            
            print(f"✅ Conversion Success: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Conversion Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
