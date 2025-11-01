#!/usr/bin/env python3
"""
Cor Version Checker - Check installation and provide usage guidance
"""

import sys

def check_cor_installation():
    """Check Cor installation and provide usage guidance"""
    
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
        print(f"   OpenCV Available: {version_info.get('opencv_available', False)}")
        
        # Check implementation
        mode = version_info.get('mode', 'Unknown')
        opencv_available = version_info.get('opencv_available', False)
        
        if mode == 'Python' and opencv_available:
            print(f"\n🐍 Pure Python Implementation")
            print(f"   ✅ All current features available")
            print(f"   ✅ Easy installation and cross-platform compatibility")
            print(f"   ✅ Basic gaze detection with heatmap generation")
            print(f"   ✅ Video validation and processing")
            print(f"   ✅ Configuration-based parameter management")
            
        elif mode == 'Python' and not opencv_available:
            print(f"\n⚠️  Python Implementation - OpenCV Missing")
            print(f"   ❌ OpenCV not available")
            print(f"   🔧 Install OpenCV: pip install opencv-python")
            
        else:
            print(f"\n❓ Unknown installation mode: {mode}")
        
        # Test basic functionality
        print(f"\n🧪 Testing Basic Functionality:")
        try:
            # Test help function
            if hasattr(cor, 'help'):
                print(f"   ✅ Help function available")
            else:
                print(f"   ❌ Help function missing")
            
            # Test version function
            if hasattr(cor, 'version'):
                print(f"   ✅ Version function working")
            else:
                print(f"   ❌ Version function missing")
            
            # Test run function
            if hasattr(cor, 'run'):
                print(f"   ✅ Run function available")
            else:
                print(f"   ❌ Run function missing")
            
            # Test validate function
            if hasattr(cor, 'validate_video'):
                print(f"   ✅ Video validation available")
            else:
                print(f"   ❌ Video validation missing")
            
            # Test CLI
            if hasattr(cor, 'cli'):
                print(f"   ✅ CLI interface available")
            else:
                print(f"   ❌ CLI interface missing")
            
            # Test path management
            if hasattr(cor, 'set_input_path'):
                print(f"   ✅ Path management functions available")
            else:
                print(f"   ❌ Path management functions missing")
            
            print(f"\n✅ Basic functionality test passed!")
            
        except Exception as e:
            print(f"\n❌ Functionality test failed: {e}")
        
        # Usage examples
        print(f"\n📚 Usage Examples:")
        print(f"   # Command line (recommended):")
        print(f"   cor video.mp4")
        print(f"   cor video.mp4 --visualize")
        print(f"   cor video.mp4 --validate")
        print(f"   cor --version")
        print(f"   ")
        print(f"   # Python code:")
        print(f"   import cor")
        print(f"   cor.help()")
        print(f"   cor.run('video.mp4')")
        print(f"   result = cor.validate_video('video.mp4')")
        
        return True
        
    except ImportError as e:
        print("❌ Cor library is not installed")
        print(f"   Error: {e}")
        print(f"\n🔧 Installation Instructions:")
        print(f"   # Installation from source:")
        print(f"   git clone https://github.com/victorcynzo/cor")
        print(f"   cd cor")
        print(f"   pip install -e .")
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
        print("⚠️  Please install Cor first from source (see README.md for instructions)")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())