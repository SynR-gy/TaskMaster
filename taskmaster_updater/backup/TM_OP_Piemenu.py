
from bpy.types import Menu
from .TM_OP_import_export import *



class VIEW3D_MT_pie_select(Menu):
    bl_idname = "VIEW3D_MT_pie_select"   
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        
        pie = layout.menu_pie()
        pie.operator('wm.import_list', text="Import", icon='COPYDOWN')
        
        pie.operator("wm.export_active_task", text="Export", icon='PASTEDOWN')
        