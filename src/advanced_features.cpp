#include "cor.h"
#include <opencv2/opencv.hpp>
#include <opencv2/videoio.hpp>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <algorithm>

using namespace cv;

// Advanced feature implementations

// Real-time processing state
static struct {
    bool is_initialized;
    VideoCapture camera;
    std::vector<GazePoint> recent_gaze_points;
    int max_history_size;
} realtime_state = {false, VideoCapture(), std::vector<GazePoint>(), 100};

// Attention analysis structures
typedef struct {
    float x, y;
    float duration;
    float intensity;
    int visit_count;
} AttentionRegion;

typedef struct {
    std::vector<AttentionRegion> regions;
    float total_duration;
    float average_fixation_duration;
    int saccade_count;
} AttentionAnalysis;

// Saccade detection parameters
static struct {
    float velocity_threshold;
    float acceleration_threshold;
    int min_duration_ms;
    int max_duration_ms;
} saccade_params = {300.0f, 500.0f, 20, 200};

// Fixation detection parameters
static struct {
    float position_threshold;
    int min_duration_ms;
    float stability_threshold;
} fixation_params = {25.0f, 100, 15.0f};

// Detect saccadic movements in gaze sequence
std::vector<int> detect_saccades(const std::vector<GazePoint>& gaze_points) {
    std::vector<int> saccade_indices;
    
    if (gaze_points.size() < 3) return saccade_indices;
    
    for (size_t i = 1; i < gaze_points.size() - 1; i++) {
        const GazePoint& prev = gaze_points[i-1];
        const GazePoint& curr = gaze_points[i];
        const GazePoint& next = gaze_points[i+1];
        
        // Calculate velocity (pixels per second, assuming normalized coordinates)
        double dt1 = curr.timestamp - prev.timestamp;
        double dt2 = next.timestamp - curr.timestamp;
        
        if (dt1 <= 0 || dt2 <= 0) continue;
        
        float dx1 = curr.x - prev.x;
        float dy1 = curr.y - prev.y;
        float dx2 = next.x - curr.x;
        float dy2 = next.y - curr.y;
        
        float velocity1 = sqrt(dx1*dx1 + dy1*dy1) / dt1;
        float velocity2 = sqrt(dx2*dx2 + dy2*dy2) / dt2;
        
        // Calculate acceleration
        float acceleration = fabs(velocity2 - velocity1) / ((dt1 + dt2) / 2.0);
        
        // Check if this is a saccade
        if (velocity1 > saccade_params.velocity_threshold || 
            velocity2 > saccade_params.velocity_threshold ||
            acceleration > saccade_params.acceleration_threshold) {
            saccade_indices.push_back(i);
        }
    }
    
    return saccade_indices;
}

// Detect fixations in gaze sequence
std::vector<AttentionRegion> detect_fixations(const std::vector<GazePoint>& gaze_points) {
    std::vector<AttentionRegion> fixations;
    
    if (gaze_points.empty()) return fixations;
    
    size_t start_idx = 0;
    
    while (start_idx < gaze_points.size()) {
        AttentionRegion fixation = {0};
        fixation.x = gaze_points[start_idx].x;
        fixation.y = gaze_points[start_idx].y;
        fixation.visit_count = 1;
        
        size_t end_idx = start_idx;
        float sum_x = gaze_points[start_idx].x;
        float sum_y = gaze_points[start_idx].y;
        
        // Find consecutive points within position threshold
        for (size_t i = start_idx + 1; i < gaze_points.size(); i++) {
            float distance = sqrt(pow(gaze_points[i].x - fixation.x, 2) + 
                                pow(gaze_points[i].y - fixation.y, 2));
            
            if (distance <= fixation_params.position_threshold / 1000.0f) {
                end_idx = i;
                sum_x += gaze_points[i].x;
                sum_y += gaze_points[i].y;
                fixation.visit_count++;
            } else {
                break;
            }
        }
        
        // Calculate fixation properties
        if (end_idx > start_idx) {
            fixation.x = sum_x / fixation.visit_count;
            fixation.y = sum_y / fixation.visit_count;
            fixation.duration = (gaze_points[end_idx].timestamp - gaze_points[start_idx].timestamp) * 1000.0f;
            
            // Calculate intensity based on duration and stability
            float stability = 0.0f;
            for (size_t i = start_idx; i <= end_idx; i++) {
                float dist = sqrt(pow(gaze_points[i].x - fixation.x, 2) + 
                                pow(gaze_points[i].y - fixation.y, 2));
                stability += dist;
            }
            stability /= (end_idx - start_idx + 1);
            fixation.intensity = fixation.duration / (1.0f + stability * 1000.0f);
            
            // Only add if duration meets minimum threshold
            if (fixation.duration >= fixation_params.min_duration_ms) {
                fixations.push_back(fixation);
            }
        }
        
        start_idx = end_idx + 1;
    }
    
    return fixations;
}

