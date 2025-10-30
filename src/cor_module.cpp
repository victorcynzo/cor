#include "cor.h"
#include <opencv2/opencv.hpp>
#include <opencv2/videoio.hpp>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <string>
#include <chrono>
#include <sys/stat.h>
#ifdef _WIN32
#include <direct.h>
#define mkdir _mkdir
#endif

// Global configuration variables
static HeatmapConfig g_heatmap_config;
static bool g_debug_mode = false;

// Python module method definitions
static PyMethodDef CorMethods[] = {
    {"help", cor_help, METH_NOARGS, "Display help information for all Cor functions"},
    {"calibrate_eyes", cor_calibrate_eyes, METH_VARARGS, "Interactive eye detection calibration"},
    {"calibrate_gaze", cor_calibrate_gaze, METH_VARARGS, "Interactive gaze direction calibration"},
    {"run", cor_run, METH_VARARGS, "Run gaze detection analysis on video file"},
    {"version", cor_version, METH_NOARGS, "Get library version information"},
    {"get_config", cor_get_config, METH_VARARGS, "Get configuration parameter value"},
    {"set_config", cor_set_config, METH_VARARGS, "Set configuration parameter value"},
    {"validate_video", cor_validate_video, METH_VARARGS, "Validate video file format and properties"},
    {"extract_frames", cor_extract_frames, METH_VARARGS, "Extract frames from video for preview"},
    {"benchmark", cor_benchmark, METH_VARARGS, "Run performance benchmark on video file"},
    {"analyze_attention", cor_analyze_attention, METH_VARARGS, "Analyze attention patterns in video"},
    {"generate_advanced_heatmap", cor_generate_advanced_heatmap, METH_VARARGS, "Generate advanced heatmap with specific mode"},
    {"init_realtime", cor_init_realtime, METH_VARARGS, "Initialize real-time camera processing"},
    {"process_realtime_frame", cor_process_realtime_frame, METH_NOARGS, "Process single frame from camera"},
    {"cleanup_realtime", cor_cleanup_realtime, METH_NOARGS, "Cleanup real-time processing"},
    {"export_analysis", cor_export_analysis, METH_VARARGS, "Export analysis results to file"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef cormodule = {
    PyModuleDef_HEAD_INIT,
    "cor",
    "Advanced gaze detection library for video analysis",
    -1,
    CorMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_cor(void) {
    PyObject* module;
    
    // Initialize numpy
    import_array();
    
    // Create module
    module = PyModule_Create(&cormodule);
    if (module == NULL) {
        return NULL;
    }
    
    // Add version information
    PyModule_AddStringConstant(module, "__version__", "1.0.1");
    PyModule_AddIntConstant(module, "VERSION_MAJOR", COR_VERSION_MAJOR);
    PyModule_AddIntConstant(module, "VERSION_MINOR", COR_VERSION_MINOR);
    PyModule_AddIntConstant(module, "VERSION_PATCH", COR_VERSION_PATCH);
    
    // Load default configuration
    load_general_config(GENERAL_CONFIG);
    
    // Initialize video processing module
    init_video_processing();
    
    return module;
}

// Help function implementation
PyObject* cor_help(PyObject* self, PyObject* args) {
    printf("\n");
    printf("=== COR GAZE DETECTION LIBRARY - HELP ===\n");
    printf("Version: %d.%d.%d\n\n", COR_VERSION_MAJOR, COR_VERSION_MINOR, COR_VERSION_PATCH);
    
    printf("AVAILABLE FUNCTIONS:\n\n");
    
    printf("cor.help()\n");
    printf("  Description: Display this help information\n");
    printf("  Parameters: None\n");
    printf("  Example: cor.help()\n\n");
    
    printf("cor.calibrate_eyes(video_file)\n");
    printf("  Description: Interactive eye detection calibration interface\n");
    printf("  Parameters: video_file (str) - Path to input video file\n");
    printf("  Output: Updates eye-detection-values.txt with calibration data\n");
    printf("  Example: cor.calibrate_eyes('sample.mp4')\n\n");
    
    printf("cor.calibrate_gaze(video_file)\n");
    printf("  Description: Interactive gaze direction calibration interface\n");
    printf("  Parameters: video_file (str) - Path to input video file\n");
    printf("  Output: Updates gaze-direction-values.txt with calibration data\n");
    printf("  Example: cor.calibrate_gaze('sample.mp4')\n\n");
    
    printf("cor.run(video_file, *args)\n");
    printf("  Description: Run gaze detection analysis on video file\n");
    printf("  Parameters: \n");
    printf("    video_file (str) - Path to input video file\n");
    printf("    *args - Optional arguments:\n");
    printf("      '--visualize' - Generate visualization video output\n");
    printf("  Output Files:\n");
    printf("    {videoname}_heatmap-pure.jpg - Pure heatmap visualization\n");
    printf("    {videoname}_heatmap-overlay.jpg - Heatmap overlaid on frame\n");
    printf("    {videoname}_heatmap.{ext} - Full video with gaze overlay (with --visualize)\n");
    printf("  Examples:\n");
    printf("    cor.run('video.mp4')\n");
    printf("    cor.run('video.mp4', '--visualize')\n\n");
    
    printf("SUPPORTED VIDEO FORMATS:\n");
    printf("  MP4, AVI, MOV, MKV, WMV, FLV, WEBM\n\n");
    
    printf("CONFIGURATION FILES:\n");
    printf("  eye-detection-values.txt - Eye detection parameters\n");
    printf("  gaze-direction-values.txt - Gaze calibration settings\n");
    printf("  cor.txt - General configuration and heatmap options\n\n");
    
    printf("WORKFLOW RECOMMENDATIONS:\n");
    printf("  1. Basic Analysis: cor.run('video.mp4')\n");
    printf("  2. Precision Analysis:\n");
    printf("     a. cor.calibrate_eyes('video.mp4')\n");
    printf("     b. cor.calibrate_gaze('video.mp4')\n");
    printf("     c. cor.run('video.mp4', '--visualize')\n\n");
    
    printf("For detailed documentation, see Documentation.txt\n");
    printf("For configuration options, see cor.txt\n");
    printf("==========================================\n\n");
    
    Py_RETURN_NONE;
}

// Eye calibration function implementation
PyObject* cor_calibrate_eyes(PyObject* self, PyObject* args) {
    const char* video_path;
    
    if (!PyArg_ParseTuple(args, "s", &video_path)) {
        return NULL;
    }
    
    // Check if video file exists and is supported
    if (!is_supported_video_format(video_path)) {
        PyErr_SetString(PyExc_ValueError, "Unsupported video format or file not found");
        return NULL;
    }
    
    printf("Starting eye detection calibration for: %s\n", video_path);
    
    // Check if existing calibration data exists
    FILE* config_file = fopen(EYE_DETECTION_CONFIG, "r");
    if (config_file != NULL) {
        fclose(config_file);
        printf("\nExisting eye detection calibration found.\n");
        printf("Choose an option:\n");
        printf("1. Overwrite current values\n");
        printf("2. Modify values to accommodate both videos\n");
        printf("Enter choice (1 or 2): ");
        
        int choice;
        if (scanf("%d", &choice) != 1 || (choice != 1 && choice != 2)) {
            printf("Invalid choice. Defaulting to overwrite.\n");
            choice = 1;
        }
        
        if (choice == 2) {
            printf("Merging with existing calibration data...\n");
        } else {
            printf("Overwriting existing calibration data...\n");
        }
    }
    
    // Run the calibration process
    int result = run_eye_calibration(video_path);
    
    if (result == 0) {
        printf("Eye calibration completed successfully!\n");
        printf("Calibration data saved to: %s\n", EYE_DETECTION_CONFIG);
    } else {
        PyErr_SetString(PyExc_RuntimeError, "Eye calibration failed");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

// Gaze calibration function implementation
PyObject* cor_calibrate_gaze(PyObject* self, PyObject* args) {
    const char* video_path;
    
    if (!PyArg_ParseTuple(args, "s", &video_path)) {
        return NULL;
    }
    
    // Check if video file exists and is supported
    if (!is_supported_video_format(video_path)) {
        PyErr_SetString(PyExc_ValueError, "Unsupported video format or file not found");
        return NULL;
    }
    
    printf("Starting gaze direction calibration for: %s\n", video_path);
    
    // Check if existing calibration data exists
    FILE* config_file = fopen(GAZE_DIRECTION_CONFIG, "r");
    if (config_file != NULL) {
        fclose(config_file);
        printf("\nExisting gaze direction calibration found.\n");
        printf("Choose an option:\n");
        printf("1. Overwrite current values\n");
        printf("2. Modify values to accommodate both videos\n");
        printf("Enter choice (1 or 2): ");
        
        int choice;
        if (scanf("%d", &choice) != 1 || (choice != 1 && choice != 2)) {
            printf("Invalid choice. Defaulting to overwrite.\n");
            choice = 1;
        }
        
        if (choice == 2) {
            printf("Merging with existing calibration data...\n");
        } else {
            printf("Overwriting existing calibration data...\n");
        }
    }
    
    // Run the calibration process
    int result = run_gaze_calibration(video_path);
    
    if (result == 0) {
        printf("Gaze calibration completed successfully!\n");
        printf("Calibration data saved to: %s\n", GAZE_DIRECTION_CONFIG);
    } else {
        PyErr_SetString(PyExc_RuntimeError, "Gaze calibration failed");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

// Main run function implementation
PyObject* cor_run(PyObject* self, PyObject* args) {
    const char* video_path;
    PyObject* extra_args = NULL;
    bool visualize = false;
    
    // Parse arguments - handle both single string and tuple of strings
    Py_ssize_t arg_count = PyTuple_Size(args);
    if (arg_count < 1) {
        PyErr_SetString(PyExc_TypeError, "run() missing required argument: video_file");
        return NULL;
    }
    
    // Get video path
    PyObject* video_path_obj = PyTuple_GetItem(args, 0);
    if (!PyUnicode_Check(video_path_obj)) {
        PyErr_SetString(PyExc_TypeError, "video_file must be a string");
        return NULL;
    }
    video_path = PyUnicode_AsUTF8(video_path_obj);
    
    // Check for additional arguments
    for (Py_ssize_t i = 1; i < arg_count; i++) {
        PyObject* arg_obj = PyTuple_GetItem(args, i);
        if (PyUnicode_Check(arg_obj)) {
            const char* arg_str = PyUnicode_AsUTF8(arg_obj);
            if (strcmp(arg_str, "--visualize") == 0) {
                visualize = true;
            }
        }
    }
    
    // Check if video file exists and is supported
    if (!is_supported_video_format(video_path)) {
        PyErr_SetString(PyExc_ValueError, "Unsupported video format or file not found");
        return NULL;
    }
    
    printf("Starting gaze detection analysis for: %s\n", video_path);
    if (visualize) {
        printf("Visualization mode enabled - will generate overlay video\n");
    }
    
    // Load configuration files
    load_eye_detection_config(EYE_DETECTION_CONFIG);
    load_gaze_direction_config(GAZE_DIRECTION_CONFIG);
    load_general_config(GENERAL_CONFIG);
    
    // Process the video
    int result = process_video_file(video_path, visualize);
    
    if (result == 0) {
        printf("Gaze detection analysis completed successfully!\n");
        
        // Generate output filenames
        char* base_name = get_output_filename(video_path, "", "");
        printf("Output files generated:\n");
        printf("  %s_heatmap-pure.jpg - Pure heatmap visualization\n", base_name);
        printf("  %s_heatmap-overlay.jpg - Heatmap overlaid on frame\n", base_name);
        
        if (visualize) {
            // Determine output video extension
            const char* ext = strrchr(video_path, '.');
            if (ext == NULL) ext = ".mp4";
            printf("  %s_heatmap%s - Full video with gaze overlay\n", base_name, ext);
        }
        
        free(base_name);
    } else {
        PyErr_SetString(PyExc_RuntimeError, "Gaze detection analysis failed");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

// Utility function to check supported video formats
bool is_supported_video_format(const char* filename) {
    if (filename == NULL) return false;
    
    // Check if file exists
    FILE* file = fopen(filename, "r");
    if (file == NULL) return false;
    fclose(file);
    
    // Check file extension
    const char* ext = strrchr(filename, '.');
    if (ext == NULL) return false;
    
    ext++; // Skip the dot
    
    // List of supported extensions
    const char* supported[] = {"mp4", "avi", "mov", "mkv", "wmv", "flv", "webm", "MP4", "AVI", "MOV", "MKV", "WMV", "FLV", "WEBM"};
    int num_supported = sizeof(supported) / sizeof(supported[0]);
    
    for (int i = 0; i < num_supported; i++) {
        if (strcmp(ext, supported[i]) == 0) {
            return true;
        }
    }
    
    return false;
}

// Utility function to generate output filenames
char* get_output_filename(const char* input_path, const char* suffix, const char* extension) {
    if (input_path == NULL) return NULL;
    
    // Find the last dot and slash
    const char* last_dot = strrchr(input_path, '.');
    const char* last_slash = strrchr(input_path, '/');
    if (last_slash == NULL) last_slash = strrchr(input_path, '\\');
    
    // Calculate base name length
    int base_len;
    if (last_dot != NULL && (last_slash == NULL || last_dot > last_slash)) {
        base_len = last_dot - input_path;
    } else {
        base_len = strlen(input_path);
    }
    
    // Allocate memory for output filename
    int total_len = base_len + strlen(suffix) + strlen(extension) + 1;
    char* output = (char*)malloc(total_len);
    
    if (output != NULL) {
        strncpy(output, input_path, base_len);
        output[base_len] = '\0';
        strcat(output, suffix);
        strcat(output, extension);
    }
    
    return output;
}

// Progress bar utility
void print_progress_bar(int current, int total, const char* prefix = "Progress", const char* suffix = "Complete", int length = 50) {
    if (total <= 0) return;
    
    float percent = (float(current) / float(total)) * 100.0f;
    int filled_length = int(length * current / total);
    
    // Create the bar string
    std::string bar(filled_length, '█');
    bar += std::string(length - filled_length, '-');
    
    // Print the progress bar
    printf("\r%s |%s| %d/%d (%.1f%%) %s", prefix, bar.c_str(), current, total, percent, suffix);
    fflush(stdout);
    
    // Print newline when complete
    if (current == total) {
        printf("\n");
    }
}

// Confidence assessment utility
void display_confidence_assessment(const std::vector<GazePoint>& gaze_points, int total_frames) {
    if (gaze_points.empty() || total_frames <= 0) {
        printf("\n=== GAZE DETECTION CONFIDENCE ASSESSMENT ===\n");
        printf("❌ No valid gaze data detected\n");
        printf("Confidence: 0.0%% (No reliable gaze tracking)\n");
        printf("============================================\n\n");
        return;
    }
    
    // Calculate confidence metrics
    float total_confidence = 0.0f;
    int high_confidence_points = 0;
    int medium_confidence_points = 0;
    int low_confidence_points = 0;
    
    for (const auto& point : gaze_points) {
        total_confidence += point.confidence;
        
        if (point.confidence >= 0.8f) {
            high_confidence_points++;
        } else if (point.confidence >= 0.6f) {
            medium_confidence_points++;
        } else {
            low_confidence_points++;
        }
    }
    
    float average_confidence = total_confidence / gaze_points.size();
    float detection_rate = (float)gaze_points.size() / total_frames;
    float high_confidence_ratio = (float)high_confidence_points / gaze_points.size();
    
    // Calculate overall accuracy confidence
    float accuracy_confidence = (average_confidence * 0.5f + detection_rate * 0.3f + high_confidence_ratio * 0.2f) * 100.0f;
    
    // Display assessment
    printf("\n=== GAZE DETECTION CONFIDENCE ASSESSMENT ===\n");
    printf("📊 Analysis Results:\n");
    printf("   • Total frames processed: %d\n", total_frames);
    printf("   • Valid gaze points detected: %zu\n", gaze_points.size());
    printf("   • Detection rate: %.1f%%\n", detection_rate * 100.0f);
    printf("   • Average confidence per point: %.1f%%\n", average_confidence * 100.0f);
    printf("\n📈 Confidence Distribution:\n");
    printf("   • High confidence (≥80%%): %d points (%.1f%%)\n", 
           high_confidence_points, (float)high_confidence_points / gaze_points.size() * 100.0f);
    printf("   • Medium confidence (60-79%%): %d points (%.1f%%)\n", 
           medium_confidence_points, (float)medium_confidence_points / gaze_points.size() * 100.0f);
    printf("   • Low confidence (<60%%): %d points (%.1f%%)\n", 
           low_confidence_points, (float)low_confidence_points / gaze_points.size() * 100.0f);
    
    printf("\n🎯 Overall Accuracy Confidence: %.1f%%\n", accuracy_confidence);
    
    // Provide interpretation
    if (accuracy_confidence >= 85.0f) {
        printf("✅ Excellent - High reliability for research and analysis\n");
    } else if (accuracy_confidence >= 70.0f) {
        printf("✅ Good - Suitable for most applications\n");
    } else if (accuracy_confidence >= 55.0f) {
        printf("⚠️  Fair - Consider recalibration for better accuracy\n");
    } else {
        printf("❌ Poor - Recalibration strongly recommended\n");
    }
    
    printf("============================================\n\n");
}

// Logging utility
void log_message(const char* level, const char* message) {
    if (g_debug_mode || strcmp(level, "ERROR") == 0) {
        printf("[%s] %s\n", level, message);
    }
}// Ve
rsion information function
PyObject* cor_version(PyObject* self, PyObject* args) {
    PyObject* version_dict = PyDict_New();
    
    PyDict_SetItemString(version_dict, "version", PyUnicode_FromString("1.0.1"));
    PyDict_SetItemString(version_dict, "major", PyLong_FromLong(COR_VERSION_MAJOR));
    PyDict_SetItemString(version_dict, "minor", PyLong_FromLong(COR_VERSION_MINOR));
    PyDict_SetItemString(version_dict, "patch", PyLong_FromLong(COR_VERSION_PATCH));
    PyDict_SetItemString(version_dict, "build_date", PyUnicode_FromString(__DATE__));
    PyDict_SetItemString(version_dict, "opencv_version", PyUnicode_FromString(CV_VERSION));
    
    return version_dict;
}

// Get configuration parameter
PyObject* cor_get_config(PyObject* self, PyObject* args) {
    const char* param_name;
    const char* config_file = NULL;
    
    if (!PyArg_ParseTuple(args, "s|s", &param_name, &config_file)) {
        return NULL;
    }
    
    // Default to general config if not specified
    if (config_file == NULL) {
        config_file = GENERAL_CONFIG;
    }
    
    FILE* file = fopen(config_file, "r");
    if (file == NULL) {
        PyErr_SetString(PyExc_FileNotFoundError, "Configuration file not found");
        return NULL;
    }
    
    char line[256];
    while (fgets(line, sizeof(line), file)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        
        char key[128], value[128];
        if (sscanf(line, "%127[^=]=%127s", key, value) == 2) {
            if (strcmp(key, param_name) == 0) {
                fclose(file);
                return PyUnicode_FromString(value);
            }
        }
    }
    
    fclose(file);
    PyErr_SetString(PyExc_KeyError, "Configuration parameter not found");
    return NULL;
}

// Set configuration parameter
PyObject* cor_set_config(PyObject* self, PyObject* args) {
    const char* param_name;
    const char* param_value;
    const char* config_file = NULL;
    
    if (!PyArg_ParseTuple(args, "ss|s", &param_name, &param_value, &config_file)) {
        return NULL;
    }
    
    // Default to general config if not specified
    if (config_file == NULL) {
        config_file = GENERAL_CONFIG;
    }
    
    // Read existing configuration
    std::vector<std::string> lines;
    bool param_found = false;
    
    FILE* file = fopen(config_file, "r");
    if (file != NULL) {
        char line[256];
        while (fgets(line, sizeof(line), file)) {
            std::string line_str(line);
            
            // Remove trailing newline
            if (!line_str.empty() && line_str.back() == '\n') {
                line_str.pop_back();
            }
            
            if (line_str[0] != '#' && line_str.find('=') != std::string::npos) {
                size_t eq_pos = line_str.find('=');
                std::string key = line_str.substr(0, eq_pos);
                
                if (key == param_name) {
                    line_str = std::string(param_name) + "=" + std::string(param_value);
                    param_found = true;
                }
            }
            
            lines.push_back(line_str);
        }
        fclose(file);
    }
    
    // Add parameter if not found
    if (!param_found) {
        lines.push_back(std::string(param_name) + "=" + std::string(param_value));
    }
    
    // Write updated configuration
    file = fopen(config_file, "w");
    if (file == NULL) {
        PyErr_SetString(PyExc_IOError, "Could not write to configuration file");
        return NULL;
    }
    
    for (const auto& line : lines) {
        fprintf(file, "%s\n", line.c_str());
    }
    
    fclose(file);
    Py_RETURN_NONE;
}

// Validate video file
PyObject* cor_validate_video(PyObject* self, PyObject* args) {
    const char* video_path;
    
    if (!PyArg_ParseTuple(args, "s", &video_path)) {
        return NULL;
    }
    
    PyObject* result_dict = PyDict_New();
    
    // Check if file exists and format is supported
    bool is_valid = is_supported_video_format(video_path);
    PyDict_SetItemString(result_dict, "valid", PyBool_FromLong(is_valid));
    
    if (is_valid) {
        // Get video properties using OpenCV
        cv::VideoCapture cap(video_path);
        if (cap.isOpened()) {
            int frame_count = (int)cap.get(cv::CAP_PROP_FRAME_COUNT);
            double fps = cap.get(cv::CAP_PROP_FPS);
            int width = (int)cap.get(cv::CAP_PROP_FRAME_WIDTH);
            int height = (int)cap.get(cv::CAP_PROP_FRAME_HEIGHT);
            double duration = frame_count / fps;
            
            PyDict_SetItemString(result_dict, "frame_count", PyLong_FromLong(frame_count));
            PyDict_SetItemString(result_dict, "fps", PyFloat_FromDouble(fps));
            PyDict_SetItemString(result_dict, "width", PyLong_FromLong(width));
            PyDict_SetItemString(result_dict, "height", PyLong_FromLong(height));
            PyDict_SetItemString(result_dict, "duration", PyFloat_FromDouble(duration));
            
            // Determine codec
            int fourcc = (int)cap.get(cv::CAP_PROP_FOURCC);
            char codec_str[5];
            codec_str[0] = (char)(fourcc & 0xFF);
            codec_str[1] = (char)((fourcc >> 8) & 0xFF);
            codec_str[2] = (char)((fourcc >> 16) & 0xFF);
            codec_str[3] = (char)((fourcc >> 24) & 0xFF);
            codec_str[4] = '\0';
            PyDict_SetItemString(result_dict, "codec", PyUnicode_FromString(codec_str));
            
            cap.release();
        } else {
            PyDict_SetItemString(result_dict, "error", PyUnicode_FromString("Could not open video file"));
        }
    } else {
        PyDict_SetItemString(result_dict, "error", PyUnicode_FromString("Unsupported format or file not found"));
    }
    
    return result_dict;
}

// Extract frames for preview
PyObject* cor_extract_frames(PyObject* self, PyObject* args) {
    const char* video_path;
    int num_frames = 5;
    const char* output_dir = "frames";
    
    if (!PyArg_ParseTuple(args, "s|is", &video_path, &num_frames, &output_dir)) {
        return NULL;
    }
    
    if (!is_supported_video_format(video_path)) {
        PyErr_SetString(PyExc_ValueError, "Unsupported video format or file not found");
        return NULL;
    }
    
    cv::VideoCapture cap(video_path);
    if (!cap.isOpened()) {
        PyErr_SetString(PyExc_RuntimeError, "Could not open video file");
        return NULL;
    }
    
    int total_frames = (int)cap.get(cv::CAP_PROP_FRAME_COUNT);
    int frame_step = total_frames / num_frames;
    
    PyObject* frame_list = PyList_New(0);
    
    for (int i = 0; i < num_frames && i * frame_step < total_frames; i++) {
        cap.set(cv::CAP_PROP_POS_FRAMES, i * frame_step);
        
        cv::Mat frame;
        if (cap.read(frame)) {
            char filename[256];
            sprintf(filename, "%s/frame_%03d.jpg", output_dir, i);
            
            // Create directory if it doesn't exist
            #ifdef _WIN32
            _mkdir(output_dir);
            #else
            mkdir(output_dir, 0755);
            #endif
            
            if (cv::imwrite(filename, frame)) {
                PyList_Append(frame_list, PyUnicode_FromString(filename));
            }
        }
    }
    
    cap.release();
    return frame_list;
}

// Performance benchmark
PyObject* cor_benchmark(PyObject* self, PyObject* args) {
    const char* video_path;
    int max_frames = 100;
    
    if (!PyArg_ParseTuple(args, "s|i", &video_path, &max_frames)) {
        return NULL;
    }
    
    if (!is_supported_video_format(video_path)) {
        PyErr_SetString(PyExc_ValueError, "Unsupported video format or file not found");
        return NULL;
    }
    
    cv::VideoCapture cap(video_path);
    if (!cap.isOpened()) {
        PyErr_SetString(PyExc_RuntimeError, "Could not open video file");
        return NULL;
    }
    
    PyObject* benchmark_dict = PyDict_New();
    
    // Benchmark eye detection
    auto start_time = std::chrono::high_resolution_clock::now();
    
    cv::Mat frame;
    int processed_frames = 0;
    int successful_detections = 0;
    
    while (cap.read(frame) && processed_frames < max_frames) {
        EyeDetectionResult eye_result = detect_eyes_in_frame(frame);
        if (eye_result.valid) {
            successful_detections++;
        }
        processed_frames++;
        
        // Update progress bar every 10 frames
        if (processed_frames % 10 == 0 || processed_frames == max_frames) {
            print_progress_bar(processed_frames, max_frames, "Benchmarking", "frames processed");
        }
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    double fps = (double)processed_frames / (duration.count() / 1000.0);
    double detection_rate = (double)successful_detections / processed_frames;
    
    PyDict_SetItemString(benchmark_dict, "processed_frames", PyLong_FromLong(processed_frames));
    PyDict_SetItemString(benchmark_dict, "successful_detections", PyLong_FromLong(successful_detections));
    PyDict_SetItemString(benchmark_dict, "processing_fps", PyFloat_FromDouble(fps));
    PyDict_SetItemString(benchmark_dict, "detection_rate", PyFloat_FromDouble(detection_rate));
    PyDict_SetItemString(benchmark_dict, "processing_time_ms", PyLong_FromLong(duration.count()));
    
    cap.release();
    return benchmark_dict;
}// Adva
nced feature function implementations

// Analyze attention patterns
PyObject* cor_analyze_attention(PyObject* self, PyObject* args) {
    const char* video_path;
    
    if (!PyArg_ParseTuple(args, "s", &video_path)) {
        return NULL;
    }
    
    if (!is_supported_video_format(video_path)) {
        PyErr_SetString(PyExc_ValueError, "Unsupported video format or file not found");
        return NULL;
    }
    
    // Process video to get gaze points
    cv::VideoCapture cap(video_path);
    if (!cap.isOpened()) {
        PyErr_SetString(PyExc_RuntimeError, "Could not open video file");
        return NULL;
    }
    
    std::vector<GazePoint> gaze_points;
    cv::Mat frame;
    
    printf("Analyzing attention patterns...\n");
    
    int frame_count = (int)cap.get(cv::CAP_PROP_FRAME_COUNT);
    int processed_frames = 0;
    
    while (cap.read(frame)) {
        processed_frames++;
        
        EyeDetectionResult eye_result = detect_eyes_in_frame(frame);
        if (eye_result.valid) {
            GazePoint gaze_point = calculate_gaze_direction(eye_result);
            if (gaze_point.confidence > 0.5f) {
                gaze_points.push_back(gaze_point);
            }
        }
        
        // Update progress bar every 50 frames
        if (processed_frames % 50 == 0 || processed_frames == frame_count) {
            print_progress_bar(processed_frames, frame_count, "Attention analysis", "frames analyzed");
        }
    }
    
    cap.release();
    
    if (gaze_points.empty()) {
        PyErr_SetString(PyExc_RuntimeError, "No valid gaze points found for analysis");
        return NULL;
    }
    
    // Perform attention analysis
    AttentionAnalysis analysis = analyze_attention_patterns(gaze_points);
    
    // Create result dictionary
    PyObject* result_dict = PyDict_New();
    PyDict_SetItemString(result_dict, "total_duration_ms", PyFloat_FromDouble(analysis.total_duration));
    PyDict_SetItemString(result_dict, "average_fixation_duration_ms", PyFloat_FromDouble(analysis.average_fixation_duration));
    PyDict_SetItemString(result_dict, "saccade_count", PyLong_FromLong(analysis.saccade_count));
    PyDict_SetItemString(result_dict, "fixation_count", PyLong_FromSize_t(analysis.regions.size()));
    
    // Add fixation regions
    PyObject* fixations_list = PyList_New(0);
    for (const auto& region : analysis.regions) {
        PyObject* fixation_dict = PyDict_New();
        PyDict_SetItemString(fixation_dict, "x", PyFloat_FromDouble(region.x));
        PyDict_SetItemString(fixation_dict, "y", PyFloat_FromDouble(region.y));
        PyDict_SetItemString(fixation_dict, "duration_ms", PyFloat_FromDouble(region.duration));
        PyDict_SetItemString(fixation_dict, "intensity", PyFloat_FromDouble(region.intensity));
        PyDict_SetItemString(fixation_dict, "visit_count", PyLong_FromLong(region.visit_count));
        PyList_Append(fixations_list, fixation_dict);
        Py_DECREF(fixation_dict);
    }
    PyDict_SetItemString(result_dict, "fixations", fixations_list);
    Py_DECREF(fixations_list);
    
    return result_dict;
}

// Generate advanced heatmap
PyObject* cor_generate_advanced_heatmap(PyObject* self, PyObject* args) {
    const char* video_path;
    const char* mode = "density";
    const char* output_path = NULL;
    
    if (!PyArg_ParseTuple(args, "s|ss", &video_path, &mode, &output_path)) {
        return NULL;
    }
    
    if (!is_supported_video_format(video_path)) {
        PyErr_SetString(PyExc_ValueError, "Unsupported video format or file not found");
        return NULL;
    }
    
    // Process video to get gaze points
    cv::VideoCapture cap(video_path);
    if (!cap.isOpened()) {
        PyErr_SetString(PyExc_RuntimeError, "Could not open video file");
        return NULL;
    }
    
    int width = (int)cap.get(cv::CAP_PROP_FRAME_WIDTH);
    int height = (int)cap.get(cv::CAP_PROP_FRAME_HEIGHT);
    
    std::vector<GazePoint> gaze_points;
    cv::Mat frame;
    
    printf("Generating advanced heatmap (mode: %s)...\n", mode);
    
    int frame_count = (int)cap.get(cv::CAP_PROP_FRAME_COUNT);
    int processed_frames = 0;
    
    while (cap.read(frame)) {
        processed_frames++;
        
        EyeDetectionResult eye_result = detect_eyes_in_frame(frame);
        if (eye_result.valid) {
            GazePoint gaze_point = calculate_gaze_direction(eye_result);
            if (gaze_point.confidence > 0.5f) {
                gaze_points.push_back(gaze_point);
            }
        }
        
        // Update progress bar every 50 frames
        if (processed_frames % 50 == 0 || processed_frames == frame_count) {
            print_progress_bar(processed_frames, frame_count, "Heatmap generation", "frames processed");
        }
    }
    
    cap.release();
    
    if (gaze_points.empty()) {
        PyErr_SetString(PyExc_RuntimeError, "No valid gaze points found for heatmap generation");
        return NULL;
    }
    
    // Generate advanced heatmap
    cv::Mat heatmap = generate_advanced_heatmap(gaze_points, width, height, mode);
    
    // Save heatmap if output path provided
    if (output_path != NULL) {
        if (cv::imwrite(output_path, heatmap)) {
            printf("Advanced heatmap saved: %s\n", output_path);
        } else {
            PyErr_SetString(PyExc_RuntimeError, "Failed to save heatmap");
            return NULL;
        }
    } else {
        // Generate default filename
        char* default_path = get_output_filename(video_path, "_advanced_heatmap", ".jpg");
        if (cv::imwrite(default_path, heatmap)) {
            printf("Advanced heatmap saved: %s\n", default_path);
        }
        free(default_path);
    }
    
    Py_RETURN_NONE;
}

// Initialize real-time processing
PyObject* cor_init_realtime(PyObject* self, PyObject* args) {
    int camera_id = 0;
    
    if (!PyArg_ParseTuple(args, "|i", &camera_id)) {
        return NULL;
    }
    
    int result = init_realtime_processing(camera_id);
    
    if (result == 0) {
        printf("Real-time processing initialized with camera %d\n", camera_id);
        Py_RETURN_TRUE;
    } else {
        PyErr_SetString(PyExc_RuntimeError, "Failed to initialize real-time processing");
        return NULL;
    }
}

// Process real-time frame
PyObject* cor_process_realtime_frame(PyObject* self, PyObject* args) {
    GazePoint gaze_point = process_realtime_frame();
    
    PyObject* result_dict = PyDict_New();
    PyDict_SetItemString(result_dict, "x", PyFloat_FromDouble(gaze_point.x));
    PyDict_SetItemString(result_dict, "y", PyFloat_FromDouble(gaze_point.y));
    PyDict_SetItemString(result_dict, "confidence", PyFloat_FromDouble(gaze_point.confidence));
    PyDict_SetItemString(result_dict, "timestamp", PyFloat_FromDouble(gaze_point.timestamp));
    
    return result_dict;
}

// Cleanup real-time processing
PyObject* cor_cleanup_realtime(PyObject* self, PyObject* args) {
    cleanup_realtime_processing();
    printf("Real-time processing cleaned up\n");
    Py_RETURN_NONE;
}

// Export analysis results
PyObject* cor_export_analysis(PyObject* self, PyObject* args) {
    const char* video_path;
    const char* output_path = NULL;
    
    if (!PyArg_ParseTuple(args, "s|s", &video_path, &output_path)) {
        return NULL;
    }
    
    if (!is_supported_video_format(video_path)) {
        PyErr_SetString(PyExc_ValueError, "Unsupported video format or file not found");
        return NULL;
    }
    
    // Process video to get gaze points
    cv::VideoCapture cap(video_path);
    if (!cap.isOpened()) {
        PyErr_SetString(PyExc_RuntimeError, "Could not open video file");
        return NULL;
    }
    
    std::vector<GazePoint> gaze_points;
    cv::Mat frame;
    
    printf("Processing video for analysis export...\n");
    
    int frame_count = (int)cap.get(cv::CAP_PROP_FRAME_COUNT);
    int processed_frames = 0;
    
    while (cap.read(frame)) {
        processed_frames++;
        
        EyeDetectionResult eye_result = detect_eyes_in_frame(frame);
        if (eye_result.valid) {
            GazePoint gaze_point = calculate_gaze_direction(eye_result);
            if (gaze_point.confidence > 0.5f) {
                gaze_points.push_back(gaze_point);
            }
        }
        
        // Update progress bar every 50 frames
        if (processed_frames % 50 == 0 || processed_frames == frame_count) {
            print_progress_bar(processed_frames, frame_count, "Analysis export", "frames processed");
        }
    }
    
    cap.release();
    
    if (gaze_points.empty()) {
        PyErr_SetString(PyExc_RuntimeError, "No valid gaze points found for export");
        return NULL;
    }
    
    // Determine output path
    char* export_path;
    if (output_path != NULL) {
        export_path = strdup(output_path);
    } else {
        export_path = get_output_filename(video_path, "_analysis", ".json");
    }
    
    // Export to JSON using C-compatible wrapper
    int result = export_analysis_to_json_wrapper(video_path, export_path);
    
    if (result == 0) {
        printf("Analysis exported to: %s\n", export_path);
        PyObject* result_str = PyUnicode_FromString(export_path);
        free(export_path);
        return result_str;
    } else {
        free(export_path);
        PyErr_SetString(PyExc_RuntimeError, "Failed to export analysis");
        return NULL;
    }
}