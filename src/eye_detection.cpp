#include "cor.h"
#include <opencv2/opencv.hpp>
#include <opencv2/objdetect.hpp>
#include <stdio.h>
#include <stdlib.h>

using namespace cv;

// Global variables for eye detection
static CascadeClassifier eye_cascade;
static bool cascade_loaded = false;

// Eye detection configuration
static struct {
    double scale_factor;
    int min_neighbors;
    Size min_size;
    double pupil_threshold;
    int pupil_min_radius;
    int pupil_max_radius;
    Point2f left_eye_offset;
    Point2f right_eye_offset;
} eye_config = {
    1.1, 5, Size(30, 30), 50.0, 5, 30, Point2f(0, 0), Point2f(0, 0)
};

// Initialize eye detection cascade
static int init_eye_cascade() {
    if (cascade_loaded) return 0;
    
    // Try to load Haar cascade for eye detection
    std::string cascade_path = "haarcascade_eye.xml";
    if (!eye_cascade.load(cascade_path)) {
        // Try alternative path
        cascade_path = "/usr/share/opencv4/haarcascades/haarcascade_eye.xml";
        if (!eye_cascade.load(cascade_path)) {
            log_message("ERROR", "Could not load eye cascade classifier");
            return -1;
        }
    }
    
    cascade_loaded = true;
    log_message("INFO", "Eye cascade classifier loaded successfully");
    return 0;
}

// Detect pupils using Hough circles
static std::vector<Vec3f> detect_pupils_hough(Mat& eye_region) {
    Mat gray, blurred;
    std::vector<Vec3f> circles;
    
    // Convert to grayscale if needed
    if (eye_region.channels() == 3) {
        cvtColor(eye_region, gray, COLOR_BGR2GRAY);
    } else {
        gray = eye_region.clone();
    }
    
    // Apply Gaussian blur
    GaussianBlur(gray, blurred, Size(9, 9), 2, 2);
    
    // Detect circles using Hough transform
    HoughCircles(blurred, circles, HOUGH_GRADIENT, 1, 
                 gray.rows/8, 100, 30, 
                 eye_config.pupil_min_radius, 
                 eye_config.pupil_max_radius);
    
    return circles;
}

