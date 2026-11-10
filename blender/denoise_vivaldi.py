import bpy, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
source=os.path.join(ROOT,'public','textures','vivaldi-cycles-lighting.jpg')
clean=os.path.join(ROOT,'public','textures','vivaldi-lighting-clean.png')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=1
bpy.ops.object.camera_add(location=(0,0,5));scene.camera=bpy.context.object
scene.render.resolution_x=6144;scene.render.resolution_y=6144;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=clean
scene.view_settings.view_transform='Standard'
tree=bpy.data.node_groups.new('Museum lightmap denoise','CompositorNodeTree');scene.compositing_node_group=tree
tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
image=tree.nodes.new('CompositorNodeImage');image.image=bpy.data.images.load(source)
denoise=tree.nodes.new('CompositorNodeDenoise')
output=tree.nodes.new('NodeGroupOutput');tree.links.new(image.outputs['Image'],denoise.inputs['Image']);tree.links.new(denoise.outputs['Image'],output.inputs['Image'])
bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'blender','Vivaldi-Four-Seasons-Web.blend'))
newimage=bpy.data.images.load(clean);newimage.pack()

for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    for node in mat.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image and 'Cycles baked' in node.image.name:node.image=newimage
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
    if ob.type=='MESH':ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'public','models','vivaldi-four-seasons.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_extras=True,export_meshopt_compression_enable=True,export_meshopt_extension='EXT_meshopt_compression',export_image_format='JPEG',export_jpeg_quality=92)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'blender','Vivaldi-Four-Seasons-Web.blend'))
print('DENOISED_WEB_READY',flush=True)
