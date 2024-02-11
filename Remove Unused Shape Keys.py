bl_info = {
    "name": "Remove Unused Shape Keys",
    "author": "Leo",
    "version": (1,   0),
    "blender": (4,   0,   0),
    "location": "View3D > Sidebar > Object Data > Shape Keys",
    "description": "Removes unused shape keys from selected objects",
    "category": "Object",
}

import bpy
import numpy as np

class OBJECT_OT_remove_unused_shapekeys(bpy.types.Operator):
    bl_idname = "object.remove_unused_shapekeys"
    bl_label = "Remove Unused Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    # Tolerance to small differences, change it if you want
    tolerance =  0.001

    def execute(self, context):
        assert bpy.context.mode == 'OBJECT', "Must be in object mode!"

        for ob in bpy.context.selected_objects:
            if ob.type != 'MESH': continue
            if not ob.data.shape_keys: continue
            if not ob.data.shape_keys.use_relative: continue

            kbs = ob.data.shape_keys.key_blocks
            nverts = len(ob.data.vertices)
            to_delete = []

            # Cache locs for rel keys since many keys have the same rel key
            cache = {}

            locs = np.empty(3*nverts, dtype=np.float32)

            for kb in kbs:
                if kb == kb.relative_key: continue

                kb.data.foreach_get("co", locs)

                if kb.relative_key.name not in cache:
                    rel_locs = np.empty(3*nverts, dtype=np.float32)
                    kb.relative_key.data.foreach_get("co", rel_locs)
                    cache[kb.relative_key.name] = rel_locs
                rel_locs = cache[kb.relative_key.name]

                locs -= rel_locs
                if (np.abs(locs) < self.tolerance).all():
                    to_delete.append(kb.name)

            for kb_name in to_delete:
                ob.shape_key_remove(ob.data.shape_keys.key_blocks[kb_name])

        return {'FINISHED'}

def draw_callback(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(OBJECT_OT_remove_unused_shapekeys.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_remove_unused_shapekeys)
    bpy.types.DATA_PT_shape_keys.append(draw_callback)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_remove_unused_shapekeys)
    bpy.types.DATA_PT_shape_keys.remove(draw_callback)

if __name__ == "__main__":
    register()