// Detect pupil using contour analysis
static Point2f detect_pupil_contour(Mat& eye_region) {
    Mat gray, thresh, blurred;
    std::vector<std::vector<Point>> contours;
    std::vector<Vec4i> hierarchy;
    
    // Convert to grayscale
    if (eye_region.channels() == 3) {
        cvtColor(eye_region, gray, COLOR_BGR2GRAY);
    } else {
        gray = eye_region.clone();
    }
    
    // Apply Gaussian blur
    GaussianBlur(gray, blurred, Size(5, 5), 0);
    
    // Apply threshold to find dark regions (pupils)
    threshold(blurred, thresh, eye_config.pupil_threshold, 255, THRESH_BINARY_INV);
    
    // Find contours
    findContours(thresh, contours, hierarchy, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
    
    // Find the best pupil candidate
    Point2f pupil_center(-1, -1);
    double max_area = 0;
    
    for (size_t i = 0; i < contours.size(); i++) {
        double area = contourArea(contours[i]);
        
        // Check if contour size is reasonable for a pupil
        if (area > max_area && area > 50 && area < 2000) {
            Moments moments = cv::moments(contours[i]);
            if (moments.m00 != 0) {
                Point2f center(moments.m10 / moments.m00, moments.m01 / moments.m00);
                
                // Check if center is within reasonable bounds
                if (center.x > 5 && center.x < eye_region.cols - 5 &&
                    center.y > 5 && center.y < eye_region.rows - 5) {
                    pupil_center = center;
                    max_area = area;
                }
            }
        }
    }
    
    return pupil_center;
}

// Main eye detection function
EyeDetectionResult detect_eyes_in_frame(Mat frame) {
    EyeDetectionResult result;
    result.valid = false;
    result.timestamp = (double)getTickCount() / getTickFrequency();
    
    // Initialize cascade if needed
    if (init_eye_cascade() != 0) {
        return result;
    }
    
    Mat gray;
    if (frame.channels() == 3) {
        cvtColor(frame, gray, COLOR_BGR2GRAY);
    } else {
        gray = frame.clone();
    }
    
    // Detect eyes using cascade classifier
    std::vector<Rect> eyes;
    eye_cascade.detectMultiScale(gray, eyes, 
                                eye_config.scale_factor, 
                                eye_config.min_neighbors, 
                                0, 
                                eye_config.min_size);
    
    if (eyes.size() >= 2) {
        // Sort eyes by x-coordinate (left to right)
        std::sort(eyes.begin(), eyes.end(), 
                  [](const Rect& a, const Rect& b) { return a.x < b.x; });
        
        // Assign left and right eyes
        Rect left_eye_rect = eyes[0];
        Rect right_eye_rect = eyes[1];
        
        // Apply offsets
        left_eye_rect.x += (int)eye_config.left_eye_offset.x;
        left_eye_rect.y += (int)eye_config.left_eye_offset.y;
        right_eye_rect.x += (int)eye_config.right_eye_offset.x;
        right_eye_rect.y += (int)eye_config.right_eye_offset.y;
        
        // Ensure rectangles are within frame bounds
        left_eye_rect &= Rect(0, 0, frame.cols, frame.rows);
        right_eye_rect &= Rect(0, 0, frame.cols, frame.rows);
        
        // Fill eye region data
        result.left_eye.x = left_eye_rect.x;
        result.left_eye.y = left_eye_rect.y;
        result.left_eye.width = left_eye_rect.width;
        result.left_eye.height = left_eye_rect.height;
        result.left_eye.confidence = 0.8f; // Default confidence
        
        result.right_eye.x = right_eye_rect.x;
        result.right_eye.y = right_eye_rect.y;
        result.right_eye.width = right_eye_rect.width;
        result.right_eye.height = right_eye_rect.height;
        result.right_eye.confidence = 0.8f;
        
        // Extract eye regions for pupil detection
        Mat left_eye_region = gray(left_eye_rect);
        Mat right_eye_region = gray(right_eye_rect);
        
        // Detect pupils in left eye
        std::vector<Vec3f> left_circles = detect_pupils_hough(left_eye_region);
        if (!left_circles.empty()) {
            Vec3f circle = left_circles[0];
            result.left_pupil.x = left_eye_rect.x + circle[0];
            result.left_pupil.y = left_eye_rect.y + circle[1];
            result.left_pupil.radius = circle[2];
            result.left_pupil.confidence = 0.7f;
        } else {
            // Fallback to contour detection
            Point2f pupil_center = detect_pupil_contour(left_eye_region);
            if (pupil_center.x >= 0) {
                result.left_pupil.x = left_eye_rect.x + pupil_center.x;
                result.left_pupil.y = left_eye_rect.y + pupil_center.y;
                result.left_pupil.radius = 8.0f; // Default radius
                result.left_pupil.confidence = 0.6f;
            } else {
                // Use eye center as fallback
                result.left_pupil.x = left_eye_rect.x + left_eye_rect.width / 2;
                result.left_pupil.y = left_eye_rect.y + left_eye_rect.height / 2;
                result.left_pupil.radius = 8.0f;
                result.left_pupil.confidence = 0.3f;
            }
        }
        
        // Detect pupils in right eye
        std::vector<Vec3f> right_circles = detect_pupils_hough(right_eye_region);
        if (!right_circles.empty()) {
            Vec3f circle = right_circles[0];
            result.right_pupil.x = right_eye_rect.x + circle[0];
            result.right_pupil.y = right_eye_rect.y + circle[1];
            result.right_pupil.radius = circle[2];
            result.right_pupil.confidence = 0.7f;
        } else {
            // Fallback to contour detection
            Point2f pupil_center = detect_pupil_contour(right_eye_region);
            if (pupil_center.x >= 0) {
                result.right_pupil.x = right_eye_rect.x + pupil_center.x;
                result.right_pupil.y = right_eye_rect.y + pupil_center.y;
                result.right_pupil.radius = 8.0f;
                result.right_pupil.confidence = 0.6f;
            } else {
                // Use eye center as fallback
                result.right_pupil.x = right_eye_rect.x + right_eye_rect.width / 2;
                result.right_pupil.y = right_eye_rect.y + right_eye_rect.height / 2;
                result.right_pupil.radius = 8.0f;
                result.right_pupil.confidence = 0.3f;
            }
        }
        
        result.valid = true;
    }
    
    return result;
}

// Load eye detection configuration
int load_eye_detection_config(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        log_message("WARNING", "Eye detection config file not found, using defaults");
        return 0; // Use defaults
    }
    
    char line[256];
    while (fgets(line, sizeof(line), file)) {
        // Skip comments and empty lines
        if (line[0] == '#' || line[0] == '\n') continue;
        
        char key[128], value[128];
        if (sscanf(line, "%127[^=]=%127s", key, value) == 2) {
            if (strcmp(key, "eye_cascade_scale_factor") == 0) {
                eye_config.scale_factor = atof(value);
            } else if (strcmp(key, "eye_cascade_min_neighbors") == 0) {
                eye_config.min_neighbors = atoi(value);
            } else if (strcmp(key, "eye_cascade_min_size_width") == 0) {
                eye_config.min_size.width = atoi(value);
            } else if (strcmp(key, "eye_cascade_min_size_height") == 0) {
                eye_config.min_size.height = atoi(value);
            } else if (strcmp(key, "pupil_detection_threshold") == 0) {
                eye_config.pupil_threshold = atof(value);
            } else if (strcmp(key, "pupil_min_radius") == 0) {
                eye_config.pupil_min_radius = atoi(value);
            } else if (strcmp(key, "pupil_max_radius") == 0) {
                eye_config.pupil_max_radius = atoi(value);
            } else if (strcmp(key, "left_eye_offset_x") == 0) {
                eye_config.left_eye_offset.x = atof(value);
            } else if (strcmp(key, "left_eye_offset_y") == 0) {
                eye_config.left_eye_offset.y = atof(value);
            } else if (strcmp(key, "right_eye_offset_x") == 0) {
                eye_config.right_eye_offset.x = atof(value);
            } else if (strcmp(key, "right_eye_offset_y") == 0) {
                eye_config.right_eye_offset.y = atof(value);
            }
        }
    }
    
    fclose(file);
    log_message("INFO", "Eye detection configuration loaded");
    return 0;
}

