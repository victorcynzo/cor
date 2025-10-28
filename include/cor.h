#ifndef COR_H
#define COR_H

#include <Python.h>
#include <numpy/arrayobject.h>
#include <opencv2/opencv.hpp>
#include <stdbool.h>

// Version information
#define COR_VERSION_MAJOR 1
#define COR_VERSION_MINOR 0
#define COR_VERSION_PATCH 0

// Configuration file paths
#define EYE_DETECTION_CONFIG "eye-detection-values.txt"
#define GAZE_DIRECTION_CONFIG "gaze-direction-values.txt"
#define GENERAL_CONFIG "cor.txt"

// Maximum supported video dimensions
#define MAX_VIDEO_WIDTH 3840
#define MAX_VIDEO_HEIGHT 2160
#define MAX_CALIBRATION_FRAMES 20

// Data structures
typedef struct {
    int x, y, width, height;
    float confidence;
} EyeRegion;

typedef struct {
    float x, y;
    float radius;
    float confidence;
} PupilData;

typedef struct {
    EyeRegion left_eye, right_eye;
    PupilData left_pupil, right_pupil;
    bool valid;
    double timestamp;
} EyeDetectionResult;

typedef struct {
    float x, y;
    float confidence;
    double timestamp;
} GazePoint;

typedef struct {
    char color_scheme[64];
    float intensity_multiplier;
    int blur_radius;
    float resolution_factor;
    float alpha_transparency;
} HeatmapConfig;

typedef struct {
    char video_file[512];
    int frame_count;
    char timestamp[64];
    char user_id[128];
    float accuracy_score;
    float precision_score;
} CalibrationData;

// Python function declarations
PyObject* cor_help(PyObject* self, PyObject* args);
PyObject* cor_calibrate_eyes(PyObject* self, PyObject* args);
PyObject* cor_calibrate_gaze(PyObject* self, PyObject* args);
PyObject* cor_run(PyObject* self, PyObject* args);
PyObject* cor_version(PyObject* self, PyObject* args);
PyObject* cor_get_config(PyObject* self, PyObject* args);
PyObject* cor_set_config(PyObject* self, PyObject* args);
PyObject* cor_validate_video(PyObject* self, PyObject* args);
PyObject* cor_extract_frames(PyObject* self, PyObject* args);
PyObject* cor_benchmark(PyObject* self, PyObject* args);
PyObject* cor_analyze_attention(PyObject* self, PyObject* args);
PyObject* cor_generate_advanced_heatmap(PyObject* self, PyObject* args);
PyObject* cor_init_realtime(PyObject* self, PyObject* args);
PyObject* cor_process_realtime_frame(PyObject* self, PyObject* args);
PyObject* cor_cleanup_realtime(PyObject* self, PyObject* args);
PyObject* cor_export_analysis(PyObject* self, PyObject* args);
PyObject* cor_analyze_attention(PyObject* self, PyObject* args);
PyObject* cor_generate_advanced_heatmap(PyObject* self, PyObject* args);
PyObject* cor_init_realtime(PyObject* self, PyObject* args);
PyObject* cor_process_realtime_frame(PyObject* self, PyObject* args);
PyObject* cor_cleanup_realtime(PyObject* self, PyObject* args);
PyObject* cor_export_analysis(PyObject* self, PyObject* args);

// Internal functions
int load_eye_detection_config(const char* filename);
int load_gaze_direction_config(const char* filename);
int load_general_config(const char* filename);
int save_eye_detection_config(const char* filename, CalibrationData* data);
int save_gaze_direction_config(const char* filename, CalibrationData* data);

EyeDetectionResult detect_eyes_in_frame(cv::Mat frame);
GazePoint calculate_gaze_direction(EyeDetectionResult eye_data);
cv::Mat generate_heatmap(std::vector<GazePoint> gaze_points, int width, int height, HeatmapConfig config);
int process_video_file(const char* video_path, bool visualize);

// Calibration functions
int run_eye_calibration(const char* video_path);
int run_gaze_calibration(const char* video_path);

// Utility functions
bool is_supported_video_format(const char* filename);
char* get_output_filename(const char* input_path, const char* suffix, const char* extension);
void log_message(const char* level, const char* message);
void print_progress_bar(int current, int total, const char* prefix, const char* suffix, int length);
void init_video_processing();
HeatmapConfig get_heatmap_config();
cv::Mat create_heatmap_overlay(cv::Mat background, cv::Mat heatmap, float alpha);
int save_heatmap_image(cv::Mat heatmap, const char* filename);

// Advanced feature structures and functions (C-compatible)
typedef struct {
    float x, y;
    float duration;
    float intensity;
    int visit_count;
} AttentionRegion;

typedef struct {
    AttentionRegion* regions;
    int region_count;
    float total_duration;
    float average_fixation_duration;
    int saccade_count;
} AttentionAnalysis;

// C++ wrapper functions (implemented in advanced_features.c)
#ifdef __cplusplus
extern "C" {
#endif

// Advanced feature functions
int init_realtime_processing(int camera_id);
GazePoint process_realtime_frame();
void cleanup_realtime_processing();
int export_analysis_to_json_wrapper(const char* video_path, const char* filename);

// Internal C++ functions (not exposed to Python directly)
#ifdef __cplusplus
}

// C++ only functions (used internally)
std::vector<int> detect_saccades(const std::vector<GazePoint>& gaze_points);
std::vector<AttentionRegion> detect_fixations(const std::vector<GazePoint>& gaze_points);
AttentionAnalysis analyze_attention_patterns(const std::vector<GazePoint>& gaze_points);
cv::Mat generate_advanced_heatmap(const std::vector<GazePoint>& gaze_points, int width, int height, const char* mode);
std::vector<GazePoint> get_realtime_history();
int export_analysis_to_json(const AttentionAnalysis& analysis, const char* filename);
#endif

#endif // COR_H