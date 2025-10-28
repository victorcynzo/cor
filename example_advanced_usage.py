#!/usr/bin/env python3
"""
Advanced usage examples for Cor Gaze Detection Library
Demonstrates advanced features and analysis capabilities
"""

import cor
import os
import tempfile
import json

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

def advanced_analysis_example():
    """Advanced attention analysis example"""
    print("\n=== ADVANCED ANALYSIS EXAMPLE ===")
    
    # Note: This would work with a real video file
    video_path = "sample_video.mp4"
    
    if os.path.exists(video_path):
        print(f"\n3. Analyzing attention patterns in {video_path}:")
        
        try:
            # Perform attention analysis
            analysis = cor.analyze_attention(video_path)
            
            print(f"Total duration: {analysis['total_duration_ms']:.2f} ms")
            print(f"Average fixation duration: {analysis['average_fixation_duration_ms']:.2f} ms")
            print(f"Number of saccades: {analysis['saccade_count']}")
            print(f"Number of fixations: {analysis['fixation_count']}")
            
            # Show first few fixations
            if analysis['fixations']:
                print("\nFirst 3 fixations:")
                for i, fixation in enumerate(analysis['fixations'][:3]):
                    print(f"  Fixation {i+1}: ({fixation['x']:.3f}, {fixation['y']:.3f}) "
                          f"duration={fixation['duration_ms']:.1f}ms intensity={fixation['intensity']:.3f}")
            
            # Export analysis to JSON
            export_path = cor.export_analysis(video_path)
            print(f"\nAnalysis exported to: {export_path}")
            
        except Exception as e:
            print(f"Analysis failed: {e}")
    else:
        print(f"Video file {video_path} not found. Skipping analysis example.")

def advanced_heatmap_example():
    """Advanced heatmap generation example"""
    print("\n=== ADVANCED HEATMAP EXAMPLE ===")
    
    video_path = "sample_video.mp4"
    
    if os.path.exists(video_path):
        print(f"\n4. Generating advanced heatmaps for {video_path}:")
        
        try:
            # Generate different types of heatmaps
            heatmap_modes = ["density", "fixation", "saccade"]
            
            for mode in heatmap_modes:
                output_path = f"heatmap_{mode}.jpg"
                cor.generate_advanced_heatmap(video_path, mode, output_path)
                print(f"Generated {mode} heatmap: {output_path}")
                
        except Exception as e:
            print(f"Advanced heatmap generation failed: {e}")
    else:
        print(f"Video file {video_path} not found. Skipping heatmap example.")

def realtime_example():
    """Real-time processing example"""
    print("\n=== REAL-TIME PROCESSING EXAMPLE ===")
    
    print("\n5. Real-time camera processing:")
    
    try:
        # Initialize real-time processing
        if cor.init_realtime(0):  # Use camera 0
            print("Real-time processing initialized")
            
            # Process a few frames
            print("Processing 10 frames from camera...")
            for i in range(10):
                gaze_data = cor.process_realtime_frame()
                print(f"Frame {i+1}: Gaze at ({gaze_data['x']:.3f}, {gaze_data['y']:.3f}) "
                      f"confidence={gaze_data['confidence']:.3f}")
            
            # Cleanup
            cor.cleanup_realtime()
            print("Real-time processing cleaned up")
        else:
            print("Failed to initialize real-time processing (camera not available)")
            
    except Exception as e:
        print(f"Real-time processing failed: {e}")
        try:
            cor.cleanup_realtime()
        except:
            pass

def configuration_example():
    """Configuration management example"""
    print("\n=== CONFIGURATION EXAMPLE ===")
    
    print("\n6. Configuration management:")
    
    try:
        # Get current heatmap color scheme
        current_scheme = cor.get_config("heatmap_color_scheme")
        print(f"Current heatmap color scheme: {current_scheme}")
        
        # Set new color scheme
        cor.set_config("heatmap_color_scheme", "sequential_red")
        print("Changed heatmap color scheme to sequential_red")
        
        # Verify change
        new_scheme = cor.get_config("heatmap_color_scheme")
        print(f"New heatmap color scheme: {new_scheme}")
        
        # Restore original
        cor.set_config("heatmap_color_scheme", current_scheme)
        print(f"Restored original color scheme: {current_scheme}")
        
    except Exception as e:
        print(f"Configuration example failed: {e}")

