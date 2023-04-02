# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name" : "TaskMaster",
    "author" : "Synrgy",
    "version" : (1, 7 ,3),
    "blender" : (3, 6, 0),
    "location" : "View3d > Tool",
    "warning" : "",
    "wiki_URL" : "",
    "description" : "Ajoute une list to-do",       
    "category" : "Gestionaire",
}


#_______________________ Imports standard de Python_______________________#


import os
import datetime
import time 
import os.path
import aud
#___________________Imports liés à Blender_______________________#

import bpy

from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty, FloatVectorProperty, FloatProperty, EnumProperty 
from bpy.types import PropertyGroup, UIList, Operator, Panel , Header , AddonPreferences
from bpy.app.handlers import persistent
import bpy.utils.previews

#___________________ Imports spécifiques_______________________#

from .TM_PT_panel_Timer import *
from .TM_OP_find_help import TM_OP_FindHelp 
from .TM_OP_modify_task import modify_task_OP     
from .TM_OP_import_export import *
from.TM_OP_TaskOp import *
from . TM_OP_Piemenu import *
from .TM_PT_panel import (TM_PT_Option ,
                            TM_UL_ListChrono,
                            MY_UL_List ,
                            MY_PT_ParentPanel)
from .TM_ul_List import *
#___________________ Imports updater_______________________#

from . import addon_updater_ops
# -----------------------------------------------------------------------------
#   VARIABLES
# ----------------------------------------------------------------------------- 

preview_collections = {}



# -----------------------------------------------------------------------------
#   ADDON PREFERENCES
# ----------------------------------------------------------------------------- 

class TaskMasterPreferences(AddonPreferences):
    bl_idname = __package__



    export_folder: bpy.props.StringProperty(
        name="Export Folder",
        subtype='DIR_PATH',
        default=bpy.utils.user_resource('CONFIG') + os.sep + __name__ + os.sep + "exports",
    )
    addon_keymaps = [] 
    
    auto_check_update : bpy.props.BoolProperty(
		name="Auto-check for Update",
		description="If enabled, auto-check for updates using an interval",
		default=True)

    updater_interval_months : bpy.props.IntProperty(
		name='Months',
		description="Number of months between checking for updates",
		default=0,
		min=0)

    updater_interval_days : bpy.props.IntProperty(
		name='Days',
		description="Number of days between checking for updates",
		default=7,
		min=0,
		max=31)

    updater_interval_hours : bpy.props.IntProperty(
		name='Hours',
		description="Number of hours between checking for updates",
		default=0,
		min=0,
		max=23)

    updater_interval_minutes : bpy.props.IntProperty(
		name='Minutes',
		description="Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59)
    

    def draw(self, context):       
        layout = self.layout
        box = layout.box()
        row = layout.row(align=True)
        
        box.prop(self, "export_folder")

        
        row = layout.row()
        
        icon = 'TRIA_DOWN' if context.scene.subpanel_status_2 else 'TRIA_RIGHT'
        row.prop(context.scene, 'subpanel_status_2', icon=icon, icon_only=True)
        row.label(text='options sound')
        box = layout.row()
        if context.scene.subpanel_status_2: 
            col= box.column(align=True)   
            col.prop(context.scene, "sound_volume")
            col.prop(context.scene, "sound_choice", text="Sound Choice")
        row = layout.row()
        icon = 'TRIA_DOWN' if context.scene.subpanel_status else 'TRIA_RIGHT'
        row.prop(context.scene, 'subpanel_status', icon=icon, icon_only=True)
        row.label(text='options updater')
        box = layout.row()
        if context.scene.subpanel_status:      
            addon_updater_ops.update_settings_ui(self,context)

# -----------------------------------------------------------------------------
#  classes
# ----------------------------------------------------------------------------- 
 
classes = (
    
    MY_PT_ParentPanel,
    TaskMasterPreferences,
    ExportActiveTaskOperator,
    ListTache,
    ListTimers,
    LIST_OT_NewItem,
    LIST_OT_DeleteItem,
    LIST_OT_PauseResumeTask,
    LIST_OT_MoveItem, 
    MY_OT_CycleTaskStatus,
    MY_UL_List,
    TM_PT_Timer_Panel,
    TM_UL_ListChrono,
    TM_OP_FindHelp,
    modify_task_OP,
    ImportListOperator, 
    TM_PT_Option,
    TM_OT_AddTimer,
    TM_OT_RemoveTimer,
    TM_OT_play_timer,
    TM_OT_reset_timer,
    VIEW3D_MT_pie_select,
    

    
    
    
    


)

# -----------------------------------------------------------------------------
#  register
# ----------------------------------------------------------------------------- 

def register():  
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
        bpy.utils.register_class(cls) 
    
    bpy.types.Scene.my_list = CollectionProperty(type=ListTache) 
    bpy.types.Scene.my_list_timer = CollectionProperty(type=ListTimers) 
    bpy.types.Scene.list_index = IntProperty(name="Index for my_list", default=0)
    bpy.types.Scene.list_index_timer = IntProperty(name="Index for my_list_timer", default=0)
    bpy.types.Scene.active_timer_index = bpy.props.IntProperty(default=-1)
    pcoll = bpy.utils.previews.new()
    preview_collections["main"] = pcoll
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    
    
    for icon_name in os.listdir(my_icons_dir):
        if icon_name.endswith(".png"):
            pcoll.load(icon_name[:-4], os.path.join(my_icons_dir, icon_name), 'IMAGE')
    bpy.types.Scene.pause_modal_timer = bpy.props.BoolProperty(
     name="Pause Modal Timer",
     description="Pause the Modal Timer",
     default=False
 )
    bpy.types.Scene.is_datecomplete = BoolProperty(
        name="afficher date",
            description="Some tooltip",
            default = True)
    bpy.types.Scene.is_recurrence = BoolProperty(
        name="afficher recurrence",
            description="Some tooltip",
            default = True)

    bpy.types.Scene.sound_volume = bpy.props.FloatProperty(
        name="Volume",
        description="Volume of the sound",
        default=0.5,
        min=0.0,
        max=1.0
    )
    bpy.types.Scene.sound_choice = bpy.props.EnumProperty(
        name="Sound Choice",
        description="Choose a sound to play",
        items=(
            ("retro-game-notification", "Retro Game Notification", ""),
            ("menuselect", "Menu Select", ""),
            ("coin-up_G#_minor", "coin-up", ""), 
            ("messenger-notification", "messenger notification", ""),   
            ("success-notification", "success notification", ""),
            ("super-mario-coin-sound", "super mario coin", ""),
               
        ),
        default="retro-game-notification"
    )
    addon_updater_ops.register(bl_info)
    bpy.types.Scene.modal_timer_running = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.subpanel_status = BoolProperty(default=False)
    bpy.types.Scene.subpanel_status_2 = BoolProperty(default=False)
    bpy.types.Scene.subpanel_status_3 = BoolProperty(default=False)
    bpy.types.Scene.subpanel_status_4 = BoolProperty(default=False)
    bpy.types.Scene.subpanel_status_5 = BoolProperty(default=False)
    bpy.context.window_manager.modal_handler_add
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)   
    
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    del bpy.types.Scene.my_list
    del bpy.types.Scene.list_index
    del bpy.types.Scene.sound_volume
    del bpy.types.Scene.sound_choice
    

if __name__ == "__main__": 
    register()  
    
    
 

    


    
