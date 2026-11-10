import bpy, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
source=os.path.join(ROOT,'public','textures','museum-cycles-lighting.jpg')
clean=os.path.join(ROOT,'public','textures','museum-lighting-clean.png')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=1
bpy.ops.object.camera_add(location=(0,0,5));scene.camera=bpy.context.object
scene.render.resolution_x=4096;scene.render.resolution_y=4096;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=clean
scene.view_settings.view_transform='Standard'
tree=bpy.data.node_groups.new('Museum lightmap denoise','CompositorNodeTree');scene.compositing_node_group=tree
tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
image=tree.nodes.new('CompositorNodeImage');image.image=bpy.data.images.load(source)
denoise=tree.nodes.new('CompositorNodeDenoise')
output=tree.nodes.new('NodeGroupOutput');tree.links.new(image.outputs['Image'],denoise.inputs['Image']);tree.links.new(denoise.outputs['Image'],output.inputs['Image'])
bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'blender','Ars-Sonora-Web.blend'))
newimage=bpy.data.images.load(clean);newimage.pack()
art=bpy.data.images.load(os.path.join(ROOT,'public','art','renaissance-music-triptych.png'));art.pack()
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    if mat.name.startswith('Oil painting'):
        nodes=mat.node_tree.nodes;nodes.clear();p=nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=.86
        tex=nodes.new('ShaderNodeTexImage');tex.image=art
        uv=nodes.new('ShaderNodeUVMap');uv.uv_map='Painting UV'
        out=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(uv.outputs['UV'],tex.inputs['Vector']);mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);mat.node_tree.links.new(p.outputs[0],out.inputs[0]);mat['cycles_baked']=False
    else:
        for node in mat.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image and 'Cycles baked' in node.image.name:node.image=newimage
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
    if ob.type=='MESH':ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'public','models','ars-sonora.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_extras=True,export_meshopt_compression_enable=True,export_meshopt_extension='EXT_meshopt_compression',export_image_format='JPEG',export_jpeg_quality=92)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'blender','Ars-Sonora-Web.blend'))
print('DENOISED_WEB_READY',flush=True)
