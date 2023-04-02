import bpy
from bpy.types import Panel , UIList, Operator
import bpy.utils.previews

import os  

preview_collections = {}
pcoll = bpy.utils.previews.new()
preview_collections["main"] = pcoll
my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
for icon_name in os.listdir(my_icons_dir):
    if icon_name.endswith(".png"):
        pcoll.load(icon_name[:-4], os.path.join(my_icons_dir, icon_name), 'IMAGE')

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
        
     
        
        