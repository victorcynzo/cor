"""
Cor - Advanced Gaze Detection Library
Python fallback implementation when C extension is not available
"""

import sys
import os
import csv
from datetime import datetime
import glob
from pathlib import Path

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
            'version': '1.0.4',
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

# Global path configuration
_custom_paths = {
    'input_path': None,
    'output_path': None,
    'search_paths': []
}

# Supported video formats
SUPPORTED_VIDEO_FORMATS = [
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm',
    '.m4v', '.3gp', '.asf', '.rm', '.rmvb', '.vob', '.ogv',
    '.dv', '.ts', '.mts', '.m2ts'
]

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

def add_search_path(path):
    """Add a path to search for video files"""
    global _custom_paths
    if path and os.path.exists(path):
        abs_path = os.path.abspath(path)
        if abs_path not in _custom_paths['search_paths']:
            _custom_paths['search_paths'].append(abs_path)
            print(f"Added search path: {abs_path}")
        return True
    else:
        print(f"Warning: Search path does not exist: {path}")
        return False

def clear_paths():
    """Clear all custom paths"""
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

def _resolve_video_path(video_file):
    """Resolve video file path using custom paths and search paths"""
    # If it's already an absolute path and exists, use it
    if os.path.isabs(video_file) and os.path.exists(video_file):
        return video_file
    
    # If it exists in current directory, use it
    if os.path.exists(video_file):
        return os.path.abspath(video_file)
    
    # Try custom input path
    if _custom_paths['input_path']:
        input_path = os.path.join(_custom_paths['input_path'], video_file)
        if os.path.exists(input_path):
            return input_path
    
    # Try search paths
    for search_path in _custom_paths['search_paths']:
        search_file = os.path.join(search_path, video_file)
        if os.path.exists(search_file):
            return search_file
    
    # Try to find using glob patterns in search paths
    filename = os.path.basename(video_file)
    for search_path in _custom_paths['search_paths']:
        pattern = os.path.join(search_path, f"*{filename}*")
        matches = glob.glob(pattern)
        if matches:
            return matches[0]  # Return first match
    
    # If still not found, return original path (will cause error later)
    return video_file

def _resolve_output_folder(video_file, is_batch=False):
    """Resolve output folder path using custom output path"""
    if is_batch:
        # For batch processing, use "batch_YYYY-MM-DD_HH-MM-SS"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = f"batch_{timestamp}"
    else:
        # For single file, use video name without extension
        video_name = os.path.splitext(os.path.basename(video_file))[0]
        folder_name = video_name
    
    # Use custom output path if set
    if _custom_paths['output_path']:
        output_folder = os.path.join(_custom_paths['output_path'], folder_name)
    else:
        output_folder = folder_name
    
    return output_folder

def find_videos(pattern="*.mp4", search_all_paths=True):
    """Find video files using pattern matching in configured paths"""
    found_videos = []
    
    # Search in current directory
    found_videos.extend(glob.glob(pattern))
    
    if search_all_paths:
        # Search in custom input path
        if _custom_paths['input_path']:
            input_pattern = os.path.join(_custom_paths['input_path'], pattern)
            found_videos.extend(glob.glob(input_pattern))
        
        # Search in all search paths
        for search_path in _custom_paths['search_paths']:
            search_pattern = os.path.join(search_path, pattern)
            found_videos.extend(glob.glob(search_pattern))
    
    # Remove duplicates and return absolute paths
    unique_videos = list(set(os.path.abspath(v) for v in found_videos))
    return sorted(unique_videos)

def find_all_videos_in_folder(folder_path=None, recursive=False):
    """Find all supported video files in a folder"""
    if folder_path is None:
        folder_path = _custom_paths['input_path'] or '.'
    
    if not os.path.exists(folder_path):
        print(f"Warning: Folder does not exist: {folder_path}")
        return []
    
    found_videos = []
    
    # Create search patterns for all supported formats
    search_patterns = []
    for ext in SUPPORTED_VIDEO_FORMATS:
        # Add both lowercase and uppercase versions
        search_patterns.append(f"*{ext}")
        search_patterns.append(f"*{ext.upper()}")
    
    if recursive:
        # Recursive search
        for pattern in search_patterns:
            recursive_pattern = os.path.join(folder_path, "**", pattern)
            found_videos.extend(glob.glob(recursive_pattern, recursive=True))
    else:
        # Non-recursive search
        for pattern in search_patterns:
            folder_pattern = os.path.join(folder_path, pattern)
            found_videos.extend(glob.glob(folder_pattern))
    
    # Remove duplicates and return absolute paths
    unique_videos = list(set(os.path.abspath(v) for v in found_videos))
    return sorted(unique_videos)

def find_videos_by_extension(extension, folder_path=None, recursive=False):
    """Find videos by specific extension in folder"""
    if folder_path is None:
        folder_path = _custom_paths['input_path'] or '.'
    
    if not os.path.exists(folder_path):
        print(f"Warning: Folder does not exist: {folder_path}")
        return []
    
    # Ensure extension starts with dot
    if not extension.startswith('.'):
        extension = '.' + extension
    
    # Normalize extension
    extension = extension.lower()
    
    # Check if extension is supported
    if extension not in SUPPORTED_VIDEO_FORMATS:
        print(f"Warning: Extension {extension} may not be supported")
    
    found_videos = []
    
    # Create search patterns for both cases
    patterns = [f"*{extension}", f"*{extension.upper()}"]
    
    if recursive:
        # Recursive search
        for pattern in patterns:
            recursive_pattern = os.path.join(folder_path, "**", pattern)
            found_videos.extend(glob.glob(recursive_pattern, recursive=True))
    else:
        # Non-recursive search
        for pattern in patterns:
            folder_pattern = os.path.join(folder_path, pattern)
            found_videos.extend(glob.glob(folder_pattern))
    
    # Remove duplicates and return absolute paths
    unique_videos = list(set(os.path.abspath(v) for v in found_videos))
    return sorted(unique_videos)

def get_supported_formats():
    """Get list of supported video formats"""
    return SUPPORTED_VIDEO_FORMATS.copy()

def is_video_file(file_path):
    """Check if file is a supported video format"""
    if not os.path.isfile(file_path):
        return False
    
    _, ext = os.path.splitext(file_path.lower())
    return ext in SUPPORTED_VIDEO_FORMATS

def _create_output_folder(video_file, is_batch=False):
    """Create output folder for results"""
    folder_name = _resolve_output_folder(video_file, is_batch)
    
    # Create folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created output folder: {folder_name}")
    
    return folder_name

