
import importlib
import bpy
import time
import aud
from bpy.props  import BoolProperty ,FloatProperty
import os
bpy.types.Scene.is_chrono = BoolProperty(name="Chrono?", default=False)




class TM_PT_Timer_Panel(bpy.types.Panel):
    bl_label = " Timer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Task Master"
    

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw(self, context):
        layout = self.layout
        list_timers = context.scene.my_list_timer
        row = layout.row()
        row.prop(context.scene,"is_chrono", text="Chronomètre" )
        row.scale_y = .8
        row = layout.row()
        if len(list_timers) <= 0:
            col = layout.column(align=True)
            col.operator("tm.add_timer", icon='ADD', text="")   
        else:
            col = row.column(align=True)
            col.template_list("TM_UL_ListChrono","", context.scene, "my_list_timer", context.scene, "list_index_timer", type='DEFAULT', rows=3)
            col = row.column(align=True)
            col.operator("tm.play_timer", icon='PLAY', text="")
            col.operator("tm.reset_timer", icon='SNAP_FACE', text="")
            col.operator("tm.add_timer", icon='ADD', text="")
            col.operator("tm.remove_timer", icon='REMOVE', text="")
       
class TM_OT_AddTimer(bpy.types.Operator):
    bl_idname = "tm.add_timer"
    bl_label = "Add Timer"
    bl_description = "Add a simple timer"
    
    chrono_time: bpy.props.IntProperty(name="Chrono Time in min ", default=1, min=1, max=1000000)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        if context.scene.is_chrono:
            self.layout.prop(self, "chrono_time")
        
    def execute(self, context):
        list_timers = context.scene.my_list_timer
        if context.scene.is_chrono:
            chrono_time_min = self.chrono_time*60
            chrono = list_timers.add()
            chrono.chrono_active = True 
            list_timers[-1].chrono_time = chrono_time_min 
            list_timers[-1].start_time = int(time.time())
            list_timers[-1].elapsed_time = 0
            list_timers[-1].is_running = False
            list_timers[-1].chrono_running = False
            list_timers[-1].chrono_paused = False    
        else:
            timer = list_timers.add()
            timer.chrono_active = False               
            list_timers[-1].start_time = int(time.time())
            list_timers[-1].elapsed_time = 0
            list_timers[-1].is_running = False
            list_timers[-1].is_paused = False
            list_timers[-1].is_paused_timer = False
        return {'FINISHED'}
    
       
class TM_OT_RemoveTimer(bpy.types.Operator):
    bl_idname = "tm.remove_timer"
    bl_label = "Remove Timer"
    bl_description = "Remove the selected timer or chrono"

    
    @classmethod
    def poll(cls, context):
        return context.scene.my_list_timer
    
    def execute(self, context):
        list_timers = context.scene.my_list_timer
        index = context.scene.list_index_timer
        list_timers.remove(index)
        context.scene.list_index_timer = min(max(0, index - 1), len(list_timers) - 1)
        return {'FINISHED'}

class TM_OT_play_timer(bpy.types.Operator):
    """Start or resume a timer"""
    bl_idname = "tm.play_timer"
    bl_label = "Play Timer"
    bl_description = "Start or resume a timer"

    timer_index: bpy.props.IntProperty() 
    _timer = None

    def execute(self, context):
        list_timers = context.scene.my_list_timer
        index = context.scene.list_index_timer
        
        if not list_timers[index].is_running:
            # Start the timer from 0
            list_timers[index].start_time = int(time.time())
            list_timers[index].is_running = True
            list_timers[index].is_paused_timer = False
            list_timers[index].is_paused = False
            
        elif list_timers[index].is_paused_timer:
            list_timers[index].start_time = int(time.time()) - list_timers[index].elapsed_time
            list_timers[index].is_paused_timer = False
            list_timers[index].is_paused = False
            self.report({'INFO'}, "Timer is running")

        else:
            # Pause the timer
            list_timers[index].is_paused_timer = True
            list_timers[index].is_paused = True
            
        # Start or stop the timer handler
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        if list_timers[index].is_running and not list_timers[index].is_paused_timer:
            self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
            context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        list_timers = context.scene.my_list_timer
          
        for timer in list_timers:
            if timer.is_running:
                if not timer.is_paused_timer:
                    current_time = int(time.time())
                    timer.elapsed_time = current_time - timer.start_time
                # Update start time if resumed from pause
                else:
                     timer.start_time = int(time.time()) - timer.elapsed_time
                # Update the initial_time when the timer is first started
                if not hasattr(timer, 'initial_time'):
                    timer.initial_time = timer.start_time
                    
                if timer.elapsed_time >= timer.chrono_time and timer.chrono_active:
                    timer.elapsed_time = timer.chrono_time
                    timer.is_running = False
                    timer.is_paused_timer = False
                    self.play_sound()
                    self.report({'INFO'}, "Timer is complete")
                    
                    return {'FINISHED'}
                # Redraw the UI list
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
        return {'PASS_THROUGH'}
    def play_sound(self):
        vol = bpy.context.scene.sound_volume
        sound_choice = bpy.context.scene.sound_choice 
        sound_path = os.path.join(os.path.dirname(__file__), f"sound/{sound_choice}.wav") 
        device = aud.Device()
        sound = aud.Sound(sound_path)
        device.volume = vol 
        device.play(sound)

    

    def invoke(self, context, event):
        # Check if there are any timers in the list
        if not context.scene.my_list_timer:
            self.report({'WARNING'}, "No timers in the list")
            return {'CANCELLED'}
        
        return self.execute(context)

class TM_OT_reset_timer(bpy.types.Operator):
    """Reset the timer"""
    bl_idname = "tm.reset_timer"
    bl_label = "Reset Timer"
    bl_description = "Reset the timer"

    timer_index: bpy.props.IntProperty()
    
    def execute(self, context):
        list_timers = context.scene.my_list_timer
        index = context.scene.list_index_timer
        if not context.scene.my_list_timer:
            self.report({'WARNING'}, "No timers in the list")
            return {'CANCELLED'}

        # Reset the timer if it's timer
        return (
            self._extracted_from_execute_13(list_timers, index)
            if list_timers[index].chrono_active
            else self._extracted_from_execute_10(list_timers, index)
        )

    def _extracted_from_execute_13(self, list_timers, index):
        # Reset the chrono at is initial value
        list_timers[index].start_time = list_timers[index].chrono_time
        print(list_timers[index].start_time)
        list_timers[index].elapsed_time = 0
        list_timers[index].is_running = False
        list_timers[index].is_paused = False
        list_timers[index].is_paused_timer = False
        return {'FINISHED'}

    
    def _extracted_from_execute_10(self, list_timers, index):
            list_timers[index].is_running = False
            list_timers[index].start_time = 0
            list_timers[index].end_time = 0
            list_timers[index].elapsed_time = 0
            list_timers[index].is_paused= True
            list_timers[index].is_paused_timer= True
            return {'FINISHED'}

