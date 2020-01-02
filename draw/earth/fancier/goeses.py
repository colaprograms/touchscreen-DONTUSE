from urllib.request import urlopen
import numpy as np
from PIL import Image
from bs4 import BeautifulSoup

G16 = "https://www.star.nesdis.noaa.gov/GOES/fulldisk.php?sat=G16"
G17 = "https://www.star.nesdis.noaa.gov/GOES/fulldisk.php?sat=G17"
GOES16 = {
    "json": "https://rammb-slider.cira.colostate.edu/data/json/goes-16/full_disk/geocolor/latest_times.json",
    "img": "https://rammb-slider.cira.colostate.edu/data/imagery/%s/goes-16---full_disk/geocolor/%s/%02d/%03d_%03d.png"
}

GOES17 = {
    "json": "https://rammb-slider.cira.colostate.edu/data/json/goes-17/full_disk/geocolor/latest_times.json",
    "img": "https://rammb-slider.cira.colostate.edu/data/imagery/%s/goes-17---full_disk/geocolor/%s/%02d/%03d_%03d.png"
}

def soupfrom(url):
    r = urlopen(url)
    return BeautifulSoup(r, 'html.parser')

def _img(u):
    r = urlopen(u)
    assert r.headers.get_content_type() in ["image/jpeg", "image/png"]
    img = Image.open(r)
    print("got", img)
    return img

def geocolor(u):
    soup = soupfrom(u)
    for c in soup.select("div.summaryContainer"):
        head = c.select("h2")
        if len(head) == 1 and head[0].text == "GeoColor":
            for link in c.select("a"):
                if "5424x5424.jpg" in link['href']:
                    return link['href']
    return None

def geocolos(u):
    
BBOX = (0, 9, 5424, 9 + 5364)

def mangle(im):
    return im.crop(BBOX).resize((4096, 4096), Image.LANCZOS)
    
if __name__ == "__main__":
    goeseast = geocolor(G16)
    goeswest = geocolor(G17)
    stale = {'east': True, 'west': True}
    try:
        lasturls = open("goeses-lasturls.txt").readlines()
        if len(lasturls) == 2:
            e, w = (_.strip() for _ in lasturls)
            if e == goeseast:
                stale['east'] = False
            if w == goeswest:
                stale['west'] = False
    except FileNotFoundError:
        pass
    if stale['east']:
        print("getting new east: %s" % goeseast)
        mangle(_img(goeseast)).save("satellite-goes-east.png")
        pass
    if stale['west']:
        print("getting new west: %s" % goeswest)
        mangle(_img(goeswest)).save("satellite-goes-west.png")
        pass
    open("goeses-lasturls.txt", "w").write("%s\n%s\n" % (goeseast, goeswest))
    