# Cor - Advanced Gaze Detection Library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)](https://opencv.org/)

Cor is a comprehensive Python library for gaze detection and eye tracking in video files. It provides automatic calibration capabilities, professional heatmap generation, and comprehensive visualization tools for gaze analysis. The library works entirely in Python using OpenCV and matplotlib, making it easy to install and use across all platforms.

## Features

- **Multi-format Video Support**: Process various video file formats (MP4, AVI, MOV, MKV, etc.)
- **Automatic Calibration**: Intelligent calibration for eye detection and gaze direction
- **Professional Heatmap Generation**: High-quality heatmaps with multiple color schemes
- **Video Visualization**: Create gaze tracking videos with overlay graphics
- **Face and Eye Detection**: Robust detection using OpenCV Haar cascades
- **Gaze Estimation**: Advanced gaze direction calculation from eye positions
- **Progress Tracking**: Real-time progress updates during video processing
- **Easy Installation**: Pure Python implementation - no C++ compilation required
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Flexible Configuration**: Extensive customization through configuration files

## Installation

### Prerequisites

- Python 3.7 or higher
- OpenCV 4.5 or higher
- NumPy 1.19 or higher

### Install from PyPI

```bash
pip install cor
```

### Install from Source

```bash
git clone https://github.com/victorcynzo/cor
cd cor
pip install -e .
```

## Command Line Usage

```bash
# Get help
python -c "import cor; cor.help()"

# Run gaze detection
python -c "import cor; cor.run('video.mp4')"

# Run with visualization
python -c "import cor; cor.run('video.mp4', '--visualize')"
```

## Quick Start

```python
import cor

# Display help and available functions
cor.help()

# Basic gaze detection (creates heatmaps)
cor.run("video.mp4")

# With visualization video
cor.run("video.mp4", "--visualize")

# Automatic calibration
cor.calibrate_eyes("video.mp4")
cor.calibrate_gaze("video.mp4")

# Check version and status
print(cor.version())
```

## Output Files

When you run `cor.run("video.mp4")`, the library creates:

- **`video_heatmap-pure.jpg`** - Pure heatmap visualization showing gaze intensity
- **`video_heatmap-overlay.jpg`** - Heatmap overlaid on the 10th frame of the video

When you run `cor.run("video.mp4", "--visualize")`, it additionally creates:

- **`video_heatmap.mp4`** - Full video with gaze tracking visualization (green circles and yellow lines)

## Core Functions

### `cor.help()`
Displays comprehensive help information about all available functions.

### `cor.run(video_file, *args)`
Performs complete gaze detection analysis:
- Detects faces and eyes in each frame
- Calculates gaze direction from eye positions
- Generates professional heatmaps
- Creates visualization video (with `--visualize` flag)
- Shows processing progress

### `cor.calibrate_eyes(video_file)`
Automatic eye detection calibration:
- Analyzes video frames for optimal detection parameters
- Tests detection success rate
- Saves calibration to `eye-detection-values.txt`
- Provides feedback on detection quality

### `cor.calibrate_gaze(video_file)`
Automatic gaze direction calibration:
- Analyzes gaze patterns across video frames
- Calculates optimal gaze estimation parameters
- Saves calibration to `gaze-direction-values.txt`
- Reports average gaze positions

### `cor.version()`
Returns version information and system status:
```python
{
    'version': '1.0.2',
    'mode': 'Python fallback',
    'c_extension': False,
    'opencv_available': True
}
```

## How It Works

1. **Face Detection**: Uses OpenCV Haar cascades to detect faces in video frames
2. **Eye Detection**: Locates eyes within detected face regions
3. **Gaze Estimation**: Calculates gaze direction based on eye center positions
4. **Heatmap Generation**: Creates Gaussian-based density maps using matplotlib
5. **Visualization**: Overlays gaze tracking graphics on video frames

## Configuration

The library uses three configuration files for customization:

- **`eye-detection-values.txt`** - Eye detection parameters
- **`gaze-direction-values.txt`** - Gaze calibration settings
- **`cor.txt`** - General configuration and heatmap options

