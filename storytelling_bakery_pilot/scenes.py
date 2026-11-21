import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
COL = { 'ink':(.055,.08,.13), 'teal':(.12,.46,.47), 'cream':(.96,.72,.44), 'red':(.83,.30,.21), 'skin':(.8,.51,.35), 'blue':(.22,.38,.70), 'road':(.15,.24,.29), 'gold':(.96,.68,.21), 'light':(.85,.89,.80) }
def paint(o,c):
    o.color=(*COL[c],1)
    return o
def box(at,size,c,edge=.10):
    bpy.ops.mesh.primitive_cube_add(size=1,location=at)
    o=bpy.context.object
    o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if edge:
        m=o.modifiers.new('Rounded edges','BEVEL');m.width=edge;m.segments=3
    return paint(o,c)
def ball(at,size,c):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=at)
    o=bpy.context.object;o.scale=size
    return paint(o,c)
def person(x,y,c,scale=1):
    box((x,y,.8*scale),(.68*scale,.48*scale,1.2*scale),c)
    ball((x,y,1.62*scale),(.32*scale,.29*scale,.35*scale),'skin')
    ball((x,y+.025,1.78*scale),(.33*scale,.28*scale,.22*scale),'ink')
    for dx in (-.17,.17):box((x+dx*scale,y,.27*scale),(.21*scale,.25*scale,.54*scale),'ink')
def camera(pos,aim,scale):
    bpy.ops.object.camera_add(location=pos)
    cam=bpy.context.object;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO';cam.data.ortho_scale=scale
    bpy.context.scene.camera=cam
def init():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=672;sc.render.resolution_y=1194
    sc.render.resolution_percentage=100
    sh=sc.display.shading;sh.light='STUDIO';sh.color_type='OBJECT';sh.background_type='WORLD'
    sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.show_specular_highlight=True
    sc.world=bpy.data.worlds.new('Dawn');sc.world.color=(.08,.13,.18)
    sc.view_settings.view_transform='Standard'
    return sc
def render(name):
    sc=bpy.context.scene;sc.render.filepath=str(ROOT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
def street():
    box((0,0,-.20),(35,35,.4),'road',0)
    box((0,2,.02),(13,4,.15),'light')
    box((0,3.1,2.3),(8.5,2.4,4.6),'cream')
    box((0,1.86,3.7),(8.8,.4,.55),'teal')
    for i in range(12):box(((i-5.5)*.69,1.39,3.25),(.70,1.45,.17),'red' if i%2 else 'cream',.035)
    box((0,1.83,1.24),(1.38,.16,2.44),'ink')
    box((0,1.72,1.25),(1.12,.09,2.12),'teal')
    ball((.37,1.62,1.18),(.067,.05,.07),'gold')
    for x in (-2.65,2.65):
        box((x,1.84,1.52),(2.8,.14,1.93),'ink')
        box((x,1.74,1.57),(2.58,.10,1.68),'teal')
        for k in range(3):box((x-.75+k*.76,1.64,.95),(.49,.13,.27),'gold')
    for i,(x,y) in enumerate([(-.35,.9),(-.85,.18),(-1.37,-.61),(-1.8,-1.44),(-2.35,-2.15)]):
        person(x,y,['red','blue','teal','gold','blue'][i])
init();street();camera((8,-13,7),(0,.15,2.05),9.3);render('queue')
init()
box((0,0,-.18),(30,30,.35),'ink')
box((0,0,.05),(6,5,.3),'road')
box((-.6,0,.25),(2.45,3.75,.22),'teal')
box((-.6,0,.39),(2.21,3.47,.09),'light')
box((-.6,.43,.45),(1.9,.77,.06),'blue')
box((1.15,-.22,.40),(1.85,.21,.11),'gold')
box((1.83,-.34,.40),(.26,.45,.12),'gold')
bpy.ops.mesh.primitive_torus_add(location=(.32,-.22,.41),major_radius=.36,minor_radius=.10)
paint(bpy.context.object,'gold')
camera((2,-4,8),(0,0,.33),6.0);render('keys')
