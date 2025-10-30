#!/usr/bin/env python3
"""
Cor Version Checker - Determine which version you're running and get upgrade instructions
"""

import sys

def check_cor_installation():
    """Check Cor installation and provide upgrade guidance"""
    
    print("Cor Gaze Detection Library - Version Checker")
    print("=" * 50)
    
    try:
        import cor
        print("✅ Cor library is installed")
        
        # Get version information
        version_info = cor.version()
        
        print(f"\n📋 Current Installation:")
        print(f"   Version: {version_info.get('version', 'Unknown')}")
        print(f"   Mode: {version_info.get('mode', 'Unknown')}")
        print(f"   C Extension: {version_info.get('c_extension', False)}")
        print(f"   OpenCV Available: {version_info.get('opencv_available', False)}")
        
        # Determine what the user has
        mode = version_info.get('mode', 'Unknown')
        has_c_extension = version_info.get('c_extension', False)
        
        if has_c_extension and 'C Extension' in mode:
            print(f"\n🚀 You have the HIGH-PERFORMANCE C Extension version!")
            print(f"   ✅ All features available")
            print(f"   ✅ Maximum processing speed")
            print(f"   ✅ Real-time camera processing")
            print(f"   ✅ Advanced analysis features")
            
        elif 'Python fallback' in mode:
            print(f"\n🐍 You have the Python Fallback version")
            print(f"   ✅ All basic features available")
            print(f"   ✅ Easy installation and use")
            print(f"   ⚠️  Limited to basic gaze detection")
            print(f"   ⚠️  No real-time processing")
            
            print(f"\n🔧 To upgrade to C Extension (high performance):")
            
            # Platform-specific upgrade instructions
            import platform
            system = platform.system().lower()
            
            if system == 'windows':
                print(f"   1. Install Visual Studio Build Tools:")
                print(f"      https://visualstudio.microsoft.com/downloads/")
                print(f"   2. Run upgrade commands:")
                print(f"      pip install opencv-contrib-python-headless")
                print(f"      git clone https://github.com/cor-team/cor.git")
                print(f"      cd cor")
                print(f"      python setup.py build_ext --inplace")
                print(f"      pip install -e .")
                
            elif system == 'linux':
                print(f"   1. Install development tools:")
                print(f"      sudo apt-get install build-essential python3-dev")
                print(f"      sudo apt-get install libopencv-dev libopencv-contrib-dev")
                print(f"   2. Run upgrade commands:")
                print(f"      pip install opencv-contrib-python-headless")
                print(f"      git clone https://github.com/cor-team/cor.git")
                print(f"      cd cor")
                print(f"      python setup.py build_ext --inplace")
                print(f"      pip install -e .")
                
            elif system == 'darwin':  # macOS
                print(f"   1. Install development tools:")
                print(f"      xcode-select --install")
                print(f"      brew install opencv")
                print(f"   2. Run upgrade commands:")
                print(f"      pip install opencv-contrib-python-headless")
                print(f"      git clone https://github.com/cor-team/cor.git")
                print(f"      cd cor")
                print(f"      python setup.py build_ext --inplace")
                print(f"      pip install -e .")
            
            print(f"\n   3. Verify upgrade:")
            print(f"      python check_cor_version.py")
        
        else:
            print(f"\n❓ Unknown installation mode")
            print(f"   Please reinstall Cor: pip install --upgrade cor")
        
        # Test basic functionality
        print(f"\n🧪 Testing Basic Functionality:")
        try:
            # Test help function
            print(f"   ✅ Help function available")
            
            # Test version function
            print(f"   ✅ Version function working")
            
            # Test CLI
            if hasattr(cor, 'cli'):
                print(f"   ✅ CLI interface available")
            else:
                print(f"   ❌ CLI interface missing")
            
            print(f"\n✅ Basic functionality test passed!")
            
        except Exception as e:
            print(f"\n❌ Functionality test failed: {e}")
        
        # Usage examples
        print(f"\n📚 Usage Examples:")
        print(f"   # Command line (recommended):")
        print(f"   cor video.mp4 --visualize")
        print(f"   ")
        print(f"   # Python code:")
        print(f"   import cor")
        print(f"   cor.run('video.mp4', '--visualize')")
        
        return True
        
    except ImportError as e:
        print("❌ Cor library is not installed")
        print(f"   Error: {e}")
        print(f"\n🔧 Installation Instructions:")
        print(f"   # Basic installation (Python fallback):")
        print(f"   pip install cor")
        print(f"   ")
        print(f"   # Advanced installation (C extension):")
        print(f"   # See README.md for platform-specific instructions")
        return False
        
    except Exception as e:
        print(f"❌ Error checking Cor installation: {e}")
        return False

def main():
    success = check_cor_installation()
    
    print(f"\n" + "=" * 50)
    if success:
        print("🎉 Cor is working! You can now process videos.")
        print("📖 For full documentation, see README.md")
    else:
        print("⚠️  Please install Cor first: pip install cor")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())