// Analyze attention patterns
AttentionAnalysis analyze_attention_patterns(const std::vector<GazePoint>& gaze_points) {
    AttentionAnalysis analysis;
    analysis.total_duration = 0.0f;
    analysis.average_fixation_duration = 0.0f;
    analysis.saccade_count = 0;
    
    if (gaze_points.empty()) return analysis;
    
    // Detect fixations
    analysis.regions = detect_fixations(gaze_points);
    
    // Calculate statistics
    float total_fixation_duration = 0.0f;
    for (const auto& region : analysis.regions) {
        total_fixation_duration += region.duration;
    }
    
    if (!analysis.regions.empty()) {
        analysis.average_fixation_duration = total_fixation_duration / analysis.regions.size();
    }
    
    // Detect saccades
    std::vector<int> saccade_indices = detect_saccades(gaze_points);
    analysis.saccade_count = saccade_indices.size();
    
    // Calculate total duration
    if (gaze_points.size() > 1) {
        analysis.total_duration = (gaze_points.back().timestamp - gaze_points.front().timestamp) * 1000.0f;
    }
    
    return analysis;
}

// Generate attention heatmap with advanced features
Mat generate_advanced_heatmap(const std::vector<GazePoint>& gaze_points, 
                             int width, int height, 
                             const char* mode) {
    Mat heatmap = Mat::zeros(height, width, CV_32F);
    
    if (strcmp(mode, "fixation") == 0) {
        // Generate fixation-based heatmap
        std::vector<AttentionRegion> fixations = detect_fixations(gaze_points);
        
        for (const auto& fixation : fixations) {
            int x = (int)(fixation.x * width);
            int y = (int)(fixation.y * height);
            
            if (x >= 0 && x < width && y >= 0 && y < height) {
                // Create circular region with intensity based on duration
                int radius = (int)(fixation.duration / 10.0f); // Scale duration to radius
                radius = std::max(5, std::min(50, radius));
                
                for (int dy = -radius; dy <= radius; dy++) {
                    for (int dx = -radius; dx <= radius; dx++) {
                        int nx = x + dx;
                        int ny = y + dy;
                        
                        if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                            float distance = sqrt(dx*dx + dy*dy);
                            if (distance <= radius) {
                                float weight = (1.0f - distance / radius) * fixation.intensity / 1000.0f;
                                heatmap.at<float>(ny, nx) += weight;
                            }
                        }
                    }
                }
            }
        }
    } else if (strcmp(mode, "saccade") == 0) {
        // Generate saccade path visualization
        std::vector<int> saccade_indices = detect_saccades(gaze_points);
        
        for (int idx : saccade_indices) {
            if (idx > 0 && idx < (int)gaze_points.size() - 1) {
                // Draw line from previous to next point
                Point2f start(gaze_points[idx-1].x * width, gaze_points[idx-1].y * height);
                Point2f end(gaze_points[idx+1].x * width, gaze_points[idx+1].y * height);
                
                line(heatmap, start, end, Scalar(1.0f), 3);
            }
        }
    } else {
        // Default density heatmap
        HeatmapConfig config = get_heatmap_config();
        return generate_heatmap(gaze_points, width, height, config);
    }
    
    // Normalize and convert to color
    normalize(heatmap, heatmap, 0, 255, NORM_MINMAX);
    
    Mat heatmap_8bit, colored_heatmap;
    heatmap.convertTo(heatmap_8bit, CV_8U);
    applyColorMap(heatmap_8bit, colored_heatmap, COLORMAP_JET);
    
    return colored_heatmap;
}

// Real-time gaze processing initialization
int init_realtime_processing(int camera_id) {
    if (realtime_state.is_initialized) {
        return 0; // Already initialized
    }
    
    realtime_state.camera.open(camera_id);
    if (!realtime_state.camera.isOpened()) {
        log_message("ERROR", "Could not open camera for real-time processing");
        return -1;
    }
    
    // Set camera properties
    realtime_state.camera.set(CAP_PROP_FRAME_WIDTH, 640);
    realtime_state.camera.set(CAP_PROP_FRAME_HEIGHT, 480);
    realtime_state.camera.set(CAP_PROP_FPS, 30);
    
    realtime_state.recent_gaze_points.clear();
    realtime_state.is_initialized = true;
    
    log_message("INFO", "Real-time processing initialized");
    return 0;
}

