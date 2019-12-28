from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import PerlinNoise2, PNMImage, PointLight, Shader, Texture, Vec3, Vec4

from pandac.PandaModules import *

import numpy as np

# atashi iya ne
class roundedplate:
    def __init__(self, path):
        self.format = GeomVertexFormat.getV3n3c4t2()
        self.vdata = GeomVertexData('quadFace', self.format, Geom.UHDynamic)
        for attr in ['vertex', 'normal', 'color', 'texcoord']:
            setattr(self, attr, GeomVertexWriter(self.vdata, attr))
        self.grid()
        self.nodePath.reparentTo(path)
            
    def grid(self):
        POINTS = 17
        points = np.linspace(-1, 1, POINTS)
        for i in range(POINTS):
            for j in range(POINTS):
                x = points[j]
                y = points[i]
                u = (x + 1) / 2
                v = (y + 1) / 2
                self.vertex.addData3f(x, y, 0)
                self.normal.addData3f(
                    Vec3(2 * x - 1, 2 * y - 1, -1).normalize()
                )
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
    
class Planet(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        planet = NodePath('planet')
        shaders = Shader.load(Shader.SLGLSL, 'vert.glsl', 'frag.glsl')
        planet.setShader(shaders)
        planet.reparentTo(base.render)

        te = loader.loadTexture('directions.png')
        for side in roundedplate.sides:
            (roundedplate(planet)
                .side(side)
                .texture(te)
            )
            
        #self.pandaActor = Actor("panda-model", {"walk": "panda-walk4"})
        #self.pandaActor.setScale(0.005, 0.005, 0.005)
        #self.pandaActor.reparentTo(self.render)
        #self.pandaActor.loop("walk")

        '''The side meshes are rotated here. They are moved to their correct
        position in the shader'''

        """
        m = create_mesh(True)
        m.reparentTo(planet)
        m.setHpr(0, 0, 0)
        m = create_mesh(True)
        m.reparentTo(planet)
        m.setHpr(0, 180, 0)

        m = create_mesh(True)
        m.reparentTo(planet)
        m.setHpr(0, -90, 0)
        m = create_mesh()
        m.reparentTo(planet)
        m.setHpr(0, 90, 0)

        m = create_mesh(True)
        m.reparentTo(planet)
        m.setHpr(0, 0, -90)
        m = create_mesh(True)
        m.reparentTo(planet)
        m.setHpr(0, 0, 90)
        """


app = Planet()
app.run()
