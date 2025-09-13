## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

import pyrealsense2 as rs
import sys

def set_sensor_preset(sensor, preset):
    try:
        # Check if the sensor supports the desired option
        if not sensor.supports(rs.option.visual_preset):
            print("This sensor does not support visual presets")
            return False
       
        # Set the preset value
        sensor.set_option(rs.option.visual_preset, preset)
        return True

    except Exception as e:
        print(f"Error setting sensor preset: {e}")
        return False

def main():
    # Preset options based on the Realsense Viewer presets
    presets = {
        'no_ambient_light': 3,  # RS2_L500_VISUAL_PRESET_NO_AMBIENT,
        'low_ambient_light': 2,  # RS2_L500_VISUAL_PRESET_LOW_AMBIENT,
        'max_range': 4,  # RS2_L500_VISUAL_PRESET_MAX_RANGE,
        'short_range': 5  # RS2_L500_VISUAL_PRESET_SHORT_RANGE
    }

    if len(sys.argv) != 2 or sys.argv[1] not in presets:
        print(f"Usage: {sys.argv[0]} <preset>")
        print(f"Preset options: {', '.join(presets.keys())}")
        return

    preset_name = sys.argv[1]
    preset_value = presets[preset_name]

    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Start streaming
    pipeline.start(config)

    try:
        device = pipeline.get_active_profile().get_device()
        depth_sensor = device.query_sensors()[0]  # Assuming the depth sensor is the first one

        if set_sensor_preset(depth_sensor, preset_value):
            print(f"Preset '{preset_name}' applied successfully")
        else:
            print(f"Failed to apply preset '{preset_name}'")

    finally:
        # Stop streaming
        pipeline.stop()

if __name__ == "__main__":
    main()