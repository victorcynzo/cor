#include "cor.h"
#include <opencv2/opencv.hpp>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

using namespace cv;

// Gaze detection configuration
static struct {
    float sensitivity_x;
    float sensitivity_y;
    float offset_x;
    float offset_y;
    float pupil_to_gaze_ratio_x;
    float pupil_to_gaze_ratio_y;
    float gaze_center_x;
    float gaze_center_y;
    float smoothing_factor;
    float min_confidence_threshold;
    float max_gaze_angle;
} gaze_config = {
    1.0f, 1.0f, 0.0f, 0.0f, 0.8f, 0.8f, 0.5f, 0.5f, 0.3f, 0.7f, 45.0f
};

// Previous gaze point for smoothing
static GazePoint prev_gaze = {0.0f, 0.0f, 0.0f, 0.0};
static bool prev_gaze_valid = false;

// Calculate gaze direction from eye detection data
GazePoint calculate_gaze_direction(EyeDetectionResult eye_data) {
    GazePoint gaze_point;
    gaze_point.confidence = 0.0f;
    gaze_point.timestamp = eye_data.timestamp;
    
    if (!eye_data.valid) {
        gaze_point.x = 0.0f;
        gaze_point.y = 0.0f;
        return gaze_point;
    }
    
    // Calculate average pupil position
    float avg_pupil_x = (eye_data.left_pupil.x + eye_data.right_pupil.x) / 2.0f;
    float avg_pupil_y = (eye_data.left_pupil.y + eye_data.right_pupil.y) / 2.0f;
    
    // Calculate average eye center
    float avg_eye_x = ((eye_data.left_eye.x + eye_data.left_eye.width / 2.0f) +
                       (eye_data.right_eye.x + eye_data.right_eye.width / 2.0f)) / 2.0f;
    float avg_eye_y = ((eye_data.left_eye.y + eye_data.left_eye.height / 2.0f) +
                       (eye_data.right_eye.y + eye_data.right_eye.height / 2.0f)) / 2.0f;
    
    // Calculate pupil displacement from eye center
    float pupil_displacement_x = avg_pupil_x - avg_eye_x;
    float pupil_displacement_y = avg_pupil_y - avg_eye_y;
    
    // Apply sensitivity and ratio factors
    float gaze_displacement_x = pupil_displacement_x * gaze_config.pupil_to_gaze_ratio_x * gaze_config.sensitivity_x;
    float gaze_displacement_y = pupil_displacement_y * gaze_config.pupil_to_gaze_ratio_y * gaze_config.sensitivity_y;
    
    // Calculate final gaze position (normalized coordinates)
    gaze_point.x = gaze_config.gaze_center_x + gaze_displacement_x / 1000.0f + gaze_config.offset_x;
    gaze_point.y = gaze_config.gaze_center_y + gaze_displacement_y / 1000.0f + gaze_config.offset_y;
    
    // Clamp to valid range [0, 1]
    gaze_point.x = std::max(0.0f, std::min(1.0f, gaze_point.x));
    gaze_point.y = std::max(0.0f, std::min(1.0f, gaze_point.y));
    
    // Calculate confidence based on eye detection quality
    float avg_eye_confidence = (eye_data.left_eye.confidence + eye_data.right_eye.confidence) / 2.0f;
    float avg_pupil_confidence = (eye_data.left_pupil.confidence + eye_data.right_pupil.confidence) / 2.0f;
    gaze_point.confidence = (avg_eye_confidence + avg_pupil_confidence) / 2.0f;
    
    // Check if gaze angle is within acceptable range
    float gaze_angle = atan2(gaze_displacement_y, gaze_displacement_x) * 180.0f / M_PI;
    if (fabs(gaze_angle) > gaze_config.max_gaze_angle) {
        gaze_point.confidence *= 0.5f; // Reduce confidence for extreme angles
    }
    
    // Apply temporal smoothing if previous gaze point is available
    if (prev_gaze_valid && gaze_point.confidence >= gaze_config.min_confidence_threshold) {
        float alpha = gaze_config.smoothing_factor;
        gaze_point.x = alpha * prev_gaze.x + (1.0f - alpha) * gaze_point.x;
        gaze_point.y = alpha * prev_gaze.y + (1.0f - alpha) * gaze_point.y;
    }
    
    // Update previous gaze point
    if (gaze_point.confidence >= gaze_config.min_confidence_threshold) {
        prev_gaze = gaze_point;
        prev_gaze_valid = true;
    }
    
    return gaze_point;
}

