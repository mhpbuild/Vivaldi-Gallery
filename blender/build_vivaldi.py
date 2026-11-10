"""Vivaldi: four connected 22 x 16 m galleries, 20 recording exhibits.
Reuses the original project's modeling utilities; builds a new, larger museum.
"""
from pathlib import Path
import json, math, os, bpy, random
from mathutils import Vector
from collections import defaultdict
ROOT=Path(__file__).resolve().parent.parent
original=(ROOT/'blender/build_museum.py').read_text()
exec(compile(original.split('# Continuous inlaid marble floor.')[0],'museum-utilities','exec'))
ROOT=Path(ROOT)
layout=json.loads((ROOT/'src/layout.json').read_text())
catalog=json.loads((ROOT/'src/catalog.json').read_text())
W=11; LENGTH=64
season_mats=[material('Spring gallery silk','#53634b'),material('Summer gallery silk','#76603f'),material('Autumn gallery silk','#754a35'),material('Winter gallery silk','#4d6570')]
violinwood=material('Violin amber varnish','#9b5626',.27)

# Floor and inlaid promenade, 2.37 times the previous usable floor area.
cube('Museum foundation',(0,0,-.2),(22.5,64.5,.4),ivory,0)
for i in range(11):
 for j in range(32):
  tile=cube('Marble paving',(-10+i*2,-31+j*2,.01),(1.994,1.994,.035),marble if (i+j)%2 else lightstone,.004)
  tile.rotation_euler.z=(i%2)*math.pi/2
for x in [-10.6,-5.0,5.0,10.6]:cube('Marble promenade border',(x,0,.04),(.13,64,.03),darkmarble,.003)
for x in [-4.87,4.87]:cube('Fine brass floor inlay',(x,0,.06),(.014,64,.008),gold,0)
for y in [-31.7,-16,0,16,31.7]:cube('Gallery threshold inlay',(0,y,.05),(21.3,.11,.025),gold,.003)

# Each season occupies an actual architectural bay with its own pigment.
for season,wallmat in zip(layout['seasons'],season_mats):
 cy=-season['center']
 for side in [-1,1]:
  cube(season['name']+' silk wall',(side*11.1,cy,3.2),(.3,16,6.4),wallmat,.01)
  cube('Continuous walnut dado',(side*10.9,cy,.6),(.18,16,1.2),walnut,.02)
  for z,w,h in [(1.22,.25,.09),(1.34,.22,.07),(5.95,.36,.13),(6.15,.5,.15),(6.36,.62,.16)]:
   cube('Carved cornice',(side*10.82,cy,z),(w,16,h),lightstone,.015)
  cube('Verde marble skirting',(side*10.8,cy,.12),(.3,16,.2),darkmarble,.015)
for side in [-1,1]:
 for y in range(-32,33,8):
  cube('Wall pilaster',(side*10.85,y,3.3),(.2,.75,5.8),ivory,.025)
  for z,r,h in [(.2,.57,.28),(.41,.46,.13),(.56,.37,.15),(5.77,.38,.14),(5.95,.5,.17),(6.13,.59,.16)]:cyl('Column turned capital',(side*10.4,y,z),r,h,lightstone,32)
  cyl('Fluted Ionic column',(side*10.4,y,3.18),.3,5.1,ivory,40)
  for i in range(12):
   a=i*2*math.pi/12;cyl('Column flute',(side*10.4+.292*math.cos(a),y+.292*math.sin(a),3.18),.016,4.86,lightstone,8)
  for d in [-.28,.28]:uvball('Ionic scroll',(side*10.4,y+d,5.88),(.12,.16,.14),gold)

# The vault faces inward so baked light rays sample the illuminated interior.
def arch(a,y):return (10.82*math.cos(a),y,6.35+4.8*math.sin(a))
vertices=[arch(i/64*math.pi,y) for y in [-32.3,32.3] for i in range(65)]
vault=mesh_obj('Interior barrel vault',vertices,[(i,i+1,i+66,i+65) for i in range(64)],plaster)
for p in vault.data.polygons:p.use_smooth=True
for y in range(-32,33,8):
 curve('Carved transverse arch',[arch(i/48*math.pi,y) for i in range(49)],.17 if y%16==0 else .1,lightstone,2)
 for dy in [-.24,.24]:curve('Bronze arch fillet',[arch(i/48*math.pi,y+dy) for i in range(49)],.021,gold,1)
