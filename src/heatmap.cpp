#include "cor.h"
#include <opencv2/opencv.hpp>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

using namespace cv;

// Heatmap generation configuration
static HeatmapConfig heatmap_config = {
    "sequential_blue", 1.0f, 15, 1.0f, 0.6f
};

// Color schemes for heatmaps
static void apply_color_scheme(Mat& heatmap, const char* scheme) {
    Mat colored_heatmap;
    
    if (strcmp(scheme, "sequential_blue") == 0) {
        applyColorMap(heatmap, colored_heatmap, COLORMAP_WINTER);
    } else if (strcmp(scheme, "sequential_red") == 0) {
        applyColorMap(heatmap, colored_heatmap, COLORMAP_HOT);
    } else if (strcmp(scheme, "sequential_green") == 0) {
        applyColorMap(heatmap, colored_heatmap, COLORMAP_SUMMER);
    } else if (strcmp(scheme, "sequential_purple") == 0) {
        applyColorMap(heatmap, colored_heatmap, COLORMAP_PLASMA);
    } else if (strcmp(scheme, "diverging_blue_red") == 0) {
        applyColorMap(heatmap, colored_heatmap, COLORMAP_COOLWARM);
    } else if (strcmp(scheme, "diverging_green_red") == 0) {
        applyColorMap(heatmap, colored_heatmap, COLORMAP_RAINBOW);
    } else if (strcmp(scheme, "diverging_blue_yellow") == 0) {
        applyColorMap(heatmap, colored_heatmap, COLORMAP_VIRIDIS);
    } else if (strcmp(scheme, "categorical_5") == 0) {
        applyColorMap(heatmap, colored_heatmap, COLORMAP_PARULA);
    } else if (strcmp(scheme, "categorical_7") == 0) {
        applyColorMap(heatmap, colored_heatmap, COLORMAP_TURBO);
    } else if (strcmp(scheme, "rainbow") == 0) {
        applyColorMap(heatmap, colored_heatmap, COLORMAP_JET);
    } else {
        // Default to blue
        applyColorMap(heatmap, colored_heatmap, COLORMAP_WINTER);
    }
    
    heatmap = colored_heatmap;
}

// Generate 2D Gaussian kernel for density estimation
static Mat create_gaussian_kernel(int radius, float sigma) {
    int size = 2 * radius + 1;
    Mat kernel(size, size, CV_32F);
    
    float sum = 0.0f;
    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            float value = exp(-(x*x + y*y) / (2.0f * sigma * sigma));
            kernel.at<float>(y + radius, x + radius) = value;
            sum += value;
        }
    }
    
    // Normalize kernel
    kernel /= sum;
    return kernel;
}

// Generate heatmap from gaze points using Gaussian density estimation
Mat generate_heatmap(std::vector<GazePoint> gaze_points, int width, int height, HeatmapConfig config) {
    // Create heatmap matrix
    int heatmap_width = (int)(width * config.resolution_factor);
    int heatmap_height = (int)(height * config.resolution_factor);
    Mat heatmap = Mat::zeros(heatmap_height, heatmap_width, CV_32F);
    
    if (gaze_points.empty()) {
        log_message("WARNING", "No gaze points provided for heatmap generation");
        Mat colored_heatmap;
        heatmap.convertTo(colored_heatmap, CV_8UC3);
        return colored_heatmap;
    }
    
    // Create Gaussian kernel for density estimation
    float sigma = config.blur_radius / 3.0f; // Standard deviation
    Mat kernel = create_gaussian_kernel(config.blur_radius, sigma);
    
    // Accumulate gaze points with progress tracking
    int total_points = gaze_points.size();
    int processed_points = 0;
    
    for (const auto& gaze_point : gaze_points) {
        processed_points++;
        
        if (gaze_point.confidence < 0.5f) {
            // Update progress even for skipped points
            if (processed_points % 100 == 0 || processed_points == total_points) {
                print_progress_bar(processed_points, total_points, "Heatmap generation", "gaze points processed");
            }
            continue; // Skip low-confidence points
        }
        
        // Convert normalized coordinates to heatmap coordinates
        int x = (int)(gaze_point.x * heatmap_width);
        int y = (int)(gaze_point.y * heatmap_height);
        
        // Ensure coordinates are within bounds
        if (x < 0 || x >= heatmap_width || y < 0 || y >= heatmap_height) {
            // Update progress even for out-of-bounds points
            if (processed_points % 100 == 0 || processed_points == total_points) {
                print_progress_bar(processed_points, total_points, "Heatmap generation", "gaze points processed");
            }
            continue;
        }
        
        // Add Gaussian blob at gaze point location
        int kernel_radius = config.blur_radius;
        for (int ky = -kernel_radius; ky <= kernel_radius; ky++) {
            for (int kx = -kernel_radius; kx <= kernel_radius; kx++) {
                int hx = x + kx;
                int hy = y + ky;
                
                if (hx >= 0 && hx < heatmap_width && hy >= 0 && hy < heatmap_height) {
                    float kernel_value = kernel.at<float>(ky + kernel_radius, kx + kernel_radius);
                    float weighted_value = kernel_value * gaze_point.confidence * config.intensity_multiplier;
                    heatmap.at<float>(hy, hx) += weighted_value;
                }
            }
        }
        
        // Update progress bar every 100 points or at the end
        if (processed_points % 100 == 0 || processed_points == total_points) {
            print_progress_bar(processed_points, total_points, "Heatmap generation", "gaze points processed");
        }
    }
    
    // Normalize heatmap to 0-255 range
    double min_val, max_val;
    minMaxLoc(heatmap, &min_val, &max_val);
    
    if (max_val > 0) {
        heatmap = (heatmap - min_val) / (max_val - min_val) * 255.0f;
    }
    
    // Convert to 8-bit
    Mat heatmap_8bit;
    heatmap.convertTo(heatmap_8bit, CV_8U);
    
    // Apply color scheme
    Mat colored_heatmap;
    apply_color_scheme(heatmap_8bit, config.color_scheme);
    
    // Resize back to original dimensions if needed
    if (config.resolution_factor != 1.0f) {
        Mat resized_heatmap;
        resize(colored_heatmap, resized_heatmap, Size(width, height), 0, 0, INTER_LINEAR);
        colored_heatmap = resized_heatmap;
    }
    
    return colored_heatmap;
}