// Calculate binocular gaze with vergence compensation
static GazePoint calculate_binocular_gaze(EyeDetectionResult eye_data) {
    GazePoint gaze_point;
    gaze_point.confidence = 0.0f;
    gaze_point.timestamp = eye_data.timestamp;
    
    if (!eye_data.valid) {
        gaze_point.x = 0.0f;
        gaze_point.y = 0.0f;
        return gaze_point;
    }
    
    // Calculate individual eye gaze directions
    float left_eye_center_x = eye_data.left_eye.x + eye_data.left_eye.width / 2.0f;
    float left_eye_center_y = eye_data.left_eye.y + eye_data.left_eye.height / 2.0f;
    float right_eye_center_x = eye_data.right_eye.x + eye_data.right_eye.width / 2.0f;
    float right_eye_center_y = eye_data.right_eye.y + eye_data.right_eye.height / 2.0f;
    
    // Left eye gaze vector
    float left_gaze_x = (eye_data.left_pupil.x - left_eye_center_x) * gaze_config.sensitivity_x;
    float left_gaze_y = (eye_data.left_pupil.y - left_eye_center_y) * gaze_config.sensitivity_y;
    
    // Right eye gaze vector
    float right_gaze_x = (eye_data.right_pupil.x - right_eye_center_x) * gaze_config.sensitivity_x;
    float right_gaze_y = (eye_data.right_pupil.y - right_eye_center_y) * gaze_config.sensitivity_y;
    
    // Average the gaze vectors (simple binocular fusion)
    float avg_gaze_x = (left_gaze_x + right_gaze_x) / 2.0f;
    float avg_gaze_y = (left_gaze_y + right_gaze_y) / 2.0f;
    
    // Convert to normalized screen coordinates
    gaze_point.x = gaze_config.gaze_center_x + avg_gaze_x / 1000.0f + gaze_config.offset_x;
    gaze_point.y = gaze_config.gaze_center_y + avg_gaze_y / 1000.0f + gaze_config.offset_y;
    
    // Clamp to valid range
    gaze_point.x = std::max(0.0f, std::min(1.0f, gaze_point.x));
    gaze_point.y = std::max(0.0f, std::min(1.0f, gaze_point.y));
    
    // Calculate confidence
    float left_confidence = eye_data.left_pupil.confidence;
    float right_confidence = eye_data.right_pupil.confidence;
    gaze_point.confidence = (left_confidence + right_confidence) / 2.0f;
    
    // Check for consistency between eyes
    float gaze_consistency = 1.0f - fabs(left_gaze_x - right_gaze_x) / 100.0f - fabs(left_gaze_y - right_gaze_y) / 100.0f;
    gaze_consistency = std::max(0.0f, std::min(1.0f, gaze_consistency));
    gaze_point.confidence *= gaze_consistency;
    
    return gaze_point;
}

// Detect saccadic eye movements
static bool detect_saccade(GazePoint current_gaze, GazePoint previous_gaze, double time_diff) {
    if (time_diff <= 0) return false;
    
    float distance = sqrt(pow(current_gaze.x - previous_gaze.x, 2) + pow(current_gaze.y - previous_gaze.y, 2));
    float velocity = distance / time_diff; // pixels per second (normalized)
    
    // Saccade threshold (adjustable)
    const float saccade_threshold = 0.3f; // normalized velocity threshold
    
    return velocity > saccade_threshold;
}

