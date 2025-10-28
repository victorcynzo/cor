#include "cor.h"
#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/videoio.hpp>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

using namespace cv;

// Calibration state
static struct {
    int current_frame;
    int total_frames;
    bool calibration_complete;
    std::vector<Mat> calibration_frames;
    std::vector<EyeDetectionResult> eye_results;
    std::vector<GazePoint> gaze_points;
} calib_state;

// Mouse callback for calibration interface
static Point2f mouse_pos;
static bool mouse_clicked = false;

static void calibration_mouse_callback(int event, int x, int y, int flags, void* userdata) {
    if (event == EVENT_LBUTTONDOWN) {
        mouse_pos.x = x;
        mouse_pos.y = y;
        mouse_clicked = true;
    } else if (event == EVENT_MOUSEMOVE) {
        mouse_pos.x = x;
        mouse_pos.y = y;
    }
}

// Extract calibration frames from video
static int extract_calibration_frames(const char* video_path) {
    VideoCapture cap(video_path);
    if (!cap.isOpened()) {
        log_message("ERROR", "Could not open video file for calibration");
        return -1;
    }
    
    int total_frames = (int)cap.get(CAP_PROP_FRAME_COUNT);
    int frame_step = total_frames / MAX_CALIBRATION_FRAMES;
    
    calib_state.calibration_frames.clear();
    calib_state.total_frames = 0;
    
    for (int i = 0; i < MAX_CALIBRATION_FRAMES && i * frame_step < total_frames; i++) {
        cap.set(CAP_PROP_POS_FRAMES, i * frame_step);
        
        Mat frame;
        if (cap.read(frame)) {
            calib_state.calibration_frames.push_back(frame.clone());
            calib_state.total_frames++;
        }
    }
    
    cap.release();
    
    if (calib_state.total_frames == 0) {
        log_message("ERROR", "No frames extracted for calibration");
        return -1;
    }
    
    printf("Extracted %d frames for calibration\n", calib_state.total_frames);
    return 0;
}

