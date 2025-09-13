## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2
import time

print("Searching for RealSense cameras...")

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Try to find any available camera
ctx = rs.context()
devices = ctx.query_devices()
if len(devices) == 0:
    print("No RealSense devices detected! Trying alternative methods...")
    
    # Print all available cameras from system
    print("System detected cameras:")
    for c in ctx.devices:
        print(f" - {c.get_info(rs.camera_info.name)} (Serial: {c.get_info(rs.camera_info.serial_number)})")
    
    # Try using specific device by serial - replace with your device's serial if known
    # The serial number can be found in the Device Manager properties
    # Or try one of the IDs from your screenshot: 6&1758D7C... or 6&1CF34A1...
    try:
        config.enable_device("6&1758D7C")  # Try the first ID from your screenshot
    except Exception as e1:
        try:
            config.enable_device("6&1CF34A1")  # Try the second ID from your screenshot
        except Exception as e2:
            print(f"Could not enable specific device: {e1}, {e2}")

# Now try to proceed normally
try:
    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))
    print(f"Connected to {device_product_line}")
except Exception as e:
    print(f"Error resolving pipeline: {e}")
    print("Continuing with default configuration...")

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
print("Starting camera stream...")
try:
    pipeline_profile = pipeline.start(config)
    print("Pipeline started successfully!")
except Exception as e:
    print(f"Error starting pipeline: {e}")
    exit(1)

try:
    print("Waiting for frames...")
    while True:
        # Wait for a coherent pair of frames: depth and color
        try:
            frames = pipeline.wait_for_frames(5000)  # 5 second timeout
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                print("Missing frames, retrying...")
                continue
        except Exception as e:
            print(f"Error getting frames: {e}")
            time.sleep(1)
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
        
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q') or key == 27:  # Press 'q' or ESC to close the window
            break
        elif key == ord('n'):  # Press 'n' to retake the photo
            continue

    cv2.destroyAllWindows()

finally:
    # Stop streaming
    pipeline.stop()
