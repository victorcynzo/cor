#!/usr/bin/env python3
"""
Build and test script for Cor Gaze Detection Library
This script handles the complete build, installation, and testing process
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path

def run_command(cmd, description="", check=True):
    """Run a command and handle errors"""
    print(f"Running: {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("Checking dependencies...")
    
    dependencies = {
        'python': 'python --version',
        'pip': 'pip --version',
        'opencv': 'python -c "import cv2; print(f\'OpenCV {cv2.__version__}\')"',
        'numpy': 'python -c "import numpy; print(f\'NumPy {numpy.__version__}\')"',
    }
    
    missing = []
    for name, cmd in dependencies.items():
        if not run_command(cmd, f"Checking {name}", check=False):
            missing.append(name)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Please install missing dependencies before continuing.")
        return False
    
    print("✓ All dependencies are available")
    return True

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '*.egg-info', '__pycache__']
    files_to_clean = ['*.so', '*.pyd', '*.pyc']
    
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                print(f"Removed directory: {path}")
    
    for pattern in files_to_clean:
        for path in Path('.').rglob(pattern):
            if path.is_file():
                path.unlink()
                print(f"Removed file: {path}")

def install_package():
    """Install the Python package"""
    print("Installing Python package...")
    
    # Try different installation approaches
    install_commands = [
        "pip install -e .",
        "python -m pip install -e .",
        "python setup.py install"
    ]
    
    for cmd in install_commands:
        print(f"Trying: {cmd}")
        if run_command(cmd, check=False):
            print("✓ Build successful")
            return True
        print(f"Build command failed: {cmd}")
    
    print("✗ All build attempts failed")
    return False

def run_tests():
    """Run the test suite"""
    print("Running test suite...")
    
    if not os.path.exists('test_cor.py'):
        print("✗ Test file not found")
        return False
    
    return run_command("python test_cor.py", "Running tests")

def create_example_usage():
    """Create example usage script"""
    example_code = '''#!/usr/bin/env python3
"""
Example usage of Cor Gaze Detection Library
"""

import cor
import tempfile
import os

def main():
    print("Cor Gaze Detection Library - Example Usage")
    print("=" * 50)
    
    # Display help
    print("\\n1. Getting Help:")
    cor.help()
    
    # Show version
    print("\\n2. Version Information:")
    version = cor.version()
    print(f"Version: {version}")
    
    # Configuration example
    print("\\n3. Configuration Example:")
    cor.set_config("example_param", "example_value")
    value = cor.get_config("example_param")
    print(f"Set and retrieved config value: {value}")
    
    print("\\n4. For video processing:")
    print("   - Create a video file (MP4, AVI, MOV, etc.)")
    print("   - Run: cor.calibrate_eyes('your_video.mp4')")
    print("   - Run: cor.calibrate_gaze('your_video.mp4')")
    print("   - Run: cor.run('your_video.mp4', '--visualize')")
    
    print("\\nExample completed successfully!")

if __name__ == "__main__":
    main()
'''
    
    with open('example_usage.py', 'w') as f:
        f.write(example_code)
    
    print("✓ Created example_usage.py")

def main():
    """Main build and test process"""
    print("Cor Gaze Detection Library - Build and Test")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('setup.py'):
        print("✗ setup.py not found. Please run this script from the project root.")
        return 1
    
    # Step 1: Check dependencies
    if not check_dependencies():
        return 1
    
    # Step 2: Clean previous builds
    clean_build()
    
    # Step 3: Install package
    if not install_package():
        print("\\n" + "=" * 60)
        print("INSTALLATION FAILED")
        print("=" * 60)
        print("Possible solutions:")
        print("1. Install OpenCV development headers:")
        print("   Ubuntu/Debian: sudo apt-get install libopencv-dev")
        print("   CentOS/RHEL: sudo yum install opencv-devel")
        print("   macOS: brew install opencv")
        print("   Windows: Install OpenCV manually")
        print("2. Install required Python packages:")
        print("   pip install -r requirements-dev.txt")
        print("3. Check Python installation and permissions")
        return 1
    
    # Step 4: Run tests
    if not run_tests():
        print("\\n" + "=" * 60)
        print("TESTS FAILED")
        print("=" * 60)
        print("The library built but some tests failed.")
        print("Check the test output above for details.")
        return 1
    
    # Step 5: Create example
    create_example_usage()
    
    # Success!
    print("\\n" + "=" * 60)
    print("BUILD AND TEST SUCCESSFUL! 🎉")
    print("=" * 60)
    print("Next steps:")
    print("1. Run: python example_usage.py")
    print("2. Try with your own video: cor.run('your_video.mp4')")
    print("3. Read Documentation.txt for detailed usage")
    print("4. Check cor.txt for configuration options")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())