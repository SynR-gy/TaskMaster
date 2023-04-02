import bpy
import time


def format_time(time):
    hours, remainder = divmod(int(time), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}".format(int(hours), int(minutes), int(seconds))

class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs itself from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Lance l'actualisation des timers"
    bl_description = "actualisation les timers"
    _timer = None
    refresh_time = bpy.props.FloatProperty(name="Refresh Time", default=1.0)

    def __init__(self):
        self._timer = None
          
        return None

    def modal(self, context, event):
        context.area.tag_redraw()
        if bpy.context.scene.pause_modal_timer:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            for task in context.scene.my_list:
                if task.is_running:
                    task.elapsed_time += int(time.time()) - int(task.start_time)
                    task.start_time = int(time.time())
                    if task.deadline_active and task.elapsed_time >= task.deadline_duration:
                        task.is_running = False
                        task.start_time = 0
                        task.elapsed_time = 0

                context.area.tag_redraw()
                if task.deadline_active:
                    time_left = task.deadline_duration - task.elapsed_time
                    if time_left < 0:
                        task.is_running = False
                        task.elapsed_time = task.deadline_duration
                    else:
                        task.countdown = time_left
                        task.countdown_str = format_time(time_left)
                context.area.tag_redraw()
        context.area.tag_redraw()
        return {'PASS_THROUGH'}
    

    def execute(self, context):
        wm = context.window_manager
        wm.modal_handler_add(self)
        self._timer = wm.event_timer_add(time_step=1.0, window=context.window)
        self.invoke(context, None)
            
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def invoke(self, context, event):
        wm = context.window_manager
        wm.modal_handler_add(self)
        self._timer = wm.event_timer_add(time_step=1.0, window=context.window)
        return {'RUNNING_MODAL'}