// Process single frame in real-time
GazePoint process_realtime_frame() {
    GazePoint gaze_point = {0.0f, 0.0f, 0.0f, 0.0};
    
    if (!realtime_state.is_initialized) {
        log_message("ERROR", "Real-time processing not initialized");
        return gaze_point;
    }
    
    Mat frame;
    if (!realtime_state.camera.read(frame)) {
        log_message("ERROR", "Could not read frame from camera");
        return gaze_point;
    }
    
    // Detect eyes and calculate gaze
    EyeDetectionResult eye_result = detect_eyes_in_frame(frame);
    if (eye_result.valid) {
        gaze_point = calculate_gaze_direction(eye_result);
        
        // Add to recent history
        realtime_state.recent_gaze_points.push_back(gaze_point);
        
        // Limit history size
        if (realtime_state.recent_gaze_points.size() > realtime_state.max_history_size) {
            realtime_state.recent_gaze_points.erase(realtime_state.recent_gaze_points.begin());
        }
    }
    
    return gaze_point;
}

// Get recent gaze history for real-time analysis
std::vector<GazePoint> get_realtime_history() {
    return realtime_state.recent_gaze_points;
}

// Cleanup real-time processing
void cleanup_realtime_processing() {
    if (realtime_state.is_initialized) {
        realtime_state.camera.release();
        realtime_state.recent_gaze_points.clear();
        realtime_state.is_initialized = false;
        log_message("INFO", "Real-time processing cleaned up");
    }
}

// C-compatible wrapper for analysis export
int export_analysis_to_json_wrapper(const char* video_path, const char* filename) {
    if (!is_supported_video_format(video_path)) {
        log_message("ERROR", "Unsupported video format for analysis export");
        return -1;
    }
    
    // Process video to get gaze points
    cv::VideoCapture cap(video_path);
    if (!cap.isOpened()) {
        log_message("ERROR", "Could not open video file for analysis export");
        return -1;
    }
    
    std::vector<GazePoint> gaze_points;
    cv::Mat frame;
    
    while (cap.read(frame)) {
        EyeDetectionResult eye_result = detect_eyes_in_frame(frame);
        if (eye_result.valid) {
            GazePoint gaze_point = calculate_gaze_direction(eye_result);
            if (gaze_point.confidence > 0.5f) {
                gaze_points.push_back(gaze_point);
            }
        }
    }
    
    cap.release();
    
    if (gaze_points.empty()) {
        log_message("ERROR", "No valid gaze points found for analysis export");
        return -1;
    }
    
    // Perform analysis
    AttentionAnalysis analysis = analyze_attention_patterns(gaze_points);
    
    // Export to JSON
    return export_analysis_to_json(analysis, filename);
}

// Export analysis results to JSON format
int export_analysis_to_json(const AttentionAnalysis& analysis, const char* filename) {
    FILE* file = fopen(filename, "w");
    if (file == NULL) {
        log_message("ERROR", "Could not create analysis export file");
        return -1;
    }
    
    fprintf(file, "{\n");
    fprintf(file, "  \"total_duration_ms\": %.2f,\n", analysis.total_duration);
    fprintf(file, "  \"average_fixation_duration_ms\": %.2f,\n", analysis.average_fixation_duration);
    fprintf(file, "  \"saccade_count\": %d,\n", analysis.saccade_count);
    fprintf(file, "  \"fixation_count\": %zu,\n", analysis.regions.size());
    fprintf(file, "  \"fixations\": [\n");
    
    for (size_t i = 0; i < analysis.regions.size(); i++) {
        const AttentionRegion& region = analysis.regions[i];
        fprintf(file, "    {\n");
        fprintf(file, "      \"x\": %.4f,\n", region.x);
        fprintf(file, "      \"y\": %.4f,\n", region.y);
        fprintf(file, "      \"duration_ms\": %.2f,\n", region.duration);
        fprintf(file, "      \"intensity\": %.4f,\n", region.intensity);
        fprintf(file, "      \"visit_count\": %d\n", region.visit_count);
        fprintf(file, "    }%s\n", (i < analysis.regions.size() - 1) ? "," : "");
    }
    
    fprintf(file, "  ]\n");
    fprintf(file, "}\n");
    
    fclose(file);
    log_message("INFO", "Analysis exported to JSON");
    return 0;
}