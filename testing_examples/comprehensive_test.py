#!/usr/bin/env python3
"""
Comprehensive test for Cor Gaze Detection Library
Tests all aspects of the codebase without requiring compilation
"""

import os
import sys
import re
from pathlib import Path

def test_c_syntax():
    """Test C code for syntax issues"""
    print("Testing C code syntax...")
    
    c_files = list(Path('src').glob('*.c')) + list(Path('src').glob('*.cpp')) + list(Path('include').glob('*.h'))
    issues = []
    
    for c_file in c_files:
        with open(c_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check for common C syntax issues
        for i, line in enumerate(lines, 1):
            # Check for missing semicolons (basic check)
            if re.search(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*$', line.strip()):
                if not line.strip().endswith(';') and not line.strip().endswith('{'):
                    if 'typedef' not in line and 'extern' not in line and '#' not in line:
                        issues.append(f"{c_file}:{i}: Possible missing semicolon: {line.strip()}")
            
            # Check for C++ syntax in C files (but allow in .cpp files)
            if c_file.suffix == '.c':
                if 'std::' in line:
                    issues.append(f"{c_file}:{i}: C++ syntax in C file: {line.strip()}")
                if 'namespace' in line:
                    issues.append(f"{c_file}:{i}: C++ namespace in C file: {line.strip()}")
                
                # Check for unmatched braces (basic check) - only for .c files
                open_braces = line.count('{')
                close_braces = line.count('}')
                if open_braces > 1 or close_braces > 1:
                    issues.append(f"{c_file}:{i}: Multiple braces on one line: {line.strip()}")
    
    if issues:
        print("⚠️  C syntax issues found:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"  {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
        return False
    else:
        print("✓ C syntax looks good")
        return True

def test_function_declarations():
    """Test that all functions are properly declared"""
    print("\nTesting function declarations...")
    
    # Read header file
    with open('include/cor.h', 'r', encoding='utf-8') as f:
        header_content = f.read()
    
    # Extract Python function declarations (PyObject* functions)
    python_declarations = re.findall(r'PyObject\*\s+(\w+)\s*\([^)]*\)\s*;', header_content)
    declared_python_functions = set(python_declarations)
    
    # Check Python module functions
    module_file = 'src/cor_module.cpp' if os.path.exists('src/cor_module.cpp') else 'src/cor_module.c'
    with open(module_file, 'r', encoding='utf-8') as f:
        module_content = f.read()
    
    # Extract Python function implementations
    python_functions = re.findall(r'PyObject\*\s+(\w+)\s*\([^)]*\)\s*{', module_content)
    
    missing_declarations = []
    for func in python_functions:
        if func not in declared_python_functions and func != 'PyInit_cor':
            missing_declarations.append(func)
    
    if missing_declarations:
        print("⚠️  Missing Python function declarations:")
        for func in missing_declarations:
            print(f"  {func}")
        return False
    else:
        print("✓ All Python functions properly declared")
        return True

def test_include_consistency():
    """Test include file consistency"""
    print("\nTesting include consistency...")
    
    issues = []
    c_files = list(Path('src').glob('*.c')) + list(Path('src').glob('*.cpp'))
    
    for c_file in c_files:
        with open(c_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required includes
        if 'opencv' in content.lower():
            if '#include <opencv2/opencv.hpp>' not in content:
                issues.append(f"{c_file}: Uses OpenCV but missing main include")
            
            if 'VideoCapture' in content and '#include <opencv2/videoio.hpp>' not in content:
                issues.append(f"{c_file}: Uses VideoCapture but missing videoio include")
            
            if 'imshow' in content and '#include <opencv2/highgui.hpp>' not in content:
                issues.append(f"{c_file}: Uses GUI functions but missing highgui include")
        
        # Check for Python API usage
        if 'PyObject' in content:
            if '#include <Python.h>' not in content and '#include "cor.h"' not in content:
                issues.append(f"{c_file}: Uses Python API but missing Python.h include")
    
    if issues:
        print("⚠️  Include consistency issues:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✓ Include consistency looks good")
        return True

def test_configuration_completeness():
    """Test configuration file completeness"""
    print("\nTesting configuration completeness...")
    
    config_files = {
        'eye-detection-values.txt': [
            'eye_cascade_scale_factor',
            'pupil_detection_threshold',
            'left_eye_offset_x',
            'calibration_video_file'
        ],
        'gaze-direction-values.txt': [
            'gaze_sensitivity_x',
            'gaze_smoothing_factor',
            'min_confidence_threshold',
            'calibration_video_file'
        ],
        'cor.txt': [
            'heatmap_color_scheme',
            'frame_skip_factor',
            'gaze_circle_radius',
            'debug_mode'
        ]
    }
    
    issues = []
    for config_file, required_params in config_files.items():
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_params = []
            for param in required_params:
                if param not in content:
                    missing_params.append(param)
            
            if missing_params:
                issues.append(f"{config_file}: Missing parameters: {', '.join(missing_params)}")
        else:
            issues.append(f"{config_file}: File not found")
    
    if issues:
        print("⚠️  Configuration issues:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✓ Configuration files complete")
        return True

def test_documentation_accuracy():
    """Test documentation accuracy"""
    print("\nTesting documentation accuracy...")
    
    # Check if all documented functions exist in code
    with open('Documentation.txt', 'r', encoding='utf-8') as f:
        doc_content = f.read()
    
    # Extract documented functions
    documented_functions = re.findall(r'cor\.(\w+)\(', doc_content)
    
    # Check against actual Python module functions
    module_file = 'src/cor_module.cpp' if os.path.exists('src/cor_module.cpp') else 'src/cor_module.c'
    with open(module_file, 'r', encoding='utf-8') as f:
        module_content = f.read()
    
    # Extract method definitions
    method_pattern = r'{"(\w+)",\s*cor_\w+,'
    actual_methods = re.findall(method_pattern, module_content)
    
    missing_docs = []
    for method in actual_methods:
        if method not in documented_functions:
            missing_docs.append(method)
    
    extra_docs = []
    for func in documented_functions:
        if func not in actual_methods:
            extra_docs.append(func)
    
    issues = []
    if missing_docs:
        issues.append(f"Functions missing from documentation: {', '.join(missing_docs)}")
    if extra_docs:
        issues.append(f"Functions documented but not implemented: {', '.join(extra_docs)}")
    
    if issues:
        print("⚠️  Documentation accuracy issues:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✓ Documentation accuracy looks good")
        return True

def test_build_system():
    """Test build system configuration"""
    print("\nTesting build system...")
    
    issues = []
    
    # Check setup.py
    if os.path.exists('setup.py'):
        with open('setup.py', 'r', encoding='utf-8') as f:
            setup_content = f.read()
        
        # Check for all source files
        src_files = [f.name for f in Path('src').glob('*.c')]
        for src_file in src_files:
            if src_file not in setup_content:
                issues.append(f"setup.py: Missing source file {src_file}")
        
        # Check for required setup elements
        required_elements = ['name=', 'version=', 'ext_modules=', 'install_requires=']
        for element in required_elements:
            if element not in setup_content:
                issues.append(f"setup.py: Missing {element}")
    else:
        issues.append("setup.py: File not found")
    
    # Check requirements files
    req_files = ['requirements.txt', 'requirements-dev.txt']
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
            if len(lines) == 0:
                issues.append(f"{req_file}: Empty requirements file")
        else:
            issues.append(f"{req_file}: File not found")
    
    if issues:
        print("⚠️  Build system issues:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✓ Build system configuration looks good")
        return True

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST REPORT")
    print("="*60)
    
    # Count files and lines
    total_files = len([f for f in Path('.').rglob('*') if f.is_file() and not f.name.startswith('.')])
    
    c_files = list(Path('src').glob('*.c')) + list(Path('src').glob('*.cpp')) + list(Path('include').glob('*.h'))
    c_lines = sum(len(open(f, 'r', encoding='utf-8').readlines()) for f in c_files)
    
    py_files = [f for f in Path('.').glob('*.py')]
    py_lines = sum(len(open(f, 'r', encoding='utf-8').readlines()) for f in py_files)
    
    print(f"Total files: {total_files}")
    print(f"C/C++ files: {len(c_files)} ({c_lines} lines)")
    print(f"Python files: {len(py_files)} ({py_lines} lines)")
    print(f"Total code lines: {c_lines + py_lines}")
    
    # Check for critical files
    critical_files = [
        'setup.py', 'README.md', 'Documentation.txt',
        'include/cor.h', 'src/cor_module.cpp',
        'eye-detection-values.txt', 'gaze-direction-values.txt', 'cor.txt'
    ]
    
    missing_critical = [f for f in critical_files if not os.path.exists(f)]
    if missing_critical:
        print(f"\n⚠️  Missing critical files: {', '.join(missing_critical)}")
    else:
        print("\n✓ All critical files present")

def main():
    """Run comprehensive tests"""
    print("Cor Gaze Detection Library - Comprehensive Test")
    print("="*60)
    
    tests = [
        ("C Syntax", test_c_syntax),
        ("Function Declarations", test_function_declarations),
        ("Include Consistency", test_include_consistency),
        ("Configuration Completeness", test_configuration_completeness),
        ("Documentation Accuracy", test_documentation_accuracy),
        ("Build System", test_build_system)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
    
    generate_test_report()
    
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST RESULTS")
    print("="*60)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All comprehensive tests passed!")
        print("\nThe Cor Gaze Detection Library codebase is ready for compilation.")
        print("Next steps:")
        print("1. Install OpenCV development headers for your platform")
        print("2. Run: python build_and_test.py")
        print("3. Test with actual video files")
        return 0
    else:
        print("⚠️  Some tests had issues.")
        print("Please review the output above and fix any identified problems.")
        return 1

if __name__ == "__main__":
    sys.exit(main())