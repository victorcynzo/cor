#!/usr/bin/env python3
"""
Structure and documentation test for Cor Gaze Detection Library
Tests the project structure and documentation without requiring compilation
"""

import os
import sys
from pathlib import Path

def test_file_structure():
    """Test if all required files are present"""
    print("Testing project file structure...")
    
    required_files = [
        # Core files
        "setup.py",
        "README.md", 
        "Documentation.txt",
        "LICENSE",
        "requirements.txt",
        "requirements-dev.txt",
        "Makefile",
        
        # Configuration files
        "eye-detection-values.txt",
        "gaze-direction-values.txt", 
        "cor.txt",
        
        # Source code
        "include/cor.h",
        "src/cor_module.c",
        "src/eye_detection.c",
        "src/gaze_detection.c",
        "src/calibration.c",
        "src/heatmap.c",
        "src/video_processing.c",
        "src/advanced_features.c",
        
        # Test and build files
        "test_cor.py",
        "build_and_test.py",
        "validate_project.py",
        "example_advanced_usage.py",
        "IMPROVEMENTS_SUMMARY.md",
        "kiro-conversation-appendix.txt"
    ]
    
    missing_files = []
    present_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            present_files.append(file_path)
            print(f"✓ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"✗ {file_path}")
    
    print(f"\nFile structure test: {len(present_files)}/{len(required_files)} files present")
    
    if missing_files:
        print("Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    return True

def test_documentation_completeness():
    """Test documentation completeness"""
    print("\nTesting documentation completeness...")
    
    # Check README.md
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            readme_content = f.read()
        
        required_sections = [
            "# Cor - Advanced Gaze Detection Library",
            "## Features",
            "## Installation", 
            "## Quick Start",
            "## Core Functions",
            "## Examples"
        ]
        
        readme_score = 0
        for section in required_sections:
            if section in readme_content:
                print(f"✓ README contains: {section}")
                readme_score += 1
            else:
                print(f"✗ README missing: {section}")
        
        print(f"README completeness: {readme_score}/{len(required_sections)}")
    
    # Check Documentation.txt
    if os.path.exists("Documentation.txt"):
        with open("Documentation.txt", "r", encoding="utf-8") as f:
            doc_content = f.read()
        
        required_functions = [
            "cor.help()",
            "cor.calibrate_eyes(",
            "cor.calibrate_gaze(",
            "cor.run(",
            "cor.version()",
            "cor.analyze_attention(",
            "cor.generate_advanced_heatmap("
        ]
        
        doc_score = 0
        for func in required_functions:
            if func in doc_content:
                print(f"✓ Documentation contains: {func}")
                doc_score += 1
            else:
                print(f"✗ Documentation missing: {func}")
        
        print(f"Documentation completeness: {doc_score}/{len(required_functions)}")
    
    return True

def test_configuration_files():
    """Test configuration file structure"""
    print("\nTesting configuration files...")
    
    config_files = {
        "eye-detection-values.txt": ["eye_cascade_scale_factor", "pupil_detection_threshold"],
        "gaze-direction-values.txt": ["gaze_sensitivity_x", "gaze_smoothing_factor"],
        "cor.txt": ["heatmap_color_scheme", "frame_skip_factor"]
    }
    
    for config_file, expected_params in config_files.items():
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            param_count = 0
            for param in expected_params:
                if param in content:
                    param_count += 1
            
            print(f"✓ {config_file}: {param_count}/{len(expected_params)} key parameters found")
        else:
            print(f"✗ {config_file}: File not found")

def test_source_code_structure():
    """Test source code file structure"""
    print("\nTesting source code structure...")
    
    # Check header file
    if os.path.exists("include/cor.h"):
        with open("include/cor.h", "r", encoding="utf-8") as f:
            header_content = f.read()
        
        required_declarations = [
            "PyObject* cor_help",
            "PyObject* cor_calibrate_eyes", 
            "PyObject* cor_run",
            "typedef struct",
            "EyeDetectionResult",
            "GazePoint"
        ]
        
        header_score = 0
        for declaration in required_declarations:
            if declaration in header_content:
                header_score += 1
        
        print(f"✓ Header file completeness: {header_score}/{len(required_declarations)}")
    
    # Check source files
    source_files = [
        "src/cor_module.c",
        "src/eye_detection.c", 
        "src/gaze_detection.c",
        "src/calibration.c",
        "src/heatmap.c",
        "src/video_processing.c",
        "src/advanced_features.c"
    ]
    
    for src_file in source_files:
        if os.path.exists(src_file):
            file_size = os.path.getsize(src_file)
            print(f"✓ {src_file}: {file_size} bytes")
        else:
            print(f"✗ {src_file}: Missing")

def test_build_system():
    """Test build system files"""
    print("\nTesting build system...")
    
    # Check setup.py
    if os.path.exists("setup.py"):
        with open("setup.py", "r", encoding="utf-8") as f:
            setup_content = f.read()
        
        required_setup_elements = [
            "from setuptools import setup",
            "Extension",
            "name='cor'",
            "ext_modules=",
            "install_requires="
        ]
        
        setup_score = 0
        for element in required_setup_elements:
            if element in setup_content:
                setup_score += 1
        
        print(f"✓ setup.py completeness: {setup_score}/{len(required_setup_elements)}")
    
    # Check requirements files
    req_files = ["requirements.txt", "requirements-dev.txt"]
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
            print(f"✓ {req_file}: {len(lines)} dependencies")
        else:
            print(f"✗ {req_file}: Missing")

def generate_project_summary():
    """Generate a summary of the project"""
    print("\n" + "="*60)
    print("PROJECT SUMMARY")
    print("="*60)
    
    # Count files by category
    categories = {
        "Core Files": ["setup.py", "README.md", "Documentation.txt", "LICENSE"],
        "Configuration": ["eye-detection-values.txt", "gaze-direction-values.txt", "cor.txt"],
        "Source Code": ["include/cor.h"] + [f"src/{f}" for f in os.listdir("src") if f.endswith(".c")],
        "Tests & Build": ["test_cor.py", "build_and_test.py", "validate_project.py", "Makefile"],
        "Examples": ["example_advanced_usage.py", "IMPROVEMENTS_SUMMARY.md"]
    }
    
    total_files = 0
    for category, files in categories.items():
        existing_files = [f for f in files if os.path.exists(f)]
        total_files += len(existing_files)
        print(f"{category}: {len(existing_files)}/{len(files)} files")
    
    print(f"\nTotal project files: {total_files}")
    
    # Calculate total lines of code
    code_files = []
    if os.path.exists("include"):
        code_files.extend([f"include/{f}" for f in os.listdir("include") if f.endswith(".h")])
    if os.path.exists("src"):
        code_files.extend([f"src/{f}" for f in os.listdir("src") if f.endswith(".c")])
    
    total_lines = 0
    for code_file in code_files:
        if os.path.exists(code_file):
            with open(code_file, "r", encoding="utf-8") as f:
                lines = len(f.readlines())
                total_lines += lines
    
    print(f"Total lines of C code: {total_lines}")
    
    # Check Python files
    python_files = [f for f in os.listdir(".") if f.endswith(".py")]
    python_lines = 0
    for py_file in python_files:
        with open(py_file, "r", encoding="utf-8") as f:
            python_lines += len(f.readlines())
    
    print(f"Total lines of Python code: {python_lines}")
    print(f"Total lines of code: {total_lines + python_lines}")

def main():
    """Run all structure tests"""
    print("Cor Gaze Detection Library - Structure Test")
    print("="*60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Documentation", test_documentation_completeness),
        ("Configuration Files", test_configuration_files),
        ("Source Code Structure", test_source_code_structure),
        ("Build System", test_build_system)
    ]
    
    passed_tests = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✓ {test_name} test passed")
            else:
                print(f"⚠ {test_name} test completed with warnings")
        except Exception as e:
            print(f"✗ {test_name} test failed: {e}")
    
    generate_project_summary()
    
    print("\n" + "="*60)
    print("STRUCTURE TEST RESULTS")
    print("="*60)
    print(f"Tests completed: {passed_tests}/{len(tests)}")
    
    if passed_tests == len(tests):
        print("🎉 All structure tests passed!")
        print("\nThe Cor Gaze Detection Library project structure is complete and well-organized.")
        print("\nNext steps:")
        print("1. Install OpenCV development headers for your platform")
        print("2. Run: python build_and_test.py (after OpenCV setup)")
        print("3. Or test individual components as needed")
        return 0
    else:
        print("⚠ Some structure tests had issues.")
        print("Please review the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())