from setuptools import setup, Extension
import numpy

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
        numpy.get_include(),
        'include',
        '/usr/include/opencv4',
        '/usr/local/include/opencv4'
    ],
    libraries=['opencv_core', 'opencv_imgproc', 'opencv_highgui', 'opencv_videoio', 'opencv_objdetect'],
    library_dirs=['/usr/lib', '/usr/local/lib'],
    extra_compile_args=['-std=c++11', '-O3']
)

setup(
    name='cor',
    version='1.0.0',
    description='Advanced gaze detection library for video analysis',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Cor Development Team',
    author_email='contact@cor-gaze.com',
    url='https://github.com/cor-team/cor',
    ext_modules=[cor_module],
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