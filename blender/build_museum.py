"""Original Renaissance music museum. Run with Blender 5.2+ in background mode.
The editable .blend and the optimized web GLB are produced from the same scene.
Blender coordinates: X across, Y toward apse, Z up. glTF converts up to Y.
"""
import bpy, math, random, os, sys
from mathutils import Vector
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, 'public', 'art', 'renaissance-music-triptych.png')
OUT = os.path.join(ROOT, 'public', 'models', 'ars-sonora.glb')
random.seed(28)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for dat in bpy.data.materials: bpy.data.materials.remove(dat)

def rgba(hexcolor):
    # Convert sRGB to linear: glTF preserves the intended, rich pigment colors.
    rgb = [int(hexcolor[i:i+2],16)/255 for i in (1,3,5)]
    return tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb) + (1,)

def material(name, color, rough=.6, metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=rgba(color); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=rgba(color)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metallic
    return m

ivory=material('Warm carved travertine','#c9bd9f',.72)
lightstone=material('Pale limestone mouldings','#e1d2af',.58)
plaster=material('Ochre lime plaster','#aa9878',.88)
green=material('Deep olive gallery velvet','#333b30',.95)
ochre=material('Coffer recess pigment','#8c7957',.9)
gold=material('Antique gilded bronze','#b28a47',.31,.78)
goldlight=material('Gilt highlights','#d8b974',.25,.73)
walnut=material('Polished walnut','#39251b',.34)
black=material('Ebony lacquer','#141713',.2,.15)
white=material('Ivory piano keys','#e8dcc1',.26)
burgundy=material('Burgundy velvet upholstery','#49271f',.88)
darkmarble=material('Verde marble','#303d34',.27)
marble=material('Carrara marble','#d4cdbc',.32)
rope=material('Braided velvet rope','#4c2921',.86)
paper=material('Aged manuscript paper','#d1bd8e',.9)

def texture_image(mat, kind, size=512):
    """Generate tileable color textures inside Blender, also exportable by glTF."""
    import numpy as np
    y,x=np.mgrid[0:size,0:size].astype(np.float32)/size
    rng=np.random.default_rng(26)
    noise=rng.random((size,size)).astype(np.float32)
    if kind=='marble':
        wave=np.sin(2*math.pi*(x*3+y*2)+np.sin(2*math.pi*(x*5-y*3))*1.8+np.sin(2*math.pi*y*7)*.4)
        veins=np.exp(-np.abs(wave)*28)*.22
        base=np.array([.73,.69,.60],dtype=np.float32)
        colors=base[None,None,:]*(1-veins[:,:,None])+(noise[:,:,None]-.5)*.032
    elif kind=='dark':
        wave=np.sin(2*math.pi*(x*2+y*3)+np.sin(2*math.pi*(x*4-y*2))*1.3)
        veins=np.exp(-np.abs(wave)*38)*.19
        colors=np.array([.041,.065,.046])[None,None,:]+veins[:,:,None]+(noise[:,:,None]-.5)*.012
    else:
        grain=np.sin(x*2*math.pi*36+np.sin(y*2*math.pi*2)*3+np.sin(x*2*math.pi*4)*2)
        colors=np.array([.095,.047,.022])[None,None,:]*(.8+.2*grain[:,:,None])+(noise[:,:,None]-.5)*.009
    pixels=np.ones((size,size,4),dtype=np.float32);pixels[:,:,:3]=np.clip(colors,0,1)
    img=bpy.data.images.new('Texture_'+kind,width=size,height=size,alpha=False)
    img.colorspace_settings.name='Non-Color';img.pixels.foreach_set(pixels.ravel())
    img.filepath_raw=os.path.join(ROOT,'public','textures',kind+'.png');img.file_format='PNG';img.save()
    p=mat.node_tree.nodes.get('Principled BSDF'); tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img
    mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
    img.pack()
texture_image(marble,'marble');texture_image(darkmarble,'dark');texture_image(walnut,'walnut')

def mesh_obj(name,verts,faces,mat):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    if mat: ob.data.materials.append(mat)
    return ob

def cube(name,loc,scale,mat,bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object;ob.name=name;ob.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if mat:ob.data.materials.append(mat)
    if bevel:
        mod=ob.modifiers.new('Carved edge','BEVEL');mod.width=bevel;mod.segments=2
    return ob

def cyl(name,loc,radius,depth,mat,vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    ob=bpy.context.object;ob.name=name;ob.data.materials.append(mat)
    for p in ob.data.polygons:p.use_smooth=len(p.vertices)==4
    bevel=ob.modifiers.new('Turned edge','BEVEL');bevel.width=.012;bevel.segments=2
    return ob

def uvball(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc)
    ob=bpy.context.object;ob.name=name;ob.scale=scale;ob.data.materials.append(mat)
    for p in ob.data.polygons:p.use_smooth=True
    return ob

def curve(name,points,radius,mat,res=3):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12
    spline=c.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
    for bp,co in zip(spline.bezier_points,points):bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
    c.bevel_depth=radius;c.bevel_resolution=res
    ob=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(ob);ob.data.materials.append(mat)
    return ob

def text(name,body,loc,size,mat,rotation=(math.pi/2,0,0),align='CENTER'):
    c=bpy.data.curves.new(name,'FONT');c.body=body;c.size=size;c.align_x=align;c.extrude=.001;c.space_character=1.12
    font='/System/Library/Fonts/Supplemental/Times New Roman.ttf'
    if os.path.exists(font):c.font=bpy.data.fonts.load(font)
    ob=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=rotation;ob.data.materials.append(mat)
    return ob

def lamp(name,loc,power,color,size,target=None,kind='AREA'):
    d=bpy.data.lights.new(name,kind);d.energy=power;d.color=color
    if kind=='AREA':d.shape='DISK';d.size=size
    elif kind=='SPOT':d.spot_size=size;d.spot_blend=.6;d.shadow_soft_size=.3
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc
    if target:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return o

# Continuous inlaid marble floor. A fine brass inlay defines the central promenade.
cube('Foundation',(0,0,-.22),(18.6,33,.4),ivory,0)
for ix in range(12):
    for iy in range(22):
        x=-8.25+ix*1.5;y=-15.75+iy*1.5
        tile=cube('Marble paving', (x,y,.012),(1.494,1.494,.035),marble if (ix+iy)%2 else lightstone,.006)
        if (ix+iy)%3==0:tile.rotation_euler.z=math.pi/2
for x in [-8.7,-5.2,5.2,8.7]:cube('Marble border',(x,0,.04),(.15,32.6,.035),darkmarble,.004)
for y in [-15.7,15.7]:cube('Marble border',(0,y,.04),(17.4,.15,.035),darkmarble,.004)
for x in [-5.05,5.05]:cube('Brass floor inlay',(x,0,.065),(.018,31.2,.008),gold,0)

# Fully enclosed palazzo gallery: no garden, no pavilion, no floating display objects.
for side in [-1,1]:
    cube('Lime plaster wall',(side*9.12,0,3.2),(.35,33,6.4),plaster,.02)
    cube('Walnut dado',(side*8.9,0,.62),(.19,32.7,1.24),walnut,.015)
    for z,w,h in [(1.26,.27,.09),(1.36,.23,.07),(5.95,.4,.15),(6.15,.51,.14),(6.36,.64,.17)]:
        cube('Continuous cornice',(side*8.83,0,z),(w,32.8,h),lightstone,.02)
    cube('Lower skirting',(side*8.82,0,.14),(.28,32.8,.22),darkmarble,.02)
    for y in [-13.8,-6.9,0,6.9,13.8]:
        cube('Pilaster behind column',(side*8.85,y,3.4),(.25,.72,5.5),ivory,.025)
        for z,r,h in [(.24,.61,.32),(.45,.49,.13),(.59,.4,.16),(5.75,.4,.15),(5.91,.53,.17),(6.08,.63,.17)]:
            cyl('Column base and capital',(side*8.4,y,z),r,h,lightstone)
        cyl('Fluted column',(side*8.4,y,3.17),.31,5.1,ivory,48)
        for i in range(16):
            a=i*2*math.pi/16
            cyl('Column flute',(side*8.4+.305*math.cos(a),y+.305*math.sin(a),3.17),.021,4.86,lightstone,8)
        for d in [-.29,.29]:
            uvball('Ionic capital scroll',(side*8.4,y+d,5.86),(.13,.18,.15),gold)

# Elliptical barrel vault and repeated arch ribs.
def arch_point(a,z):return (8.95*math.cos(a),z,6.35+4.7*math.sin(a))
verts=[];faces=[]
for y in [-16.5,16.5]:
    for i in range(65):verts.append(arch_point(i/64*math.pi,y))
for i in range(64):faces.append((i,i+65,i+66,i+1))
vault=mesh_obj('Barrel-vaulted plaster ceiling',verts,faces,plaster)
for poly in vault.data.polygons:poly.use_smooth=True
for y in [-16,-13.8,-6.9,0,6.9,13.8,16]:
    pts=[arch_point(i/48*math.pi,y) for i in range(49)]
    curve('Carved limestone arch rib',pts,.15,lightstone,2)
    for off in [-.22,.22]:curve('Gilded arch fillet',[arch_point(i/48*math.pi,y+off) for i in range(49)],.028,gold,1)
for by in [-10.35,-3.45,3.45,10.35]:
    for k in range(9):
        a0=.05+k*(math.pi-.1)/9+.025;a1=.05+(k+1)*(math.pi-.1)/9-.025
        # Recessed panels with bevel-like nested frames following the vault curve.
        for inset,mat in [(0,lightstone),(.04,gold),(.065,ochre)]:
            aa0=a0+inset;aa1=a1-inset; yy0=by-2.9+inset*5; yy1=by+2.9-inset*5
            ps=[arch_point(aa0,yy0),arch_point(aa1,yy0),arch_point(aa1,yy1),arch_point(aa0,yy1)]
            ps=[(x,y,z-.04-inset) for x,y,z in ps]
            mesh_obj('Inset coffer panel',ps,[(0,1,2,3)],mat)
        ac=(a0+a1)/2
        pos=arch_point(ac,by)
        uvball('Coffer rosette',(pos[0],pos[1],pos[2]-.17),(.12,.12,.045),goldlight)

# Decorative end walls and deep apse, all within the walking boundary.
for y in [-16.35,16.35]:
    cube('End wall',(0,y,3.3),(18.5,.3,6.6),green,.03)
    ps=[(-9,y,6.3),(9,y,6.3)]+[arch_point(i/48*math.pi,y) for i in range(49)]
    mesh_obj('Vault end tympanum',ps,[tuple(range(len(ps)))],plaster)
    for x in [-7,-4.2,4.2,7]:
        cube('End wall pilaster',(x,y-.22 if y>0 else y+.22,3.15),(.32,.28,6.1),ivory,.02)

# Original, generated old-master artwork. UV thirds select each complete panel.
painting_image=bpy.data.images.load(ART);painting_image.pack()
artmats=[]
for i in range(3):
    m=material('Oil painting '+str(i),'#ffffff',.86);p=m.node_tree.nodes.get('Principled BSDF')
    t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=painting_image;m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);artmats.append(m)

def painting(name,center,w,h,index,side=None,zone=None):
    # Initially faces the entrance (negative Y), then rotates to a side wall.
    x,y,z=center
    verts=[(-w/2,0,-h/2),(w/2,0,-h/2),(w/2,0,h/2),(-w/2,0,h/2)]
    art=mesh_obj(name,verts,[(0,1,2,3)],artmats[index])
    art.location=center
    angle=math.pi/2 if side==-1 else -math.pi/2 if side==1 else 0
    art.rotation_euler.z=angle
    uv=art.data.uv_layers.new(name='Painting UV')
    for loop,coord in zip(art.data.loops,[(index/3,0),((index+1)/3,0),((index+1)/3,1),(index/3,1)]):uv.data[loop.index].uv=coord
    if zone is not None:art['zone']=zone
    def localpos(a,b,c):return (x+a*math.cos(angle)-b*math.sin(angle),y+a*math.sin(angle)+b*math.cos(angle),z+c)
    for margin,thick,depth,mat in [(.03,.08,.065,black),(.12,.15,.13,gold),(.24,.075,.17,goldlight),(.31,.08,.12,walnut),(.36,.045,.16,gold)]:
        for s in [-1,1]:
            ob=cube('Ornate frame vertical',localpos(s*(w/2+margin),-.04,0),(thick,depth,h+2*margin),mat,.015);ob.rotation_euler.z=angle
            ob=cube('Ornate frame horizontal',localpos(0,-.04,s*(h/2+margin)),(w+2*margin,depth,thick),mat,.015);ob.rotation_euler.z=angle
    for sx in [-1,1]:
        for sz in [-1,1]:
            centerRos=localpos(sx*(w/2+.18),-.14,sz*(h/2+.18))
            for j in range(7):
                a=j*math.pi*2/7
                loc=localpos(sx*(w/2+.18)+math.cos(a)*.08,-.15,sz*(h/2+.18)+math.sin(a)*.08)
                uvball('Gilt floral corner',loc,(.045,.035,.045),goldlight)
            uvball('Gilt floral center',centerRos,(.07,.05,.07),gold)
    # Picture light and a small readable museum label.
    ob=cube('Picture light',localpos(0,-.35,h/2+.65),(w*.55,.14,.09),gold,.025);ob.rotation_euler.z=angle
    plaque=cube('Museum label',localpos(0,-.02,-h/2-.57),(min(w,1.9),.035,.3),paper,.008);plaque.rotation_euler.z=angle
    return art

painting('Exhibit_Piano',(-8.68,3.45,3.65),2.75,3.7,0,-1,1)
painting('Exhibit_Landscape',(0,16.10,3.7),6.3,4.0,1,None,2)
painting('Exhibit_Jazz',(8.68,3.45,3.65),2.75,3.7,2,1,3)
for side in [-1,1]:
    painting('Collection painting',(side*8.68,10.35,3.65),2.8,3.5,1 if side==-1 else 0,side)
    painting('Collection painting',(side*8.68,-10.35,3.65),2.8,3.5,2 if side==-1 else 1,side)
    if side==-1:painting('Collection painting',(side*8.68,-3.45,3.65),2.8,3.5,1,side)
text('Apse title','A R S   S O N O R A',(0,16.08,6.65),.53,goldlight)
text('Apse subtitle',"L' A R T E   D I   A S C O L T A R E",(0,16.075,6.05),.17,paper)

# Centerpiece: a sculpted ancient lyre, with modeled strings and carved volutes.
cube('Lyre stepped plinth lower',(0,0,.2),(2.8,2.1,.4),darkmarble,.08)
cube('Lyre stepped plinth upper',(0,0,.51),(2.5,1.9,.23),marble,.05)
cube('Lyre plinth',(0,0,1.0),(2.05,1.5,.8),darkmarble,.06)
cube('Lyre gilded plinth cap',(0,0,1.43),(2.26,1.7,.08),gold,.025)
text('Lyre plaque','H A R M O N I A',(0,-.765,1.02),.15,goldlight)
for side in [-1,1]:
    pts=[(side*.38,0,1.62),(side*.9,0,1.9),(side*1.06,.03,2.9),(side*.98,.03,3.65),(side*.62,0,3.85),(side*.46,-.02,3.55)]
    curve('Carved lyre arm',pts,.095,walnut,4)
    curve('Lyre gold inlay',[(x,y-.082,z) for x,y,z in pts],.017,goldlight,2)
    uvball('Lyre curled volute',(side*.53,-.02,3.64),(.17,.1,.17),gold)
curve('Lyre lower soundbox',[(-.8,0,1.9),(-.48,-.12,1.63),(0,-.18,1.57),(.48,-.12,1.63),(.8,0,1.9)],.18,walnut,4)
curve('Lyre crossbar',[(-.82,0,3.39),(0,0,3.47),(.82,0,3.39)],.065,gold,3)
for i in range(11):
    x=-.68+i*.136
    curve('Lyre string',[(x*.68,-.13,1.7),(x,-.06,3.42)],.005,goldlight,1)
    uvball('String tuning peg',(x,.01,3.5),(.035,.065,.035),goldlight)

# Museum benches and brass stanchions, with ropes that sag naturally.
for x,y in [(-4,-2),(4,-2),(-4,8),(4,8)]:
    cube('Velvet museum bench',(x,y,.67),(1.3,2.8,.22),burgundy,.12)
    cube('Bench walnut apron',(x,y,.48),(1.15,2.65,.16),walnut,.025)
    for dx in [-.45,.45]:
        for dy in [-1.05,1.05]:cyl('Turned bench leg',(x+dx,y+dy,.23),.065,.45,walnut,16)
for x,y in [(-1.8,-1.5),(1.8,-1.5),(-1.8,1.5),(1.8,1.5)]:
    cyl('Stanchion base',(x,y,.08),.22,.14,gold)
    cyl('Stanchion',(x,y,.55),.035,.95,gold,20)
    uvball('Stanchion finial',(x,y,1.05),(.075,.075,.075),goldlight)
for side in [-1,1]:curve('Velvet barrier',[(side*1.8,-1.5,1.0),(side*1.8,0,.77),(side*1.8,1.5,1)],.028,rope,2)
for y in [-1.5,1.5]:curve('Velvet barrier',[(-1.8,y,1),(0,y,.77),(1.8,y,1)],.028,rope,2)

# Grand piano: shaped case, open lid, cast frame, strings, keys and tapered legs.
outline=[(-1.5,-1), (1.5,-1),(1.5,.7),(1.35,1.5),(.8,2.1),(-.05,2.25),(-.9,1.95),(-1.4,1.25)]
def piano_shape(name,z,depth,mat):
    verts=[(x,y+9,zv) for zv in [z,z+depth] for x,y in outline];n=len(outline)
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=mesh_obj(name,verts,faces,mat);m=ob.modifiers.new('Piano soft edge','BEVEL');m.width=.04;m.segments=3;return ob
piano_shape('Grand piano ebony case',.92,.28,black)
piano_shape('Grand piano soundboard',1.205,.025,gold)
for x,y in [(-1.2,8.4),(1.2,8.4),(.1,10.65)]:
    ob=cyl('Piano turned leg',(x,y,.45),.09,.92,black,24)
    cyl('Piano brass caster',(x,y,.05),.1,.1,gold,20)
for i in range(36):
    x=-1.35+i*.075
    cube('Piano ivory key',(x,7.78,1.07),(.07,.57,.07),white,.004)
    if i%7 not in [2,6]:cube('Piano ebony key',(x+.036,7.96,1.13),(.036,.3,.07),black,.003)
cube('Keyboard fallboard',(0,8.13,1.27),(2.9,.08,.28),black,.025)
for i in range(32):
    x=-1.18+i*.074
    curve('Piano internal strings',[(x,8.4,1.25),(x*.6,10.6,1.25)],.003,goldlight,0)
lid=piano_shape('Raised grand piano lid',1.31,.055,black)
lid.rotation_euler.y=-.38
curve('Piano lid support',[(1.1,8.8,1.27),(1.1,8.8,1.95)],.023,walnut,2)
cube('Piano stool',(0,6.9,.6),(1.05,.6,.18),burgundy,.06)
for x in [-.38,.38]:cube('Piano stool leg',(x,6.9,.27),(.09,.4,.55),black,.025)

# Antique retail cabinet in the entrance-side bay, not a temporary outdoor kiosk.
sx,sy=6.35,-6.8
cube('Bottega cabinet back',(sx,sy,1.8),(3.4,.25,3.6),walnut,.03)
for dx in [-1.7,1.7]:cube('Bottega cabinet pilaster',(sx+dx,sy-.32,1.9),(.19,.55,3.8),walnut,.025)
for z in [.4,1.35,2.35,3.45]:cube('Bottega shelf',(sx,sy-.43,z),(3.5,.8,.11),walnut,.02)
cube('Bottega cornice',(sx,sy-.15,3.78),(3.7,.8,.2),gold,.035)
text('Bottega shop sign','B O T T E G A',(sx,sy-.58,3.94),.25,goldlight)
text('Bottega shop subtitle','M E M O R I E   D E L   S U O N O',(sx,sy-.59,3.61),.087,paper)
for i in range(13):
    for z in [.8,1.78,2.78]:
        book=cube('Museum shop art book',(sx-1.38+i*.22,sy-.45,z),(.12,.37,.63),[green,burgundy,paper,walnut][i%4],.008)
        cube('Book gilded band',(sx-1.38+i*.22,sy-.645,z+.22),(.105,.01,.015),gold,0)
cube('Bottega counter',(sx,sy-1.75,.55),(3.6,1.05,1.1),walnut,.04)
cube('Bottega marble counter top',(sx,sy-1.75,1.16),(3.8,1.2,.12),marble,.045)
for dx in [-1.3,0,1.3]:
    cube('Counter inlay',(sx+dx,sy-2.29,.58),(.9,.025,.65),green,.025)
    for dz in [-.35,.35]:cube('Counter inlay fillet',(sx+dx,sy-2.31,.58+dz),(.95,.02,.018),gold,0)
text('Counter lettering','S O U V E N I R S',(sx,sy-2.325,.52),.18,goldlight)

# Chandelier with real geometry, warm luminous candles, and slender arms.
emissive=material('Warm lamp glass','#ffdeb0',.4)
node=emissive.node_tree.nodes.get('Principled BSDF');node.inputs['Emission Color'].default_value=rgba('#ffcc82');node.inputs['Emission Strength'].default_value=3
for cy in [-8,6]:
    cyl('Chandelier chain',(0,cy,8.5),.018,3.2,gold,12)
    cyl('Chandelier central body',(0,cy,6.93),.17,.55,gold,32)
    for i in range(8):
        a=i*2*math.pi/8;dx=math.cos(a);dy=math.sin(a)
        curve('Chandelier scroll arm',[(0,cy,6.8),(dx*.6,cy+dy*.6,6.55),(dx*1.25,cy+dy*1.25,6.8)],.024,gold,2)
        cyl('Chandelier candle cup',(dx*1.25,cy+dy*1.25,6.9),.1,.08,goldlight,24)
        cyl('Chandelier candle',(dx*1.25,cy+dy*1.25,7.05),.034,.26,paper,16)
        uvball('Chandelier flame',(dx*1.25,cy+dy*1.25,7.23),(.035,.035,.07),emissive)

# Cinematic lighting for the Blender render; web lights are placed identically.
lamp('Entrance daylight',(0,-15,6.8),1900,(1,.86,.68),8,(0,0,1.4))
for y in [-9,0,9]:
    lamp('Vault softbox',(0,y,9),1400,(1,.83,.62),5,(0,y,0))
    lamp('Chandelier glow',(0,y,6.7),180,(1,.68,.36),1,(0,y,2))
for x,y in [(-7.1,3.45),(7.1,3.45),(-7.1,10.35),(7.1,10.35),(-7.1,-10.35),(7.1,-10.35)]:
    lamp('Picture wash',(x,y,5.9),240,(1,.84,.61),1.1,(math.copysign(8.68,x),y,3.3),'SPOT')
lamp('Apse picture wash',(0,12.7,6.5),450,(1,.84,.64),1.25,(0,16.1,3.5),'SPOT')
lamp('Lyre key',(-3,-3,6),650,(1,.83,.56),3,(0,0,2))
lamp('Lyre rim',(3,2,6),500,(1,.77,.47),2,(0,0,2))

# Convert curves and texts, apply bevels, merge static meshes by material.
# Art meshes retain names/extras for click interaction in the web app.
bpy.ops.object.select_all(action='DESELECT')
for obj in list(bpy.context.scene.objects):
    if obj.type in {'CURVE','FONT'}:
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.convert(target='MESH');obj.select_set(False)
for obj in list(bpy.context.scene.objects):
    if obj.type=='MESH' and obj.modifiers:
        bpy.context.view_layer.objects.active=obj
        for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
groups=defaultdict(list)
for obj in list(bpy.context.scene.objects):
    if obj.type=='MESH' and not obj.name.startswith('Exhibit_'):
        key=obj.data.materials[0].name if obj.data.materials else 'none';groups[key].append(obj)
for key,objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join();bpy.context.object.name='Architecture · '+key
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.type=='MESH':obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_extras=True)

# Save an editable scene and a physically rendered architectural preview.
scene=bpy.context.scene
scene.world.color=(.12,.10,.075)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.22,.17,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
bpy.ops.object.camera_add(location=(4.8,-13.8,2.45));camera=bpy.context.object;camera.name='Gallery entrance architectural camera'
camera.rotation_euler=(Vector((-.5,4.5,3.5))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=23;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(ROOT,'blender','museum-preview.png')
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'blender','Ars-Sonora-Museum.blend'))
print('MUSEUM_EXPORTED',OUT,flush=True)
if '--render-preview' in sys.argv:bpy.ops.render.render(write_still=True)
print('MUSEUM_COMPLETE',flush=True)
