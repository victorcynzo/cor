#!/usr/bin/env python3
"""
Cor Gaze Detection Library - Custom CLI Wrapper Example
=======================================================

⚠️  IMPORTANT: This is an EXAMPLE file for educational purposes!
    The CLI functionality is already BUILT-IN to the Cor library.

🎯 RECOMMENDED USAGE (use the built-in CLI instead):
    cor video.mp4 --visualize              # Direct command (after pip install)
    python -m cor video.mp4 --visualize    # Python module execution

📚 PURPOSE OF THIS EXAMPLE:
    This file demonstrates how you could create your own custom CLI wrapper
    if you need additional functionality, different command structure, or
    want to integrate Cor into a larger application.

🔧 USAGE OF THIS EXAMPLE FILE:
    python example_cli_wrapper.py video.mp4 --visualize

📖 LEARNING OBJECTIVES:
    - How to use argparse with Cor functions
    - How to handle command-line arguments
    - How to create custom workflows
    - How to add error handling and user feedback
"""

import sys
import os
import argparse
import cor

def main():
    print("=" * 60)
    print("🔧 EXAMPLE CLI WRAPPER - For demonstration purposes only")
    print("📋 The CLI is already built into Cor! Use these instead:")
    print("   cor video.mp4 --visualize              # Built-in CLI")
    print("   python -m cor video.mp4 --visualize    # Python module")
    print("=" * 60)
    print()
    
    parser = argparse.ArgumentParser(
        description='Cor Gaze Detection Library - CLI Example (functionality already built-in)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
IMPORTANT: This is an EXAMPLE file! The CLI is already built into Cor.

Recommended usage (built-in CLI):
  cor video.mp4 --visualize              # Direct command
  python -m cor video.mp4 --visualize    # Python module

This example file usage:
  python cor_cli.py video.mp4                    # Basic gaze detection
  python cor_cli.py video.mp4 --visualize       # With visualization video
  python cor_cli.py video.mp4 --calibrate       # Run calibration first
  python cor_cli.py --help                      # Show this help
        """
    )
    
    # Positional argument for video file
    parser.add_argument('video_file', nargs='?', help='Path to input video file')
    
    # Optional arguments
    parser.add_argument('--visualize', action='store_true', 
                       help='Generate visualization video with gaze overlay')
    parser.add_argument('--calibrate', action='store_true',
                       help='Run eye and gaze calibration before analysis')
    parser.add_argument('--eye-calibrate', action='store_true',
                       help='Run only eye detection calibration')
    parser.add_argument('--gaze-calibrate', action='store_true',
                       help='Run only gaze direction calibration')
    parser.add_argument('--validate', action='store_true',
                       help='Validate video file and show properties')
    parser.add_argument('--extract-frames', type=int, metavar='N',
                       help='Extract N frames from video for preview')
    parser.add_argument('--benchmark', type=int, metavar='N', default=100,
                       help='Run performance benchmark (default: 100 frames)')
    parser.add_argument('--config', nargs=2, metavar=('PARAM', 'VALUE'),
                       help='Set configuration parameter: --config param_name value')
    parser.add_argument('--get-config', metavar='PARAM',
                       help='Get configuration parameter value')
    parser.add_argument('--version', action='store_true',
                       help='Show version information')
    parser.add_argument('--help-cor', action='store_true',
                       help='Show Cor library help information')
    
    args = parser.parse_args()
    
    # Handle version request
    if args.version:
        version_info = cor.version()
        print(f"Cor Gaze Detection Library")
        print(f"Version: {version_info.get('version', 'Unknown')}")
        print(f"Mode: {version_info.get('mode', 'Unknown')}")
        print(f"C Extension: {version_info.get('c_extension', False)}")
        print(f"OpenCV Available: {version_info.get('opencv_available', False)}")
        return 0
    
    # Handle Cor help request
    if args.help_cor:
        cor.help()
        return 0
    
    # Handle configuration get/set
    if args.get_config:
        try:
            value = cor.get_config(args.get_config)
            if value:
                print(f"{args.get_config} = {value}")
            else:
                print(f"Configuration parameter '{args.get_config}' not found")
        except Exception as e:
            print(f"Error getting configuration: {e}")
            return 1
        return 0
    
    if args.config:
        try:
            param_name, param_value = args.config
            success = cor.set_config(param_name, param_value)
            if success:
                print(f"Set {param_name} = {param_value}")
            else:
                print(f"Failed to set configuration parameter")
                return 1
        except Exception as e:
            print(f"Error setting configuration: {e}")
            return 1
        return 0
    
    # Video file is required for all other operations
    if not args.video_file:
        parser.print_help()
        return 1
    
    # Check if video file exists
    if not os.path.exists(args.video_file):
        print(f"Error: Video file '{args.video_file}' not found")
        return 1
    
    print(f"Processing video: {args.video_file}")
    
    try:
        # Handle validation request
        if args.validate:
            print("Validating video file...")
            result = cor.validate_video(args.video_file)
            if isinstance(result, dict):
                print(f"Valid: {result.get('valid', False)}")
                if result.get('valid'):
                    print(f"Dimensions: {result.get('width', 'Unknown')}x{result.get('height', 'Unknown')}")
                    print(f"Frame count: {result.get('frame_count', 'Unknown')}")
                    print(f"FPS: {result.get('fps', 'Unknown')}")
                    print(f"Duration: {result.get('duration', 'Unknown'):.2f} seconds")
                    print(f"Codec: {result.get('codec', 'Unknown')}")
            else:
                print(f"Validation result: {result}")
            return 0
        
        # Handle frame extraction
        if args.extract_frames:
            print(f"Extracting {args.extract_frames} frames...")
            frames = cor.extract_frames(args.video_file, args.extract_frames)
            print(f"Extracted {len(frames)} frames to frames/ directory")
            return 0
        
        # Handle benchmark
        if hasattr(args, 'benchmark') and args.benchmark:
            print(f"Running benchmark with {args.benchmark} frames...")
            result = cor.benchmark(args.video_file, args.benchmark)
            if isinstance(result, dict):
                print(f"Processing FPS: {result.get('processing_fps', 0):.2f}")
                print(f"Detection rate: {result.get('detection_rate', 0):.2%}")
                print(f"Processing time: {result.get('processing_time', 0):.2f}s")
            return 0
        
        # Handle calibration requests
        if args.calibrate or args.eye_calibrate:
            print("Running eye detection calibration...")
            eye_result = cor.calibrate_eyes(args.video_file)
            print(f"Eye calibration completed: {eye_result}")
        
        if args.calibrate or args.gaze_calibrate:
            print("Running gaze direction calibration...")
            gaze_result = cor.calibrate_gaze(args.video_file)
            print(f"Gaze calibration completed: {gaze_result}")
        
        # Run main gaze detection analysis
        print("Running gaze detection analysis...")
        if args.visualize:
            print("Visualization mode enabled - will create overlay video")
            success = cor.run(args.video_file, "--visualize")
        else:
            success = cor.run(args.video_file)
        
        if success is not False:  # Handle both None and True as success
            print("✅ Gaze detection completed successfully!")
            
            # Show output files
            video_name = os.path.splitext(os.path.basename(args.video_file))[0]
            print("\nGenerated files:")
            print(f"  📊 {video_name}_heatmap-pure.jpg - Pure heatmap visualization")
            print(f"  📊 {video_name}_heatmap-overlay.jpg - Heatmap overlaid on frame")
            
            if args.visualize:
                video_ext = os.path.splitext(args.video_file)[1]
                print(f"  🎥 {video_name}_heatmap{video_ext} - Video with gaze tracking overlay")
        else:
            print("❌ Gaze detection failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    print("🔔 REMINDER: This is just an example! Use the built-in CLI instead:")
    print("   cor video.mp4 --visualize")
    print("   python -m cor video.mp4 --visualize")
    print()
    sys.exit(main())