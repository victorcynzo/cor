#!/usr/bin/env python3
"""
Project validation script for Cor Gaze Detection Library
Checks for missing files, broken references, and potential issues
"""

import os
import re
from pathlib import Path

def check_file_exists(filepath, description=""):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {filepath} {description}")
        return True
    else:
        print(f"✗ Missing: {filepath} {description}")
        return False

def check_c_includes():
    """Check C include statements and function references"""
    print("\nChecking C code includes and references...")
    
    c_files = list(Path('src').glob('*.c')) + list(Path('src').glob('*.cpp')) + list(Path('include').glob('*.h'))
    issues = []
    
    for c_file in c_files:
        with open(c_file, 'r') as f:
            content = f.read()
            
        # Check for common include issues
        if '#include <opencv2/opencv.hpp>' in content:
            if '#include <opencv2/highgui.hpp>' not in content and 'highgui' in content:
                issues.append(f"{c_file}: Missing highgui include")
            if '#include <opencv2/videoio.hpp>' not in content and 'VideoCapture' in content:
                issues.append(f"{c_file}: Missing videoio include")
        
        # Check for function declarations vs implementations
        if c_file.suffix == '.c':
            functions = re.findall(r'(\w+)\s*\([^)]*\)\s*{', content)
            for func in functions:
                if func not in ['main', 'if', 'for', 'while', 'switch']:
                    print(f"  Function found in {c_file}: {func}")
    
    if issues:
        for issue in issues:
            print(f"⚠️  {issue}")
    else:
        print("✓ C code includes look good")

def check_python_imports():
    """Check Python import statements"""
    print("\nChecking Python imports...")
    
    py_files = [f for f in Path('.').glob('*.py') if f.name != 'validate_project.py']
    
    for py_file in py_files:
        try:
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Look for import statements
            imports = re.findall(r'import\s+(\w+)', content)
            from_imports = re.findall(r'from\s+(\w+)\s+import', content)
            
            all_imports = imports + from_imports
            if all_imports:
                print(f"  {py_file}: {', '.join(set(all_imports))}")
                
        except Exception as e:
            print(f"⚠️  Could not read {py_file}: {e}")

def check_config_references():
    """Check configuration file references"""
    print("\nChecking configuration file references...")
    
    config_files = ['eye-detection-values.txt', 'gaze-direction-values.txt', 'cor.txt']
    
    for config_file in config_files:
        if check_file_exists(config_file):
            with open(config_file, 'r') as f:
                lines = f.readlines()
            
            param_count = sum(1 for line in lines if '=' in line and not line.strip().startswith('#'))
            print(f"  {config_file}: {param_count} parameters")

def check_documentation_consistency():
    """Check documentation consistency"""
    print("\nChecking documentation consistency...")
    
    doc_files = ['README.md', 'Documentation.txt']
    
    for doc_file in doc_files:
        if check_file_exists(doc_file):
            with open(doc_file, 'r') as f:
                content = f.read()
            
            # Check for function mentions
            functions = ['cor.help', 'cor.calibrate_eyes', 'cor.calibrate_gaze', 'cor.run']
            for func in functions:
                if func in content:
                    print(f"  {doc_file}: ✓ {func} documented")
                else:
                    print(f"  {doc_file}: ⚠️  {func} not found")

def check_setup_py():
    """Check setup.py configuration"""
    print("\nChecking setup.py...")
    
    if check_file_exists('setup.py'):
        with open('setup.py', 'r') as f:
            content = f.read()
        
        # Check for required sections
        required_sections = ['name=', 'version=', 'ext_modules=', 'install_requires=']
        for section in required_sections:
            if section in content:
                print(f"  ✓ {section} found")
            else:
                print(f"  ⚠️  {section} missing")

def main():
    """Run all validation checks"""
    print("Cor Gaze Detection Library - Project Validation")
    print("=" * 60)
    
    # Check core files
    print("\nChecking core files...")
    core_files = [
        ('setup.py', '- Python package setup'),
        ('README.md', '- Main documentation'),
        ('Documentation.txt', '- Technical documentation'),
        ('LICENSE', '- License file'),
        ('requirements.txt', '- Runtime dependencies'),
        ('requirements-dev.txt', '- Development dependencies'),
        ('Makefile', '- Build automation'),
    ]
    
    missing_core = 0
    for filepath, desc in core_files:
        if not check_file_exists(filepath, desc):
            missing_core += 1
    
    # Check configuration files
    print("\nChecking configuration files...")
    config_files = [
        ('eye-detection-values.txt', '- Eye detection parameters'),
        ('gaze-direction-values.txt', '- Gaze direction parameters'),
        ('cor.txt', '- General configuration'),
    ]
    
    missing_config = 0
    for filepath, desc in config_files:
        if not check_file_exists(filepath, desc):
            missing_config += 1
    
    # Check source code
    print("\nChecking source code...")
    src_files = [
        ('include/cor.h', '- Main header file'),
        ('src/cor_module.cpp', '- Python module interface'),
        ('src/eye_detection.cpp', '- Eye detection implementation'),
        ('src/gaze_detection.cpp', '- Gaze detection implementation'),
        ('src/calibration.cpp', '- Calibration interface'),
        ('src/heatmap.cpp', '- Heatmap generation'),
        ('src/video_processing.cpp', '- Video processing'),
    ]
    
    missing_src = 0
    for filepath, desc in src_files:
        if not check_file_exists(filepath, desc):
            missing_src += 1
    
    # Check test and build files
    print("\nChecking test and build files...")
    test_files = [
        ('test_cor.py', '- Test suite'),
        ('build_and_test.py', '- Build automation'),
        ('validate_project.py', '- This validation script'),
    ]
    
    missing_test = 0
    for filepath, desc in test_files:
        if not check_file_exists(filepath, desc):
            missing_test += 1
    
    # Run additional checks
    check_c_includes()
    check_python_imports()
    check_config_references()
    check_documentation_consistency()
    check_setup_py()
    
    # Summary
    total_missing = missing_core + missing_config + missing_src + missing_test
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if total_missing == 0:
        print("🎉 All files present and project structure looks good!")
        print("\nNext steps:")
        print("1. Run: python build_and_test.py")
        print("2. Or run: make auto")
        print("3. Check build output for any compilation issues")
        return 0
    else:
        print(f"⚠️  {total_missing} files missing or issues found")
        print("\nPlease address the missing files before building.")
        return 1

if __name__ == "__main__":
    exit(main())