// Create heatmap overlay on a background image
Mat create_heatmap_overlay(Mat background, Mat heatmap, float alpha) {
    if (background.size() != heatmap.size()) {
        resize(heatmap, heatmap, background.size());
    }
    
    Mat overlay;
    addWeighted(background, 1.0f - alpha, heatmap, alpha, 0, overlay);
    
    return overlay;
}

// Save heatmap as image file
int save_heatmap_image(Mat heatmap, const char* filename) {
    if (heatmap.empty()) {
        log_message("ERROR", "Cannot save empty heatmap");
        return -1;
    }
    
    bool success = imwrite(filename, heatmap);
    if (success) {
        printf("Heatmap saved: %s\n", filename);
        return 0;
    } else {
        log_message("ERROR", "Failed to save heatmap image");
        return -1;
    }
}

// Generate attention map (alternative visualization)
Mat generate_attention_map(std::vector<GazePoint> gaze_points, int width, int height) {
    Mat attention_map = Mat::zeros(height, width, CV_32F);
    
    if (gaze_points.empty()) return attention_map;
    
    // Create attention regions based on gaze clustering with progress tracking
    int total_points = gaze_points.size();
    int processed_points = 0;
    
    for (const auto& gaze_point : gaze_points) {
        processed_points++;
        
        if (gaze_point.confidence < 0.6f) {
            // Update progress even for skipped points
            if (processed_points % 100 == 0 || processed_points == total_points) {
                print_progress_bar(processed_points, total_points, "Attention map", "gaze points processed");
            }
            continue;
        }
        
        int x = (int)(gaze_point.x * width);
        int y = (int)(gaze_point.y * height);
        
        if (x >= 0 && x < width && y >= 0 && y < height) {
            // Create circular attention region
            int radius = 30; // Attention region radius
            for (int dy = -radius; dy <= radius; dy++) {
                for (int dx = -radius; dx <= radius; dx++) {
                    int nx = x + dx;
                    int ny = y + dy;
                    
                    if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                        float distance = sqrt(dx*dx + dy*dy);
                        if (distance <= radius) {
                            float weight = (1.0f - distance / radius) * gaze_point.confidence;
                            attention_map.at<float>(ny, nx) += weight;
                        }
                    }
                }
            }
        }
        
        // Update progress bar every 100 points or at the end
        if (processed_points % 100 == 0 || processed_points == total_points) {
            print_progress_bar(processed_points, total_points, "Attention map", "gaze points processed");
        }
    }
    
    // Normalize and convert to color
    normalize(attention_map, attention_map, 0, 255, NORM_MINMAX);
    
    Mat attention_8bit, colored_attention;
    attention_map.convertTo(attention_8bit, CV_8U);
    applyColorMap(attention_8bit, colored_attention, COLORMAP_HOT);
    
    return colored_attention;
}

// Load general configuration including heatmap settings
int load_general_config(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        log_message("WARNING", "General config file not found, using defaults");
        return 0; // Use defaults
    }
    
    char line[256];
    while (fgets(line, sizeof(line), file)) {
        // Skip comments and empty lines
        if (line[0] == '#' || line[0] == '\n') continue;
        
        char key[128], value[128];
        if (sscanf(line, "%127[^=]=%127s", key, value) == 2) {
            if (strcmp(key, "heatmap_color_scheme") == 0) {
                strncpy(heatmap_config.color_scheme, value, sizeof(heatmap_config.color_scheme) - 1);
                heatmap_config.color_scheme[sizeof(heatmap_config.color_scheme) - 1] = '\0';
            } else if (strcmp(key, "heatmap_intensity_multiplier") == 0) {
                heatmap_config.intensity_multiplier = atof(value);
            } else if (strcmp(key, "heatmap_blur_radius") == 0) {
                heatmap_config.blur_radius = atoi(value);
            } else if (strcmp(key, "heatmap_resolution_factor") == 0) {
                heatmap_config.resolution_factor = atof(value);
            } else if (strcmp(key, "heatmap_alpha_transparency") == 0) {
                heatmap_config.alpha_transparency = atof(value);
            }
        }
    }
    
    fclose(file);
    log_message("INFO", "General configuration loaded");
    return 0;
}

// Get current heatmap configuration
HeatmapConfig get_heatmap_config() {
    return heatmap_config;
}