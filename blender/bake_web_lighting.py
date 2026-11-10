"""Bake Cycles diffuse GI into a shared UV atlas for the real-time museum.
Metallic gilding remains PBR, to retain view-dependent highlights in Three.js.
The editable, fully lit master .blend is preserved without baked material edits.
"""
import bpy, os, math, bmesh
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'blender','Ars-Sonora-Museum.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12
# A vaulted interior needs inward-facing ceiling normals for lightmap rays.
for ob in scene.objects:
    if ob.type=='MESH' and 'Ochre lime plaster' in ob.name:
        bm=bmesh.new();bm.from_mesh(ob.data)
        for face in bm.faces:
            center=ob.matrix_world @ face.calc_center_median()
            normal=ob.matrix_world.to_3x3() @ face.normal
            if center.z>6.4 and normal.z>.15:face.normal_flip()
        bm.to_mesh(ob.data);bm.free();ob.data.update()

try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='METAL';prefs.get_devices()
    if any(d.type=='METAL' for d in prefs.devices):
        for d in prefs.devices:d.use=d.type=='METAL'
        scene.cycles.device='GPU'
except Exception:pass

objects=[];materials=set()
for ob in scene.objects:
    if ob.type!='MESH' or not ob.data.materials:continue
    mat=ob.data.materials[0]
    p=mat.node_tree.nodes.get('Principled BSDF')
    if mat.name.startswith('Oil painting'):continue
    if p and (p.inputs['Metallic'].default_value>.5 or p.inputs['Emission Strength'].default_value>0):continue
    if not ob.data.uv_layers:ob.data.uv_layers.new(name='UVMap')
    original_uv=ob.data.uv_layers[0].name
    if mat not in materials:
        for node in list(mat.node_tree.nodes):
            if node.type=='TEX_IMAGE' and not node.inputs['Vector'].is_linked:
                uvnode=mat.node_tree.nodes.new('ShaderNodeUVMap');uvnode.uv_map=original_uv
                mat.node_tree.links.new(uvnode.outputs['UV'],node.inputs['Vector'])
    materials.add(mat)
    layer=ob.data.uv_layers.new(name='BakedUV');ob.data.uv_layers.active=layer
    objects.append(ob)

bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.002,area_weight=.5,scale_to_bounds=True)
bpy.ops.object.mode_set(mode='OBJECT')
image=bpy.data.images.new('Cycles baked museum diffuse lighting',width=4096,height=4096,alpha=False)
for mat in materials:
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;tex.name='BAKED_GI_TARGET';mat.node_tree.nodes.active=tex
scene.render.bake.use_pass_direct=True;scene.render.bake.use_pass_indirect=True;scene.render.bake.use_pass_color=True
scene.render.bake.margin=8
print('BAKING_MUSEUM_GI',len(objects),'objects, 4096 atlas',flush=True)
bpy.ops.object.bake(type='DIFFUSE')
image.filepath_raw=os.path.join(ROOT,'public','textures','museum-cycles-lighting.jpg');image.file_format='JPEG';image.save();image.pack()
for mat in materials:
    tree=mat.node_tree;tree.nodes.clear()
    output=tree.nodes.new('ShaderNodeOutputMaterial');emission=tree.nodes.new('ShaderNodeEmission');tex=tree.nodes.new('ShaderNodeTexImage');tex.image=image
    uv=tree.nodes.new('ShaderNodeUVMap');uv.uv_map='BakedUV'
    tree.links.new(uv.outputs['UV'],tex.inputs['Vector']);tree.links.new(tex.outputs['Color'],emission.inputs['Color']);tree.links.new(emission.outputs[0],output.inputs[0])
    mat['cycles_baked']=True
for ob in objects:ob['cycles_baked']=True
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob.type=='MESH':ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'public','models','ars-sonora.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_extras=True,export_meshopt_compression_enable=True,export_meshopt_extension='EXT_meshopt_compression',export_image_format='JPEG',export_jpeg_quality=92)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'blender','Ars-Sonora-Web.blend'))
print('BAKED_MUSEUM_READY',flush=True)
