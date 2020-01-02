from PIL import Image
from projec import convert
import math
import numpy as np

class sphereimage:
    def __init__(self, img):
        self.img = img
        self.width, self.height = self.img.size
        assert self.width == self.height # it has to be square
    
    def map(self, x, y, z):
        raise NotImplementedError()
    
    def get_pixel(self, x, y, z):
        arr = np.array(self.img)
        j, i = self.map(x, y, z)
        return arr[i, j, :]
        
    def imagefromgrid(self, g):
        assert g.shape[2] == 3
        pix = self.get_pixel(g[:, :, 0], g[:, :, 1], g[:, :, 2])
        return Image.fromarray(np.transpose(pix, (1, 0, 2)), 'RGB')
        
class mercator_on_sphere (sphereimage):
    def map(self, x, y, z):
        x, y = convert.pt_to_mercator(x, y, z)
        return (
            (x * (self.width - 1)).astype(np.int),
            (y * (self.height - 1)).astype(np.int)
        )
        pass

def grid(m, o, x, y):
    o, x, y = [np.array(z)[None, None, :] for z in (o, x, y)]
    l = np.linspace(-1, 1, m)
    return o + l[:, None, None] * x + l[None, :, None] * y

def _broadcast(o):
    return np.array(o)[None, None, :]
    
class grid:
    dirs = np.eye(3)
    X, Y, Z = dirs[:, 0], dirs[:, 1], dirs[:, 2]
    what = (
        (Z, X, -Y),
        (-Z, -X, -Y),
        (Y, -X, -Z),
        (-Y, X, -Z),
        (-X, -Y, -Z),
        (X, Y, -Z)
    )
    
    @staticmethod
    def grid(m, o, x, y):
        o, x, y = map(_broadcast, (o, x, y))
        l = np.linspace(-1, 1, m)
        lx = l[:, None, None]
        ly = l[None, :, None]
        return o + lx * x + ly * y
    
    @staticmethod
    def makegrid(m, d):
        return grid.grid(m, *grid.what[d])
    
    @staticmethod
    def makegrids(m):
        return tuple(grid.grid(m, *_) for _ in grid.what)

def makeimages(m, filename="satellite-%d.png"):
    gr = grid.makegrids(m)
    mercator = mercator_on_sphere(Image.open("satellite.png"))
    for i in range(6):
        print("image %d" % i)
        img = mercator.imagefromgrid(gr[i])
        img.save(filename % i)
        
if __name__ == "__main__":
    makeimages(512) # iya
 