import torch
import sys

print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Device count: {torch.cuda.device_count()}")
    print(f"Current device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")
else:
    print("\nWhy CUDA might not be available:")
    if not torch.cuda.is_available():
        print("- torch.cuda.is_available() returned False")
    
    # Check if this is a CPU-only build
    if "cu" not in torch.__version__ and "+" in torch.__version__:
        print("- This looks like a version without CUDA support (no 'cu' in version string)")
    elif "+" not in torch.__version__:
        print("- This might be a standard PyPI version which may or may not support your GPU/CUDA.")

    try:
        import torch.cuda
        print("- torch.cuda module is importable")
    except ImportError:
        print("- torch.cuda module is NOT importable")
