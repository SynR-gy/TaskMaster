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
    "version" : (1, 7 ,0),
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

#___________________ Imports updater_______________________#

from . import addon_updater_ops
# -----------------------------------------------------------------------------
#   VARIABLES
# ----------------------------------------------------------------------------- 
def reset_filename(dummy):
    global filename
    filename = "default"



preview_collections = {}

addon_dir = os.path.dirname(__file__)
csv_file = os.path.join(addon_dir, "tasks.csv")

# -----------------------------------------------------------------------------
bpy.app.handlers.load_post.append(reset_filename)
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
#    LISTE DES TACHES  
# ----------------------------------------------------------------------------- 



class ListTache(PropertyGroup):
    tags: EnumProperty(
        name="Tags",
        items=[
            ('MOD', "Modeling", ""),
            ('SHADING', "Shadding", ""),
            ('RENDER', "Render", ""),
            ('POST_PROD', "Post-prod", ""),
            ('ANIM', "Animation", ""),
            ('Sculp', "Sculpting", ""),
            ('UV', "Uv Edit", ""),
            ('GN', "geo-node", ""),
            ('SCRIPT', "Scripting", ""),
        ],
        default='MOD',
    )
    task_index = IntProperty()

    name: StringProperty(
       name="Name",
       description="A name for this item",
       default="Tache",
    )
    description: StringProperty(
       name="Description",
       description="Description of the task",
       default="description",
    )
    
    date_created: StringProperty(
        name="Date Created",
        description="Date the task was created",
        default="datetime.now().isoformat()",
    )
    file_name: StringProperty(
        name="File Name",
        description="Name of the file in which the task was created",
        default="",
    )
    is_pausedtask: BoolProperty(
        name="Is Paused?",
        default=False,
    )
    is_resumedtask: BoolProperty(
        name="Is Resumed?",
        default=True,
    )
    
    is_running: BoolProperty(
        name="is_running?",
        default=False,
    )
    
    task_status: EnumProperty(
        name="Task Status",
        items=[('PENDING', "Pending", "The task is yet to start"),
               ('IN_PROGRESS', "In Progress", "The task is currently in progress"),
               ('COMPLETED', "Completed", "The task is completed")],
        default='PENDING',
    )
    end_time: IntProperty(
        name="End Time",
        default=0,
    )
    
    
    active_index: IntProperty()
    is_completed: BoolProperty(
        name="Tâche terminée",
        description="Indique si la tâche est terminée",
        default=False
    )

    is_datecomplete = bpy.props.BoolProperty(default=False)
    checkbox_timer = bpy.props.BoolProperty(default=False)
    is_timer_running: BoolProperty(default=False)
    recurrence: bpy.props.EnumProperty(name="Récurrence", 
                                       items=[("NONE", "Aucune", "Aucune"), 
                                            ("DAILY", "Quotidienne", "Quotidienne"),
                                            ("WEEKLY", "Hebdomadaire", "Hebdomadaire"),
                                            ("MONTHLY", "Mensuelle", "Mensuelle"),
                                            ("YEARLY", "Annuelle", "Annuelle")]
                                            )
    
class ListTimers(PropertyGroup):
    timer_index = IntProperty()
    active_timer_index = IntProperty()
    is_paused_timer: BoolProperty(
        name="Is Paused?",
        default=False,
    )
    is_resumed_timer: BoolProperty(
        name="Is Resumed?",
        default=True,
    )
    elapsed_time: IntProperty(
        name="Elapsed Time",
        description="Time elapsed since between play and pause",
        default=0,
    )
    is_running: BoolProperty(
        name="is_running?",
        default=False,
    )
    start_time: IntProperty(
        name="Start Time",
        default=0,
    )
    end_time: IntProperty(
        name="End Time",
        default=0,
    )
    chrono_active: BoolProperty(
        name="Is deadline active?",
        default=True,
    )
    
    is_completed: BoolProperty(
        name="Timer terminé",
        description="Indique si le timer est terminé",
        default=False
    )
    chrono_time: IntProperty(
        name="Chrono Time",
        description="Chrono Time",
        default=0,
    )
    chrono_running: BoolProperty(
        name="Chrono Running",
        description="Chrono Running",
        default=False,
    )
    chrono_paused: BoolProperty(
        name="Chrono Paused",
        description="Chrono Paused",
        default=False,
    )
    
