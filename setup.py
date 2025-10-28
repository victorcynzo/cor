from setuptools import setup, Extension, find_packages
import sys
import os

def get_numpy_include():
    try:
        import numpy
        return numpy.get_include()
    except ImportError:
        # If numpy is not installed, return empty string
        # setuptools will handle the dependency
        return ""

def get_opencv_info():
    """Get OpenCV include and library information"""
    try:
        import cv2
        import os
        
        # Get OpenCV installation path
        cv2_path = os.path.dirname(cv2.__file__)
        
        # Common include directories
        include_dirs = []
        library_dirs = []
        libraries = []
        
        if sys.platform == 'win32':
            # Try to find OpenCV headers in opencv-python installation
            possible_include_dirs = [
                os.path.join(cv2_path, 'include'),
                os.path.join(cv2_path, '..', 'include'),
                os.path.join(cv2_path, 'headers'),
                os.path.join(cv2_path, '..', 'headers'),
                # Check site-packages for opencv headers
                os.path.join(os.path.dirname(cv2_path), 'opencv_python.libs', 'include'),
                # Common Windows OpenCV installation paths
                'C:/opencv/build/include',
                'C:/opencv/include',
                'C:/Program Files/opencv/include',
                'C:/Program Files (x86)/opencv/include'
            ]
            
            # Find existing include directories
            for inc_dir in possible_include_dirs:
                if os.path.exists(inc_dir):
                    include_dirs.append(inc_dir)
                    # Also add opencv2 subdirectory if it exists
                    opencv2_dir = os.path.join(inc_dir, 'opencv2')
                    if os.path.exists(opencv2_dir):
                        include_dirs.append(inc_dir)
                        break
            
            # opencv-python usually comes with pre-built libraries
            libraries = []  # opencv-python handles this internally
        else:
            # For Linux/Mac
            include_dirs = ['/usr/include/opencv4', '/usr/local/include/opencv4']
            library_dirs = ['/usr/lib', '/usr/local/lib']
            libraries = ['opencv_core', 'opencv_imgproc', 'opencv_highgui', 'opencv_videoio', 'opencv_objdetect']
            
        return include_dirs, library_dirs, libraries
    except ImportError:
        # Fallback if OpenCV not installed
        if sys.platform == 'win32':
            return [], [], []
        else:
            return ['/usr/include/opencv4'], ['/usr/lib'], ['opencv_core', 'opencv_imgproc', 'opencv_highgui', 'opencv_videoio', 'opencv_objdetect']

def check_opencv_headers():
    """Check if OpenCV headers are available"""
    include_dirs, _, _ = get_opencv_info()
    
    for inc_dir in include_dirs:
        opencv_hpp = os.path.join(inc_dir, 'opencv2', 'opencv.hpp')
        if os.path.exists(opencv_hpp):
            return True
    
    # Also check common header locations
    common_headers = [
        'C:/opencv/build/include/opencv2/opencv.hpp',
        '/usr/include/opencv4/opencv2/opencv.hpp',
        '/usr/local/include/opencv4/opencv2/opencv.hpp'
    ]
    
    for header in common_headers:
        if os.path.exists(header):
            return True
    
    return False

# Get OpenCV configuration
opencv_includes, opencv_lib_dirs, opencv_libs = get_opencv_info()

# Check if we can build the C extension
can_build_extension = check_opencv_headers()

ext_modules = []
if can_build_extension:
    # Define the extension module
    cor_module = Extension(
        'cor',
        sources=[
            'src/cor_module.cpp',
            'src/eye_detection.cpp',
            'src/gaze_detection.cpp',
            'src/calibration.cpp',
            'src/heatmap.cpp',
            'src/video_processing.cpp',
            'src/advanced_features.cpp'
        ],
        include_dirs=[
            get_numpy_include(),
            'include'
        ] + opencv_includes,
        libraries=opencv_libs,
        library_dirs=opencv_lib_dirs,
        extra_compile_args=['/std:c++14' if sys.platform == 'win32' else '-std=c++11'] + 
                           (['/O2'] if sys.platform == 'win32' else ['-O3'])
    )
    ext_modules = [cor_module]
else:
    print("WARNING: OpenCV development headers not found.")
    print("The C extension will not be built. Installing Python-only version.")
    print("To get full functionality, install OpenCV development headers:")
    print("  - Windows: Install opencv-contrib-python or build OpenCV from source")
    print("  - Linux: sudo apt-get install libopencv-dev")
    print("  - macOS: brew install opencv")

setup(
    name='cor',
    version='1.0.2',
    description='Advanced gaze detection library for video analysis',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Cor Development Team',
    author_email='contact@cor-gaze.com',
    url='https://github.com/cor-team/cor',
    packages=find_packages(),
    ext_modules=ext_modules,
    setup_requires=[
        'numpy>=1.19.0'
    ],
    install_requires=[
        'numpy>=1.19.0',
        'opencv-python>=4.5.0',
        'matplotlib>=3.3.0',
        'Pillow>=8.0.0'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Image Processing',
        'Topic :: Multimedia :: Video'
    ],
    keywords='gaze detection, eye tracking, computer vision, video analysis'
)