# setup_video.py
import subprocess
import sys
import os

def install_packages():
    print("Setting up video processing packages...")
    
    # List of required packages
    packages = [
        "imageio==2.31.1",
        "imageio-ffmpeg>=0.4.9",
        "moviepy==1.0.3",
        "decorator>=4.4.2",
        "proglog>=0.1.10"
    ]
    
    for package in packages:
        try:
            print(f"\nInstalling {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully!")
        except Exception as e:
            print(f"❌ Error installing {package}: {str(e)}")
            return False
    
    return True

def verify_installation():
    print("\nVerifying installations...")
    try:
        # Test imageio and ffmpeg
        import imageio
        import imageio_ffmpeg
        print("✅ imageio and ffmpeg imported successfully")
        
        # Test moviepy
        import moviepy.editor as mp
        print("✅ moviepy imported successfully")
        
        # Print versions
        print(f"\nInstalled versions:")
        print(f"imageio: {imageio.__version__}")
        print(f"imageio-ffmpeg: {imageio_ffmpeg.__version__}")
        print(f"moviepy: {mp.__version__}")
        
        return True
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False