# -----------------------------------------------------------------------------
#  FUNCTIONS 
# ----------------------------------------------------------------------------- 


def format_time(time):
    hours, remainder = divmod(int(time), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}".format(int(hours), int(minutes), int(seconds))

# -----------------------------------------------------------------------------
#   ui list tasks
# ----------------------------------------------------------------------------- 

class MY_UL_List(UIList):
    task_index: bpy.props.IntProperty() 
    

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout = layout.row()
        row = layout.row()  
        pcoll = preview_collections["main"]
        
        if item.is_pausedtask:
            my_icon = pcoll["uncheck2"]    
        else:
            my_icon = pcoll["check1"]  
        row.scale_x = .7  
        row.operator("my_list.pause_resume_task", icon_value=my_icon.icon_id, text="", emboss=False).task_index = index
        row = layout.row()   
        row.scale_x = .7
        row.prop(item, "name", text="", emboss=False)  
        row.scale_x =  .7   
        row.prop(item, "tags", text="", emboss=False)  
         
        if context.scene.is_recurrence:
            row.scale_x =.5
            row.label(text=item.recurrence)  
            
        if context.scene.is_datecomplete:
            row.scale_x = .8
            row.label(text=item.date_created)   
        else:
            row.scale_x =  .4  
            row.label(text=item.date_created.split(" ")[0])

        if item.task_status == 'PENDING':
            layout.label(text='To Do', icon_value=pcoll["afaire1"].icon_id)               
        elif item.task_status == 'IN_PROGRESS':
            layout.label(text='Begin', icon_value=pcoll["begin"].icon_id)         
        elif item.task_status == 'COMPLETED':
            layout.label(text='Finish', icon_value=pcoll["fini1"].icon_id)
        row.scale_x = 2   
        layout.operator("my.cycle_task_status", text="", icon_value=pcoll["refresh1"].icon_id).task_index = index
        


    def update_timer(self, context):
        task = context.scene.my_list[self.task_index]
        if task.is_running:
            task.elapsed_time += time.time() - task.start_time
            task.start_time = time.time()
            bpy.context.area.tag_redraw()
    def modal(self, context, event):
        if event.type == 'TIMER': 
                bpy.context.area.tag_redraw()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return {'RUNNING_MODAL'}
    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# -----------------------------------------------------------------------------