## Supported Video Formats

- MP4, AVI, MOV, MKV, WMV, FLV, WEBM
- Automatic format detection and validation
- Various codecs: H.264, H.265, VP8, VP9, etc.

## Example Workflow

```python
import cor

# Step 1: Calibrate for your specific video (optional but recommended)
cor.calibrate_eyes("sample_video.mp4")
cor.calibrate_gaze("sample_video.mp4")

# Step 2: Run basic analysis
cor.run("sample_video.mp4")

# Step 3: Create visualization video
cor.run("sample_video.mp4", "--visualize")

# Step 4: Check results
# - sample_video_heatmap-pure.jpg
# - sample_video_heatmap-overlay.jpg  
# - sample_video_heatmap.mp4
```

## Batch Processing

```python
import cor
import os

video_files = ["video1.mp4", "video2.avi", "video3.mov"]

for video in video_files:
    if os.path.exists(video):
        print(f"Processing {video}...")
        cor.run(video, "--visualize")
        print(f"Completed: {video}")
```

## Technical Details

### Algorithms Used
- **Face Detection**: OpenCV Haar Cascade Classifiers
- **Eye Detection**: Haar Cascade with region-of-interest optimization
- **Gaze Estimation**: Eye center triangulation with forward projection
- **Heatmap Generation**: Gaussian kernel density estimation
- **Video Processing**: OpenCV VideoCapture and VideoWriter

### Performance
- **Processing Speed**: ~30-60 FPS on modern hardware
- **Memory Usage**: Efficient frame-by-frame processing
- **Output Quality**: High-resolution heatmaps and smooth video visualization

## Installation Notes

This library uses a pure Python implementation that works out-of-the-box with standard packages:
- No C++ compilation required
- No complex dependencies
- Works with standard `opencv-python` package
- Cross-platform compatibility

## Basic gaze detection
cor.run("video.mp4")

# With visualization
cor.run("video.mp4", "--visualize")

# Interactive calibration
cor.calibrate_eyes("video.mp4")
cor.calibrate_gaze("video.mp4")

# Advanced analysis
analysis = cor.analyze_attention("video.mp4")
cor.generate_advanced_heatmap("video.mp4", "fixation")
cor.export_analysis("video.mp4", "results.json")

# Real-time processing
cor.init_realtime(0)  # Camera 0
gaze_data = cor.process_realtime_frame()
cor.cleanup_realtime()
```

## Command Line Usage

```bash
# Get help
python -c "import cor; cor.help()"

# Run gaze detection
python -c "import cor; cor.run('video.mp4')"

