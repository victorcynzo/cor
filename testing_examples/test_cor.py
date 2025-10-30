#!/usr/bin/env python3
"""
Test script for Cor Gaze Detection Library
This script validates the installation and basic functionality
"""

import sys
import os
import tempfile
import numpy as np

def test_import():
    """Test if cor module can be imported"""
    try:
        import cor
        print("✓ Cor module imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import cor module: {e}")
        return False

def test_help():
    """Test help function"""
    try:
        import cor
        cor.help()
        print("✓ Help function works")
        return True
    except Exception as e:
        print(f"✗ Help function failed: {e}")
        return False

def test_version():
    """Test version function"""
    try:
        import cor
        version_info = cor.version()
        print(f"✓ Version function works: {version_info}")
        return True
    except Exception as e:
        print(f"✗ Version function failed: {e}")
        return False

def test_opencv():
    """Test OpenCV availability"""
    try:
        import cv2
        print(f"✓ OpenCV available: {cv2.__version__ if hasattr(cv2, '__version__') else 'Version unknown'}")
        return True
    except ImportError as e:
        print(f"✗ OpenCV not available: {e}")
        return False

def test_dependencies():
    """Test all required dependencies"""
    dependencies = {
        'numpy': 'numpy',
        'opencv': 'cv2', 
        'matplotlib': 'matplotlib.pyplot',
        'PIL': 'PIL'
    }
    
    all_good = True
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} available")
        except ImportError as e:
            print(f"✗ {name} not available: {e}")
            all_good = False
    
    return all_good

def test_basic_functionality():
    """Test basic cor functionality without requiring video files"""
    try:
        import cor
        
        # Test validate_video with non-existent file
        result = cor.validate_video("nonexistent.mp4")
        print(f"✓ validate_video works (returned {result} for non-existent file)")
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False
        
        # Test getting the config value
        value = cor.get_config("test_param")
        
        if value == "test_value":
            print("✓ Configuration functions work")
            return True
        else:
            print(f"✗ Configuration test failed: expected 'test_value', got '{value}'")
            return False
    except Exception as e:
        print(f"✗ Configuration functions failed: {e}")
        return False

def create_test_video():
    """Create a simple test video for testing"""
    try:
        import cv2
        
        # Create a temporary video file
        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, "test_video.mp4")
        
        # Video properties
        width, height = 640, 480
        fps = 30
        duration = 2  # seconds
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
        
        # Generate frames with a moving circle (simulating eye movement)
        for frame_num in range(fps * duration):
            # Create black frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add moving circle (simulating face/eye)
            center_x = int(width/2 + 50 * np.sin(frame_num * 0.1))
            center_y = int(height/2 + 30 * np.cos(frame_num * 0.1))
            
            # Draw face circle
            cv2.circle(frame, (center_x, center_y), 80, (100, 100, 100), -1)
            
            # Draw eyes
            eye_left = (center_x - 25, center_y - 10)
            eye_right = (center_x + 25, center_y - 10)
            cv2.circle(frame, eye_left, 15, (255, 255, 255), -1)
            cv2.circle(frame, eye_right, 15, (255, 255, 255), -1)
            
            # Draw pupils
            pupil_offset_x = int(5 * np.sin(frame_num * 0.2))
            pupil_offset_y = int(3 * np.cos(frame_num * 0.2))
            cv2.circle(frame, (eye_left[0] + pupil_offset_x, eye_left[1] + pupil_offset_y), 5, (0, 0, 0), -1)
            cv2.circle(frame, (eye_right[0] + pupil_offset_x, eye_right[1] + pupil_offset_y), 5, (0, 0, 0), -1)
            
            out.write(frame)
        
        out.release()
        print(f"✓ Test video created: {video_path}")
        return video_path
        
    except Exception as e:
        print(f"✗ Failed to create test video: {e}")
        return None

def test_video_validation():
    """Test video validation function"""
    try:
        import cor
        
        # Create test video
        video_path = create_test_video()
        if video_path is None:
            return False
        
        # Test validation
        result = cor.validate_video(video_path)
        
        if result.get('valid', False):
            print(f"✓ Video validation works: {result}")
            return True
        else:
            print(f"✗ Video validation failed: {result}")
            return False
            
    except Exception as e:
        print(f"✗ Video validation test failed: {e}")
        return False

def test_frame_extraction():
    """Test frame extraction function"""
    try:
        import cor
        
        # Create test video
        video_path = create_test_video()
        if video_path is None:
            return False
        
        # Test frame extraction
        frames = cor.extract_frames(video_path, 3)
        
        if len(frames) > 0:
            print(f"✓ Frame extraction works: extracted {len(frames)} frames")
            return True
        else:
            print("✗ Frame extraction failed: no frames extracted")
            return False
            
    except Exception as e:
        print(f"✗ Frame extraction test failed: {e}")
        return False

def test_benchmark():
    """Test benchmark function"""
    try:
        import cor
        
        # Create test video
        video_path = create_test_video()
        if video_path is None:
            return False
        
        # Test benchmark
        result = cor.benchmark(video_path, 10)
        
        if 'processing_fps' in result:
            print(f"✓ Benchmark works: {result}")
            return True
        else:
            print(f"✗ Benchmark failed: {result}")
            return False
            
    except Exception as e:
        print(f"✗ Benchmark test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Cor Gaze Detection Library - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_import),
        ("Help Function", test_help),
        ("Version Function", test_version),
        ("Configuration Functions", test_config),
        ("Video Validation", test_video_validation),
        ("Frame Extraction", test_frame_extraction),
        ("Benchmark Function", test_benchmark),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Cor library is working correctly.")
        return 0
    else:
        print("Some tests failed. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())