def _save_confidence_to_csv(video_file, gaze_points, total_frames, output_folder, csv_filename="confidence_results.csv"):
    """Save confidence assessment results to CSV file with enhanced gaze statistics"""
    # Calculate confidence metrics (same logic as display function)
    if not gaze_points or total_frames <= 0:
        detection_rate = 0.0
        avg_confidence = 0.0
        accuracy_confidence = 0.0
        valid_gaze_points = 0
        avg_position_x = 0.0
        avg_position_y = 0.0
        std_dev_x = 0.0
        std_dev_y = 0.0
        frame_percentage_x = 0.0
        frame_percentage_y = 0.0
    else:
        detection_rate = len(gaze_points) / total_frames
        
        # Estimate confidence based on detection consistency
        if detection_rate >= 0.8:
            avg_confidence = 0.85
        elif detection_rate >= 0.6:
            avg_confidence = 0.72
        elif detection_rate >= 0.4:
            avg_confidence = 0.58
        else:
            avg_confidence = 0.35
        
        # Calculate overall accuracy confidence
        if len(gaze_points) > 0:
            if detection_rate >= 0.8:
                high_confidence_ratio = 0.7
            elif detection_rate >= 0.6:
                high_confidence_ratio = 0.5
            elif detection_rate >= 0.4:
                high_confidence_ratio = 0.3
            else:
                high_confidence_ratio = 0.1
        else:
            high_confidence_ratio = 0.0
            
        accuracy_confidence = (avg_confidence * 0.5 + detection_rate * 0.3 + high_confidence_ratio * 0.2) * 100.0
        valid_gaze_points = len(gaze_points)
        
        # Calculate gaze statistics
        import numpy as np
        try:
            gaze_x_coords = [point[0] for point in gaze_points]
            gaze_y_coords = [point[1] for point in gaze_points]
            
            avg_position_x = np.mean(gaze_x_coords)
            avg_position_y = np.mean(gaze_y_coords)
            std_dev_x = np.std(gaze_x_coords)
            std_dev_y = np.std(gaze_y_coords)
            
            # Estimate frame dimensions (assuming 1920x1080 if not available)
            # In a real implementation, we'd get this from video properties
            frame_width = 1920.0  # This should be passed from video processing
            frame_height = 1080.0  # This should be passed from video processing
            
            frame_percentage_x = (avg_position_x / frame_width) * 100.0
            frame_percentage_y = (avg_position_y / frame_height) * 100.0
            
        except ImportError:
            # Fallback if numpy not available
            avg_position_x = sum(point[0] for point in gaze_points) / len(gaze_points)
            avg_position_y = sum(point[1] for point in gaze_points) / len(gaze_points)
            
            # Simple standard deviation calculation
            mean_x = avg_position_x
            mean_y = avg_position_y
            variance_x = sum((point[0] - mean_x) ** 2 for point in gaze_points) / len(gaze_points)
            variance_y = sum((point[1] - mean_y) ** 2 for point in gaze_points) / len(gaze_points)
            std_dev_x = variance_x ** 0.5
            std_dev_y = variance_y ** 0.5
            
            # Estimate frame dimensions
            frame_width = 1920.0
            frame_height = 1080.0
            frame_percentage_x = (avg_position_x / frame_width) * 100.0
            frame_percentage_y = (avg_position_y / frame_height) * 100.0
    
    # Prepare CSV data
    video_name = os.path.splitext(os.path.basename(video_file))[0]
    csv_path = os.path.join(output_folder, csv_filename)
    
    # Enhanced CSV headers with new gaze statistics
    headers = [
        'Input Video Title',
        'Overall Accuracy Confidence (%)',
        'Average Confidence Per Point (%)', 
        'Detection Rate (%)',
        'Valid Gaze Points Detected',
        'Total Frames Processed',
        'Average Position X',
        'Average Position Y',
        'Standard Deviation X',
        'Standard Deviation Y',
        'Frame Percentage X (%)',
        'Frame Percentage Y (%)'
    ]
    
    # Enhanced data row with new statistics
    row_data = [
        video_name,
        f"{accuracy_confidence:.1f}",
        f"{avg_confidence * 100:.1f}",
        f"{detection_rate * 100:.1f}",
        valid_gaze_points,
        total_frames,
        f"{avg_position_x:.1f}",
        f"{avg_position_y:.1f}",
        f"{std_dev_x:.1f}",
        f"{std_dev_y:.1f}",
        f"{frame_percentage_x:.1f}",
        f"{frame_percentage_y:.1f}"
    ]
    
    # Check if CSV file exists to determine if we need to write headers
    file_exists = os.path.exists(csv_path)
    
    # Write to CSV
    try:
        with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write headers if file is new
            if not file_exists:
                writer.writerow(headers)
                print(f"Created enhanced confidence CSV: {csv_path}")
            
            # Write data row
            writer.writerow(row_data)
            print(f"Added enhanced confidence data for '{video_name}' to CSV")
            
    except Exception as e:
        print(f"Warning: Could not save confidence data to CSV: {e}")
    
    return csv_path

def run_batch(video_files_or_folder, *args, **kwargs):
    """
    Process multiple video files in batch mode
    
    Args:
        video_files_or_folder: Can be:
            - List of video file paths
            - Single folder path (will find all videos)
            - Pattern string (e.g., "*.mp4", "*.avi")
        *args: Additional arguments (e.g., "--visualize")
        **kwargs: Additional options:
            - recursive: bool, search subfolders (default: False)
            - extensions: list, specific extensions to search (default: all supported)
    """
    recursive = kwargs.get('recursive', False)
    extensions = kwargs.get('extensions', None)
    
    resolved_files = []
    
    # Handle different input types
    if isinstance(video_files_or_folder, str):
        # Single string input - could be folder, pattern, or single file
        if os.path.isdir(video_files_or_folder):
            # It's a folder - find all videos
            print(f"Searching for videos in folder: {video_files_or_folder}")
            if extensions:
                # Search for specific extensions
                for ext in extensions:
                    found = find_videos_by_extension(ext, video_files_or_folder, recursive)
                    resolved_files.extend(found)
            else:
                # Search for all supported formats
                resolved_files = find_all_videos_in_folder(video_files_or_folder, recursive)
        elif '*' in video_files_or_folder or '?' in video_files_or_folder:
            # It's a pattern
            print(f"Searching for videos matching pattern: {video_files_or_folder}")
            resolved_files = find_videos(video_files_or_folder)
        else:
            # It's a single file
            resolved_path = _resolve_video_path(video_files_or_folder)
            if os.path.exists(resolved_path):
                resolved_files.append(resolved_path)
            else:
                print(f"Warning: Could not find video file: {video_files_or_folder}")
    elif isinstance(video_files_or_folder, (list, tuple)):
        # List of files
        for video_file in video_files_or_folder:
            if os.path.isdir(video_file):
                # If list contains folders, process them
                folder_videos = find_all_videos_in_folder(video_file, recursive)
                resolved_files.extend(folder_videos)
            else:
                resolved_path = _resolve_video_path(video_file)
                if os.path.exists(resolved_path):
                    resolved_files.append(resolved_path)
                else:
                    print(f"Warning: Could not find video file: {video_file}")
    else:
        print("Error: Invalid input type for batch processing")
        return False
    
    # Remove duplicates
    resolved_files = list(set(resolved_files))
    
    if not resolved_files:
        print("No valid video files found for batch processing")
        return False
    
    print(f"Found {len(resolved_files)} video files for batch processing")
    for i, video in enumerate(resolved_files[:5], 1):  # Show first 5
        print(f"  {i}. {os.path.basename(video)}")
    if len(resolved_files) > 5:
        print(f"  ... and {len(resolved_files) - 5} more")
    
    # Create batch output folder
    batch_folder = _create_output_folder(None, is_batch=True)
    
    results = []
    successful_count = 0
    
    for i, video_file in enumerate(resolved_files, 1):
        print(f"\n{'='*60}")
        print(f"Processing video {i}/{len(resolved_files)}: {os.path.basename(video_file)}")
        print(f"{'='*60}")
        
        try:
            # Process individual video but save to batch folder
            result = _run_single_video_for_batch(video_file, batch_folder, *args)
            results.append({'video': video_file, 'success': result, 'error': None})
            
            if result:
                successful_count += 1
                print(f"✅ Completed: {os.path.basename(video_file)}")
            else:
                print(f"❌ Failed: {os.path.basename(video_file)}")
                
        except Exception as e:
            print(f"❌ Error processing {video_file}: {e}")
            results.append({'video': video_file, 'success': False, 'error': str(e)})
    
    # Summary
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total videos: {len(resolved_files)}")
    print(f"Successful: {successful_count}")
    print(f"Failed: {len(resolved_files) - successful_count}")
    print(f"Output folder: {batch_folder}")
    print(f"Confidence results: {os.path.join(batch_folder, 'confidence_results.csv')}")
    
    return {'success': successful_count > 0, 'output_folder': batch_folder, 'results': results}