// Run eye detection calibration
int run_eye_calibration(const char* video_path) {
    // Extract frames for calibration
    if (extract_calibration_frames(video_path) != 0) {
        return -1;
    }
    
    // Initialize calibration state
    calib_state.current_frame = 0;
    calib_state.calibration_complete = false;
    calib_state.eye_results.clear();
    
    // Create calibration window
    namedWindow("Eye Calibration", WINDOW_AUTOSIZE);
    setMouseCallback("Eye Calibration", calibration_mouse_callback, NULL);
    
    printf("\nEye Detection Calibration\n");
    printf("=========================\n");
    printf("Instructions:\n");
    printf("- Adjust the detection boundaries around eyes and pupils\n");
    printf("- Press SPACE to accept current frame and move to next\n");
    printf("- Press ESC to cancel calibration\n");
    printf("- Press 'r' to reset current frame\n\n");
    
    while (calib_state.current_frame < calib_state.total_frames && !calib_state.calibration_complete) {
        Mat frame = calib_state.calibration_frames[calib_state.current_frame].clone();
        Mat display_frame = frame.clone();
        
        // Detect eyes in current frame
        EyeDetectionResult eye_result = detect_eyes_in_frame(frame);
        
        // Draw eye detection results
        if (eye_result.valid) {
            // Draw left eye rectangle
            rectangle(display_frame, 
                     Rect(eye_result.left_eye.x, eye_result.left_eye.y, 
                          eye_result.left_eye.width, eye_result.left_eye.height),
                     Scalar(0, 255, 0), 2);
            
            // Draw right eye rectangle
            rectangle(display_frame, 
                     Rect(eye_result.right_eye.x, eye_result.right_eye.y, 
                          eye_result.right_eye.width, eye_result.right_eye.height),
                     Scalar(0, 255, 0), 2);
            
            // Draw left pupil
            circle(display_frame, 
                   Point(eye_result.left_pupil.x, eye_result.left_pupil.y),
                   eye_result.left_pupil.radius, Scalar(255, 0, 0), 2);
            
            // Draw right pupil
            circle(display_frame, 
                   Point(eye_result.right_pupil.x, eye_result.right_pupil.y),
                   eye_result.right_pupil.radius, Scalar(255, 0, 0), 2);
        }
        
        // Add frame information
        char frame_info[128];
        sprintf(frame_info, "Frame %d/%d", calib_state.current_frame + 1, calib_state.total_frames);
        putText(display_frame, frame_info, Point(10, 30), FONT_HERSHEY_SIMPLEX, 1, Scalar(255, 255, 255), 2);
        
        // Add instructions
        putText(display_frame, "SPACE: Next  ESC: Cancel  R: Reset", 
                Point(10, display_frame.rows - 20), FONT_HERSHEY_SIMPLEX, 0.7, Scalar(255, 255, 255), 2);
        
        imshow("Eye Calibration", display_frame);
        
        int key = waitKey(30) & 0xFF;
        if (key == 27) { // ESC key
            printf("Calibration cancelled by user\n");
            destroyAllWindows();
            return -1;
        } else if (key == 32) { // SPACE key
            // Accept current frame and move to next
            calib_state.eye_results.push_back(eye_result);
            calib_state.current_frame++;
            printf("Frame %d accepted\n", calib_state.current_frame);
        } else if (key == 'r' || key == 'R') {
            // Reset current frame (reload detection)
            printf("Frame %d reset\n", calib_state.current_frame + 1);
        }
    }
    
    destroyAllWindows();
    
    if (calib_state.current_frame >= calib_state.total_frames) {
        // Save calibration data
        CalibrationData calib_data;
        strcpy(calib_data.video_file, video_path);
        calib_data.frame_count = calib_state.total_frames;
        
        // Get current timestamp
        time_t now = time(0);
        struct tm* timeinfo = localtime(&now);
        strftime(calib_data.timestamp, sizeof(calib_data.timestamp), "%Y-%m-%d %H:%M:%S", timeinfo);
        
        strcpy(calib_data.user_id, "default_user");
        calib_data.accuracy_score = 0.85f; // Placeholder
        calib_data.precision_score = 0.80f; // Placeholder
        
        if (save_eye_detection_config(EYE_DETECTION_CONFIG, &calib_data) == 0) {
            printf("Eye calibration completed successfully!\n");
            return 0;
        } else {
            printf("Failed to save calibration data\n");
            return -1;
        }
    }
    
    return -1;
}

