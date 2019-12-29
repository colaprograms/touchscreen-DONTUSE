from PIL  import Image
import numpy as np

def round(x, size):
    return int((x + 1) / 2 * size)

class earths:
    def __init__(self):
        self.im = np.array(
            Image.open("satelliteh.png")
        )
        self.height, self.width, _ = self.im.shape
        self.cim = np.cumsum(np.cumsum(self.im, axis=0), axis=1)

    _z = np.zeros((3,), dtype=np.uint32)

    def cumsumat(self, x, y):
        if x == 0 or y == 0:
            return earths._z
        return self.cim[y - 1, x - 1, :] #[y - 1, x - 1]

    def getsum(self, x0, y0, x1, y1):
        ff = self.cumsumat
        return (ff(x1, y1) - ff(x0, y1) - ff(x1, y0) + ff(x0, y0)).astype(np.float64)

    def getavg(self, x0, y0, x1, y1):
        x0, y0, x1, y1 = [int(z) for z in (x0, y0, x1, y1)]
        x0 %= self.width
        x1 %= self.width
        #print x0, y0, x1, y1
        assert x0 != x1
        assert y0 < y1
        if x0 > x1:
            #accum = self.getsum(0, x1, y0, y1) + self.getsum(x0, self.width, y0, y1)
            accum = self.getsum(0, y0, x1, y1) + self.getsum(x0, y0, self.width, y1)
            count = x1 + self.width - x0
            count *= y1 - y0
            return accum / count
        else:
            return self.getsum(x0, y0, x1, y1) / ((y1 - y0) * (x1 - x0))
            #return self.getsum(x0, x1, y0, y1) / ((y1 - y0) * (x1 - x0))

    def getpixel(self, rotation, x, y):
        SIZE = 100.0
        x = (x - 64.0) / SIZE * 2
        y = (y - 64.0) / SIZE * 2
        if x*x + y*y >= 1:
            return (0, 0, 0)
        f = lambda x: np.arcsin(x) / np.pi + 2*rotation
        HALFPIXEL = 1.0/128
        x0 = f(x - HALFPIXEL)
        x1 = f(x + HALFPIXEL)
        y0 = y - HALFPIXEL
        y1 = y + HALFPIXEL
        if y0 < -1:
            y0 = -1
        if y1 > 1:
            y1 = 1
        x0 = (x0 + 1) * self.width / 2
        x1 = (x1 + 1) * self.width / 2
        y0 = (y0 + 1) * self.height / 2
        y1 = (y1 + 1) * self.height / 2
        return self.getavg(x0, y0, x1, y1)

    #def displayat(self, rotation):
    def displayat(self, rot):
        bf = np.zeros((128, 128, 3), dtype=np.uint8)
        for j in range(128):
            for i in range(128):
                bf[i, j, :] = self.getpixel(rot, j, i)
        return bf

    def makeim(self):
        for j in range(360):
            rot = 1.0 / 360 * j
            img = self.displayat(rot)
            Image.fromarray(img).save("finnearth/%03d.png" % j)
            print("saved %d" % j)
            
if __name__ == "__main__":
    earths().makeim()