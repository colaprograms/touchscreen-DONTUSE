# modified from librealsense/wrappers/python/examples/opencv_viewer_example.py
# and http://dlib.net/face_landmark_detection.py.html

import pyrealsense2 as rs
import numpy as np
import cv2
import dlib

class facedetector:
  def __init__(self):
    pass

  def start(self):
    self.pipeline = rs.pipeline()
    self.config = rs.config()
    self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
    self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)

    self.fd = dlib.get_frontal_face_detector()
    self.sp = dlib.shape_predictor("landmarks.dat")

    self.pipeline.start(self.config)

  def face_detector(self, im):
    facebb = self.fd(im)
    print(f"Number of faces: {len(facebb)}")
    return [self.sp(im, b) for b in facebb]

  def get(self):
    frames = self.pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    if not depth_frame or not color_frame:
      return None
    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())
    color_image = color_image[:, :, [2,1,0]]
    shape = self.face_detector(color_image)
    return (depth_image, color_image, shape)

  def stop(self):
    self.pipeline.stop()

if __name__ == "__main__":
  fd = facedetector()
  fd.start()
  wi = dlib.image_window()
  try:
    while True:
      out = fd.get()
      if out is not None:
        depthimage, colorimage, shape = out
        print(colorimage.shape)
        wi.set_image(colorimage)
        wi.clear_overlay()
        for s in shape:
          print(f"{s.part(0)} {s.part(1)}")
          wi.add_overlay(s)
  finally:
    fd.stop()
