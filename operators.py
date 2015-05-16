from bpy import types, props, utils

from .configuration import DEFAULT_TEMPLATE_MODULES
from .utilities import get_active_item


class LOGIC_OT_add_rpc(types.Operator):
    """Add a new RPC call"""
    bl_idname = "network.add_rpc_call"
    bl_label = "Add RPC call"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        obj.rpc_calls.add()

        return {'FINISHED'}


class LOGIC_OT_remove_rpc(types.Operator):
    """Delete selected RPC call"""
    bl_idname = "network.remove_rpc_call"
    bl_label = "Remove RPC call"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        obj.rpc_calls.remove(obj.rpc_calls_index)

        return {'FINISHED'}


class LOGIC_OT_add_template(types.Operator):
    """Load templates from a module"""
    bl_idname = "network.add_template"
    bl_label = "Add template"

    path = props.StringProperty(name="Path", description="Path to templates")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.active_object
        name = self.path

        try:
            __import__(name, fromlist=[''])

        except (ValueError, ImportError):
            return {'CANCELLED'}

        template = obj.templates.add()
        template.name = name

        return {'FINISHED'}


class LOGIC_OT_remove_template(types.Operator):
    """Unload templates from a module"""
    bl_idname = "network.remove_template"
    bl_label = "Remove template"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        active_template = get_active_item(obj.templates, obj.templates_index)

        if not active_template.name in DEFAULT_TEMPLATE_MODULES:
            obj.templates.remove(obj.templates_index)

        return {'FINISHED'}


class LOGIC_OT_set_states_from_visible(types.Operator):
    """Write currently visible states to mask for this netmode"""
    bl_idname = "network.set_states_from_visible"
    bl_label = "Save logic states for this netmode"

    set_simulated = props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        if self.set_simulated:
            states = obj.simulated_states

        else:
            states = obj.states[obj.states_index].states

        states[:] = obj.game.states_visible

        return {'FINISHED'}


class LOGIC_OT_show_states(types.Operator):
    """Read currently visible states from mask for this netmode"""
    bl_idname = "network.show_states"
    bl_label = "Set the states for this netmode visible"

    index = props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object

        active_state = obj.states[self.index]
        obj.game.states_visible = active_state.states

        for area in context.screen.areas:
            if area.type != 'LOGIC_EDITOR':
                continue

            area.tag_redraw()

        return {'FINISHED'}


class LOGIC_OT_select_network_objects(types.Operator):
    """Create group for network objects in scene"""
    bl_idname = "network.select_all"
    bl_label = "Select all network objects"

    def execute(self, context):
        for obj in context.scene.objects:
            obj.select = obj.use_network

        return {'FINISHED'}


class WM_OT_info_operator(types.Operator):
    bl_idname = "wm.display_info"
    bl_label = "Popup Message"

    message = props.StringProperty(name="Message")

    def execute(self, context):
        self.report({'INFO'}, self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text=self.message, icon='INFO')


def register():
    utils.register_module(__name__)


def unregister():
    utils.unregister_module(__name__)