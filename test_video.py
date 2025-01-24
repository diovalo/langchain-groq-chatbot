# test_video.py
import os
import tempfile


def test_video_processing():
    print("Testing video processing capabilities...")
    
    try:
        import moviepy.editor as mp
        print("✅ MoviePy imported successfully")
        
        # Create a simple test video
        duration = 3
        size = (320, 240)
        color = (255, 0, 0)  # Red
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Create test video
        clip = mp.ColorClip(size, color, duration=duration)
        clip.write_videofile(temp_path, fps=24)
        
        # Read the video back
        video = mp.VideoFileClip(temp_path)
        print(f"✅ Video processing works! Duration: {video.duration} seconds")
        
        # Cleanup
        video.close()
        os.unlink(temp_path)
        
        print("\n✨ All video processing tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_video_processing()