for cy in range(-28,29,8):
 for k in range(9):
  a0=.05+k*(math.pi-.1)/9+.023;a1=.05+(k+1)*(math.pi-.1)/9-.023
  for inset,mat in [(0,lightstone),(.035,gold),(.06,ochre)]:
   ps=[arch(a0+inset,cy-3.35+inset*5),arch(a1-inset,cy-3.35+inset*5),arch(a1-inset,cy+3.35-inset*5),arch(a0+inset,cy+3.35-inset*5)]
   mesh_obj('Recessed vault coffer',[(x,y,z-.04-inset) for x,y,z in ps],[(0,1,2,3)],mat)
  x,y,z=arch((a0+a1)/2,cy);uvball('Gilt coffer rosette',(x,y,z-.16),(.1,.1,.04),goldlight)

for y in [-32.3,32.3]:
 cube('End wall',(0,y,3.2),(22.4,.3,6.4),green,.02)
 # Infill above the spring line of the vault.
 ps=[(-10.82,y,6.35),(10.82,y,6.35)]+[arch(i/64*math.pi,y) for i in range(65)]
 mesh_obj('End tympanum',ps,[tuple(range(len(ps)))],plaster)
 for x in [-8,-5,5,8]:cube('Apse pilaster',(x,y-.23 if y>0 else y+.23,3.2),(.3,.25,6.1),ivory,.02)

