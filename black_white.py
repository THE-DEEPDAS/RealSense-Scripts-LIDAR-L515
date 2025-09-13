## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2
import os

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Try to find any connected device
ctx = rs.context()
devices = ctx.query_devices()
if len(devices) == 0:
    print("No Intel RealSense devices connected!")
    exit(0)

# Print information about connected devices to help with debugging
print(f"Found {len(devices)} RealSense device(s):")
for i, dev in enumerate(devices):
    print(f"  Device {i}: {dev.get_info(rs.camera_info.name)}")
    print(f"    Serial Number: {dev.get_info(rs.camera_info.serial_number)}")
    print(f"    Product Line: {dev.get_info(rs.camera_info.product_line)}")

# You can uncomment and modify this line to connect to a specific device by serial number
# config.enable_device('YOUR_CAMERA_SERIAL_NUMBER')

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

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
pipeline.start(config)

# Directory to save images
save_dir = "saved_images"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def create_color_scale_bar(height, max_distance_cm=100):
    """Create a vertical color scale bar."""
    scale_bar_width = 50
    scale_bar = np.zeros((height, scale_bar_width), dtype=np.uint8)

    # Create the grayscale scale bar
    for i in range(height):
        intensity = 255 - int(255 * (i / height))
        scale_bar[i, :] = intensity

    # Add text labels to the scale bar
    step = height // 10
    for i in range(0, height, step):
        distance_cm = int((1 - i / height) * max_distance_cm)
        cv2.putText(scale_bar, f"{distance_cm} cm", (5, i + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 255, 1)

    return scale_bar

try:
    print("Starting camera stream...")
    
    # Wait for a coherent pair of frames to get dimensions
    try:
        frames = pipeline.wait_for_frames(5000)  # 5 second timeout
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            raise RuntimeError("Could not get frames from the camera")
        print("Successfully retrieved frames from camera!")
    except Exception as e:
        print(f"Error getting frames: {str(e)}")
        raise RuntimeError("Failed to get frames from the camera. Check connections and try again.")

    # Get frame dimensions
    depth_colormap_dim = np.asanyarray(depth_frame.get_data()).shape
    color_colormap_dim = np.asanyarray(color_frame.get_data()).shape
    if depth_colormap_dim != color_colormap_dim:
        height, _ = depth_colormap_dim
    else:
        height, _ = color_colormap_dim

    # Create the color scale bar once
    color_scale_bar = create_color_scale_bar(height)

    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Convert depth image to grayscale (8-bit)
        depth_gray = cv2.convertScaleAbs(depth_image, alpha=0.03)

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_gray.shape != color_image.shape[:2]:
            resized_color_image = cv2.resize(color_image, dsize=(depth_gray.shape[1], depth_gray.shape[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, cv2.cvtColor(depth_gray, cv2.COLOR_GRAY2BGR)))
        else:
            images = np.hstack((color_image, cv2.cvtColor(depth_gray, cv2.COLOR_GRAY2BGR)))

        # Add grayscale scale to the depth image
        color_scale_bar_bgr = cv2.cvtColor(color_scale_bar, cv2.COLOR_GRAY2BGR)
        images_with_scale = np.hstack((images, color_scale_bar_bgr))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images_with_scale)
        key = cv2.waitKey(1)
        # Press 's' to save the image
        if key & 0xFF == ord('s'):
            filename = os.path.join(save_dir, f"image_{int(cv2.getTickCount())}.png")
            cv2.imwrite(filename, images_with_scale)
            print(f"Image saved to {filename}")
        # Press esc or 'q' to close the image window
        elif key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break

finally:
    # Stop streaming
    pipeline.stop()