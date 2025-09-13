
import numpy as np                        # fundamental package for scientific computing
import matplotlib
import matplotlib.pyplot as plt           # 2D plotting library producing publication quality figures
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pyrealsense2 as rs                 # Intel RealSense cross-platform open-source API
import json
from pathlib import Path


context = rs.context()
config = rs.config()
#dev = context.query_devices()
#d= dev[0]
pipe = rs.pipeline(context)
config.enable_device("00000000f0141140")   # replace with actual serial

config.enable_stream(rs.stream.depth,1024,768, rs.format.z16,30)

pipeline_profile = pipe.start()
pipe.stop()