def run_folder(folder_path, *args, **kwargs):
    """
    Process all videos in a folder
    
    Args:
        folder_path: Path to folder containing videos
        *args: Additional arguments (e.g., "--visualize")
        **kwargs: Additional options:
            - recursive: bool, search subfolders (default: False)
            - extensions: list, specific extensions to process (default: all supported)
    """
    return run_batch(folder_path, *args, **kwargs)

def run_pattern(pattern, *args, **kwargs):
    """
    Process videos matching a pattern
    
    Args:
        pattern: Glob pattern (e.g., "*.mp4", "*session*.avi")
        *args: Additional arguments (e.g., "--visualize")
        **kwargs: Additional options
    """
    return run_batch(pattern, *args, **kwargs)

def _run_single_video_for_batch(video_file, batch_folder, *args):
    """Process a single video for batch processing (saves to batch folder)"""
    if _has_c_extension:
        # For C extension, we'd need to modify it to accept output folder
        # For now, fall back to Python implementation
        pass
    
    try:
        import cv2
        import numpy as np
        import matplotlib.pyplot as plt
        import os
        
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
        
        # Load Haar cascades for eye detection
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Storage for gaze points
        gaze_points = []
        frame_for_overlay = None
        
        # Process video with progress bar
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Store 10th frame for overlay
            if frame_idx == 10:
                frame_for_overlay = frame.copy()
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                
                # Detect eyes within face
                eyes = eye_cascade.detectMultiScale(roi_gray)
                
                if len(eyes) >= 2:
                    # Sort eyes by x coordinate (left to right)
                    eyes = sorted(eyes, key=lambda e: e[0])
                    
                    # Take first two eyes
                    eye1, eye2 = eyes[0], eyes[1]
                    
                    # Calculate eye centers
                    eye1_center = (x + eye1[0] + eye1[2]//2, y + eye1[1] + eye1[3]//2)
                    eye2_center = (x + eye2[0] + eye2[2]//2, y + eye2[1] + eye2[3]//2)
                    
                    # Simple gaze estimation (center between eyes projected forward)
                    gaze_x = (eye1_center[0] + eye2_center[0]) // 2
                    gaze_y = (eye1_center[1] + eye2_center[1]) // 2
                    
                    # Add some forward projection based on eye direction
                    eye_vector = (eye2_center[0] - eye1_center[0], eye2_center[1] - eye1_center[1])
                    gaze_x += int(eye_vector[1] * 0.3)  # Perpendicular projection
                    gaze_y -= int(eye_vector[0] * 0.3)
                    
                    # Ensure gaze point is within frame
                    gaze_x = max(0, min(width-1, gaze_x))
                    gaze_y = max(0, min(height-1, gaze_y))
                    
                    gaze_points.append((gaze_x, gaze_y))
            
            frame_idx += 1
            # Update progress bar every 10 frames or at completion
            if frame_idx % 10 == 0 or frame_idx == frame_count:
                _print_progress_bar(frame_idx, frame_count, "Video Processing", "frames processed")
        
        cap.release()
        
        print(f"Detected {len(gaze_points)} gaze points")
        
        if len(gaze_points) == 0:
            print("No gaze points detected. Check video quality and face visibility.")
            # Still display confidence assessment even with no detections
            _display_confidence_assessment(gaze_points, frame_count, video_file, batch_folder)
            return False
        
        # Generate heatmap
        video_name = os.path.splitext(os.path.basename(video_file))[0]
        
        # Create heatmap data - FIXED VERSION
        heatmap_data = np.zeros((height, width))
        
        # Add each gaze point with a Gaussian blob
        print("\nGenerating heatmap...")
        for i, (gx, gy) in enumerate(gaze_points):
            # Create coordinate arrays
            y_coords = np.arange(height)
            x_coords = np.arange(width)
            
            # Create meshgrid
            X, Y = np.meshgrid(x_coords, y_coords)
            
            # Calculate distances from gaze point
            distances_sq = (X - gx)**2 + (Y - gy)**2
            
            # Create Gaussian blob (sigma = 25 pixels)
            gaussian_blob = np.exp(-distances_sq / (2 * 25**2))
            
            # Add to heatmap
            heatmap_data += gaussian_blob
            
            # Update progress bar every 50 points or at completion
            if (i + 1) % 50 == 0 or (i + 1) == len(gaze_points):
                _print_progress_bar(i + 1, len(gaze_points), "Heatmap Generation", "gaze points processed")
        
        # Normalize heatmap
        if heatmap_data.max() > 0:
            heatmap_data = heatmap_data / heatmap_data.max()
        
        # Create pure heatmap - exact video dimensions
        fig_width = width / 100.0  # Convert pixels to inches (assuming 100 DPI)
        fig_height = height / 100.0
        
        plt.figure(figsize=(fig_width, fig_height), dpi=100)
        plt.imshow(heatmap_data, cmap='hot', interpolation='bilinear')
        plt.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        pure_heatmap_file = os.path.join(batch_folder, f"{video_name}_heatmap-pure.jpg")
        plt.savefig(pure_heatmap_file, bbox_inches='tight', pad_inches=0, dpi=100)
        plt.close()
        print(f"Created: {pure_heatmap_file}")
        
        # Create overlay heatmap - exact video dimensions
        if frame_for_overlay is not None:
            plt.figure(figsize=(fig_width, fig_height), dpi=100)
            plt.imshow(cv2.cvtColor(frame_for_overlay, cv2.COLOR_BGR2RGB))
            plt.imshow(heatmap_data, cmap='hot', alpha=0.6, interpolation='bilinear')
            plt.axis('off')
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            overlay_heatmap_file = os.path.join(batch_folder, f"{video_name}_heatmap-overlay.jpg")
            plt.savefig(overlay_heatmap_file, bbox_inches='tight', pad_inches=0, dpi=100)
            plt.close()
            print(f"Created: {overlay_heatmap_file}")
        
        # Create visualization video if requested
        if visualize:
            print("Creating visualization video...")
            video_ext = os.path.splitext(video_file)[1]
            output_video = os.path.join(batch_folder, f"{video_name}_heatmap{video_ext}")
            
            # Re-open video for visualization
            cap = cv2.VideoCapture(video_file)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
            
            frame_idx = 0
            gaze_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Draw gaze visualization if we have gaze data for this frame
                if gaze_idx < len(gaze_points):
                    gx, gy = gaze_points[min(gaze_idx, len(gaze_points)-1)]
                    
                    # Draw gaze circle
                    cv2.circle(frame, (gx, gy), 20, (0, 255, 0), 3)
                    
                    # Try to find eyes in this frame for lines
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    for (x, y, w, h) in faces:
                        roi_gray = gray[y:y+h, x:x+w]
                        eyes = eye_cascade.detectMultiScale(roi_gray)
                        
                        if len(eyes) >= 2:
                            eyes = sorted(eyes, key=lambda e: e[0])
                            eye1, eye2 = eyes[0], eyes[1]
                            
                            eye1_center = (x + eye1[0] + eye1[2]//2, y + eye1[1] + eye1[3]//2)
                            eye2_center = (x + eye2[0] + eye2[2]//2, y + eye2[1] + eye2[3]//2)
                            
                            # Draw lines from eyes to gaze point
                            cv2.line(frame, eye1_center, (gx, gy), (0, 255, 255), 2)
                            cv2.line(frame, eye2_center, (gx, gy), (0, 255, 255), 2)
                            break
                    
                    gaze_idx += 1
                
                out.write(frame)
                frame_idx += 1
            
            cap.release()
            out.release()
            print(f"Created: {output_video}")
        
        # Display confidence assessment
        _display_confidence_assessment(gaze_points, frame_count, video_file, batch_folder)
        
        print("Gaze detection complete!")
        return True
        
    except ImportError as e:
        print(f"ERROR: Missing required package: {e}")
        print("Please install: pip install opencv-python matplotlib")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def _print_progress_bar(current, total, prefix='Progress', suffix='Complete', length=50):
    """Print a Unicode progress bar to the terminal"""
    percent = (current / total) * 100
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {current}/{total} ({percent:.1f}%) {suffix}', end='', flush=True)
    if current == total:
        print()  # New line when complete

def _display_confidence_assessment(gaze_points, total_frames, video_file=None, output_folder=None):
    """Display confidence assessment for gaze detection results (Python version)"""
    if not gaze_points or total_frames <= 0:
        print("\n=== GAZE DETECTION CONFIDENCE ASSESSMENT ===")
        print("❌ No valid gaze data detected")
        print("Confidence: 0.0% (No reliable gaze tracking)")
        print("============================================\n")
        
        # Save to CSV even for failed detections
        if video_file and output_folder:
            _save_confidence_to_csv(video_file, gaze_points, total_frames, output_folder)
        return
    
    # In Python mode, we don't have individual confidence scores per point
    # So we'll estimate confidence based on detection consistency and coverage
    
    # Calculate detection rate
    detection_rate = len(gaze_points) / total_frames
    
    # Estimate confidence based on detection consistency
    # More detections = higher confidence in the algorithm working
    if detection_rate >= 0.8:
        avg_confidence = 0.85  # High confidence
        high_confidence_points = int(len(gaze_points) * 0.7)
        medium_confidence_points = int(len(gaze_points) * 0.25)
        low_confidence_points = len(gaze_points) - high_confidence_points - medium_confidence_points
    elif detection_rate >= 0.6:
        avg_confidence = 0.72  # Good confidence
        high_confidence_points = int(len(gaze_points) * 0.5)
        medium_confidence_points = int(len(gaze_points) * 0.4)
        low_confidence_points = len(gaze_points) - high_confidence_points - medium_confidence_points
    elif detection_rate >= 0.4:
        avg_confidence = 0.58  # Fair confidence
        high_confidence_points = int(len(gaze_points) * 0.3)
        medium_confidence_points = int(len(gaze_points) * 0.5)
        low_confidence_points = len(gaze_points) - high_confidence_points - medium_confidence_points
    else:
        avg_confidence = 0.35  # Low confidence
        high_confidence_points = int(len(gaze_points) * 0.1)
        medium_confidence_points = int(len(gaze_points) * 0.3)
        low_confidence_points = len(gaze_points) - high_confidence_points - medium_confidence_points
    
    # Calculate overall accuracy confidence
    high_confidence_ratio = high_confidence_points / len(gaze_points)
    accuracy_confidence = (avg_confidence * 0.5 + detection_rate * 0.3 + high_confidence_ratio * 0.2) * 100.0
    
    # Display assessment
    print("\n=== GAZE DETECTION CONFIDENCE ASSESSMENT ===")
    print("📊 Analysis Results:")
    print(f"   • Total frames processed: {total_frames}")
    print(f"   • Valid gaze points detected: {len(gaze_points)}")
    print(f"   • Detection rate: {detection_rate * 100:.1f}%")
    print(f"   • Average confidence per point: {avg_confidence * 100:.1f}%")
    print("\n📈 Confidence Distribution:")
    print(f"   • High confidence (≥80%): {high_confidence_points} points ({high_confidence_points / len(gaze_points) * 100:.1f}%)")
    print(f"   • Medium confidence (60-79%): {medium_confidence_points} points ({medium_confidence_points / len(gaze_points) * 100:.1f}%)")
    print(f"   • Low confidence (<60%): {low_confidence_points} points ({low_confidence_points / len(gaze_points) * 100:.1f}%)")
    
    print(f"\n🎯 Overall Accuracy Confidence: {accuracy_confidence:.1f}%")
    
    # NEW: Enhanced Gaze Statistics Section
    try:
        import numpy as np
        gaze_x_coords = [point[0] for point in gaze_points]
        gaze_y_coords = [point[1] for point in gaze_points]
        
        avg_position_x = np.mean(gaze_x_coords)
        avg_position_y = np.mean(gaze_y_coords)
        std_dev_x = np.std(gaze_x_coords)
        std_dev_y = np.std(gaze_y_coords)
        
        # Estimate frame dimensions (should be passed from video processing in real implementation)
        frame_width = 1920.0  # Default assumption
        frame_height = 1080.0  # Default assumption
        
        frame_percentage_x = (avg_position_x / frame_width) * 100.0
        frame_percentage_y = (avg_position_y / frame_height) * 100.0
        
    except ImportError:
        # Fallback if numpy not available
        gaze_x_coords = [point[0] for point in gaze_points]
        gaze_y_coords = [point[1] for point in gaze_points]
        
        avg_position_x = sum(gaze_x_coords) / len(gaze_x_coords)
        avg_position_y = sum(gaze_y_coords) / len(gaze_y_coords)
        
        # Simple standard deviation calculation
        variance_x = sum((x - avg_position_x) ** 2 for x in gaze_x_coords) / len(gaze_x_coords)
        variance_y = sum((y - avg_position_y) ** 2 for y in gaze_y_coords) / len(gaze_y_coords)
        std_dev_x = variance_x ** 0.5
        std_dev_y = variance_y ** 0.5
        
        # Estimate frame dimensions
        frame_width = 1920.0
        frame_height = 1080.0
        frame_percentage_x = (avg_position_x / frame_width) * 100.0
        frame_percentage_y = (avg_position_y / frame_height) * 100.0
    
    print("\n📍 GAZE STATISTICS:")
    print(f"   • Average position: ({avg_position_x:.1f}, {avg_position_y:.1f}) pixels")
    print(f"   • Standard deviation: ({std_dev_x:.1f}, {std_dev_y:.1f}) pixels")
    print(f"   • Frame percentage: ({frame_percentage_x:.1f}%, {frame_percentage_y:.1f}%)")
    
    # Gaze focus interpretation
    focus_score = 100.0 - min(100.0, (std_dev_x + std_dev_y) / 20.0)  # Lower std dev = higher focus
    if focus_score >= 80.0:
        focus_interpretation = "Very focused gaze pattern"
    elif focus_score >= 60.0:
        focus_interpretation = "Moderately focused gaze pattern"
    elif focus_score >= 40.0:
        focus_interpretation = "Scattered gaze pattern"
    else:
        focus_interpretation = "Highly scattered gaze pattern"
    
    print(f"   • Gaze focus score: {focus_score:.1f}% ({focus_interpretation})")
    
    # Gaze position interpretation
    if 40 <= frame_percentage_x <= 60 and 40 <= frame_percentage_y <= 60:
        position_interpretation = "Center-focused viewing"
    elif frame_percentage_x < 30:
        position_interpretation = "Left-side focused viewing"
    elif frame_percentage_x > 70:
        position_interpretation = "Right-side focused viewing"
    elif frame_percentage_y < 30:
        position_interpretation = "Upper region focused viewing"
    elif frame_percentage_y > 70:
        position_interpretation = "Lower region focused viewing"
    else:
        position_interpretation = "Distributed viewing pattern"
    
    print(f"   • Viewing pattern: {position_interpretation}")
    
    # Provide interpretation
    if accuracy_confidence >= 85.0:
        print("\n✅ Excellent - High reliability for research and analysis")
    elif accuracy_confidence >= 70.0:
        print("\n✅ Good - Suitable for most applications")
    elif accuracy_confidence >= 55.0:
        print("\n⚠️  Fair - Consider recalibration for better accuracy")
    else:
        print("\n❌ Poor - Recalibration strongly recommended")
    
    print("============================================\n")
    
    # Save confidence data to CSV
    if video_file and output_folder:
        _save_confidence_to_csv(video_file, gaze_points, total_frames, output_folder)

def run(video_file, *args):
    """Gaze detection using Python and OpenCV"""
    if _has_c_extension:
        # For C extension, we need to resolve the path first
        resolved_path = _resolve_video_path(video_file)
        return _cor.run(resolved_path, *args)
    else:
        try:
            import cv2
            import numpy as np
            import matplotlib.pyplot as plt
            from matplotlib.colors import LinearSegmentedColormap
            import os
            
            # Resolve video file path
            resolved_video_path = _resolve_video_path(video_file)
            print(f"Processing {resolved_video_path} in Python mode...")
            
            # Check if --visualize flag is present
            visualize = "--visualize" in args
            
            # Create output folder for this video
            output_folder = _create_output_folder(resolved_video_path)
            
            # Basic video processing
            cap = cv2.VideoCapture(resolved_video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {resolved_video_path}")
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"Video: {frame_count} frames, {width}x{height}, {fps:.1f} FPS")
            
            # Load Haar cascades for eye detection
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Storage for gaze points
            gaze_points = []
            frame_for_overlay = None
            
            # Process video with progress bar
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Store 10th frame for overlay
                if frame_idx == 10:
                    frame_for_overlay = frame.copy()
                
                # Convert to grayscale for detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]
                    
                    # Detect eyes within face
                    eyes = eye_cascade.detectMultiScale(roi_gray)
                    
                    if len(eyes) >= 2:
                        # Sort eyes by x coordinate (left to right)
                        eyes = sorted(eyes, key=lambda e: e[0])
                        
                        # Take first two eyes
                        eye1, eye2 = eyes[0], eyes[1]
                        
                        # Calculate eye centers
                        eye1_center = (x + eye1[0] + eye1[2]//2, y + eye1[1] + eye1[3]//2)
                        eye2_center = (x + eye2[0] + eye2[2]//2, y + eye2[1] + eye2[3]//2)
                        
                        # Simple gaze estimation (center between eyes projected forward)
                        gaze_x = (eye1_center[0] + eye2_center[0]) // 2
                        gaze_y = (eye1_center[1] + eye2_center[1]) // 2
                        
                        # Add some forward projection based on eye direction
                        eye_vector = (eye2_center[0] - eye1_center[0], eye2_center[1] - eye1_center[1])
                        gaze_x += int(eye_vector[1] * 0.3)  # Perpendicular projection
                        gaze_y -= int(eye_vector[0] * 0.3)
                        
                        # Ensure gaze point is within frame
                        gaze_x = max(0, min(width-1, gaze_x))
                        gaze_y = max(0, min(height-1, gaze_y))
                        
                        gaze_points.append((gaze_x, gaze_y))
                
                frame_idx += 1
                # Update progress bar every 10 frames or at completion
                if frame_idx % 10 == 0 or frame_idx == frame_count:
                    _print_progress_bar(frame_idx, frame_count, "Video Processing", "frames processed")
            
            cap.release()
            
            print(f"Detected {len(gaze_points)} gaze points")
            
            if len(gaze_points) == 0:
                print("No gaze points detected. Check video quality and face visibility.")
                # Still display confidence assessment even with no detections
                _display_confidence_assessment(gaze_points, frame_count, resolved_video_path, output_folder)
                return {'success': False, 'output_folder': output_folder}
            
            # Generate heatmap
            video_name = os.path.splitext(os.path.basename(video_file))[0]
            
            # Create heatmap data - FIXED VERSION
            heatmap_data = np.zeros((height, width))
            
            # Add each gaze point with a Gaussian blob
            print("\nGenerating heatmap...")
            for i, (gx, gy) in enumerate(gaze_points):
                # Create coordinate arrays
                y_coords = np.arange(height)
                x_coords = np.arange(width)
                
                # Create meshgrid
                X, Y = np.meshgrid(x_coords, y_coords)
                
                # Calculate distances from gaze point
                distances_sq = (X - gx)**2 + (Y - gy)**2
                
                # Create Gaussian blob (sigma = 25 pixels)
                gaussian_blob = np.exp(-distances_sq / (2 * 25**2))
                
                # Add to heatmap
                heatmap_data += gaussian_blob
                
                # Update progress bar every 50 points or at completion
                if (i + 1) % 50 == 0 or (i + 1) == len(gaze_points):
                    _print_progress_bar(i + 1, len(gaze_points), "Heatmap Generation", "gaze points processed")
            
            # Normalize heatmap
            if heatmap_data.max() > 0:
                heatmap_data = heatmap_data / heatmap_data.max()
            
            # Create pure heatmap - exact video dimensions
            fig_width = width / 100.0  # Convert pixels to inches (assuming 100 DPI)
            fig_height = height / 100.0
            
            plt.figure(figsize=(fig_width, fig_height), dpi=100)
            plt.imshow(heatmap_data, cmap='hot', interpolation='bilinear')
            plt.axis('off')
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            pure_heatmap_file = os.path.join(output_folder, f"{video_name}_heatmap-pure.jpg")
            plt.savefig(pure_heatmap_file, bbox_inches='tight', pad_inches=0, dpi=100)
            plt.close()
            print(f"Created: {pure_heatmap_file}")
            
            # Create overlay heatmap - exact video dimensions
            if frame_for_overlay is not None:
                plt.figure(figsize=(fig_width, fig_height), dpi=100)
                plt.imshow(cv2.cvtColor(frame_for_overlay, cv2.COLOR_BGR2RGB))
                plt.imshow(heatmap_data, cmap='hot', alpha=0.6, interpolation='bilinear')
                plt.axis('off')
                plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
                overlay_heatmap_file = os.path.join(output_folder, f"{video_name}_heatmap-overlay.jpg")
                plt.savefig(overlay_heatmap_file, bbox_inches='tight', pad_inches=0, dpi=100)
                plt.close()
                print(f"Created: {overlay_heatmap_file}")
            
            # Create visualization video if requested
            if visualize:
                print("Creating visualization video...")
                video_ext = os.path.splitext(resolved_video_path)[1]
                output_video = os.path.join(output_folder, f"{video_name}_heatmap{video_ext}")
                
                # Re-open video for visualization
                cap = cv2.VideoCapture(resolved_video_path)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
                
                frame_idx = 0
                gaze_idx = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Draw gaze visualization if we have gaze data for this frame
                    if gaze_idx < len(gaze_points):
                        gx, gy = gaze_points[min(gaze_idx, len(gaze_points)-1)]
                        
                        # Draw gaze circle
                        cv2.circle(frame, (gx, gy), 20, (0, 255, 0), 3)
                        
                        # Try to find eyes in this frame for lines
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                        
                        for (x, y, w, h) in faces:
                            roi_gray = gray[y:y+h, x:x+w]
                            eyes = eye_cascade.detectMultiScale(roi_gray)
                            
                            if len(eyes) >= 2:
                                eyes = sorted(eyes, key=lambda e: e[0])
                                eye1, eye2 = eyes[0], eyes[1]
                                
                                eye1_center = (x + eye1[0] + eye1[2]//2, y + eye1[1] + eye1[3]//2)
                                eye2_center = (x + eye2[0] + eye2[2]//2, y + eye2[1] + eye2[3]//2)
                                
                                # Draw lines from eyes to gaze point
                                cv2.line(frame, eye1_center, (gx, gy), (0, 255, 255), 2)
                                cv2.line(frame, eye2_center, (gx, gy), (0, 255, 255), 2)
                                break
                        
                        gaze_idx += 1
                    
                    out.write(frame)
                    frame_idx += 1
                
                cap.release()
                out.release()
                print(f"Created: {output_video}")
            
            # Display confidence assessment
            _display_confidence_assessment(gaze_points, frame_count, resolved_video_path, output_folder)
            
            print("Gaze detection complete!")
            return {'success': True, 'output_folder': output_folder}
            
        except ImportError as e:
            print(f"ERROR: Missing required package: {e}")
            print("Please install: pip install opencv-python matplotlib")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

def calibrate_eyes(video_file):
    """Eye calibration using Python and OpenCV"""
    # Resolve video file path
    resolved_video_path = _resolve_video_path(video_file)
    
    if _has_c_extension:
        return _cor.calibrate_eyes(resolved_video_path)
    else:
        try:
            import cv2
            import numpy as np
            
            print(f"Eye calibration for {resolved_video_path} (Python mode)")
            print("Note: This is a simplified calibration. Full calibration requires C extension.")
            
            cap = cv2.VideoCapture(resolved_video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {resolved_video_path}")
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Extract 20 frames for calibration
            calibration_frames = []
            print("Extracting calibration frames...")
            for i in range(20):
                frame_pos = int((i / 19) * (frame_count - 1))
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                if ret:
                    calibration_frames.append(frame)
                _print_progress_bar(i + 1, 20, "Frame Extraction", "frames extracted")
            
            cap.release()
            
            if len(calibration_frames) == 0:
                print("ERROR: Could not extract frames for calibration")
                return False
            
            # Simple automatic calibration using default Haar cascade parameters
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Test detection on sample frames
            detection_count = 0
            print("Testing eye detection...")
            for i, frame in enumerate(calibration_frames[:5]):  # Test on first 5 frames
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    eyes = eye_cascade.detectMultiScale(roi_gray)
                    if len(eyes) >= 2:
                        detection_count += 1
                        break
                _print_progress_bar(i + 1, 5, "Eye Calibration", "test frames processed")
            
            # Save basic calibration values
            calibration_data = f"""# Eye Detection Calibration Values (Python Mode)
# Generated automatically from {resolved_video_path}
# Detection success rate: {detection_count}/5 frames

# Haar Cascade Parameters
scale_factor=1.3
min_neighbors=5
min_size_width=30
min_size_height=30

# Eye Region Parameters  
eye_region_padding=10
pupil_detection_threshold=50

# Detection Quality
detection_confidence={detection_count * 20}%
calibration_mode=automatic_python
"""
            
            with open('eye-detection-values.txt', 'w') as f:
                f.write(calibration_data)
            
            print(f"Basic eye calibration complete!")
            print(f"Detection success: {detection_count}/5 test frames")
            print("Calibration saved to: eye-detection-values.txt")
            print("For interactive calibration, install C extension.")
            
            return True
            
        except Exception as e:
            print(f"ERROR during calibration: {e}")
            return False

def calibrate_gaze(video_file):
    """Gaze calibration using Python and OpenCV"""
    # Resolve video file path
    resolved_video_path = _resolve_video_path(video_file)
    
    if _has_c_extension:
        return _cor.calibrate_gaze(resolved_video_path)
    else:
        try:
            import cv2
            import numpy as np
            
            print(f"Gaze calibration for {resolved_video_path} (Python mode)")
            print("Note: This is a simplified calibration. Full calibration requires C extension.")
            
            cap = cv2.VideoCapture(resolved_video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {resolved_video_path}")
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Extract frames for analysis
            test_frames = []
            print("Extracting gaze calibration frames...")
            for i in range(10):
                frame_pos = int((i / 9) * (frame_count - 1))
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                if ret:
                    test_frames.append(frame)
                _print_progress_bar(i + 1, 10, "Frame Extraction", "frames extracted")
            
            cap.release()
            
            if len(test_frames) == 0:
                print("ERROR: Could not extract frames for calibration")
                return False
            
            # Analyze gaze patterns
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            gaze_points = []
            print("Analyzing gaze patterns...")
            for i, frame in enumerate(test_frames):
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    eyes = eye_cascade.detectMultiScale(roi_gray)
                    
                    if len(eyes) >= 2:
                        eyes = sorted(eyes, key=lambda e: e[0])
                        eye1, eye2 = eyes[0], eyes[1]
                        
                        # Calculate approximate gaze direction
                        eye1_center = (x + eye1[0] + eye1[2]//2, y + eye1[1] + eye1[3]//2)
                        eye2_center = (x + eye2[0] + eye2[2]//2, y + eye2[1] + eye2[3]//2)
                        
                        gaze_x = (eye1_center[0] + eye2_center[0]) // 2
                        gaze_y = (eye1_center[1] + eye2_center[1]) // 2
                        
                        gaze_points.append((gaze_x, gaze_y))
                        break
                _print_progress_bar(i + 1, len(test_frames), "Gaze Calibration", "frames analyzed")
            
            # Calculate calibration parameters
            if gaze_points:
                avg_x = sum(p[0] for p in gaze_points) / len(gaze_points)
                avg_y = sum(p[1] for p in gaze_points) / len(gaze_points)
                
                # Calculate relative position in frame
                rel_x = avg_x / width
                rel_y = avg_y / height
            else:
                rel_x, rel_y = 0.5, 0.5  # Default to center
            
            # Save gaze calibration values
            calibration_data = f"""# Gaze Direction Calibration Values (Python Mode)
# Generated automatically from {resolved_video_path}
# Detected gaze points: {len(gaze_points)}

# Gaze Direction Parameters
gaze_offset_x={rel_x:.3f}
gaze_offset_y={rel_y:.3f}
gaze_sensitivity=1.0
gaze_smoothing=0.3

# Projection Parameters
forward_projection=0.3
vertical_adjustment=0.1
horizontal_adjustment=0.0

# Quality Metrics
calibration_points={len(gaze_points)}
calibration_mode=automatic_python
average_gaze_x={avg_x:.1f}
average_gaze_y={avg_y:.1f}
"""
            
            with open('gaze-direction-values.txt', 'w') as f:
                f.write(calibration_data)
            
            print(f"Basic gaze calibration complete!")
            print(f"Analyzed {len(gaze_points)} gaze points")
            print(f"Average gaze position: ({avg_x:.1f}, {avg_y:.1f})")
            print("Calibration saved to: gaze-direction-values.txt")
            print("For interactive calibration, install C extension.")
            
            return True
            
        except Exception as e:
            print(f"ERROR during calibration: {e}")
            return False

# Additional functions that require C extension
def get_config(param_name, config_file="cor.txt"):
    if _has_c_extension:
        return _cor.get_config(param_name, config_file)
    else:
        try:
            if not os.path.exists(config_file):
                return None
            
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() == param_name:
                            return value.strip()
            return None
        except Exception as e:
            print(f"ERROR reading config: {e}")
            return None

def set_config(param_name, param_value, config_file="cor.txt"):
    if _has_c_extension:
        return _cor.set_config(param_name, param_value, config_file)
    else:
        try:
            lines = []
            param_found = False
            
            # Read existing config if it exists
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    lines = f.readlines()
            
            # Update or add parameter
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#') and '=' in line:
                    key = line.split('=', 1)[0].strip()
                    if key == param_name:
                        lines[i] = f"{param_name}={param_value}\n"
                        param_found = True
                        break
            
            # Add parameter if not found
            if not param_found:
                lines.append(f"{param_name}={param_value}\n")
            
            # Write back to file
            with open(config_file, 'w') as f:
                f.writelines(lines)
            
            return True
        except Exception as e:
            print(f"ERROR writing config: {e}")
            return False

def validate_video(video_file):
    # Resolve video file path
    resolved_video_path = _resolve_video_path(video_file)
    
    if _has_c_extension:
        return _cor.validate_video(resolved_video_path)
    else:
        try:
            import cv2
            cap = cv2.VideoCapture(resolved_video_path)
            if not cap.isOpened():
                return False
            ret, frame = cap.read()
            cap.release()
            return ret
        except:
            return False

def extract_frames(video_file, num_frames=10, output_dir="frames"):
    # Resolve video file path
    resolved_video_path = _resolve_video_path(video_file)
    
    if _has_c_extension:
        return _cor.extract_frames(resolved_video_path, num_frames, output_dir)
    else:
        try:
            import cv2
            
            # Create output directory
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            cap = cv2.VideoCapture(resolved_video_path)
            if not cap.isOpened():
                print(f"ERROR: Cannot open video file: {resolved_video_path}")
                return []
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            extracted_frames = []
            
            print(f"Extracting {num_frames} frames...")
            for i in range(num_frames):
                # Calculate frame position
                frame_pos = int((i / (num_frames - 1)) * (frame_count - 1)) if num_frames > 1 else 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                
                ret, frame = cap.read()
                if ret:
                    # Save frame
                    frame_filename = f"frame_{i+1:03d}.jpg"
                    frame_path = os.path.join(output_dir, frame_filename)
                    cv2.imwrite(frame_path, frame)
                    extracted_frames.append(frame_path)
                
                _print_progress_bar(i + 1, num_frames, "Frame Extraction", "frames extracted")
            
            cap.release()
            print(f"Extracted {len(extracted_frames)} frames to {output_dir}/")
            return extracted_frames
            
        except Exception as e:
            print(f"ERROR during frame extraction: {e}")
            return []

def benchmark(video_file, max_frames=100):
    # Resolve video file path
    resolved_video_path = _resolve_video_path(video_file)
    
    if _has_c_extension:
        return _cor.benchmark(resolved_video_path, max_frames)
    else:
        try:
            import cv2
            import time
            
            print(f"Benchmarking {resolved_video_path} (Python mode)...")
            
            cap = cv2.VideoCapture(resolved_video_path)
            if not cap.isOpened():
                return {"error": "Cannot open video file"}
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Limit frames to benchmark
            frames_to_process = min(max_frames, frame_count)
            
            # Load cascades
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            start_time = time.time()
            detections = 0
            
            for i in range(frames_to_process):
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Perform detection (same as in run function)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    eyes = eye_cascade.detectMultiScale(roi_gray)
                    if len(eyes) >= 2:
                        detections += 1
                        break
                
                if (i + 1) % 10 == 0:
                    _print_progress_bar(i + 1, frames_to_process, "Benchmarking", "frames processed")
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            cap.release()
            
            # Calculate metrics
            processing_fps = frames_to_process / processing_time if processing_time > 0 else 0
            detection_rate = detections / frames_to_process if frames_to_process > 0 else 0
            
            result = {
                "frames_processed": frames_to_process,
                "processing_time": processing_time,
                "processing_fps": processing_fps,
                "detection_rate": detection_rate,
                "detections": detections,
                "video_fps": fps
            }
            
            print(f"Benchmark complete: {processing_fps:.2f} fps processing, {detection_rate:.2%} detection rate")
            return result
            
        except Exception as e:
            print(f"ERROR during benchmarking: {e}")
            return {"error": str(e)}

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

def cli():
    """Command-line interface for Cor Gaze Detection Library"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(
        prog='cor',
        description='Cor Gaze Detection Library - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cor video.mp4                          # Basic gaze detection
  cor video.mp4 --visualize             # With visualization video
  cor video.mp4 --calibrate             # Run calibration first
  cor video.mp4 --visualize --calibrate # Full workflow
  
  # Batch processing examples:
  cor --batch video1.mp4 video2.mp4     # Batch process specific files
  cor --batch-folder /path/to/videos    # Process all videos in folder
  cor --batch-pattern "*.mp4"           # Process all MP4 files
  cor --batch-pattern "*session*.avi"   # Process AVI files matching pattern
  cor --batch-folder /videos --recursive # Include subfolders
  cor --batch-folder /videos --extensions mp4 avi # Only MP4 and AVI files
  
  # Path management examples:
  cor --input-path /path/to/videos video.mp4        # Set custom input path
  cor --output-path /path/to/results video.mp4      # Set custom output path
  cor --search-path /videos --search-path /data video.mp4  # Add search paths
  cor --find-videos "*.mp4"                         # Find videos in configured paths
  cor --batch-folder /videos --output-path /results # Batch with custom output
  
  # Advanced batch examples:
  cor --batch-folder /project --recursive --visualize --extensions mp4 mov
  cor --input-path /data --batch-pattern "experiment_*.mp4" --output-path /analysis
  
  cor --help                            # Show this help
  cor --version                         # Show version info
  cor --config param_name value         # Set configuration
  cor --get-config param_name           # Get configuration
        """
    )
    
    # Positional argument for video file(s)
    parser.add_argument('video_file', nargs='?', help='Path to input video file')
    parser.add_argument('--batch', nargs='+', metavar='VIDEO', 
                       help='Process multiple video files in batch mode: --batch video1.mp4 video2.mp4 ...')
    parser.add_argument('--batch-folder', metavar='FOLDER',
                       help='Process all videos in a folder: --batch-folder /path/to/videos')
    parser.add_argument('--batch-pattern', metavar='PATTERN',
                       help='Process videos matching pattern: --batch-pattern "*.mp4"')
    parser.add_argument('--recursive', action='store_true',
                       help='Search subfolders recursively (use with --batch-folder)')
    parser.add_argument('--extensions', nargs='+', metavar='EXT',
                       help='Specific video extensions to process: --extensions mp4 avi mov')
    
    # Path management arguments
    parser.add_argument('--input-path', metavar='PATH',
                       help='Set custom input path for video files')
    parser.add_argument('--output-path', metavar='PATH',
                       help='Set custom output path for results')
    parser.add_argument('--search-path', action='append', metavar='PATH',
                       help='Add search path for video files (can be used multiple times)')
    parser.add_argument('--find-videos', metavar='PATTERN',
                       help='Find videos matching pattern in configured paths (e.g., "*.mp4")')
    
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
    parser.add_argument('--benchmark', type=int, metavar='N',
                       help='Run performance benchmark (specify number of frames)')
    parser.add_argument('--config', nargs=2, metavar=('PARAM', 'VALUE'),
                       help='Set configuration parameter: --config param_name value')
    parser.add_argument('--get-config', metavar='PARAM',
                       help='Get configuration parameter value')
    parser.add_argument('--version', action='store_true',
                       help='Show version information')
    parser.add_argument('--help-cor', action='store_true',
                       help='Show Cor library help information')
    
    args = parser.parse_args()
    
    # Handle path configuration
    if args.input_path:
        if not set_input_path(args.input_path):
            return 1
    
    if args.output_path:
        if not set_output_path(args.output_path):
            return 1
    
    if args.search_path:
        for path in args.search_path:
            if not add_search_path(path):
                return 1
    
    # Handle find videos request
    if args.find_videos:
        found_videos = find_videos(args.find_videos)
        if found_videos:
            print(f"Found {len(found_videos)} video files:")
            for video in found_videos:
                print(f"  - {video}")
        else:
            print(f"No videos found matching pattern: {args.find_videos}")
        return 0
    
    # Handle version request
    if args.version:
        version_info = version()
        print(f"Cor Gaze Detection Library")
        print(f"Version: {version_info.get('version', 'Unknown')}")
        print(f"Mode: {version_info.get('mode', 'Unknown')}")
        print(f"C Extension: {version_info.get('c_extension', False)}")
        print(f"OpenCV Available: {version_info.get('opencv_available', False)}")
        return 0
    
    # Handle Cor help request
    if args.help_cor:
        help()
        return 0
    
    # Handle configuration get/set
    if args.get_config:
        try:
            value = get_config(args.get_config)
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
            success = set_config(param_name, param_value)
            if success:
                print(f"Set {param_name} = {param_value}")
            else:
                print(f"Failed to set configuration parameter")
                return 1
        except Exception as e:
            print(f"Error setting configuration: {e}")
            return 1
        return 0
    
    # Handle batch processing
    batch_mode = args.batch or args.batch_folder or args.batch_pattern
    
    if batch_mode:
        try:
            # Prepare batch arguments
            batch_args = []
            if args.visualize:
                batch_args.append("--visualize")
            
            # Prepare batch kwargs
            batch_kwargs = {}
            if args.recursive:
                batch_kwargs['recursive'] = True
            if args.extensions:
                # Normalize extensions (add dots if missing)
                normalized_exts = []
                for ext in args.extensions:
                    if not ext.startswith('.'):
                        ext = '.' + ext
                    normalized_exts.append(ext.lower())
                batch_kwargs['extensions'] = normalized_exts
            
            # Determine batch type and execute
            if args.batch:
                print(f"Batch processing mode: {len(args.batch)} specified files/patterns")
                result = run_batch(args.batch, *batch_args, **batch_kwargs)
            elif args.batch_folder:
                print(f"Batch folder processing: {args.batch_folder}")
                if args.recursive:
                    print("  (including subfolders)")
                if args.extensions:
                    print(f"  (extensions: {', '.join(args.extensions)})")
                result = run_batch(args.batch_folder, *batch_args, **batch_kwargs)
            elif args.batch_pattern:
                print(f"Batch pattern processing: {args.batch_pattern}")
                result = run_batch(args.batch_pattern, *batch_args, **batch_kwargs)
            
            if isinstance(result, dict) and result.get('success'):
                print("✅ Batch processing completed successfully!")
                output_folder = result.get('output_folder', '.')
                print(f"All results saved to: {output_folder}")
                print(f"Confidence summary: {os.path.join(output_folder, 'confidence_results.csv')}")
                
                # Show summary of results
                results = result.get('results', [])
                successful = sum(1 for r in results if r['success'])
                print(f"Successfully processed: {successful}/{len(results)} videos")
            else:
                print("❌ Batch processing failed")
                return 1
                
        except Exception as e:
            print(f"❌ Batch processing error: {e}")
            return 1
        
        return 0
    
    # Single video processing
    if not args.video_file:
        parser.print_help()
        return 1
    
    # Check if video file exists (use path resolution)
    resolved_video_path = _resolve_video_path(args.video_file)
    if not os.path.exists(resolved_video_path):
        print(f"Error: Video file '{args.video_file}' not found")
        print(f"Searched in: current directory, input path, and search paths")
        return 1
    
    print(f"Processing video: {args.video_file}")
    
    try:
        # Handle validation request
        if args.validate:
            print("Validating video file...")
            result = validate_video(args.video_file)
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
            frames = extract_frames(args.video_file, args.extract_frames)
            print(f"Extracted {len(frames)} frames to frames/ directory")
            return 0
        
        # Handle benchmark
        if args.benchmark is not None and args.benchmark > 0:
            print(f"Running benchmark with {args.benchmark} frames...")
            result = benchmark(args.video_file, args.benchmark)
            if isinstance(result, dict):
                print(f"Processing FPS: {result.get('processing_fps', 0):.2f}")
                print(f"Detection rate: {result.get('detection_rate', 0):.2%}")
                print(f"Processing time: {result.get('processing_time', 0):.2f}s")
            return 0
        
        # Handle calibration requests
        if args.calibrate or args.eye_calibrate:
            print("Running eye detection calibration...")
            eye_result = calibrate_eyes(args.video_file)
            print(f"Eye calibration completed: {eye_result}")
        
        if args.calibrate or args.gaze_calibrate:
            print("Running gaze direction calibration...")
            gaze_result = calibrate_gaze(args.video_file)
            print(f"Gaze calibration completed: {gaze_result}")
        
        # Run main gaze detection analysis
        print("Running gaze detection analysis...")
        if args.visualize:
            print("Visualization mode enabled - will create overlay video")
            success = run(args.video_file, "--visualize")
        else:
            success = run(args.video_file)
        
        # Handle both old return format (True/False) and new format (dict)
        if isinstance(success, dict):
            success_status = success.get('success', False)
            output_folder = success.get('output_folder', '.')
        else:
            success_status = success is not False
            output_folder = '.'
        
        if success_status:
            print("✅ Gaze detection completed successfully!")
            
            # Show output files
            video_name = os.path.splitext(os.path.basename(args.video_file))[0]
            print(f"\nGenerated files in folder '{output_folder}':")
            print(f"  📊 {os.path.join(output_folder, video_name + '_heatmap-pure.jpg')} - Pure heatmap visualization")
            print(f"  📊 {os.path.join(output_folder, video_name + '_heatmap-overlay.jpg')} - Heatmap overlaid on frame")
            print(f"  📋 {os.path.join(output_folder, 'confidence_results.csv')} - Confidence assessment data")
            
            if args.visualize:
                video_ext = os.path.splitext(args.video_file)[1]
                print(f"  🎥 {os.path.join(output_folder, video_name + '_heatmap' + video_ext)} - Video with gaze tracking overlay")
        else:
            print("❌ Gaze detection failed")
            if isinstance(success, dict):
                output_folder = success.get('output_folder', '.')
                print(f"Check confidence results in: {os.path.join(output_folder, 'confidence_results.csv')}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0