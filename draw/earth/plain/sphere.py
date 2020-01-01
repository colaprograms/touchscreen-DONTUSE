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
from projec import pt2sphere

# atashi iya ne
class roundedplate:
    def __init__(self, path):
        self.grid()
        self.nodePath.reparentTo(path)
            
    def grid(self):
        self.format = GeomVertexFormat.getV3n3c4t2()
        self.vdata = GeomVertexData('quadFace', self.format, Geom.UHDynamic)
        for attr in ['vertex', 'normal', 'color', 'texcoord']:
            setattr(self, attr, GeomVertexWriter(self.vdata, attr))
        
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
                X, Y, Z = pt2sphere(x, y)
                self.vertex.addData3f(X, Y, Z)
                self.normal.addData3f(X, Y, Z)
                self.texcoord.addData2f(u, v)

        triangles = []
        
        class newtriangle:
            def __init__(self):
                self.triangle = GeomTriangles(Geom.UHDynamic)
            
            def pt(self, i, j):
                self.triangle.addVertex(i * POINTS + j)
                return self
        
            def put_in(self, triangles):
                self.triangle.closePrimitive()
                triangles.append(self.triangle)
        
        for i in range(POINTS - 1):
            for j in range(POINTS - 1):
                (newtriangle()
                    .pt(i, j)
                    .pt(i, j+1)
                    .pt(i+1, j)
                    .put_in(triangles)
                )
                
                (newtriangle()
                    .pt(i, j+1)
                    .pt(i+1, j+1)
                    .pt(i+1, j)
                    .put_in(triangles)
                )
                
        mesh = Geom(self.vdata)
        for t in triangles:
            mesh.addPrimitive(t)
        mnode = GeomNode('quadface')
        mnode.addGeom(mesh)
        self.nodePath = base.render.attachNewNode(mnode)
        return self.nodePath
    
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
        
        for (j, side) in enumerate(roundedplate.sides.keys()):
            te = loader.loadTexture("satellite-%d.png" % j)
            te.setMinfilter(SamplerState.FT_linear_mipmap_linear)
            te.setAnisotropicDegree(16)
            te.setWrapU(Texture.WM_clamp)
            te.setWrapV(Texture.WM_clamp)
            (roundedplate(planet)
                .side(side)
                .texture(te)
            )
        
        planet.setScale(1/2) # iya
        planet.setMaterial(material)
        self.nodePath = planet

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
        
        planet(base.render)
        
        light = plight()
        light.on()
        
        """
        planet = NodePath('planet')
        shaders = Shader.load(Shader.SLGLSL, 'vert.glsl', 'frag.glsl')
        planet.setShader(shaders)
        planet.reparentTo(base.render)
        
        for (j, side) in enumerate(roundedplate.sides.keys()):
            te = loader.loadTexture("satellite-%d.png" % j)
            te.setWrapU(Texture.WM_clamp)
            te.setWrapV(Texture.WM_clamp)
            (roundedplate(planet)
                .side(side)
                .texture(te)
            )
        """
        
        self.taskMgr.add(self.rotator, "rotateplanet")

        self.taskMgr.add(self.cameracontrol, "cameramove")
        self.pausecontrol = False
        def out():
            self.pausecontrol = not self.pausecontrol
            base.oobe()
        self.accept("o", out)
        
    def rotator(self, task):
        planet = render.find("planet")
        planet.setHpr(task.time, 0, 0)
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