// Save eye detection configuration
int save_eye_detection_config(const char* filename, CalibrationData* data) {
    FILE* file = fopen(filename, "w");
    if (file == NULL) {
        log_message("ERROR", "Could not save eye detection configuration");
        return -1;
    }
    
    fprintf(file, "# Eye Detection Configuration Values\n");
    fprintf(file, "# Generated by Cor Gaze Detection Library\n");
    fprintf(file, "# Last Updated: %s\n\n", data->timestamp);
    
    fprintf(file, "eye_cascade_scale_factor=%.2f\n", eye_config.scale_factor);
    fprintf(file, "eye_cascade_min_neighbors=%d\n", eye_config.min_neighbors);
    fprintf(file, "eye_cascade_min_size_width=%d\n", eye_config.min_size.width);
    fprintf(file, "eye_cascade_min_size_height=%d\n", eye_config.min_size.height);
    fprintf(file, "pupil_detection_threshold=%.1f\n", eye_config.pupil_threshold);
    fprintf(file, "pupil_min_radius=%d\n", eye_config.pupil_min_radius);
    fprintf(file, "pupil_max_radius=%d\n", eye_config.pupil_max_radius);
    fprintf(file, "left_eye_offset_x=%.1f\n", eye_config.left_eye_offset.x);
    fprintf(file, "left_eye_offset_y=%.1f\n", eye_config.left_eye_offset.y);
    fprintf(file, "right_eye_offset_x=%.1f\n", eye_config.right_eye_offset.x);
    fprintf(file, "right_eye_offset_y=%.1f\n", eye_config.right_eye_offset.y);
    
    fprintf(file, "\n# Calibration Metadata\n");
    fprintf(file, "calibration_video_file=%s\n", data->video_file);
    fprintf(file, "calibration_timestamp=%s\n", data->timestamp);
    fprintf(file, "calibration_frame_count=%d\n", data->frame_count);
    fprintf(file, "calibration_user_id=%s\n", data->user_id);
    
    fclose(file);
    log_message("INFO", "Eye detection configuration saved");
    return 0;
}