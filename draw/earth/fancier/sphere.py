from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import PerlinNoise2, PNMImage, PointLight, Shader, Texture, Vec3, Vec4, loadPrcFileData

# atashi iya ne
loadPrcFileData('', """
    frame-rate-meter-side-margin 0.1
    show-frame-rate-meter 1
    framebuffer-multisample 1
    multisamples 2
""")

from pandac.PandaModules import *
from direct.task import Task
import numpy as np
from projec import convert

class mesh:
    def __init__(self, path):
        self.nodePath = self.mesh()
        self.nodePath.reparentTo(path)
    
    def mesh(self):
        self.format = GeomVertexFormat.getV3n3c4t2()
        self.data = GeomVertexData('quadFace', self.format, Geom.UHStatic)
        for attr in ['vertex', 'normal', 'color', 'texcoord']:
            setattr(self, attr, GeomVertexWriter(self.data, attr))
        self.triangles = GeomTriangles(Geom.UHStatic)
        self.create()
        
        mesh = Geom(self.data)
        mesh.addPrimitive(self.triangles)
        mnode = GeomNode('quadface')
        mnode.addGeom(mesh)
        
        return base.render.attachNewNode(mnode)
        
    def addvertex(self, pos, nor, tex):
        self.vertex.addData3f(*pos)
        self.normal.addData3f(*nor)
        self.texcoord.addData2f(*tex)
    
    def addtriang(self, i, j, l):
        self.triangles.addVertices(i, j, l)

    def create(self):
        raise NotImplementedError()

class cube(mesh):
    def create(self):
        for x in [-1, 1]:
            for y in [-1, 1]:
                for z in [-1, 1]:
                    r = (x*x + y*y + z*z)**0.5
                    self.addvertex((x, y, z), (x/r, y/r, z/r), (0, 0))
        
        def do(a, b, c):
            self.addtriang(a, a^b, a^c)
            self.addtriang(a^c, a^b, a^b^c)
        
        # sides
        do(0, 4, 1)
        do(0, 2, 4)
        do(2, 1, 4)
        do(1, 4, 2)
        #top
        do(4, 2, 1)
        #bottom
        do(0, 1, 2)
        
    def texture(self, te):
        self.nodePath.setTexture(te)
class roundedplate(mesh):
    def create(self):
        POINTS = 33
        points = np.linspace(-1, 1, POINTS)
        for i in range(POINTS):
            for j in range(POINTS):
                x = points[j]
                y = points[i]
                u = (x + 1) / 2
                v = (y + 1) / 2
                #u = u * 0.999 + 0.0005
                #v = v * 0.999 + 0.0005
                X, Y, Z = convert.pt_to_sphere(x, y, 1)#pt2sphere(x, y)
                self.addvertex( (X, Y, Z), (X, Y, Z), (u, v) )
        
        def what(i, j):
            return POINTS * i + j
        
        for i in range(POINTS - 1):
            for j in range(POINTS - 1):
                self.addtriang(
                    what(i, j),
                    what(i, j+1),
                    what(i+1, j)
                )
                self.addtriang(
                    what(i, j+1),
                    what(i+1, j+1),
                    what(i+1, j)
                )
        
    sides = {
        "top": (0, 0, 0),
        "bottom": (0, 0, 180),
        "front": (0, 90, 180),
        "back": (0, 90, 0),
        "left": (0, 90, -90),
        "right": (0, 90, 90)
    }
    
    def side(self, which):
        self.nodePath.setHpr( *roundedplate.sides[which] )
        return self
        
    def texture(self, te):
        self.nodePath.setTexture(te, 3)
        return self
    
    def overlay(self, ts, te):
        self.nodePath.setTexture(ts, te)
        return self

    def clear(self, ts):
        self.nodePath.clearTexture(ts)
def maketexture(fn):
    te = loader.loadTexture(fn)
    te.setMinfilter(SamplerState.FT_linear_mipmap_linear)
    te.setAnisotropicDegree(16)
    te.setWrapU(Texture.WM_clamp)
    te.setWrapV(Texture.WM_clamp)
    return te
    
