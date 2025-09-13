## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Direct Camera Access Attempt         ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2
import time
import os

def print_section(text):
    print("\n" + "-" * 40)
    print(text)
    print("-" * 40)

def main():
    print_section("DIRECT CAMERA ACCESS ATTEMPT")
    print("This script attempts alternative methods to access your RealSense camera")
    
    # First approach: Try different config options
    print_section("APPROACH 1: CUSTOM CONFIG OPTIONS")
    
    # Configure depth and color streams with more explicit options
    try:
        pipeline = rs.pipeline()
        config = rs.config()
        
        # Get device product line for setting a supporting resolution
        ctx = rs.context()
        devices = ctx.query_devices()
        
        if len(devices) == 0:
            print("No devices detected by context.query_devices()")
            print("Trying alternate detection method...")
            
            # Force discovery by creating a pipeline
            pipe = rs.pipeline()
            try:
                # Force the pipeline to try to connect to any available device
                cfg = rs.config()
                cfg.enable_stream(rs.stream.depth)
                pipe.start(cfg)
                print("Device found through forced pipeline start!")
                pipe.stop()
            except Exception as e:
                print(f"Forced discovery failed: {e}")
        else:
            print(f"Found {len(devices)} device(s)")
            
            for i, dev in enumerate(devices):
                print(f"Device {i+1}:")
                try:
                    print(f"  Name: {dev.get_info(rs.camera_info.name)}")
                    print(f"  Serial: {dev.get_info(rs.camera_info.serial_number)}")
                except Exception as e:
                    print(f"  Error getting device info: {e}")
        
        # Enable streams with explicit format and resolution for L515
        print("\nEnabling streams with custom configuration...")
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        
        # Try to start streaming with generous timeout
        print("Starting pipeline with custom configuration...")
        profile = pipeline.start(config)
        print("Pipeline started successfully!")
        
        # Get device info from the active profile
        dev = profile.get_device()
        print(f"Connected to: {dev.get_info(rs.camera_info.name)}")
        print(f"Serial number: {dev.get_info(rs.camera_info.serial_number)}")
        
        # Wait for a coherent pair of frames
        print("Waiting for frames...")
        tries = 0
        max_tries = 5
        while tries < max_tries:
            tries += 1
            print(f"Attempt {tries}/{max_tries}...")
            
            try:
                frames = pipeline.wait_for_frames(timeout_ms=5000)  # 5 second timeout
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                
                if depth_frame and color_frame:
                    print("Successfully received frames!")
                    
                    # Save a sample image to verify
                    color_image = np.asanyarray(color_frame.get_data())
                    filename = os.path.join("saved_images", f"test_connection_{int(time.time())}.jpg")
                    cv2.imwrite(filename, color_image)
                    print(f"Saved test image to {filename}")
                    
                    # Show success and clean up
                    print("\n✅ CONNECTION SUCCESSFUL! Your camera is working!")
                    pipeline.stop()
                    return True
                else:
                    print("Missing frames, retrying...")
            except Exception as e:
                print(f"Error waiting for frames: {e}")
            
            time.sleep(1)
        
        print("❌ Failed to get frames after multiple attempts")
        pipeline.stop()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        try:
            pipeline.stop()
        except:
            pass
    
    # Second approach: Try with minimal configuration
    print_section("APPROACH 2: MINIMAL CONFIGURATION")
    
    try:
        pipeline = rs.pipeline()
        config = rs.config()
        
        # Enable only depth stream with minimal configuration
        config.enable_stream(rs.stream.depth)
        
        print("Starting pipeline with minimal configuration...")
        profile = pipeline.start(config)
        print("Pipeline started successfully!")
        
        print("Waiting for frames...")
        frames = pipeline.wait_for_frames(timeout_ms=5000)
        print("Got frames!")
        
        pipeline.stop()
        print("\n✅ MINIMAL CONFIGURATION WORKED!")
        return True
        
    except Exception as e:
        print(f"❌ Minimal configuration failed: {e}")
        try:
            pipeline.stop()
        except:
            pass
    
    # Third approach: Try disabling USB power management
    print_section("APPROACH 3: USB POWER MANAGEMENT")
    print("For Windows systems, try these steps:")
    print("1. Open Device Manager")
    print("2. Expand 'Universal Serial Bus controllers'")
    print("3. Right-click on each 'USB Root Hub' and select 'Properties'")
    print("4. Go to the 'Power Management' tab")
    print("5. Uncheck 'Allow the computer to turn off this device to save power'")
    print("6. Click OK and restart your computer")
    
    print("\nAdditional troubleshooting steps:")
    print("1. Install the Intel RealSense Viewer application")
    print("2. Check if the camera is detected there")
    print("3. Update firmware if available")
    print("4. Try a different USB 3.0 port")
    print("5. Try a different USB cable")
    print("6. Try connecting the camera to a powered USB hub")
    
    return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ All connection attempts failed.")
            print("Please try the troubleshooting steps listed above.")
        
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"Unhandled error: {str(e)}")
        input("Press Enter to exit...")