#   ui list timers
# ----------------------------------------------------------------------------- 
class TM_UL_ListChrono(UIList):
    timer_index : bpy.props.IntProperty() 

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            
            if item.chrono_active:
                # Get time remaining
                tabs = layout.row()
                remaining_time =  ( item.chrono_time - item.elapsed_time )
                remaining_time_max = max(remaining_time, 0)
                hours, remainder = divmod(remaining_time_max, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                row.label(text="{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds)))
                progress = item.elapsed_time / item.chrono_time
                if progress < 101:
                    tabs=layout.row()
                    tabs.scale_x = 1.3
                    tabs.label(text=f"Progress: {progress:.0%}")
                    
            else:
                
                # Draw timer with elapsed time
                elapsed_time = item.elapsed_time
                hours, remainder = divmod(elapsed_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                row.label(text="{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds)))
                
            
# -----------------------------------------------------------------------------
#    OPERATORS
# ----------------------------------------------------------------------------- 

class MY_OT_CycleTaskStatus(Operator):
    bl_idname = "my.cycle_task_status"
    bl_label = "Cycle Task Status"
    task_index: IntProperty()
    bpy.types.Scene.my_list_index = bpy.props.IntProperty()
    def execute(self, context):
        task_list = context.scene.my_list
        task = task_list[self.task_index]
        if task.task_status == 'PENDING':
            task.task_status = 'IN_PROGRESS'
            
        elif task.task_status == 'IN_PROGRESS':
            task.task_status = 'COMPLETED'
            
        elif task.task_status == 'COMPLETED':
            task.task_status = 'PENDING'
            
        return {'FINISHED'}
    
# -----------------------------------------------------------------------------
#  panel
# ----------------------------------------------------------------------------- 

class MY_PT_ParentPanel(Panel):
    bl_label = "Task Master"
    bl_idname = "MY_PT_ParentPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Task Master"
    preview_collections = {"main"}
    
    _test_modal = None
    
    def __init__(self):
        self._timer = None
        self.start_time = None
        self.elapsed_time = 0
        
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        
        icon = 'TRIA_DOWN' if context.scene.subpanel_status_4 else 'TRIA_RIGHT'
        row.prop(context.scene, 'subpanel_status_4', icon=icon, icon_only=True)
        row.label(text='Tasks')
        
        if context.scene.subpanel_status_4:
            pcoll = preview_collections["main"]
            row.alignment = 'LEFT'

            finished_tasks_count = 0
            task_list = context.scene.my_list
            for task in task_list:
                if task.is_resumedtask :
                    finished_tasks_count += 1
                elif task.task_status == 'COMPLETED':
                    finished_tasks_count += 1
            
                


            # Afficher le nombre de tâches terminées / nombre total de tâches
            layout = self.layout
            row = layout.row()
            col = row.column()
            split = col.split(align=True)
            split.label(text="Tâches terminées : {} / {}".format(finished_tasks_count, len(task_list)))
            row = layout.row()
            
            split.label(text="Tâches en cours : {}".format(len(task_list) - finished_tasks_count))
            row = col.row(align=True)
            row.template_list("MY_UL_List", "", context.scene, "my_list", context.scene, "list_index")   
            
            col = row.column(align=True)
            col.operator("my_list.new_item", text="", icon_value=pcoll["plusblack1"].icon_id)
            col.operator("my_list.delete_item", text="", icon_value=pcoll["minusblack1"].icon_id)
            col.operator('my_list.move_item', icon_value=pcoll["plus1"].icon_id, text="").direction = 'UP'
            col.operator('my_list.move_item', icon_value=pcoll["minus1"].icon_id, text="").direction = 'DOWN'
            col.operator("object.modify_task", icon_value=pcoll["Setting"].icon_id, text="")
            pie_menu = col.menu_pie()
            pie_menu.operator("wm.call_menu_pie", icon_value=pcoll["importcsv1"].icon_id, text="").name = "VIEW3D_MT_pie_select"
            
                        
           
        row = layout.row()
        icon = 'TRIA_DOWN' if context.scene.subpanel_status_5 else 'TRIA_RIGHT'
        row.prop(context.scene, 'subpanel_status_5', icon=icon, icon_only=True)
        row.label(text='options')
        
        if context.scene.subpanel_status_5:
            pcoll = preview_collections["main"]
            split = layout.split(factor=.5, align=True)
            sce = context.scene
            box = layout.box()
            row = box.row(align=True)
            row.prop(sce, "is_datecomplete") 
            row.prop(sce, "is_recurrence", text="afficher recurrence")
        layout = self.layout
        row = layout.row()
        # subpanel
        
     
        
        

class TM_PT_Option(Panel):
    bl_label = "Options"
    bl_idname = "MY_PT_OptionPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Task Master"
    preview_collections = {"main"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.operator('taskmaster.find_help', text="Find help.", icon='INFO')                
        
        
        

            

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

addon_keymaps = []

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
    
    
 

    


    