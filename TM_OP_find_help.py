import bpy
import webbrowser



def make_oops(msgs):
    def draw(self, context):
        for msg in msgs:
            self.layout.label(text=msg)
    return draw

class TM_OP_FindHelp(bpy.types.Operator):
    """How to find help"""
    bl_idname = 'taskmaster.find_help'
    bl_label = 'How to find help'

    def execute(self, context):
        url = "https://github.com/SynR-gy/TaskMaster/wiki"
        webbrowser.open(url)
        return {'FINISHED'}
