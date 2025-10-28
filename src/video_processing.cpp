#include "cor.h"
#include <opencv2/opencv.hpp>
#include <opencv2/videoio.hpp>
#include <stdio.h>
#include <stdlib.h>
#include <vector>

using namespace cv;

// Video processing configuration
static struct {
    int frame_skip_factor;
    int max_processing_fps;
    float output_video_quality;
    bool enable_gpu_acceleration;
    int thread_count;
} video_config = {
    1, 30, 0.8f, false, 0
};

// Visualization configuration
static struct {
    int gaze_circle_radius;
    Scalar gaze_circle_color;
    int gaze_circle_thickness;
    int pupil_line_thickness;
    Scalar pupil_line_color;
    bool show_eye_boundaries;
    Scalar eye_boundary_color;
    bool show_pupil_centers;
    Scalar pupil_center_color;
} viz_config = {
    10, Scalar(0, 255, 0), 2, 2, Scalar(255, 255, 0), 
    false, Scalar(255, 0, 0), true, Scalar(0, 0, 255)
};

// Process single frame for gaze detection
static GazePoint process_frame(Mat frame, bool visualize, Mat& output_frame) {
    // Detect eyes in frame
    EyeDetectionResult eye_result = detect_eyes_in_frame(frame);
    
    // Calculate gaze direction
    GazePoint gaze_point = calculate_gaze_direction(eye_result);
    
    if (visualize && eye_result.valid) {
        output_frame = frame.clone();
        
        // Convert normalized gaze coordinates to pixel coordinates
        int gaze_x = (int)(gaze_point.x * frame.cols);
        int gaze_y = (int)(gaze_point.y * frame.rows);
        
        // Draw gaze indicator circle
        circle(output_frame, Point(gaze_x, gaze_y), 
               viz_config.gaze_circle_radius, 
               viz_config.gaze_circle_color, 
               viz_config.gaze_circle_thickness);
        
        // Draw lines from gaze point to pupils
        if (gaze_point.confidence > 0.5f) {
            line(output_frame, Point(gaze_x, gaze_y),
                 Point(eye_result.left_pupil.x, eye_result.left_pupil.y),
                 viz_config.pupil_line_color, viz_config.pupil_line_thickness);
            line(output_frame, Point(gaze_x, gaze_y),
                 Point(eye_result.right_pupil.x, eye_result.right_pupil.y),
                 viz_config.pupil_line_color, viz_config.pupil_line_thickness);
        }
        
        // Draw eye boundaries if enabled
        if (viz_config.show_eye_boundaries) {
            rectangle(output_frame,
                     Rect(eye_result.left_eye.x, eye_result.left_eye.y,
                          eye_result.left_eye.width, eye_result.left_eye.height),
                     viz_config.eye_boundary_color, 2);
            rectangle(output_frame,
                     Rect(eye_result.right_eye.x, eye_result.right_eye.y,
                          eye_result.right_eye.width, eye_result.right_eye.height),
                     viz_config.eye_boundary_color, 2);
        }
        
        // Draw pupil centers if enabled
        if (viz_config.show_pupil_centers) {
            circle(output_frame, Point(eye_result.left_pupil.x, eye_result.left_pupil.y),
                   3, viz_config.pupil_center_color, -1);
            circle(output_frame, Point(eye_result.right_pupil.x, eye_result.right_pupil.y),
                   3, viz_config.pupil_center_color, -1);
        }
        
        // Add confidence indicator
        if (gaze_point.confidence > 0.0f) {
            char conf_text[64];
            sprintf(conf_text, "Confidence: %.2f", gaze_point.confidence);
            putText(output_frame, conf_text, Point(10, 30), 
                   FONT_HERSHEY_SIMPLEX, 0.7, Scalar(255, 255, 255), 2);
        }
    }
    
    return gaze_point;
}

