from PIL import Image
from urllib.request import urlopen
import time
import numpy

def _img(u):
    r = urlopen(u)
    assert r.headers.get_content_type() in ["image/jpeg", "image/png"]
    img = Image.open(r)
    print("got", img)
    return img
    
class stitch:
    def __init__(self, zoomlevel):
        self.zoomlevel = zoomlevel
        self.ntiles = 1 << zoomlevel
        self.tilesize = None
    
    def makeimage_once_tilesize_known(self, tile):
        size = tile.size
        mode = tile.mode
        
        if size[0] != size[1]:
            raise Exception("tiles are not square!?")
        if size[0] > 1024:
            raise Exception("tiles are too big.")
        
        self.tilesize = size[0]
        self.img = Image.new(mode, (self.tilesize * self.ntiles, self.tilesize * self.ntiles))
        print("created (%s, (%d, %d))" % (mode, self.img.size[0], self.img.size[1]))
        
    def pastetile(self, i, j, tile):
        # if the image is RGBA and totally blank, then we ignore it
        if tile.mode == "RGBA" and numpy.all(numpy.array(tile) == 0):
            return
        if self.tilesize is None:
            self.makeimage_once_tilesize_known(tile)
        else:
            assert tile.size == (self.tilesize, self.tilesize)
            if tile.mode != self.img.mode:
                raise Exception("modes differ. tile.mode %s, self.img.mode %s" % (tile.mode, self.img.mode))
        self.img.paste(
            tile,
            box = (self.tilesize * j, self.tilesize * i),
            mask = tile.split()[-1]
        )
        
    def paste(self, i, j, url):
        u = url % (self.zoomlevel, i, j)
        print("loading %s" % u)
        tile = _img(u)
        self.pastetile(i, j, tile)
    
    def get(self, url, bbox=None):
        if bbox is None:
            i0 = 0
            i1 = self.ntiles
            j0 = 0
            j1 = self.ntiles
        else:
            i0, j0, i1, j1 = bbox
            i1 += 1
            j1 += 1
        
        for i in range(i0, i1):
            for j in range(j0, j1):
                self.paste(i, j, url)
                time.sleep(1)

class epsg3857:
    # mercator projection
    URL = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/"
    BLUEMARBLESHADED = URL + "BlueMarble_ShadedRelief/" +\
                       "default/GoogleMapsCompatible_Level8/%d/%d/%d.jpeg"
    
    GOESEAST = URL + "GOES-East_ABI_Band2_Red_Visible_1km/default/default/1km/%d/%d/%d.png"
    GOESWEST = URL + "GOES-West_ABI_Band2_Red_Visible_1km/default/default/1km/%d/%d/%d.png"
    
class marble:
    #URL_EPSG3413 = "https://gibs.earthdata.nasa.gov/wmts/epsg3413/best/Blue_Marble_Extended/default/1.5km/%d/%d/%d.jpeg"
    
    @staticmethod
    def arctic(zoomlevel):
        return stitch_tiles_from_url(marble.URL_EPSG3413, zoomlevel)
    
    @staticmethod
    def mercator(zoomlevel):
        return stitch_tiles_from_url(epsg3857.BLUEMARBLESHADED, zoomlevel)
    
    @staticmethod
    def goes():
        #st = stitch(4)
        #st.get(epsg3857.GOESEAST, (0, 1, 9, 10))
        #st.get(epsg3857.GOESWEST, (0, 0, 9, 6))
        #st.get(epsg3857.GOESWEST, (0, 17, 9, 19))
        st = stitch(2)
        st.get(epsg3857.GOESWEST, (0, 0, 2, 1))
        st.get(epsg3857.GOESWEST, (0, 4, 2, 4))
        st.get(epsg3857.GOESEAST, (0, 0, 2, 2))
        st.img.save("satellite-goes.png")
    
if __name__ == "__main__":
    marble.goes()