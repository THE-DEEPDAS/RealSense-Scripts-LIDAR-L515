## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      RealSense Camera Diagnostic Tool     ##
###############################################

import pyrealsense2 as rs
import sys
import time
import os
import platform

def get_system_info():
    info = {}
    info["Platform"] = platform.platform()
    info["Python Version"] = platform.python_version()
    try:
        info["RealSense SDK"] = rs.get_librealsense_version()
    except:
        info["RealSense SDK"] = "Unknown"
    return info

def main():
    print("\n" + "=" * 50)
    print("Intel RealSense Camera Diagnostic Tool")
    print("=" * 50 + "\n")
    
    # Print system information
    sys_info = get_system_info()
    print("System Information:")
    for key, value in sys_info.items():
        print(f"  {key}: {value}")
    print("")

    # Create a context object to manage RealSense devices
    print("Looking for RealSense devices...")
    ctx = rs.context()
    
    # Check if any devices are connected
    devices = ctx.query_devices()
    device_count = len(devices)
    
    if device_count == 0:
        print("ERROR: No Intel RealSense devices detected!\n")
        print("Troubleshooting steps:")
        print("1. Check that the camera is properly connected via USB")
        print("2. Try a different USB port (preferably USB 3.0)")
        print("3. Restart your computer")
        print("4. Reinstall the Intel RealSense SDK")
        print("5. Check Windows Device Manager for issues with the camera")
        return
    
    print(f"\nSuccess! Found {device_count} RealSense device(s):")
    
    # Enumerate all devices
    for i, dev in enumerate(devices):
        try:
            print(f"\nDEVICE {i+1}:")
            print(f"  Name:          {dev.get_info(rs.camera_info.name)}")
            print(f"  Serial Number: {dev.get_info(rs.camera_info.serial_number)}")
            print(f"  Product Line:  {dev.get_info(rs.camera_info.product_line)}")
            print(f"  Firmware:      {dev.get_info(rs.camera_info.firmware_version)}")
            print(f"  USB Type:      {dev.get_info(rs.camera_info.usb_type_descriptor)}")
            
            # Try to get additional info that might be helpful
            try:
                print(f"  Physical Port: {dev.get_info(rs.camera_info.physical_port)}")
            except:
                pass
                
            # Get sensors
            sensors = dev.query_sensors()
            print(f"\n  Device has {len(sensors)} sensors:")
            
            for j, sensor in enumerate(sensors):
                print(f"    Sensor {j+1}: {sensor.get_info(rs.camera_info.name)}")
                
                # List supported stream profiles
                profiles = sensor.get_stream_profiles()
                print(f"      Supported profiles: {len(profiles)}")
                
                # Group profiles by stream type
                stream_types = {}
                for profile in profiles:
                    stream_name = str(profile.stream_type()).split('.')[-1]
                    if stream_name not in stream_types:
                        stream_types[stream_name] = []
                    
                    # For video streams, get resolution and format
                    if profile.is_video_stream_profile():
                        video_profile = profile.as_video_stream_profile()
                        width, height = video_profile.width(), video_profile.height()
                        fps = profile.fps()
                        format_name = str(profile.format()).split('.')[-1]
                        stream_types[stream_name].append(f"{width}x{height} {format_name} {fps}fps")
                
                # Print grouped profiles
                for stream_name, details in stream_types.items():
                    print(f"      {stream_name}: {len(details)} modes")
                    for i, detail in enumerate(details):
                        if i < 3:  # Only show first 3 to avoid cluttering output
                            print(f"        - {detail}")
                    if len(details) > 3:
                        print(f"        - ... and {len(details)-3} more modes")
        
        except Exception as e:
            print(f"  Error querying device: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Attempting to start a test stream...")
    
    # Try to start a stream with the first device
    try:
        print(f"Setting up pipeline for device: {devices[0].get_info(rs.camera_info.name)}")
        
        # Create pipeline
        pipeline = rs.pipeline()
        config = rs.config()
        
        # Try to enable both depth and color streams
        try:
            serial = devices[0].get_info(rs.camera_info.serial_number)
            config.enable_device(serial)
            print(f"Targeting specific device with serial: {serial}")
        except:
            print("Using default device (first available)")
        
        try:
            config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            
            print("Starting stream...")
            profile = pipeline.start(config)
            print("Pipeline started successfully!")
            
            # Get device info from the active profile
            dev = profile.get_device()
            print(f"Streaming from: {dev.get_info(rs.camera_info.name)} ({dev.get_info(rs.camera_info.serial_number)})")
            
            # Wait for a few frames
            print("Waiting for frames...")
            for i in range(5):
                print(f"  Frame {i+1}/5...")
                try:
                    frames = pipeline.wait_for_frames(1000)  # 1 second timeout
                    depth = frames.get_depth_frame()
                    color = frames.get_color_frame()
                    
                    if depth and color:
                        print(f"  Success! Received depth and color frames.")
                        if i == 4:  # Only show detailed info on last frame
                            depth_data = depth.get_data()
                            color_data = color.get_data()
                            print(f"  Depth frame: {depth.get_width()}x{depth.get_height()}")
                            print(f"  Color frame: {color.get_width()}x{color.get_height()}")
                    else:
                        print(f"  Warning: Missing {'depth' if not depth else ''} {'color' if not color else ''} frame.")
                    
                except Exception as e:
                    print(f"  Error waiting for frame: {str(e)}")
                
                time.sleep(0.5)
                
            print("\nStream test PASSED! Your camera is working correctly.")
            
        except Exception as e:
            print(f"Failed to start stream: {str(e)}")
            
        finally:
            print("Stopping pipeline...")
            pipeline.stop()
            print("Pipeline stopped.")
            
    except Exception as e:
        print(f"Error during stream test: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Diagnostic complete")
    print("=" * 50 + "\n")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled error: {str(e)}")
        input("Press Enter to exit...")