// Main video processing function
int process_video_file(const char* video_path, bool visualize) {
    // Open video file
    VideoCapture cap(video_path);
    if (!cap.isOpened()) {
        log_message("ERROR", "Could not open video file");
        return -1;
    }
    
    // Get video properties
    int frame_count = (int)cap.get(CAP_PROP_FRAME_COUNT);
    double fps = cap.get(CAP_PROP_FPS);
    int frame_width = (int)cap.get(CAP_PROP_FRAME_WIDTH);
    int frame_height = (int)cap.get(CAP_PROP_FRAME_HEIGHT);
    
    printf("Video properties:\n");
    printf("  Frames: %d\n", frame_count);
    printf("  FPS: %.2f\n", fps);
    printf("  Resolution: %dx%d\n", frame_width, frame_height);
    
    // Initialize video writer for visualization
    VideoWriter video_writer;
    if (visualize) {
        // Determine output codec and filename
        char* output_video_path = get_output_filename(video_path, "_heatmap", "");
        const char* ext = strrchr(video_path, '.');
        if (ext == NULL) ext = ".mp4";
        
        char full_output_path[512];
        sprintf(full_output_path, "%s%s", output_video_path, ext);
        
        // Initialize video writer
        int fourcc = VideoWriter::fourcc('H', '2', '6', '4');
        video_writer.open(full_output_path, fourcc, fps, Size(frame_width, frame_height));
        
        if (!video_writer.isOpened()) {
            log_message("ERROR", "Could not initialize video writer");
            free(output_video_path);
            return -1;
        }
        
        printf("Output video: %s\n", full_output_path);
        free(output_video_path);
    }
    
    // Process video frames
    std::vector<GazePoint> gaze_points;
    Mat frame, output_frame;
    int processed_frames = 0;
    int frame_number = 0;
    
    printf("Processing video frames...\n");
    
    while (cap.read(frame)) {
        frame_number++;
        
        // Skip frames based on frame_skip_factor
        if ((frame_number - 1) % video_config.frame_skip_factor != 0) {
            continue;
        }
        
        // Process frame
        GazePoint gaze_point = process_frame(frame, visualize, output_frame);
        
        // Store gaze point if valid
        if (gaze_point.confidence > 0.3f) {
            gaze_points.push_back(gaze_point);
        }
        
        // Write visualization frame
        if (visualize && video_writer.isOpened()) {
            if (!output_frame.empty()) {
                video_writer.write(output_frame);
            } else {
                video_writer.write(frame);
            }
        }
        
        processed_frames++;
        
        // Progress indicator
        if (processed_frames % 100 == 0) {
            printf("Processed %d frames (%.1f%%)\n", 
                   processed_frames, 
                   (float)frame_number / frame_count * 100.0f);
        }
    }
    
    cap.release();
    if (video_writer.isOpened()) {
        video_writer.release();
    }
    
    printf("Processed %d frames total\n", processed_frames);
    printf("Collected %zu valid gaze points\n", gaze_points.size());
    
    if (gaze_points.empty()) {
        log_message("WARNING", "No valid gaze points detected");
        return -1;
    }
    
    // Generate heatmaps
    HeatmapConfig heatmap_config = get_heatmap_config();
    
    // Generate pure heatmap
    Mat pure_heatmap = generate_heatmap(gaze_points, frame_width, frame_height, heatmap_config);
    
    // Save pure heatmap
    char* pure_heatmap_path = get_output_filename(video_path, "_heatmap-pure", ".jpg");
    if (save_heatmap_image(pure_heatmap, pure_heatmap_path) != 0) {
        free(pure_heatmap_path);
        return -1;
    }
    free(pure_heatmap_path);
    
    // Generate overlay heatmap (on 10th frame or middle frame)
    cap.open(video_path);
    Mat overlay_frame;
    int target_frame = std::min(10, frame_count / 2);
    cap.set(CAP_PROP_POS_FRAMES, target_frame);
    
    if (cap.read(overlay_frame)) {
        Mat overlay_heatmap = create_heatmap_overlay(overlay_frame, pure_heatmap, 
                                                    heatmap_config.alpha_transparency);
        
        // Save overlay heatmap
        char* overlay_heatmap_path = get_output_filename(video_path, "_heatmap-overlay", ".jpg");
        if (save_heatmap_image(overlay_heatmap, overlay_heatmap_path) != 0) {
            free(overlay_heatmap_path);
            cap.release();
            return -1;
        }
        free(overlay_heatmap_path);
    }
    
    cap.release();
    
    printf("Gaze detection analysis completed successfully!\n");
    return 0;
}

// Load video processing configuration from general config
static void load_video_config() {
    FILE* file = fopen(GENERAL_CONFIG, "r");
    if (file == NULL) return;
    
    char line[256];
    while (fgets(line, sizeof(line), file)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        
        char key[128], value[128];
        if (sscanf(line, "%127[^=]=%127s", key, value) == 2) {
            if (strcmp(key, "frame_skip_factor") == 0) {
                video_config.frame_skip_factor = atoi(value);
            } else if (strcmp(key, "max_processing_fps") == 0) {
                video_config.max_processing_fps = atoi(value);
            } else if (strcmp(key, "output_video_quality") == 0) {
                video_config.output_video_quality = atof(value);
            } else if (strcmp(key, "enable_gpu_acceleration") == 0) {
                video_config.enable_gpu_acceleration = (strcmp(value, "true") == 0);
            } else if (strcmp(key, "thread_count") == 0) {
                video_config.thread_count = atoi(value);
            }
            // Visualization config
            else if (strcmp(key, "gaze_circle_radius") == 0) {
                viz_config.gaze_circle_radius = atoi(value);
            } else if (strcmp(key, "gaze_circle_color") == 0) {
                int r, g, b;
                if (sscanf(value, "%d,%d,%d", &r, &g, &b) == 3) {
                    viz_config.gaze_circle_color = Scalar(b, g, r); // BGR format
                }
            } else if (strcmp(key, "gaze_circle_thickness") == 0) {
                viz_config.gaze_circle_thickness = atoi(value);
            } else if (strcmp(key, "pupil_line_thickness") == 0) {
                viz_config.pupil_line_thickness = atoi(value);
            } else if (strcmp(key, "pupil_line_color") == 0) {
                int r, g, b;
                if (sscanf(value, "%d,%d,%d", &r, &g, &b) == 3) {
                    viz_config.pupil_line_color = Scalar(b, g, r); // BGR format
                }
            } else if (strcmp(key, "show_eye_boundaries") == 0) {
                viz_config.show_eye_boundaries = (strcmp(value, "true") == 0);
            } else if (strcmp(key, "show_pupil_centers") == 0) {
                viz_config.show_pupil_centers = (strcmp(value, "true") == 0);
            }
        }
    }
    
    fclose(file);
}

// Initialize video processing module
void init_video_processing() {
    load_video_config();
    
    // Set OpenCV thread count if specified
    if (video_config.thread_count > 0) {
        setNumThreads(video_config.thread_count);
    }
    
    log_message("INFO", "Video processing module initialized");
}