# Twelve unique seasonal paintings plus two documented historical Vivaldi portraits.
artmats=[]
for season in layout['seasons']:
 img=bpy.data.images.load(str(ROOT/'public/art'/('vivaldi-'+season['id']+'.png')));img.pack()
 for movement in range(3):
  mat=material(f"Vivaldi Artwork {len(artmats):02d}",'#ffffff',.86)
  tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;mat.node_tree.links.new(tex.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color']);artmats.append(mat)
for name in ['vivaldi-portrait.jpg','vivaldi-engraving.jpg']:
 img=bpy.data.images.load(str(ROOT/'public/art'/name));img.pack();mat=material('Vivaldi Portrait '+name,'#ffffff',.86)
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;mat.node_tree.links.new(tex.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color']);artmats.append(mat)
painting_source=original[original.index('def painting('):original.index("\npainting('Exhibit_Piano'")]
painting_source=painting_source.replace("for loop,coord in zip(art.data.loops,[(index/3,0),((index+1)/3,0),((index+1)/3,1),(index/3,1)]):uv.data[loop.index].uv=coord", "start=(index%3)/3 if index<12 else 0;end=((index%3)+1)/3 if index<12 else 1\n    for loop,coord in zip(art.data.loops,[(start,0),(end,0),(end,1),(start,1)]):uv.data[loop.index].uv=coord")
exec(compile(painting_source,'framed-painting','exec'))
for si,season in enumerate(layout['seasons']):
 cy=-season['center']
 for mi,spec in enumerate(season['paintings']):
  px,pz,py=spec['position']; side=spec['side'];idx=si*3+mi
  art=painting(f'Exhibit_Vivaldi_{idx:02d}',(px,-py,pz),3.4,3.7,idx,side,si+1);art['track']=idx;art['season']=season['id']
  rotation=(math.pi/2,0,math.pi/2 if side==-1 else -math.pi/2)
  text('Movement label',str(mi+1)+'. '+catalog['tracks'][idx]['tempo'],(side*10.12,-py,1.17),.14,walnut,rotation)
 painting('Portrait_'+season['id'],(10.42,cy-4,3.65),2.9,3.7,12 if si%2==0 else 13,1)
 # A sign above the entrance to each season bay.
 text('Gallery season title',season['italian'].upper(),(0,cy-7.1,6.5),.45,goldlight)
 text('Gallery catalogue',season['rv']+'   /   '+season['key'].upper(),(0,cy-7.12,6.08),.13,paper)
painting('Portrait_Antonio_Vivaldi',(0,32.08,3.7),3.5,4.3,13)
text('Museum apse name','ANTONIO VIVALDI',(0,32.06,6.7),.57,goldlight)
text('Museum apse dates','1678  —  1741',(0,32.05,6.05),.18,paper)
text('Entrance title','LE QUATTRO STAGIONI',(0,-32.08,6.55),.46,goldlight,(math.pi/2,0,math.pi))

# Hero instrument, a modeled violin with carved bouts, bridge, pegs and four strings.
cy=-24
cube('Violin lower plinth',(0,cy,.16),(2.5,2,.32),darkmarble,.06)
cube('Violin marble cap',(0,cy,.4),(2.3,1.8,.16),marble,.04)
cube('Violin exhibition plinth',(0,cy,.83),(1.85,1.4,.7),darkmarble,.04)
cube('Violin gilt top',(0,cy,1.23),(2.05,1.6,.08),gold,.018)
text('Violin plinth title','IL VIOLINO DI VIVALDI',(0,cy-.72,.83),.12,goldlight)
profile=[(-.12,0),(-.43,.09),(-.62,.38),(-.56,.68),(-.3,.87),(-.34,1.04),(-.51,1.25),(-.4,1.53),(-.12,1.64),(.12,1.64),(.4,1.53),(.51,1.25),(.34,1.04),(.3,.87),(.56,.68),(.62,.38),(.43,.09),(.12,0)]
c=bpy.data.curves.new('Carved violin soundbox','CURVE');c.dimensions='2D';c.resolution_u=16;c.fill_mode='BOTH';c.extrude=.1;c.bevel_depth=.025;c.bevel_resolution=3
sp=c.splines.new('BEZIER');sp.bezier_points.add(len(profile)-1);sp.use_cyclic_u=True
for bp,(x,z) in zip(sp.bezier_points,profile):bp.co=(x,z,0);bp.handle_left_type=bp.handle_right_type='AUTO'
ob=bpy.data.objects.new('Amber violin soundbox',c);bpy.context.collection.objects.link(ob);ob.location=(0,cy,1.45);ob.rotation_euler.x=math.pi/2;ob.data.materials.append(violinwood)
cube('Violin maple neck',(0,cy,3.48),(.14,.17,1.05),violinwood,.04)
cube('Violin ebony fingerboard',(0,cy-.13,3.35),(.115,.035,1.1),black,.01)
cube('Violin tailpiece',(0,cy-.17,1.75),(.14,.04,.36),black,.04)
cube('Violin bridge',(0,cy-.19,2.37),(.29,.025,.1),white,.02)
for side in [-1,1]:
 curve('Violin f-hole',[(side*.33,cy-.135,2.64),(side*.27,cy-.135,2.48),(side*.37,cy-.135,2.22)],.017,black,2)
 uvball('F hole eye',(side*.33,cy-.137,2.66),(.04,.012,.04),black)
for i in range(4):
 x=-.035+i*.023;curve('Violin string',[(x,cy-.22,1.86),(x,cy-.22,2.38),(x,cy-.15,3.97)],.0035,goldlight,1)
 cyl('Violin tuning peg',((-.15 if i%2 else .15),cy,3.85+i*.07),.045,.13,black,16).rotation_euler.y=math.pi/2
curve('Violin scroll',[(0,cy,3.95),(0,cy,4.15),(0,cy-.12,4.24),(0,cy-.22,4.14)],.065,violinwood,3)
curve('Violin bow',[(.85,cy-.08,1.45),(.66,cy-.08,4.15)],.014,walnut,2)
curve('Bow horsehair',[(.8,cy-.09,1.55),(.61,cy-.09,4.07)],.007,white,1)

# Reading benches and interpretation desks house the additional recordings.
for si,season in enumerate(layout['seasons']):
 cy=-season['center']
 for x in [-5.7,5.7]:
  cube('Museum velvet bench',(x,cy+.8,.62),(1.25,2.8,.2),burgundy,.09)
  for dx in [-.44,.44]:
   for dy in [-1.04,1.04]:cyl('Bench leg',(x+dx,cy+.8+dy,.26),.05,.5,walnut,12)
 dx,dy=6.4,cy-3.4
 cube('Interpretation listening cabinet',(dx,dy,.56),(2.8,1.5,1.1),walnut,.04)
 cube('Interpretation marble desk',(dx,dy,1.17),(3,1.65,.12),marble,.035)
 text('Interpretation cabinet inscription','INTERPRETAZIONI',(dx,dy-.77,.62),.13,goldlight)
 for j in range(3):
  cube('Listening catalogue folio',(dx-.85+j*.85,dy-.1,1.3),(.65,.9,.06),paper,.015)
  for line in range(5):cube('Printed music staff',(dx-.85+j*.85,dy-.1+line*.07,1.337),(.52,.005,.002),walnut,0)
 # A named picking mesh for opening all versions in this season.
 target=cube('Exhibit_Interpretations_'+season['id'],(dx,dy,1),(2.9,1.55,.1),paper,.01);target['zone']=si+1

# Museum shop remains near the entrance, separate from the four season displays.
sx,sy=7.1,-29
cube('Museum shop cabinet',(sx,sy,1.7),(3.2,.25,3.4),walnut,.025)
for dx in [-1.6,1.6]:cube('Shop cabinet pilaster',(sx+dx,sy-.27,1.8),(.17,.5,3.6),walnut,.02)
for z in [.4,1.4,2.4,3.3]:
 cube('Shop walnut shelf',(sx,sy-.4,z),(3.35,.7,.1),walnut,.02)
 if z<3:
  for j in range(12):
   cube('Four Seasons souvenir folio',(sx-1.35+j*.245,sy-.42,z+.36),(.13,.35,.6),season_mats[j%4],.008)
cube('Shop gilt cornice',(sx,sy-.2,3.53),(3.6,.8,.18),gold,.03)
text('Shop title','BOTTEGA VIVALDI',(sx,sy-.6,3.8),.22,goldlight)
cube('Shop counter',(sx,sy-1.55,.55),(3.3,1,1.1),walnut,.035)
cube('Shop counter marble',(sx,sy-1.55,1.16),(3.5,1.12,.12),marble,.04)
text('Shop counter inscription','LE QUATTRO STAGIONI',(sx,sy-2.07,.6),.12,goldlight)

# Lit chandeliers and large interior area lights used for the Cycles bake.
emissive=material('Warm lamp glass','#ffdeb0',.4);node=emissive.node_tree.nodes['Principled BSDF'];node.inputs['Emission Color'].default_value=rgba('#ffd9a0');node.inputs['Emission Strength'].default_value=3
for season in layout['seasons']:
 cy=-season['center']
 cyl('Chandelier suspension',(0,cy,8.4),.016,3,gold,12)
 for i in range(8):
  a=i*math.pi/4;x=1.2*math.cos(a);y=1.2*math.sin(a)
  curve('Chandelier arm',[(0,cy,6.8),(x*.5,cy+y*.5,6.55),(x,cy+y,6.8)],.02,gold,2)
  cyl('Candle holder',(x,cy+y,6.88),.09,.07,goldlight,16)
  cyl('Wax candle',(x,cy+y,7.03),.032,.24,paper,12)
  uvball('Candle flame',(x,cy+y,7.2),(.03,.03,.06),emissive)
 lamp('Vault softbox',(0,cy,9),1600,(1,.87,.7),6,(0,cy,0))
 lamp('Gallery frontal fill',(0,cy-6,5.9),850,(1,.88,.73),5,(0,cy,2))
 for spec in season['paintings']:
  x,z,y=spec['position'];lamp('Artwork wash',(math.copysign(8.3,x),-y,5.8),270,(1,.86,.7),1.2,(x,-y,3.5),'SPOT')
lamp('Violin hero softbox',(-3,-27,5.8),500,(1,.86,.65),3,(0,-24,2.5))

# Preserve the art/recording identities; batch the static architecture by material.
bpy.ops.object.select_all(action='DESELECT')
for ob in list(bpy.context.scene.objects):
 if ob.type in {'CURVE','FONT'}:
  bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.modifiers:
  bpy.context.view_layer.objects.active=ob
  for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
groups=defaultdict(list)
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and not ob.name.startswith(('Exhibit_','Portrait_')):groups[ob.data.materials[0].name if ob.data.materials else 'none'].append(ob)
for name,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 if len(objects)>1:bpy.ops.object.join()
 bpy.context.object.name='Architecture · '+name
scene=bpy.context.scene;scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.22,.17,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.38
bpy.ops.object.camera_add(location=(0,-31,2.15));camera=bpy.context.object;camera.rotation_euler=(Vector((0,-20,3.25))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=23;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'blender/vivaldi-museum-preview.png')
scene['gallery_area_m2']=1408;scene['recording_capacity']=20;scene['season_galleries']=4
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Vivaldi-Four-Seasons-Museum.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
 if ob.type=='MESH':ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/vivaldi-four-seasons.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_extras=True,export_meshopt_compression_enable=True,export_image_format='JPEG',export_jpeg_quality=92)
print('VIVALDI_MUSEUM_BUILT',flush=True)
if '--render-preview' in __import__('sys').argv:bpy.ops.render.render(write_still=True)
