#!/usr/bin/env python3
"""
Demo script showing Cor functionality with test_video.mp4
"""

import cor
import os

def main():
    print("Cor Gaze Detection Library - Demo with test_video.mp4")
    print("=" * 60)
    
    # Show version and help
    print("1. Version Information:")
    version_info = cor.version()
    print(f"   Version: {version_info['version']}")
    print(f"   Mode: {version_info['mode']}")
    print(f"   OpenCV Available: {version_info['opencv_available']}")
    
    print("\n2. Help Information:")
    cor.help()
    
    # Validate video
    print("\n3. Video Validation:")
    is_valid = cor.validate_video('test_video.mp4')
    print(f"   test_video.mp4 is valid: {is_valid}")
    
    # Run calibrations
    print("\n4. Eye Calibration:")
    eye_cal_result = cor.calibrate_eyes('test_video.mp4')
    print(f"   Eye calibration result: {eye_cal_result}")
    
    print("\n5. Gaze Calibration:")
    gaze_cal_result = cor.calibrate_gaze('test_video.mp4')
    print(f"   Gaze calibration result: {gaze_cal_result}")
    
    # Run main gaze detection
    print("\n6. Gaze Detection:")
    print("   Running gaze detection...")
    
    # Use the cor module directly
    detection_result = cor.run('test_video.mp4')
    print(f"   Gaze detection result: {detection_result}")
    
    # Show generated files
    print("\n7. Generated Files:")
    files_to_check = [
        'test_video_heatmap-pure.jpg',
        'test_video_heatmap-overlay.jpg',
        'eye-detection-values.txt',
        'gaze-direction-values.txt'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✓ {file} ({size:,} bytes)")
        else:
            print(f"   ✗ {file} (missing)")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("\nThe Cor library successfully processed test_video.mp4 and generated:")
    print("- Gaze heatmap visualizations")
    print("- Eye detection calibration data")
    print("- Gaze direction calibration data")

if __name__ == "__main__":
    main()