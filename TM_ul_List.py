import bpy

from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty, FloatVectorProperty, FloatProperty, EnumProperty 
from bpy.types import PropertyGroup, UIList, Operator, Panel , Header , AddonPreferences
from bpy.app.handlers import persistent
import bpy.utils.previews


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
    
