#!/usr/bin/env python3
"""
Test script to verify CLI installation and functionality
"""

import subprocess
import sys
import os

def test_cli_commands():
    """Test various CLI commands"""
    
    print("Testing Cor CLI Installation...")
    print("=" * 50)
    
    # Test commands to run
    test_commands = [
        # Basic help and version
        ["cor", "--version"],
        ["cor", "--help-cor"],
        ["python", "-m", "cor", "--version"],
        
        # Configuration tests
        ["cor", "--config", "test_param", "test_value"],
        ["cor", "--get-config", "test_param"],
    ]
    
    # Test with video file if available
    if os.path.exists("test_video.mp4"):
        test_commands.extend([
            ["cor", "test_video.mp4", "--validate"],
            ["cor", "test_video.mp4", "--extract-frames", "3"],
            ["cor", "test_video.mp4", "--benchmark", "10"],
        ])
    
    success_count = 0
    total_count = len(test_commands)
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n{i}. Testing: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"   ✅ SUCCESS")
                if result.stdout.strip():
                    # Show first few lines of output
                    lines = result.stdout.strip().split('\n')[:3]
                    for line in lines:
                        print(f"   📄 {line}")
                success_count += 1
            else:
                print(f"   ❌ FAILED (exit code: {result.returncode})")
                if result.stderr.strip():
                    print(f"   🚨 Error: {result.stderr.strip()[:100]}")
        except subprocess.TimeoutExpired:
            print(f"   ⏰ TIMEOUT (command took too long)")
        except FileNotFoundError:
            print(f"   ❓ COMMAND NOT FOUND (CLI not installed)")
        except Exception as e:
            print(f"   💥 EXCEPTION: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"CLI Test Results: {success_count}/{total_count} commands successful")
    
    if success_count == total_count:
        print("🎉 All CLI tests passed! Installation successful.")
    elif success_count > 0:
        print("⚠️  Some CLI tests passed. Partial installation.")
    else:
        print("❌ No CLI tests passed. Installation may have failed.")
    
    return success_count == total_count

def test_python_import():
    """Test Python import functionality"""
    print("\nTesting Python Import...")
    print("-" * 30)
    
    try:
        import cor
        print("✅ Cor module imported successfully")
        
        # Test version
        version = cor.version()
        print(f"📋 Version: {version.get('version', 'Unknown')}")
        print(f"📋 Mode: {version.get('mode', 'Unknown')}")
        
        # Test CLI function exists
        if hasattr(cor, 'cli'):
            print("✅ CLI function available")
        else:
            print("❌ CLI function not found")
            
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"💥 Error testing import: {e}")
        return False

def main():
    print("Cor Gaze Detection Library - CLI Installation Test")
    print("=" * 60)
    
    # Test Python import first
    import_success = test_python_import()
    
    # Test CLI commands
    cli_success = test_cli_commands()
    
    print(f"\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"Python Import: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"CLI Commands:  {'✅ PASS' if cli_success else '❌ FAIL'}")
    
    if import_success and cli_success:
        print("\n🎉 INSTALLATION SUCCESSFUL!")
        print("You can now use:")
        print("  - cor video.mp4 --visualize")
        print("  - python -m cor video.mp4")
        print("  - import cor; cor.run('video.mp4')")
    else:
        print("\n⚠️  INSTALLATION ISSUES DETECTED")
        print("Try reinstalling with: pip install -e .")
    
    return 0 if (import_success and cli_success) else 1

if __name__ == "__main__":
    sys.exit(main())