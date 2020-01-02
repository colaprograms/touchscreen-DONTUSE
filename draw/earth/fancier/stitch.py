from PIL import Image
from urllib.request import urlopen
import time

def stitch_tiles_from_url(url, zoomlevel, bbox=None):
    ntiles = 1 << zoomlevel
    
    if bbox is None:
        i0 = 0
        i1 = ntiles - 1
        j0 = 0
        j1 = ntiles - 1
    else:
        i0, j0, i1, j1 = bbox
    
    tilesize = None
    
    def makeimage_once_tilesize_known(mode, size):
        if size[0] != size[1]:
            raise Exception("tiles are not square!?")
        if size[0] > 1024:
            raise Exception("tiles are too big.")
        
        tilesize = size[0]
        w, h = size[0] * (j1 - j0), size[0] * (i1 - i0)
        print("creating (%s, (%d, %d))" % (mode, w, h))
        return tilesize, Image.new(mode, (w, h))
        
    for i in range(i1 - i0):
        for j in range(j1 - j0):
            print("getting %d %d" % (i + i0, j + j0))
            u = url % (zoomlevel, i + i0, j + j0)
            r = urlopen(u)
            assert r.headers.get_content_type() in ["image/jpeg", "image/png"]
            tile = Image.open(r)
            if tilesize is None:
                tilesize, img = makeimage_once_tilesize_known(tile.mode, tile.size)
            img.paste(tile, (tilesize * j, tilesize * i))
            time.sleep(1)
    return img

class epsg3857:
    # mercator projection
    URL = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/"
    BLUEMARBLESHADED = URL + "BlueMarble_ShadedRelief/" +\
                       "default/GoogleMapsCompatible_Level8/%d/%d/%d.jpeg"
    
    GOESEAST = URL + "GOES-East_ABI_Band2_Red_Visible_1km/default/default/1km/%d/%d/%d.png"
    
class marble:
    #URL_EPSG3413 = "https://gibs.earthdata.nasa.gov/wmts/epsg3413/best/Blue_Marble_Extended/default/1.5km/%d/%d/%d.jpeg"
    
    @staticmethod
    def arctic(zoomlevel):
        return stitch_tiles_from_url(marble.URL_EPSG3413, zoomlevel)
    
    @staticmethod
    def mercator(zoomlevel):
        return stitch_tiles_from_url(epsg3857.BLUEMARBLESHADED, zoomlevel)
    
    @staticmethod
    def goeseast():
        return stitch_tiles_from_url(epsg3857.GOESEAST, 4, (0, 1, 9, 10))

if __name__ == "__main__":
    img = marble.goeseast()
    img.save("satellite-goeseast.png")
    