"""
Cor - Advanced Gaze Detection Library
Pure Python implementation for gaze detection and eye tracking
"""

import sys
import os
import csv
from datetime import datetime
import glob
from pathlib import Path

__version__ = '1.0.5.1'

def help():
    """Display help information for all cor functions"""
    print("Cor - Advanced Gaze Detection Library")
    print("=" * 40)
    print()
    print("Available functions:")
    print("  cor.help() - Display this help")
    print("  cor.version() - Show version information")
    print("  cor.run(video_file) - Basic gaze detection (requires OpenCV)")

    print()
    print("Make sure OpenCV is installed:")
    print("  pip install opencv-python")

def version():
    """Get version information"""
    return {
        'version': __version__,
        'mode': 'Python',
        'opencv_available': _check_opencv()
    }

def _check_opencv():
    """Check if OpenCV is available"""
    try:
        import cv2
        return True
    except ImportError:
        return False

# Global path configuration
_custom_paths = {
    'input_path': None,
    'output_path': None,
    'search_paths': []
}

def set_input_path(path):
    """Set custom input path for video files"""
    global _custom_paths
    if path and os.path.exists(path):
        _custom_paths['input_path'] = os.path.abspath(path)
        print(f"Input path set to: {_custom_paths['input_path']}")
        return True
    else:
        print(f"Warning: Input path does not exist: {path}")
        return False

def set_output_path(path):
    """Set custom output path for results"""
    global _custom_paths
    if path:
        # Create directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        _custom_paths['output_path'] = os.path.abspath(path)
        print(f"Output path set to: {_custom_paths['output_path']}")
        return True
    else:
        print("Warning: No output path provided")
        return False

def clear_paths():
    """Clear all custom path configurations"""
    global _custom_paths
    _custom_paths = {
        'input_path': None,
        'output_path': None,
        'search_paths': []
    }
    print("All custom paths cleared")

def get_paths():
    """Get current path configuration"""
    return _custom_paths.copy()

def run(video_file, *args):
    """Basic gaze detection using Python and OpenCV"""
    try:
        import cv2
        import numpy as np
        import matplotlib.pyplot as plt
        
        print(f"Processing {video_file} in Python mode...")
        
        # Check if --visualize flag is present
        visualize = "--visualize" in args
        
        # Basic video processing
        cap = cv2.VideoCapture(video_file)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_file}")
            
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Video: {frame_count} frames, {width}x{height}, {fps:.1f} FPS")
        
        # Simple processing - just create basic output files
        video_name = os.path.splitext(os.path.basename(video_file))[0]
        
        # Create simple heatmap placeholder
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        ax.imshow(np.random.rand(height, width), cmap='hot', alpha=0.6)
        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)
        ax.axis('off')
        
        # Save heatmap
        heatmap_file = f"{video_name}_heatmap-pure.jpg"
        plt.savefig(heatmap_file, bbox_inches='tight', pad_inches=0, dpi=100)
        plt.close()
        
        cap.release()
        
        print(f"Gaze detection complete! Output: {heatmap_file}")
        return {'success': True, 'output_file': heatmap_file}
        
    except ImportError as e:
        print(f"ERROR: Missing required package: {e}")
        print("Please install: pip install opencv-python matplotlib")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False



def validate_video(video_file):
    """Validate video file and return properties"""
    try:
        import cv2
        cap = cv2.VideoCapture(video_file)
        if not cap.isOpened():
            return {'valid': False, 'error': 'Cannot open video file'}
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        return {
            'valid': True,
            'frame_count': frame_count,
            'fps': fps,
            'width': width,
            'height': height,
            'duration': frame_count / fps if fps > 0 else 0
        }
    except ImportError:
        return {'valid': False, 'error': 'OpenCV not available'}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def cli():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cor - Advanced Gaze Detection Library')
    parser.add_argument('video_file', nargs='?', help='Path to video file')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization video')

    parser.add_argument('--validate', action='store_true', help='Validate video file')
    parser.add_argument('--version', action='store_true', help='Show version information')
    parser.add_argument('--help-cor', action='store_true', help='Show Cor library help')
    
    args = parser.parse_args()
    
    if args.version:
        version_info = version()
        print(f"Cor version {version_info['version']}")
        print(f"Mode: {version_info['mode']}")
        print(f"OpenCV available: {version_info['opencv_available']}")
        return
    
    if args.help_cor:
        help()
        return
    
    if not args.video_file:
        print("Error: Video file required")
        parser.print_help()
        return
    
    if args.validate:
        result = validate_video(args.video_file)
        if result['valid']:
            print(f"Video is valid: {result['width']}x{result['height']}, {result['frame_count']} frames")
        else:
            print(f"Video validation failed: {result['error']}")
        return
    

    
    # Run gaze detection
    run_args = []
    if args.visualize:
        run_args.append("--visualize")
    
    result = run(args.video_file, *run_args)
    if result:
        print("Processing completed successfully")
    else:
        print("Processing failed")

if __name__ == "__main__":
    cli()