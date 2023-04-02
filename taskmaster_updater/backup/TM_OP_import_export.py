

import bpy
import json
import os


class ImportListOperator(bpy.types.Operator):
    """Importer une liste à partir d'un fichier json"""
    bl_idname = "wm.import_list"
    bl_label = "Importer une liste"
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        task_list = context.scene.my_list

        # Vérifier que le fichier existe
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "Le fichier n'existe pas : {}".format(self.filepath))
            return {'CANCELLED'}

        # Ouvrir le fichier JSON et lire son contenu
        with open(self.filepath, mode='r') as json_file:
            data = json.load(json_file)

        # Supprimer tous les éléments de la liste existante
        task_list.clear()

        # Ajouter les éléments du fichier à la liste
        for item in data:
            task = task_list.add()
            task.name = item.get("name")
            task.description = item.get("description")
            
            task.is_completed = item.get("is_completed")
            task.task_status = item.get("task_status")
            task.date_created = item.get("date_created")
            task.file_name = item.get("file_name")
            task.tags = item.get("tags")
            task.end_time = item.get("end_time")
            task.recurrence = item.get("reccurence")

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ExportActiveTaskOperator(bpy.types.Operator):
    """Exporter la tâche active dans un fichier json"""
    bl_idname = "wm.export_active_task"
    bl_label = "Exporter la tâche"
    bl_description = "Exporter la tâche active dans un fichier de tableau"


    filepath: bpy.props.StringProperty(subtype='FILE_PATH', options={'LIBRARY_EDITABLE'})
    exported_active_task = False
    export_all_tasks: bpy.props.BoolProperty(
        name="Export all tasks",
        description="Export all tasks in the list",
        default=True
    )
    filter_glob: bpy.props.StringProperty(
        default='*.csv;*.xlsx;*.json',
        options={'HIDDEN'},
        maxlen=255,
    )
    filename: bpy.props.StringProperty(
        name="Filename",
        default="export.json",
        description="Name of file to save",
        maxlen=255,
        subtype='FILE_NAME'
    )
    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def execute(self, context):
        task_list = context.scene.my_list

        # Convertir les tâches en liste de dictionnaires
        data = []
        for task in task_list:
            item = {
                "name": task.name,
                "description": task.description,

                "is_completed": task.is_completed,
                "task_status": task.task_status,
                "date_created": task.date_created,
                "file_name": task.file_name,
                "tags": task.tags,
                "end_time": task.end_time,
                "reccurence": task.recurrence,
            }
            data.append(item)

        # Écrire les données dans le fichier JSON
        with open(self.filepath, mode='w') as json_file:
            json.dump(data, json_file, indent=4)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        
         
   
        return {'RUNNING_MODAL'}