class planet:
    def __init__(self, nodepath):
        self.init()
        self.nodePath.reparentTo(nodepath) # iya
        
    def init(self):
        planet = NodePath('planet')
        #shaders = Shader.load(Shader.SLGLSL, 'vert.glsl', 'frag.glsl')
        #planet.setShader(shaders)
        
        material = Material()
        #material.setShininess(0.1)
        material.setShininess(1)
        material.setSpecular((0.2, 0.2, 0.2, 1))
        
        self.ov = TextureStage('overlay')
        self.ov.setMode(TextureStage.MDecal)
        self.textures = []
        self.overlays = []
        
        self.cube = []
        for (j, side) in enumerate(roundedplate.sides.keys()):
            self.textures.append( maketexture("satellite-%d.png" % j) )
            self.overlays.append( maketexture("satellite-goes-%d.png" % j) )
            #te = maketexture("satellite-%d.png" % j)
            #t2 = maketexture("satellite-goes-%d.png" % j)
            self.cube.append(
                roundedplate(planet)
                    .side(side)
                    
            )
 
        self.texture()
        
        planet.setScale(1/2) # iya
        planet.setMaterial(material)
        self.nodePath = planet
    
    def texture(self):
        for c, t, t2 in zip(self.cube, self.textures, self.overlays):
            (c.texture(t)
                .overlay(self.ov, t2)
            
            )
            
        #for _ in self.cube:
        #    _.texture(self.te).overlay(self.ov, self.t2)
    
    def overlayswitch(self, which):
        if which:
            self.texture()
        else:
            for c in self.cube:
                c.clear(self.ov)
                
class plight:
    def __init__(self):
        spot = Spotlight('spot')
        lens = PerspectiveLens()
        spot.setLens(lens)
        spot.setColor((1, 1, 1, 1))
        
        ambi = AmbientLight('ambient')
        ambi.setColor((0.4, 0.4, 0.4, 1))
        
        spotNP = render.attachNewNode(spot)
        spotNP.setPos(-1, -2, 1)
        #spotNP.setPos(-1, -2, 0)
        spotNP.lookAt(0, 0, 0)
        
        ambiNP = render.attachNewNode(ambi)
        
        self.spotNP = spotNP
        self.ambiNP = ambiNP
        self.lights = [self.spotNP, self.ambiNP]
    
    def on(self, bool=True):
        f = render.setLight if bool else render.clearLight
        for l in self.lights:
            f(l)
        
class Planet(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        base.setBackgroundColor(0, 0, 0)
        
        render.setShaderAuto()

        render.setAntialias(AntialiasAttrib.MMultisample)
        base.disableMouse()
        base.camLens.setNearFar(0.1, 20)
        
        p = planet(base.render)
        
        """
        cuby = cube(base.render)
        material = Material()
        material.setShininess(1)
        material.setSpecular((1, 0.2, 0.2, 1))
        cuby.nodePath.setScale(1/10)
        cuby.nodePath.setPos(0, -1, 0)
        cuby.nodePath.setMaterial(material)
        cuby.nodePath.reparentTo(p.nodePath)
        """
        
        light = plight()
        light.on()
        
        self.taskMgr.add(self.rotator, "rotateplanet")

        self.taskMgr.add(self.cameracontrol, "cameramove")
        self.pausecontrol = False
        self.overlaycontrol = True
        
        #def out():
        #    self.pausecontrol = not self.pausecontrol
        #    base.oobe()
        
        #self.accept("o", out)
        
        def tsswitch():
            print("switching")
            self.overlaycontrol = not self.overlaycontrol
            p.overlayswitch(self.overlaycontrol)
        
        self.accept("o", tsswitch)
            
    def rotator(self, task):
        planet = render.find("planet")
        planet.setHpr(task.time*3, 0, 0)
        return Task.cont

    def cameracontrol(self, task):
        if self.pausecontrol:
            return
        
        def mouse():
            props = base.win.getProperties()
            w, h = props.getXSize(), props.getYSize()
            r = w / h
            if base.mouseWatcherNode.hasMouse():
                x, y = base.mouseWatcherNode.getMouseX(), base.mouseWatcherNode.getMouseY()
                return x * r, y, r
                # rar
            else:
                return 0, 0, r
                
        planet = render.find("planet")
        x, y, r = mouse()
        # atashi iya ne
        offset = LVector3(x, -6, y)
        ul, ur, ll, lr = (
            LPoint3(-r, 0, 1) - offset,
            LPoint3(r, 0, 1) - offset,
            LPoint3(-r, 0, -1) - offset,
            LPoint3(r, 0, -1) - offset
        )
        base.camLens.setFrustumFromCorners(ul, ur, ll, lr, Lens.FC_off_axis | Lens.FC_aspect_ratio | Lens.FC_shear)
        base.cam.setPos(offset)
        return Task.cont
    
app = Planet()
app.run()
