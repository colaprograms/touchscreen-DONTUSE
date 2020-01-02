from PIL import Image
from projec import convert
import math
import numpy as np

Image.MAX_IMAGE_PIXELS = 300000000

def _sca(x, w):
    return (x * (w-1)).astype(int)

class sphereimage:
    def __init__(self, img):
        self.img = img
        self.width, self.height = self.img.size
        assert self.width == self.height # it has to be square
    
    def map(self, x, y, z):
        raise NotImplementedError()
    
    def get_pixel(self, x, y, z):
        arr = np.array(self.img)
        j, i, *extra = self.map(x, y, z)
        if extra:
            (mask,) = extra
            if self.img.mode in ["LA", "RGBA"]:
                out = arr[i, j, :]
                out[np.logical_not(mask), :] = 0
                #out[mask, :] = 0
                return out
            else:
                raise Exception("mode has to be LA or RGBA to use the mask")
        else:
            return arr[i, j, :]
        
    def imagefromgrid(self, g):
        g = np.transpose(g, (1, 0, 2)) # y, x, xyz
        pix = self.get_pixel(g[:, :, 0], g[:, :, 1], g[:, :, 2])
        return Image.fromarray(pix, self.img.mode)
    
class mercator_on_sphere (sphereimage):
    def map(self, x, y, z):
        x, y = convert.pt_to_mercator(x, y, z)
        return _sca(x, self.width), _sca(y, self.height)

class cybermercator (sphereimage):
    def __init__(self, img):
        super().__init__(img)
    
    def map(self, x, y, z):
        x, y = convert.pt_to_mercator(x, y, z)
        return _sca(x, self.width), _sca(y, self.height)
    
    def imagefromgrid(self, g):
        g = np.transpose(g, (1, 0, 2)) # y, x, xyz
        x, y, z = convert.pt_to_sphere(g[:, :, 0], g[:, :, 1], g[:, :, 2])
        pix = self.get_pixel(g[:, :, 0], g[:, :, 1], g[:, :, 2])
        R, G, B = pix[:, :, 0], pix[:, :, 1], pix[:, :, 2]
        L = R * 299/1000 + G * 587/1000 + B * 114/1000
        pix[:, :, 0] = 0
        pix[:, :, 1] = L
        pix[:, :, 2] = 0
        lat = np.remainder(z[:, :], 0.02)
        pix[lat < 0.005] = [0, 20, 0]
        return Image.fromarray(pix, self.img.mode)
        
    
class disk_on_sphere (sphereimage):
    def __init__(self, img, degre):
        super().__init__(img)
        self.rad = degre / 180 * np.pi
    
    def map(self, x, y, z):
        x, y, z = convert.pt_to_sphere(x, y, z)
        x, y = (
            np.cos(self.rad) * x - np.sin(self.rad) * y,
            np.sin(self.rad) * x + np.cos(self.rad) * y
        )
        x = (x + 1) / 2
        z = (1 - z) / 2
        #return _sca(x, self.width), _sca(z, self.height), self.which * y >= 0
        #mask = np.logical_and.reduce((y <= 0, x >= 0, x < 1, z >= 0, z < 1))
        #revs = np.logical_not(mask)
        #x[revs] = 0
        #z[revs] = 0
        return _sca(x, self.width), _sca(z, self.height), y <= 0
        
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

def composecubemap(projs, m, out):
    gr = grid.makegrids(m)
    for i in range(6):
        print("image %d" % i)
        for (j, p) in enumerate(projs):
            if j == 0:
                img = p.imagefromgrid(gr[i])
            else:
                tmp = p.imagefromgrid(gr[i])
                img.alpha_composite(tmp)
                #img.paste(tmp, mask=tmp)
        img.save(out % i)

def cut_out_disc(im):
    out = im.convert('RGBA')
    buf = np.array(out)
    h, w, _ = buf.shape
    y, x = np.meshgrid(np.linspace(-1, 1, h), np.linspace(-1, 1, w))
    r2 = y**2 + x**2
    mask = np.zeros_like(r2)
    mask[r2 >= 1] = 0
    mask[r2 < 1] = 255 * ((1 - r2[r2 < 1]) / (1 - 0.9)) ** 0.2
    mask[r2 < 0.9] = 255
    buf[..., -1] = mask.astype(np.int)
    return Image.fromarray(buf, 'RGBA')

if __name__ == "__main__":
    print("Make regular cubemap? [y/N] ", end="")
    if input().strip() in ["y", "yes"]:
        imgs = "satellite.png",
        projs = [cybermercator(Image.open(_)) for _ in imgs]
        composecubemap(projs, 1024, "satellite-%d.png")
        #composecubemap(projs, 512, "satellite-%d.png") # whee
    
    print("Make GOES? [y/N] ", end="")
    if input().strip() in ["y", "yes"]:
        imgs = "satellite-goes-east.png", "satellite-goes-west.png"
        disc = [cut_out_disc(Image.open(_)) for _ in imgs]
        projs = [
            disk_on_sphere(disc[0], 75 - 90),
            disk_on_sphere(disc[1], 135 - 90),
            #disk_on_sphere(disc[0], 0)
            #disk_on_sphere(disc[0], np.pi / 2),
            #disk_on_sphere(disc[1], +1)
        ]
        composecubemap(projs, 512, "satellite-goes-%d.png")
    
    pass
    