// Run gaze direction calibration
int run_gaze_calibration(const char* video_path) {
    // Extract frames for calibration
    if (extract_calibration_frames(video_path) != 0) {
        return -1;
    }
    
    // Initialize calibration state
    calib_state.current_frame = 0;
    calib_state.calibration_complete = false;
    calib_state.gaze_points.clear();
    
    // Create calibration window
    namedWindow("Gaze Calibration", WINDOW_AUTOSIZE);
    setMouseCallback("Gaze Calibration", calibration_mouse_callback, NULL);
    
    printf("\nGaze Direction Calibration\n");
    printf("==========================\n");
    printf("Instructions:\n");
    printf("- Click on the screen where the person is looking\n");
    printf("- Green ball shows current gaze estimate\n");
    printf("- Yellow lines connect gaze point to pupils\n");
    printf("- Press SPACE to accept current frame and move to next\n");
    printf("- Press ESC to cancel calibration\n");
    printf("- Press 'r' to reset current frame\n\n");
    
    while (calib_state.current_frame < calib_state.total_frames && !calib_state.calibration_complete) {
        Mat frame = calib_state.calibration_frames[calib_state.current_frame].clone();
        Mat display_frame = frame.clone();
        
        // Detect eyes in current frame
        EyeDetectionResult eye_result = detect_eyes_in_frame(frame);
        
        if (eye_result.valid) {
            // Calculate gaze direction
            GazePoint gaze_point = calculate_gaze_direction(eye_result);
            
            // Convert normalized gaze coordinates to pixel coordinates
            int gaze_x = (int)(gaze_point.x * frame.cols);
            int gaze_y = (int)(gaze_point.y * frame.rows);
            
            // Draw gaze indicator (green ball)
            circle(display_frame, Point(gaze_x, gaze_y), 15, Scalar(0, 255, 0), -1);
            circle(display_frame, Point(gaze_x, gaze_y), 15, Scalar(0, 0, 0), 2);
            
            // Draw lines from gaze point to pupils (yellow lines)
            line(display_frame, Point(gaze_x, gaze_y), 
                 Point(eye_result.left_pupil.x, eye_result.left_pupil.y), 
                 Scalar(0, 255, 255), 2);
            line(display_frame, Point(gaze_x, gaze_y), 
                 Point(eye_result.right_pupil.x, eye_result.right_pupil.y), 
                 Scalar(0, 255, 255), 2);
            
            // Draw pupils
            circle(display_frame, 
                   Point(eye_result.left_pupil.x, eye_result.left_pupil.y),
                   5, Scalar(255, 0, 0), -1);
            circle(display_frame, 
                   Point(eye_result.right_pupil.x, eye_result.right_pupil.y),
                   5, Scalar(255, 0, 0), -1);
            
            // Show mouse position if clicked
            if (mouse_clicked) {
                circle(display_frame, Point(mouse_pos.x, mouse_pos.y), 10, Scalar(0, 0, 255), 2);
                mouse_clicked = false;
            }
        }
        
        // Add frame information
        char frame_info[128];
        sprintf(frame_info, "Frame %d/%d", calib_state.current_frame + 1, calib_state.total_frames);
        putText(display_frame, frame_info, Point(10, 30), FONT_HERSHEY_SIMPLEX, 1, Scalar(255, 255, 255), 2);
        
        // Add instructions
        putText(display_frame, "Click where person is looking, then press SPACE", 
                Point(10, display_frame.rows - 40), FONT_HERSHEY_SIMPLEX, 0.6, Scalar(255, 255, 255), 2);
        putText(display_frame, "SPACE: Next  ESC: Cancel  R: Reset", 
                Point(10, display_frame.rows - 20), FONT_HERSHEY_SIMPLEX, 0.6, Scalar(255, 255, 255), 2);
        
        imshow("Gaze Calibration", display_frame);
        
        int key = waitKey(30) & 0xFF;
        if (key == 27) { // ESC key
            printf("Calibration cancelled by user\n");
            destroyAllWindows();
            return -1;
        } else if (key == 32) { // SPACE key
            // Accept current frame and move to next
            if (eye_result.valid) {
                GazePoint gaze_point = calculate_gaze_direction(eye_result);
                calib_state.gaze_points.push_back(gaze_point);
            }
            calib_state.current_frame++;
            printf("Frame %d accepted\n", calib_state.current_frame);
        } else if (key == 'r' || key == 'R') {
            // Reset current frame
            printf("Frame %d reset\n", calib_state.current_frame + 1);
        }
    }
    
    destroyAllWindows();
    
    if (calib_state.current_frame >= calib_state.total_frames) {
        // Save calibration data
        CalibrationData calib_data;
        strcpy(calib_data.video_file, video_path);
        calib_data.frame_count = calib_state.total_frames;
        
        // Get current timestamp
        time_t now = time(0);
        struct tm* timeinfo = localtime(&now);
        strftime(calib_data.timestamp, sizeof(calib_data.timestamp), "%Y-%m-%d %H:%M:%S", timeinfo);
        
        strcpy(calib_data.user_id, "default_user");
        
        // Calculate accuracy and precision scores based on calibration data
        calib_data.accuracy_score = 0.82f; // Placeholder - would be calculated from actual calibration
        calib_data.precision_score = 0.78f; // Placeholder - would be calculated from actual calibration
        
        if (save_gaze_direction_config(GAZE_DIRECTION_CONFIG, &calib_data) == 0) {
            printf("Gaze calibration completed successfully!\n");
            return 0;
        } else {
            printf("Failed to save calibration data\n");
            return -1;
        }
    }
    
    return -1;
}