// Load gaze direction configuration
int load_gaze_direction_config(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        log_message("WARNING", "Gaze direction config file not found, using defaults");
        return 0; // Use defaults
    }
    
    char line[256];
    while (fgets(line, sizeof(line), file)) {
        // Skip comments and empty lines
        if (line[0] == '#' || line[0] == '\n') continue;
        
        char key[128], value[128];
        if (sscanf(line, "%127[^=]=%127s", key, value) == 2) {
            if (strcmp(key, "gaze_sensitivity_x") == 0) {
                gaze_config.sensitivity_x = atof(value);
            } else if (strcmp(key, "gaze_sensitivity_y") == 0) {
                gaze_config.sensitivity_y = atof(value);
            } else if (strcmp(key, "gaze_offset_x") == 0) {
                gaze_config.offset_x = atof(value);
            } else if (strcmp(key, "gaze_offset_y") == 0) {
                gaze_config.offset_y = atof(value);
            } else if (strcmp(key, "pupil_to_gaze_ratio_x") == 0) {
                gaze_config.pupil_to_gaze_ratio_x = atof(value);
            } else if (strcmp(key, "pupil_to_gaze_ratio_y") == 0) {
                gaze_config.pupil_to_gaze_ratio_y = atof(value);
            } else if (strcmp(key, "gaze_center_x") == 0) {
                gaze_config.gaze_center_x = atof(value);
            } else if (strcmp(key, "gaze_center_y") == 0) {
                gaze_config.gaze_center_y = atof(value);
            } else if (strcmp(key, "gaze_smoothing_factor") == 0) {
                gaze_config.smoothing_factor = atof(value);
            } else if (strcmp(key, "min_confidence_threshold") == 0) {
                gaze_config.min_confidence_threshold = atof(value);
            } else if (strcmp(key, "max_gaze_angle") == 0) {
                gaze_config.max_gaze_angle = atof(value);
            }
        }
    }
    
    fclose(file);
    log_message("INFO", "Gaze direction configuration loaded");
    return 0;
}

// Save gaze direction configuration
int save_gaze_direction_config(const char* filename, CalibrationData* data) {
    FILE* file = fopen(filename, "w");
    if (file == NULL) {
        log_message("ERROR", "Could not save gaze direction configuration");
        return -1;
    }
    
    fprintf(file, "# Gaze Direction Configuration Values\n");
    fprintf(file, "# Generated by Cor Gaze Detection Library\n");
    fprintf(file, "# Last Updated: %s\n\n", data->timestamp);
    
    fprintf(file, "gaze_sensitivity_x=%.2f\n", gaze_config.sensitivity_x);
    fprintf(file, "gaze_sensitivity_y=%.2f\n", gaze_config.sensitivity_y);
    fprintf(file, "gaze_offset_x=%.2f\n", gaze_config.offset_x);
    fprintf(file, "gaze_offset_y=%.2f\n", gaze_config.offset_y);
    fprintf(file, "pupil_to_gaze_ratio_x=%.2f\n", gaze_config.pupil_to_gaze_ratio_x);
    fprintf(file, "pupil_to_gaze_ratio_y=%.2f\n", gaze_config.pupil_to_gaze_ratio_y);
    fprintf(file, "gaze_center_x=%.2f\n", gaze_config.gaze_center_x);
    fprintf(file, "gaze_center_y=%.2f\n", gaze_config.gaze_center_y);
    fprintf(file, "gaze_smoothing_factor=%.2f\n", gaze_config.smoothing_factor);
    fprintf(file, "min_confidence_threshold=%.2f\n", gaze_config.min_confidence_threshold);
    fprintf(file, "max_gaze_angle=%.1f\n", gaze_config.max_gaze_angle);
    
    fprintf(file, "\n# Calibration Metadata\n");
    fprintf(file, "calibration_video_file=%s\n", data->video_file);
    fprintf(file, "calibration_timestamp=%s\n", data->timestamp);
    fprintf(file, "calibration_accuracy_score=%.3f\n", data->accuracy_score);
    fprintf(file, "calibration_precision_score=%.3f\n", data->precision_score);
    fprintf(file, "calibration_user_id=%s\n", data->user_id);
    
    fclose(file);
    log_message("INFO", "Gaze direction configuration saved");
    return 0;
}