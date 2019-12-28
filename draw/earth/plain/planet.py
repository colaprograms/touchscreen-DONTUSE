from pandac.PandaModules import loadPrcFileData

loadPrcFileData('', 'frame-rate-meter-scale 0.035')
loadPrcFileData('', 'frame-rate-meter-side-margin 0.1')
loadPrcFileData('', 'show-frame-rate-meter 1')
loadPrcFileData('', 'window-title ' + "Vortex")
loadPrcFileData('', "sync-video 0")
loadPrcFileData('', 'basic-shaders-only #f')

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import PerlinNoise2, PNMImage, PointLight, Shader, Texture, Vec3, Vec4
from direct.filter.CommonFilters import CommonFilters

from pandac.PandaModules import *

#def toggleWireframe():
#    base.toggleWireframe()

#base.accept('w', toggleWireframe)


def myNormalize(myVec):
    myVec.normalize()
    return myVec

format = GeomVertexFormat.getV3n3c4t2()
vdata = GeomVertexData('quadFace', format, Geom.UHDynamic)
vertex = GeomVertexWriter(vdata, 'vertex')
normal = GeomVertexWriter(vdata, 'normal')
color = GeomVertexWriter(vdata, 'color')
texcoord = GeomVertexWriter(vdata, 'texcoord')

def create_mesh(debug=False):
    '''This creates a simple 17x17 grid mesh for the sides of our cube.
    The ultimate goal is to use a LOD system, probably based on quadtrees.
    If debug is true then we get a color gradiant on our vertexes.'''
    x = -1.0
    y = -1.0
    vertex_count = 0
    u = 0.0
    v = 1.0

    WIDTH_STEP = 2/16.0

    while y <= 1.0:
        while x <= 1.0:
            vertex.addData3f(x, y, 0)
            normal.addData3f(myNormalize((Vec3(2*x-1, 2*y-1, 2*0-1))))
            if debug:
                color.addData4f(1.0, u, v, 1.0)
            texcoord.addData2f(u, v)
            vertex_count += 1
            x += WIDTH_STEP
            u += WIDTH_STEP/2.0
        x = -1.0
        u = 0
        y += WIDTH_STEP
        v -= WIDTH_STEP/2.0

    print(vertex_count)
    triangles = []

    for y in range(0, 16):
        for x in range(0, 16):
            v = 17 * y + x
            tri = GeomTriangles(Geom.UHDynamic)
            tri.addVertex(v)
            tri.addVertex(v+1)
            tri.addVertex(v+17)
            tri.closePrimitive()
            triangles.append(tri)

            tri = GeomTriangles(Geom.UHDynamic)
            tri.addVertex(v+1)
            tri.addVertex(v+18)
            tri.addVertex(v+17)
            
            tri.closePrimitive()
            triangles.append(tri)

    mesh = Geom(vdata)
    for t in triangles:
        mesh.addPrimitive(t)
    mnode = GeomNode('quadface')
    mnode.addGeom(mesh)
    nodePath = base.render.attachNewNode(mnode)
    return nodePath

'''planet is a parent nodepath that the 6 side mesh nodepaths will parent to.
planet can be moved, scale, and rotated with no problems'''

class Planet(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        planet = NodePath('planet')
        shaders = Shader.load(Shader.SLGLSL, 'vert.glsl', 'frag.glsl')
        planet.setShader(shaders)
        planet.reparentTo(base.render)

        self.pandaActor = Actor("panda-model", {"walk": "panda-walk4"})
        self.pandaActor.setScale(0.005, 0.005, 0.005)
        self.pandaActor.reparentTo(self.render)
        self.pandaActor.loop("walk")

        '''The side meshes are rotated here. They are moved to their correct
        position in the shader'''

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

app = Planet()
app.run()
