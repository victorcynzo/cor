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
            'version': '1.0.1',
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

def _print_progress_bar(current, total, prefix='Progress', suffix='Complete', length=50):
    """Print a Unicode progress bar to the terminal"""
    percent = (current / total) * 100
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {current}/{total} ({percent:.1f}%) {suffix}', end='', flush=True)
    if current == total:
        print()  # New line when complete

def run(video_file, *args):
    """Gaze detection using Python and OpenCV"""
    if _has_c_extension:
        return _cor.run(video_file, *args)
    else:
        try:
            import cv2
            import numpy as np
            import matplotlib.pyplot as plt
            from matplotlib.colors import LinearSegmentedColormap
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
            pure_heatmap_file = f"{video_name}_heatmap-pure.jpg"
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
                overlay_heatmap_file = f"{video_name}_heatmap-overlay.jpg"
                plt.savefig(overlay_heatmap_file, bbox_inches='tight', pad_inches=0, dpi=100)
                plt.close()
                print(f"Created: {overlay_heatmap_file}")
            
            # Create visualization video if requested
            if visualize:
                print("Creating visualization video...")
                video_ext = os.path.splitext(video_file)[1]
                output_video = f"{video_name}_heatmap{video_ext}"
                
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
            
            print("Gaze detection complete!")
            return True
            
        except ImportError as e:
            print(f"ERROR: Missing required package: {e}")
            print("Please install: pip install opencv-python matplotlib")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

def calibrate_eyes(video_file):
    """Eye calibration using Python and OpenCV"""
    if _has_c_extension:
        return _cor.calibrate_eyes(video_file)
    else:
        try:
            import cv2
            import numpy as np
            
            print(f"Eye calibration for {video_file} (Python mode)")
            print("Note: This is a simplified calibration. Full calibration requires C extension.")
            
            cap = cv2.VideoCapture(video_file)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_file}")
            
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
# Generated automatically from {video_file}
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
    if _has_c_extension:
        return _cor.calibrate_gaze(video_file)
    else:
        try:
            import cv2
            import numpy as np
            
            print(f"Gaze calibration for {video_file} (Python mode)")
            print("Note: This is a simplified calibration. Full calibration requires C extension.")
            
            cap = cv2.VideoCapture(video_file)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_file}")
            
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
# Generated automatically from {video_file}
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
        try:
            import cv2
            
            # Create output directory
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            cap = cv2.VideoCapture(video_file)
            if not cap.isOpened():
                print(f"ERROR: Cannot open video file: {video_file}")
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
    if _has_c_extension:
        return _cor.benchmark(video_file, max_frames)
    else:
        try:
            import cv2
            import time
            
            print(f"Benchmarking {video_file} (Python mode)...")
            
            cap = cv2.VideoCapture(video_file)
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