from PIL import Image
from projec import pt_to_mercator
import math
import numpy as np

class mercator_projected_image:
    def __init__(self, fn="satellite.png"): #(self, fn):
        self.img = Image.open(fn)
        self.width, self.height = self.img.size
        assert self.width == self.height
    
    def map(self, x, y, z):
        x, y = pt_to_mercator(x, y, z)
        return x * (self.width - 1), y * (self.height - 1)
    
    def get_pixel(self, x, y, z):
        x, y = self.map(x, y, z)
        return self.img.getpixel((int(x), int(y)))
        # should think of something better probably

    def imagefromgrid(self, g):
        assert g.shape[2] == 3
        w, h = g.shape[0], g.shape[1]
        img = Image.new('RGB', (w, h))
        for j in range(g.shape[0]):
            for i in range(g.shape[1]):
                x, y, z = g[j, i, :]
                img.putpixel((j, i), self.get_pixel(x, y, z))
        return img
     
class height_and_latitude_projection:
    def __init__(self, fn="satellite.png"):
        self.img = Image.open(fn)
        self.width, self.height = self.img.size

    def map(self, l, h):
        from projec import latlon_to_mercator
        if h > 0.996:
            h = 0.996
        if h < -0.996:
            h = -0.996
        lat = math.asin(h) * 180 / math.pi
        x, y = latlon_to_mercator(lat, l)
        return x * (self.width - 1), y * (self.height - 1)

    def get_pixel(self, l, h):
        x, y = self.map(l, h)
        t = (int(x), int(y))
        return self.img.getpixel(t)

    def imagefromgrid(self, g):
        assert g.shape[2] == 2
        w, h = g.shape[0], g.shape[1]
        img = Image.new('RGB', (w, h))
        for j in range(g.shape[0]):
            for i in range(g.shape[1]):
                l, h = g[j, i, :]
                img.putpixel((j, i), self.get_pixel(l, h))
        return img


def grid(m, o, x, y):
    o, x, y = [np.array(z)[None, None, :] for z in (o, x, y)]
    l = np.linspace(-1, 1, m)
    return o + l[:, None, None] * x + l[None, :, None] * y

def makegrids(m):
    dirs = np.eye(3)
    X, Y, Z = dirs[:, 0], dirs[:, 1], dirs[:, 2]
    top = grid(m, Z, X, -Y)
    bottom = grid(m, -Z, -X, -Y)
    front = grid(m, Y, -X, -Z)
    back = grid(m, -Y, X, -Z)
    left = grid(m, -X, -Y, -Z)
    right = grid(m, X, Y, -Z)
    return (top, bottom, front, back, left, right)

def makeimages(m):
    gr = makegrids(m)
    mercator = mercator_projected_image()
    for i in range(6):
        print("image %d" % i)
        img = mercator.imagefromgrid(gr[i])
        img.save("satellite-%d.png" % i)

def makeimages2():
    WIDTH, HEIGHT = 512, 256
    o = np.zeros((WIDTH, HEIGHT, 2))
    o[:, :, 0] = np.linspace(-180, 180, WIDTH)[:, None]
    o[:, :, 1] = np.linspace(1, -1, HEIGHT)[None, :]
    heightlat = height_and_latitude_projection()
    img = heightlat.imagefromgrid(o)
    img.save("satelliteh.png")

if __name__ == "__main__":
    #makeimages(512) # iya
    makeimages2()
