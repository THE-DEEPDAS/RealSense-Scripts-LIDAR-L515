## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

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

def add_color_scale_bar(image, max_distance_cm=100):
    """Add a vertical color scale bar to the image."""
    h, w = image.shape[:2]
    scale_bar_width = 50
    scale_bar = np.zeros((h, scale_bar_width, 3), dtype=np.uint8)

    # Create the color scale bar
    for i in range(h):
        color = cv2.applyColorMap(np.array([[255 - int(255 * (i / h))]], dtype=np.uint8), cv2.COLORMAP_JET)[0][0]
        scale_bar[i, :] = color

    # Add text labels to the scale bar
    step = h // 10
    for i in range(0, h, step):
        distance_cm = int((1 - i / h) * max_distance_cm)
        cv2.putText(scale_bar, f"{distance_cm} cm", (5, i + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Add the scale bar to the right of the image
    combined_image = np.hstack((image, scale_bar))

    return combined_image

try:
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

        # Add color scale to the depth image
        images_with_scale = add_color_scale_bar(images)

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images_with_scale)
        
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q') or key == 27:  # Press 'q' or ESC to close the window
            break
        elif key == ord('n'):  # Press 'n' to retake the photo
            continue

    cv2.destroyAllWindows()

finally:
    # Stop streaming
    pipeline.stop()
