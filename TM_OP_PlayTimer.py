import bpy


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
                    play_sound()
                    self.report({'INFO'}, "Timer is complete")
                    
                    return {'FINISHED'}
                # Redraw the UI list
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        # Check if there are any timers in the list
        if not context.scene.my_list_timer:
            self.report({'WARNING'}, "No timers in the list")
            return {'CANCELLED'}
        
        return self.execute(context)


