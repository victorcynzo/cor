from setuptools import setup, find_packages

# Pure Python implementation - no C++ extensions

setup(
    name='cor',
    version='1.0.4',
    description='Advanced gaze detection library for video analysis',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Cor Development Team',
    author_email='contact@cor-gaze.com',
    url='https://github.com/cor-team/cor',
    packages=find_packages(),


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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Image Processing',
        'Topic :: Multimedia :: Video'
    ],
    keywords='gaze detection, eye tracking, computer vision, video analysis',
    entry_points={
        'console_scripts': [
            'cor=cor:cli',
        ],
    },
)