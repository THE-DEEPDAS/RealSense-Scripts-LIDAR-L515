## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##    Advanced RealSense Diagnostic Tool     ##
###############################################

import pyrealsense2 as rs
import sys
import os
import time
import platform
import subprocess

def print_header(text):
    print("\n" + "=" * 50)
    print(text)
    print("=" * 50)

def print_section(text):
    print("\n" + "-" * 40)
    print(text)
    print("-" * 40)

def check_usb_devices():
    """Check connected USB devices using platform-specific commands"""
    print_section("USB DEVICES CHECK")
    
    if platform.system() == 'Windows':
        try:
            print("Running PowerShell command to list USB devices...")
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-PnpDevice | Where-Object {$_.Class -eq 'Camera' -or $_.Class -eq 'Image' -or $_.Class -eq 'USB'} | Format-Table -AutoSize"],
                capture_output=True, text=True, timeout=10
            )
            print(result.stdout)
            
            print("Looking for Intel devices in all USB devices...")
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-PnpDevice | Where-Object {$_.FriendlyName -like '*Intel*' -or $_.FriendlyName -like '*RealSense*'} | Format-Table -AutoSize"],
                capture_output=True, text=True, timeout=10
            )
            print(result.stdout)
            
        except Exception as e:
            print(f"Error running PowerShell command: {e}")
    else:
        print("USB device check is only supported on Windows")

def main():
    print_header("INTEL REALSENSE ADVANCED DIAGNOSTIC TOOL")
    
    # System Information
    print_section("SYSTEM INFORMATION")
    print(f"OS: {platform.platform()}")
    print(f"Python: {platform.python_version()}")
    try:
        print(f"RealSense SDK: {rs.get_librealsense_version()}")
    except Exception as e:
        print(f"Error getting RealSense SDK version: {e}")
    
    # Check environment variables that might affect USB/camera access
    print_section("ENVIRONMENT VARIABLES")
    relevant_vars = ['PYTHONPATH', 'PATH', 'LIBUSB_DEBUG']
    for var in relevant_vars:
        print(f"{var}: {os.environ.get(var, 'Not set')}")
    
    # Check USB devices
    check_usb_devices()
    
    # Method 1: Standard Context Query
    print_section("METHOD 1: STANDARD QUERY")
    try:
        ctx = rs.context()
        devices = ctx.query_devices()
        print(f"Devices found: {len(devices)}")
        for i, dev in enumerate(devices):
            try:
                print(f"Device {i+1}:")
                print(f"  Name: {dev.get_info(rs.camera_info.name)}")
                print(f"  Serial: {dev.get_info(rs.camera_info.serial_number)}")
            except Exception as e:
                print(f"  Error getting device info: {e}")
    except Exception as e:
        print(f"Error in standard query: {e}")
    
    # Method 2: Direct Device Query
    print_section("METHOD 2: DIRECT DEVICE QUERY")
    try:
        ctx = rs.context()
        for i in range(10):  # Try different device indices
            try:
                dev = ctx.get_sensor(i)
                print(f"Found device at index {i}")
                print(f"  Type: {type(dev)}")
            except:
                pass
    except Exception as e:
        print(f"Error in direct device query: {e}")
    
    # Method 3: Pipeline with different configuration attempts
    print_section("METHOD 3: PIPELINE ATTEMPTS")
    
    # Try different stream combinations
    stream_configs = [
        {"depth": True, "color": True},
        {"depth": True, "color": False},
        {"depth": False, "color": True},
        {"infrared": True}
    ]
    
    for i, config_settings in enumerate(stream_configs):
        print(f"\nAttempt {i+1}: Testing with {config_settings}")
        pipeline = rs.pipeline()
        config = rs.config()
        
        try:
            # Configure streams based on settings
            if config_settings.get("depth", False):
                config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
                print("  Enabled depth stream")
                
            if config_settings.get("color", False):
                config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
                print("  Enabled color stream")
                
            if config_settings.get("infrared", False):
                config.enable_stream(rs.stream.infrared, 640, 480, rs.format.y8, 30)
                print("  Enabled infrared stream")
            
            # Try starting the pipeline
            print("  Starting pipeline...")
            profile = pipeline.start(config)
            print("  Pipeline started successfully!")
            
            # Get device info
            dev = profile.get_device()
            print(f"  Connected to: {dev.get_info(rs.camera_info.name)}")
            print(f"  Serial number: {dev.get_info(rs.camera_info.serial_number)}")
            
            # Try to get a frame
            print("  Waiting for frames...")
            frames = pipeline.wait_for_frames(5000)
            print(f"  Received {len(frames)} frames!")
            
            # Success - this configuration works
            print("  ✅ SUCCESS: This configuration works!")
            pipeline.stop()
            
            # If we got here, we have a working configuration
            print("\n📋 WORKING CONFIGURATION:")
            print(f"  Depth stream: {config_settings.get('depth', False)}")
            print(f"  Color stream: {config_settings.get('color', False)}")
            print(f"  Infrared stream: {config_settings.get('infrared', False)}")
            break
            
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
            try:
                pipeline.stop()
            except:
                pass
    
    # Method 4: Try to connect with specific attributes
    print_section("METHOD 4: SPECIFIC ATTRIBUTES")
    try:
        # Try connecting with all possible USB ports/controllers
        ctx = rs.context()
        for i in range(10):  # Try multiple USB controllers
            try:
                config = rs.config()
                # Try with a hint to use a specific USB controller
                config.enable_device_from_file(None, f"{{'usb_port_id':'{i}'}}")
                pipeline = rs.pipeline()
                pipeline.start(config)
                print(f"Success connecting via USB controller {i}")
                pipeline.stop()
                break
            except:
                pass
    except Exception as e:
        print(f"Error in specific attributes method: {e}")
    
    print_header("DIAGNOSTIC COMPLETE")
    
    print("\nTROUBLESHOOTING RECOMMENDATIONS:")
    print("1. Check if the Intel RealSense Viewer application can detect your camera")
    print("2. Try installing/reinstalling the latest Intel RealSense SDK")
    print("3. Try different USB ports (preferably USB 3.0 or higher)")
    print("4. Check camera firmware using Intel RealSense Device Manager")
    print("5. Try using a powered USB hub if your camera requires more power")
    print("6. Check for conflicting applications that might be using the camera")
    print("7. Try rebooting your computer with the camera connected")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled error: {str(e)}")
        input("Press Enter to exit...")
