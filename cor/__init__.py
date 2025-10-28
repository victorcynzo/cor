"""
Cor - Advanced Gaze Detection Library
Python fallback implementation when C extension is not available
"""

import sys
import os

# Try to import the C extension first
try:
    from . import cor_c_extension as _cor
    _has_c_extension = True
except ImportError:
    _has_c_extension = False
    _cor = None

def help():
    """Display help information for all cor functions"""
    if _has_c_extension:
        return _cor.help()
    else:
        print("Cor - Advanced Gaze Detection Library (Python fallback mode)")
        print("=" * 60)
        print("WARNING: C extension not available. Limited functionality.")
        print()
        print("Available functions:")
        print("  cor.help() - Display this help")
        print("  cor.version() - Show version information")
        print("  cor.run(video_file) - Basic gaze detection (requires OpenCV)")
        print()
        print("For full functionality, install OpenCV development headers:")
        print("  - Windows: pip install opencv-contrib-python")
        print("  - Linux: sudo apt-get install libopencv-dev")
        print("  - macOS: brew install opencv")

def version():
    """Get version information"""
    if _has_c_extension:
        return _cor.version()
    else:
        return {
            'version': '1.0.2',
            'mode': 'Python fallback',
            'c_extension': False,
            'opencv_available': _check_opencv()
        }

def _check_opencv():
    """Check if OpenCV is available"""
    try:
        import cv2
        return True
    except ImportError:
        return False

def run(video_file, *args):
    """Basic gaze detection using Python and OpenCV"""
    if _has_c_extension:
        return _cor.run(video_file, *args)
    else:
        try:
            import cv2
            import numpy as np
            print(f"Processing {video_file} in Python fallback mode...")
            print("Note: This is a basic implementation. Install C extension for full features.")
            
            # Basic video processing
            cap = cv2.VideoCapture(video_file)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_file}")
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"Video has {frame_count} frames")
            
            # Simple processing - just validate the video
            ret, frame = cap.read()
            if ret:
                print(f"Video resolution: {frame.shape[1]}x{frame.shape[0]}")
                print("Basic validation complete. For full gaze detection, install C extension.")
            
            cap.release()
            return True
            
        except ImportError:
            print("ERROR: OpenCV not available. Please install opencv-python.")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

def calibrate_eyes(video_file):
    """Eye calibration (requires C extension)"""
    if _has_c_extension:
        return _cor.calibrate_eyes(video_file)
    else:
        print("ERROR: Eye calibration requires C extension.")
        print("Install OpenCV development headers to enable this feature.")
        return False

def calibrate_gaze(video_file):
    """Gaze calibration (requires C extension)"""
    if _has_c_extension:
        return _cor.calibrate_gaze(video_file)
    else:
        print("ERROR: Gaze calibration requires C extension.")
        print("Install OpenCV development headers to enable this feature.")
        return False

# Additional functions that require C extension
def get_config(param_name, config_file="cor.txt"):
    if _has_c_extension:
        return _cor.get_config(param_name, config_file)
    else:
        print("ERROR: Configuration management requires C extension.")
        return None

def set_config(param_name, param_value, config_file="cor.txt"):
    if _has_c_extension:
        return _cor.set_config(param_name, param_value, config_file)
    else:
        print("ERROR: Configuration management requires C extension.")
        return False

def validate_video(video_file):
    if _has_c_extension:
        return _cor.validate_video(video_file)
    else:
        try:
            import cv2
            cap = cv2.VideoCapture(video_file)
            if not cap.isOpened():
                return False
            ret, frame = cap.read()
            cap.release()
            return ret
        except:
            return False

def extract_frames(video_file, num_frames=10, output_dir="frames"):
    if _has_c_extension:
        return _cor.extract_frames(video_file, num_frames, output_dir)
    else:
        print("ERROR: Frame extraction requires C extension.")
        return False

def benchmark(video_file, max_frames=100):
    if _has_c_extension:
        return _cor.benchmark(video_file, max_frames)
    else:
        print("ERROR: Benchmarking requires C extension.")
        return False

def analyze_attention(video_file):
    if _has_c_extension:
        return _cor.analyze_attention(video_file)
    else:
        print("ERROR: Attention analysis requires C extension.")
        return False

def generate_advanced_heatmap(video_file, mode="density"):
    if _has_c_extension:
        return _cor.generate_advanced_heatmap(video_file, mode)
    else:
        print("ERROR: Advanced heatmap generation requires C extension.")
        return False

def export_analysis(video_file, output_file="analysis.json"):
    if _has_c_extension:
        return _cor.export_analysis(video_file, output_file)
    else:
        print("ERROR: Analysis export requires C extension.")
        return False

def init_realtime(camera_id=0):
    if _has_c_extension:
        return _cor.init_realtime(camera_id)
    else:
        print("ERROR: Real-time processing requires C extension.")
        return False

def process_realtime_frame():
    if _has_c_extension:
        return _cor.process_realtime_frame()
    else:
        print("ERROR: Real-time processing requires C extension.")
        return None

def cleanup_realtime():
    if _has_c_extension:
        return _cor.cleanup_realtime()
    else:
        print("ERROR: Real-time processing requires C extension.")
        return False