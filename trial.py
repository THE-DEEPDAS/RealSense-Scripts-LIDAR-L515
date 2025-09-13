import pyrealsense2 as rs

ctx = rs.context()
devices = ctx.query_devices()

if not devices:
    print("❌ No RealSense devices detected. Check drivers, cable, and USB port.")
else:
    for dev in devices:
        print("✅ Found device:", dev.get_info(rs.camera_info.name))
        print("Serial number:", dev.get_info(rs.camera_info.serial_number))

    # Create pipeline
    pipe = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    print("⏳ Starting pipeline...")
    profile = pipe.start(config)
    print("✅ Pipeline started successfully.")

    pipe.stop()
    print("✅ Pipeline stopped.")
