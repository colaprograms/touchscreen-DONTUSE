# modified from librealsense/wrappers/python/examples/opencv_viewer_example.py
# and http://dlib.net/face_landmark_detection.py.html

import pyrealsense2 as rs
import numpy as np
import time
import dlib

class average:
    def __init__(self):
        self.count = 0
        self.accum = 0

    def add(self, j):
        self.count += 1
        self.accum += j

    def get(self):
        return self.accum / self.count if self.count >= 1 else 0

class timeaverage:
    def __init__(self):
        self.avg = average()
        self.t = None

    def start(self):
        if self.t is not None:
            raise Exception("started twice")
        self.t = time.time()

    def stop(self):
        if self.t is None:
            return #raise Exception("already stop")
        self.avg.add(time.time() - self.t)
        self.t = None

    def get(self):
        return self.avg.get()

facebbtimer = timeaverage()

shapestimer = timeaverage()

shortftimer = timeaverage()

otherstimer = timeaverage()

def decompose(r):
    return r.top(), r.bottom(), r.left(), r.right()

class facedetector:
    def __init__(self):
        self.currentbb = None
        self.last = None

    def start(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)

        self.fd = dlib.get_frontal_face_detector()
        self.sp = dlib.shape_predictor("landmarks.dat")
        class pyramid:
            def __init__(self):
                pass

            def __call__(self, im):
                return im

            def rect_down(self, rect):
                return rect

            def rect_up(self, rect):
                return rect
        self.pd = pyramid() #self.pd = dlib.pyramid_down(2)

        self.pipeline.start(self.config)

        self.alignment = rs.align(rs.stream.color)

    def face_detector(self, im):
        def sp(b):
            shapestimer.start()
            out = self.sp.calldpoint(im, b)
            shapestimer.stop()
            return out
        if self.currentbb is None:
            facebbtimer.start()
            i2 = self.pd(im)
            facebb = self.fd(i2)
            facebbtimer.stop()
            if len(facebb) > 0:
                self.currentbb = self.pd.rect_up(facebb[0])
        else:
            shortftimer.start()
            i2 = self.pd(im)
            h, w, _ = i2.shape
            #t, b, l, r = decompose(self.currentbb)
            t, b, l, r = decompose(self.pd.rect_down(self.currentbb))
            def tryfindface(t, b, l, r, expand):
                extra_top = 20
                t = max(0, t - extra_top - expand)
                b = min(h, b + expand)
                l = max(0, l - expand)
                r = min(w, r + expand)
                facebb = self.fd(i2[t:b, l:r, :])
                if len(facebb) > 1:
                    raise Exception("too many faces in the little box??")
                elif len(facebb) == 1:
                    rect = facebb[0]
                    rect = dlib.translate_rect(rect, dlib.point(l, t))
                    return self.pd.rect_up(rect)
                else:
                    return None
            #expands = [60, 640]
            expands = [30, 320]
            for ex in expands:
                rect = tryfindface(t, b, l, r, ex)
                if rect:
                    break
                print(f"couldn't find the face with expansion {ex}")
            shortftimer.stop()
            self.currentbb = rect
        if self.currentbb is not None:
            self.last = sp(self.currentbb)
        else:
            self.last = None
        return self.last

    def get(self):
        frames = self.pipeline.wait_for_frames()
        frames = self.alignment.process(frames)
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        t = color_frame.get_frame_metadata(rs.frame_metadata_value.backend_timestamp)
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        color_image = color_image[:, :, [2,1,0]]
        shape = self.face_detector(color_image)
        return (
            t,
            depth_image,
            color_image,
            shape
        )

    def stop(self):
        self.pipeline.stop()

class midavg:
    def __init__(self, lth):
        self.last = np.zeros(lth)
        self.idx = 0
        self.valid = 0
        assert lth & 3 == 0

    def add(self, z):
        self.last[idx] = z
        self.idx += 1
        l = self.last.shape[0]
        if self.valid < l:
            self.valid += 1
        if self.idx >= l:
            self.idx -= l
        out = np.sort(self.last)
        return np.mean(out[l//4, 3*l//4])

class predicteyes:
    def __init__(self):
        self.t0 = None

    def __call__(self, t, x, y, z):
        if self.t0 is None:
            self.t0 = t
        t -= self.t0

    """
    def __call__(self, t, l, le, r, re):
        if self.t0 is None:
            self.t0 = t
        t -= self.t0
        scale = ((le[0]**2 + re[0]**2) / 2) ** 0.5
        print("t = %6.2f   scale = %6.2f   l = %9.2f %9.2f"% (t, scale, l[0], l[1]))
    """

PARTS_L_EYE = range(36, 42)
PARTS_R_EYE = range(42, 48)
def average_on_box_around_point(img, x, y, scale):
    x = int(x)
    y = int(y)
    scale = int(scale + 0.5)
    scale //= 2
    l = max(0, x - scale)
    r = min(img.shape[1], x + scale)
    t = max(0, y - scale)
    b = min(img.shape[0], y + scale)
    img = img[t:b, l:r]
    return np.mean(img[img != 0])

def coordinates(t, depthimage, colorimage, shape):
    left, leftv = meanof(shape, PARTS_L_EYE)
    right, rightv = meanof(shape, PARTS_R_EYE)
    lscale = leftv[0]
    rscale = rightv[0]
    ld = average_on_box_around_point(depthimage, left[0], left[1], lscale)
    rd = average_on_box_around_point(depthimage, right[0], right[1], rscale)
    return np.array([(left[0] + right[0]) / 2, (left[1] + right[1]) / 2, (ld + rd) / 2])

if __name__ == "__main__":
    fd = facedetector()
    fd.start()
    framecount = -1
    predict = predicteyes()
    def meanof(shape, ix):
        sp = [shape.part(i) for i in ix]
        v = np.array([[p.x, p.y] for p in sp])
        return np.mean(v, axis=0), np.std(v, axis=0)
    try:
        while True:
            otherstimer.stop()
            out = fd.get()
            otherstimer.start()
            if out is not None:
                framecount += 1
                if framecount > 0:
                    if framecount % 100 == 0:
                        print(f"FPS: {framecount / (time.time() - starttime)}")
                        """
                        print(f"Face bounding boxes take {facebbtimer.get()} on average")
                        print(f"Shape prediction takes {shapestimer.get()} on average")
                        print(f"Small face bounding boxes: {shortftimer.get()} on average")
                        print(f"Other stuff: {otherstimer.get()} on average")
                        """
                        framecount = 0
                        starttime = time.time()
                else:
                    starttime = time.time()
                t, depthimage, colorimage, shape = out
                if shape is not None:
                    (x, y, z) = coordinates(t, depthimage, colorimage, shape)
                    print("%6.2f    %6.2f    %6.2f" % (x, y, z))
                    #print(t, x, y, z)
                    #predict(t, left, right)
                else:
                    print("no eyes found this frame")
    finally:
        fd.stop()
