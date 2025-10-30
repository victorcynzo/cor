#!/usr/bin/env python3
"""
Usage examples for Cor Gaze Detection Library
Demonstrates working functionality in Python fallback mode
"""

import cor
import os

def basic_example():
    """Basic gaze detection workflow"""
    print("=== BASIC GAZE DETECTION EXAMPLE ===")
    
    # Display help
    print("\n1. Getting Help:")
    cor.help()
    
    # Show version
    print("\n2. Version Information:")
    version = cor.version()
    print(f"Cor Version: {version}")
    print(f"Mode: {version.get('mode', 'Unknown')}")
    print(f"OpenCV Available: {version.get('opencv_available', False)}")

def working_gaze_detection_example():
    """Complete gaze detection workflow with working functions"""
    print("\n=== WORKING GAZE DETECTION WORKFLOW ===")
    
    # Use test_video.mp4 if available, otherwise use a sample path
    video_path = "test_video.mp4" if os.path.exists("test_video.mp4") else "sample_video.mp4"
    
    if os.path.exists(video_path):
        print(f"\n3. Processing {video_path}:")
        
        try:
            # Step 1: Validate video
            print("Step 1: Validating video...")
            is_valid = cor.validate_video(video_path)
            print(f"Video validation result: {is_valid}")
            
            if not is_valid:
                print("❌ Video validation failed")
                return
            
            # Step 2: Calibrate eyes (automatic)
            print("Step 2: Calibrating eye detection...")
            eye_result = cor.calibrate_eyes(video_path)
            print(f"Eye calibration result: {eye_result}")
            
            # Step 3: Calibrate gaze (automatic)
            print("Step 3: Calibrating gaze direction...")
            gaze_result = cor.calibrate_gaze(video_path)
            print(f"Gaze calibration result: {gaze_result}")
            
            # Step 4: Run basic gaze detection
            print("Step 4: Running gaze detection...")
            success = cor.run(video_path)
            
            if success:
                print("✅ Basic analysis complete!")
                print("Generated files:")
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                print(f"  - {base_name}_heatmap-pure.jpg")
                print(f"  - {base_name}_heatmap-overlay.jpg")
                
                # Step 5: Create visualization video
                print("Step 5: Creating visualization video...")
                success_viz = cor.run(video_path, "--visualize")
                
                if success_viz:
                    print("✅ Visualization complete!")
                    print(f"  - {base_name}_heatmap.mp4")
            else:
                print("❌ Analysis failed")
                
        except Exception as e:
            print(f"❌ Error during processing: {e}")
    else:
        print(f"⚠️  Video file not found: {video_path}")
        print("To test with your own video, place a video file named 'test_video.mp4' in this directory")

def python_enhanced_functions_example():
    """Demonstrate enhanced Python functions (v1.0.1)"""
    print("\n=== ENHANCED PYTHON FUNCTIONS (v1.0.1) ===")
    
    print("\n4. New Python functions available in v1.0.1:")
    
    # Configuration management
    print("   Testing configuration management...")
    current_value = cor.get_config("heatmap_color_scheme")
    print(f"   Current heatmap_color_scheme: {current_value}")
    
    # Set a test value
    set_result = cor.set_config("test_param", "test_value")
    if set_result:
        retrieved_value = cor.get_config("test_param")
        print(f"   Set and retrieved test_param: {retrieved_value}")
    else:
        print("   Config set operation failed")
    
    # Frame extraction
    if os.path.exists("test_video.mp4"):
        print("   Testing frame extraction...")
        frames = cor.extract_frames("test_video.mp4", 3, "sample_frames")
        print(f"   Extracted frames: {len(frames)} files")
        
        # Clean up extracted frames
        import shutil
        if os.path.exists("sample_frames"):
            shutil.rmtree("sample_frames")
            print("   Cleaned up extracted frames")
    
    # Benchmarking
    if os.path.exists("test_video.mp4"):
        print("   Testing performance benchmarking...")
        benchmark_result = cor.benchmark("test_video.mp4", 20)
        if isinstance(benchmark_result, dict) and "processing_fps" in benchmark_result:
            print(f"   Benchmark: {benchmark_result['processing_fps']:.2f} fps, {benchmark_result['detection_rate']:.2%} detection rate")

def c_extension_only_functions():
    """Demonstrate functions that still require C extension"""
    print("\n=== C EXTENSION ONLY FUNCTIONS ===")
    
    print("\n5. Functions that still require C extension:")
    
    # These functions will show error messages in Python fallback mode
    print("   Testing attention analysis...")
    result = cor.analyze_attention("test_video.mp4")
    print(f"   analyze_attention result: {result}")
    
    print("   Testing advanced heatmap generation...")
    result = cor.generate_advanced_heatmap("test_video.mp4", "density")
    print(f"   generate_advanced_heatmap result: {result}")
    
    print("   Testing real-time processing...")
    result = cor.init_realtime(0)
    print(f"   init_realtime result: {result}")

def main():
    """Run all examples"""
    print("Cor Gaze Detection Library - Usage Examples")
    print("=" * 60)
    print("NOTE: This library is running in Python fallback mode.")
    print("Some advanced features require the C extension to be compiled.")
    print("=" * 60)
    
    # Run examples
    basic_example()
    working_gaze_detection_example()
    python_enhanced_functions_example()
    c_extension_only_functions()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("\nPython fallback mode functions (v1.0.1):")
    print("✅ cor.help() - Display help information")
    print("✅ cor.version() - Show version information")
    print("✅ cor.validate_video() - Basic video validation")
    print("✅ cor.calibrate_eyes() - Automatic eye calibration")
    print("✅ cor.calibrate_gaze() - Automatic gaze calibration")
    print("✅ cor.run() - Complete gaze detection with heatmaps")
    print("✅ cor.get_config() / cor.set_config() - Configuration management")
    print("✅ cor.extract_frames() - Frame extraction with progress bars")
    print("✅ cor.benchmark() - Performance benchmarking")
    print("\nC extension only functions:")
    print("⚠️  Real-time processing, advanced attention analysis, advanced heatmaps")

if __name__ == "__main__":
    main()