# Run with visualization
python -c "import cor; cor.run('video.mp4', '--visualize')"
```

## Core Functions

### `cor.help()`
Displays all available commands and their descriptions.

### `cor.calibrate_eyes(video_file)`
Opens an interactive calibration window for eye detection:
- Shows 20 frames from the video sequentially
- Allows manual adjustment of detection boundaries around eyes and pupils
- Saves calibration values to `eye-detection-values.txt`
- Handles existing calibration data with overwrite/merge options

### `cor.calibrate_gaze(video_file)`
Opens an interactive calibration window for gaze direction:
- Shows 20 frames from the video sequentially
- Provides visual gaze direction adjustment with green indicator and pupil lines
- Saves calibration values to `gaze-direction-values.txt`
- Handles existing calibration data with overwrite/merge options

### `cor.run(video_file, *args)`
Performs gaze detection analysis on the specified video:

**Standard Output:**
- `{videoname}_heatmap-pure.jpg`: Pure heatmap visualization
- `{videoname}_heatmap-overlay.jpg`: Heatmap overlaid on 10th frame

**With `--visualize` flag:**
- `{videoname}_heatmap.{ext}`: Full video with gaze visualization overlay

## Configuration

Cor uses several configuration files for customization:

- **`eye-detection-values.txt`**: Eye detection parameters
- **`gaze-direction-values.txt`**: Gaze calibration settings  
- **`cor.txt`**: General configuration and heatmap options

### Heatmap Color Schemes

Available in `cor.txt`:

1. **Sequential Numerical**: Single color gradient (default: blue)
2. **Diverging Numerical**: Two-color gradient (default: blue to red)
3. **Multi-color**: 5 or 7 color categorical schemes

## Supported Video Formats

- MP4, AVI, MOV, MKV, WMV, FLV, WEBM
- Various codecs: H.264, H.265, VP8, VP9, etc.

## Performance

Cor is optimized for performance with:
- Native C++ implementation for core algorithms
- OpenCV integration for efficient video processing
- Multi-threaded processing capabilities
- Memory-efficient streaming for large video files

## Progress Tracking

All video processing operations include real-time progress bars:
- **Video Processing**: Shows frame-by-frame progress during analysis
- **Calibration**: Tracks progress through calibration frames
- **Attention Analysis**: Displays progress during pattern analysis
- **Heatmap Generation**: Shows processing status for visualization
- **Benchmarking**: Real-time performance measurement progress

Progress bars use Unicode block characters (█) for clear visual feedback and display:
- Current/total frames processed
- Percentage completion
- Operation-specific status messages

## Confidence Assessment

After each gaze detection analysis, Cor automatically evaluates and displays the confidence in its accuracy:

### Assessment Metrics
- **Detection Rate**: Percentage of frames with successful gaze detection
- **Average Confidence**: Mean confidence score across all detected gaze points
- **Confidence Distribution**: Breakdown of high/medium/low confidence detections
- **Overall Accuracy Confidence**: Composite score indicating reliability

### Example Output
```
=== GAZE DETECTION CONFIDENCE ASSESSMENT ===
📊 Analysis Results:
   • Total frames processed: 1500
   • Valid gaze points detected: 1342
   • Detection rate: 89.5%
   • Average confidence per point: 76.3%

📈 Confidence Distribution:
   • High confidence (≥80%): 892 points (66.5%)
   • Medium confidence (60-79%): 321 points (23.9%)
   • Low confidence (<60%): 129 points (9.6%)

🎯 Overall Accuracy Confidence: 82.4%
✅ Excellent - High reliability for research and analysis
============================================
```

### Confidence Levels
- **85%+**: Excellent - High reliability for research and analysis
- **70-84%**: Good - Suitable for most applications
- **55-69%**: Fair - Consider recalibration for better accuracy
- **<55%**: Poor - Recalibration strongly recommended

## Examples

### Basic Workflow

```python
import cor

# Step 1: Calibrate eye detection (optional)
cor.calibrate_eyes("sample_video.mp4")

# Step 2: Calibrate gaze detection (optional)  
cor.calibrate_gaze("sample_video.mp4")

# Step 3: Run analysis
cor.run("sample_video.mp4")

# Step 4: Run with visualization
cor.run("sample_video.mp4", "--visualize")
```

### Batch Processing

```python
import cor
import os

video_files = ["video1.mp4", "video2.avi", "video3.mov"]

for video in video_files:
    if os.path.exists(video):
        cor.run(video, "--visualize")
        print(f"Processed: {video}")
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Cor in your research, please cite:

```bibtex
@software{cor_gaze_detection,
  title={Cor: Advanced Gaze Detection Library},
  author={Cor Development Team},
  year={2024},
  url={https://github.com/cor-team/cor}
}
```

## Support

- **Documentation**: [Full Documentation](https://cor-gaze.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/cor-team/cor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cor-team/cor/discussions)

## Changelog

### v1.0.1
- Added comprehensive progress bars for all video processing operations
- Implemented confidence assessment system with detailed accuracy metrics
- Enhanced heatmap generation with real-time progress tracking
- Improved user experience with visual feedback during processing
- Added confidence distribution analysis and interpretation

### v1.0.0
- Initial release
- Core gaze detection functionality
- Interactive calibration tools
- Heatmap generation with multiple color schemes
- Multi-format video support