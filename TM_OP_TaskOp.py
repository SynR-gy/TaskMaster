#_______________________ Imports standard de Python_______________________#


import os
import datetime
import time 
import os.path

#___________________Imports liés à Blender_______________________#

import bpy

from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty, FloatVectorProperty, FloatProperty, EnumProperty 
from bpy.types import PropertyGroup, UIList, Operator, Panel , Header
from bpy.app.handlers import persistent
import bpy.utils.previews



def get_filename():
    if hasattr(bpy.context, "blend_data") and bpy.context.blend_data.is_saved:
        return os.path.splitext(os.path.basename(bpy.data.filepath))[0]
    else:
        return "default"

filename = get_filename()




class LIST_OT_NewItem(Operator):
    """Add a new item to the list."""
    bl_idname = "my_list.new_item"
    bl_label = "Options d'ajout d'une tache"
   
    tags: EnumProperty(
        items=[
            ('MOD', "Modelisation", ""),
            ('SHADING', "Shadding", ""),
            ('RENDER', "Rendu", ""),
            ('POST_PROD', "Post-prod", ""),
            ('ANIM', "Animation", ""),
            ('SCRIPT', "Scripting", ""),
            ('Sculp', "Sculpting", ""),
            ('UV', "Uv Edit", ""),
            ('GN', "geo-node", ""),
        ],
        name="Tags",
    )
    recurrence: bpy.props.EnumProperty(name="Récurrence", 
                                       items=[("NONE", "Aucune", "Aucune"), 
                                            ("DAILY", "Quotidienne", "Quotidienne"),
                                            ("WEEKLY", "Hebdomadaire", "Hebdomadaire"),
                                            ("MONTHLY", "Mensuelle", "Mensuelle"),
                                            ("YEARLY", "Annuelle", "Annuelle")]
                                            )
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")   
    
    
    def get_display_duration(self):
        if self.deadline_duration >= 60:
            return f"{self.deadline_duration // 60} min"
        else:
            return f"{self.deadline_duration} sec"
       
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        self.layout.prop(self, "name")
        self.layout.prop(self, "description")
        self.layout.prop(self, "recurrence")
        self.layout.prop(self, "tags")
        
                
    def execute(self, context):
        context.scene.my_list.add()
        new_item = context.scene.my_list[-1]
        new_item.name = self.name
        new_item.description = self.description
        new_item.date_created = datetime.datetime.now().strftime("%H:%M %d/%m/%Y")
        new_item.file_name = filename
        new_item.is_pausedtask = True
        new_item.tags = self.tags
        new_item.recurrence = self.recurrence
        if new_item.recurrence != "NONE":
            new_item.reminder_date = self.calculate_reminder_date(new_item.date_created, new_item.recurrence)
    
        
        new_item.task_status = "PENDING"
        return {'FINISHED'}
    
    def calculate_reminder_date(self, start_date, recurrence):
        start_date = datetime.datetime.strptime(start_date, "%H:%M %d/%m/%Y")
        if recurrence == "NONE":
            print(start_date + datetime.timedelta(weeks=1))
            return start_date + datetime.timedelta(weeks=1)
        elif recurrence == 'DAILY':
            print(start_date + datetime.timedelta(days=1))
            return start_date + datetime.timedelta(days=1)
        elif recurrence == 'WEEKLY':
            print(start_date + datetime.timedelta(weeks=1))
            return start_date + datetime.timedelta(weeks=1)

        elif recurrence == 'MONTHLY':
            next_month = start_date.month + 1
            next_year = start_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            print(start_date.replace(month=next_month, year=next_year))
            return start_date.replace(month=next_month, year=next_year)
        
        elif recurrence == 'YEARLY':
            return start_date + datetime.timedelta(days=365)
        else:
            raise ValueError('Invalid reminder mode')

class LIST_OT_PauseResumeTask(Operator):
    bl_idname = "my_list.pause_resume_task"
    bl_label = "Pause or Resume Task"
    task_index: IntProperty()
    
    def execute(self, context):
        task = context.scene.my_list[self.task_index]
        if task.is_pausedtask:
            task.is_pausedtask = False
            task.is_resumedtask = True
            task.task_status = 'COMPLETED'
            
        else:
            task.is_pausedtask = True
            task.is_resumedtask = False
            task.task_status = 'PENDING'
        return {'FINISHED'}

class LIST_OT_DeleteItem(Operator):
    bl_idname = "my_list.delete_item"
    bl_label = "Deletes an item"
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    exported_active_task = False
    

    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.list_index
        my_list.remove(index)
        context.scene.list_index = min(max(0, index - 1), len(my_list) - 1)
        return {'FINISHED'}

class LIST_OT_MoveItem(Operator):
    """Move an item in the list."""
    bl_idname = "my_list.move_item"
    bl_label = "Move an item in the list"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))
    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.scene.list_index
        list_length = len(bpy.context.scene.my_list) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)
        bpy.context.scene.list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.list_index
        neighbor = index + (-1 if self.direction == 'UP' else 1)
        my_list.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}


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
