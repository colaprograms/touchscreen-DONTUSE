from PIL import Image

def create():
    TILESIZE = 256
    NTILES = 32
    img = Image.new('RGB', (TILESIZE * NTILES, TILESIZE * NTILES))
    for i in range(NTILES):
        for j in range(NTILES):
            tile = Image.open(f"{5}/{j}/{i}.png")
            img.paste(tile, (TILESIZE * j, TILESIZE * i))
    img.save("stitched.png")

if __name__ == "__main__":
    create()