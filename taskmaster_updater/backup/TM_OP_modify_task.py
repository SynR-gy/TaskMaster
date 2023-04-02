import bpy



class modify_task_OP(bpy.types.Operator):
    bl_idname = "object.modify_task"
    bl_label = "Modify Task"
    bl_options = {'REGISTER', 'UNDO'}
    
    name: bpy.props.StringProperty(name="Name")
    description: bpy.props.StringProperty(name="Description")
    
    
    @classmethod
    def poll(cls, context):
        return context.scene.my_list
    
    def execute(self, context):
        scene = context.scene
        index = scene.list_index
        scene.my_list[index].name = self.name
        scene.my_list[index].description = self.description
  
        
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        scene = context.scene
        index = scene.list_index
        self.name = scene.my_list[index].name
        self.description = scene.my_list[index].description
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)