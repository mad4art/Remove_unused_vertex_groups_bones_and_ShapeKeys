bl_info = {
 "name": "Remove unused Vertex Groups, Bones, and Shape Keys",
 "author": "Leo",
 "version": (1, 0),
 "blender": (4, 0, 0),
 "location": "View3D > Tool Shelf > Object > Remove unused Vertex Groups, Bones, and Shape Keys",
 "description": "Deletes Vertex Groups, Bones, and Shape Keys with no assigned weight of active object",
 "warning": "",
 "wiki_url": "",
 "category": "3D View",
}

import bpy
from bpy.types import Operator
import numpy as np

class OBJECT_OT_remove_unused(Operator):
 """Tooltip"""
 bl_idname = "object.remove_unused"
 bl_label = "Remove unused Vertex Groups and Bones"
 bl_options = {'REGISTER', 'UNDO'}

 @classmethod
 def poll(cls, context):
     return (context.object is not None and
             context.object.type == 'MESH')

 def execute(self, context):
     ob = context.active_object
     ob.update_from_editmode()
     
     vgroup_used = {i: False for i, k in enumerate(ob.vertex_groups)}
     
     for v in ob.data.vertices:
         for g in v.groups:
             if g.weight > 0.0:
               vgroup_used[g.group] = True
     
     for i, used in sorted(vgroup_used.items(), reverse=True):
         if not used:
             ob.vertex_groups.remove(ob.vertex_groups[i])

     if ob.type == 'ARMATURE':
         bone_used = {i: False for i, k in enumerate(ob.pose.bones)}
         
         for v in ob.data.vertices:
             for g in v.bone_groups:
                if g.weight > 0.0:
                 bone_used[g.group] = True
         
         for i, used in sorted(bone_used.items(), reverse=True):
             if not used:
                ob.pose.bones.remove(ob.pose.bones[i])
             
     return {'FINISHED'}

class OBJECT_OT_remove_unused_shape_keys(Operator):
 """Tooltip"""
 bl_idname = "object.remove_unused_shape_keys"
 bl_label = "Remove unused Shape Keys"
 bl_options = {'REGISTER', 'UNDO'}

 @classmethod
 def poll(cls, context):
     return (context.object is not None and
             context.object.type == 'MESH' and
             context.object.data.shape_keys)

 def execute(self, context):
     ob = context.active_object
     ob.update_from_editmode()
     
     shape_key_used = {i: False for i, kb in enumerate(ob.data.shape_keys.key_blocks)}
     
     for i, kb in enumerate(ob.data.shape_keys.key_blocks):
         if kb != ob.data.shape_keys.reference_key:
             for v1, v2 in zip(ob.data.vertices, kb.data):
                 if v1.co != v2.co:
                     shape_key_used[i] = True
                     break
     
     for i, used in sorted(shape_key_used.items(), reverse=True):
         if not used:
             ob.shape_key_remove(ob.data.shape_keys.key_blocks[i])
             
     return {'FINISHED'}

def register():
 bpy.utils.register_class(OBJECT_OT_remove_unused)
 bpy.utils.register_class(OBJECT_OT_remove_unused_shape_keys)
 bpy.types.OBJECT_PT_transform.append(draw_func)

def unregister():
 bpy.utils.unregister_class(OBJECT_OT_remove_unused)
 bpy.utils.unregister_class(OBJECT_OT_remove_unused_shape_keys)
 bpy.types.OBJECT_PT_transform.remove(draw_func)

def draw_func(self, context):
    self.layout.operator(
        OBJECT_OT_remove_unused.bl_idname,
        text="Remove unused Vertex Groups and Bones",
        icon='X'
    )
    self.layout.operator(
        OBJECT_OT_remove_unused_shape_keys.bl_idname,
        text="Remove unused Shape Keys",
        icon='X'
    )

if __name__ == "__main__":
 register()
