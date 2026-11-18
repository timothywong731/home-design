"""glTF export with settings verified on 5.1.1 (operator property names from the live RNA)."""
import bpy
def export_glb(path, draco=False, quality=85):
    bpy.ops.export_scene.gltf(
        filepath=path, export_format='GLB',
        export_image_format='AUTO',  # keep PNG; compress textures afterwards with gltf-transform (webp/ktx2)
        export_image_quality=quality,
        export_texcoords=True, export_normals=True, export_tangents=False,
        export_apply=True,                 # apply modifiers (bevel/smooth-by-angle/mirror) on export
        export_yup=True, export_cameras=False, export_lights=False,
        export_extras=False, export_unused_images=False, export_unused_textures=False,
        export_draco_mesh_compression_enable=draco)