def video_validation_example():
    """Video validation and analysis example"""
    print("\n=== VIDEO VALIDATION EXAMPLE ===")
    
    print("\n7. Video validation and properties:")
    
    # Test with different file types
    test_files = ["sample.mp4", "test.avi", "nonexistent.mov"]
    
    for video_file in test_files:
        try:
            if os.path.exists(video_file):
                info = cor.validate_video(video_file)
                
                if info['valid']:
                    print(f"\n{video_file} - VALID:")
                    print(f"  Resolution: {info['width']}x{info['height']}")
                    print(f"  FPS: {info['fps']:.2f}")
                    print(f"  Duration: {info['duration']:.2f} seconds")
                    print(f"  Frames: {info['frame_count']}")
                    print(f"  Codec: {info['codec']}")
                    
                    # Extract sample frames
                    frames = cor.extract_frames(video_file, 3, "sample_frames")
                    print(f"  Extracted {len(frames)} sample frames")
                    
                    # Run benchmark
                    benchmark = cor.benchmark(video_file, 50)
                    print(f"  Processing speed: {benchmark['processing_fps']:.2f} fps")
                    print(f"  Detection rate: {benchmark['detection_rate']:.2%}")
                else:
                    print(f"\n{video_file} - INVALID: {info.get('error', 'Unknown error')}")
            else:
                print(f"\n{video_file} - FILE NOT FOUND")
                
        except Exception as e:
            print(f"\n{video_file} - ERROR: {e}")

def complete_workflow_example():
    """Complete workflow from calibration to analysis"""
    print("\n=== COMPLETE WORKFLOW EXAMPLE ===")
    
    video_path = "sample_video.mp4"
    
    if os.path.exists(video_path):
        print(f"\n8. Complete workflow with {video_path}:")
        
        try:
            # Step 1: Validate video
            info = cor.validate_video(video_path)
            if not info['valid']:
                print(f"Video validation failed: {info.get('error')}")
                return
            
            print(f"Video validated: {info['width']}x{info['height']}, {info['duration']:.1f}s")
            
            # Step 2: Optional calibration (commented out for automated example)
            # print("Running eye calibration...")
            # cor.calibrate_eyes(video_path)
            # print("Running gaze calibration...")
            # cor.calibrate_gaze(video_path)
            
            # Step 3: Basic gaze detection
            print("Running basic gaze detection...")
            cor.run(video_path)
            
            # Step 4: Advanced analysis
            print("Performing attention analysis...")
            analysis = cor.analyze_attention(video_path)
            print(f"Found {analysis['fixation_count']} fixations and {analysis['saccade_count']} saccades")
            
            # Step 5: Generate advanced visualizations
            print("Generating advanced heatmaps...")
            cor.generate_advanced_heatmap(video_path, "fixation", "fixation_heatmap.jpg")
            cor.generate_advanced_heatmap(video_path, "saccade", "saccade_paths.jpg")
            
            # Step 6: Export results
            export_path = cor.export_analysis(video_path)
            print(f"Results exported to: {export_path}")
            
            print("Complete workflow finished successfully!")
            
        except Exception as e:
            print(f"Workflow failed: {e}")
    else:
        print(f"Video file {video_path} not found. Skipping complete workflow.")

def main():
    """Run all examples"""
    print("Cor Gaze Detection Library - Advanced Usage Examples")
    print("=" * 60)
    
    # Run examples
    basic_example()
    configuration_example()
    video_validation_example()
    advanced_analysis_example()
    advanced_heatmap_example()
    realtime_example()
    complete_workflow_example()
    
    print("\n" + "=" * 60)
    print("Advanced examples completed!")
    print("\nNext steps:")
    print("1. Try with your own video files")
    print("2. Experiment with different configuration settings")
    print("3. Use real-time processing with a connected camera")
    print("4. Analyze the exported JSON results")

if __name__ == "__main__":
    main()