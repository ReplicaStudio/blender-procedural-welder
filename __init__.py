import os

import bpy

ASSET_FILE_NAME = "weld_assets.blend"
GEO_NODE_NAME = "GN_Procedural_Weld"
FADE_NODE_GROUP_NAME = "NG_Weld_Edge_Fade"


# ==============================================================================
# 1. 中英字典
# ==============================================================================
TRANSLATIONS_DICT = {
    "zh_HANS": {
        ("*", "Procedural Welder"): "程序化焊缝生成器",
        ("*", "Create"): "创建",
        ("*", "Create Weld"): "生成焊缝",
        ("*", "Parameter Control"): "参数控制",
        ("*", "Material Blending"): "材质融合",
        ("*", "Apply Edge Fade"): "应用边缘羽化",
        ("*", "Convert to Mesh"): "转为静态网格",
        ("Operator", "Create Weld"): "生成焊缝",
        ("Operator", "Apply Edge Fade"): "应用边缘羽化",
        ("Operator", "Convert to Mesh"): "转为静态网格",
    },
}
# 兼容地区代码
TRANSLATIONS_DICT["zh_CN"] = TRANSLATIONS_DICT["zh_HANS"]

# 几何节点暴露端口映射表
NODE_SOCKET_I18N = {
    "Target Collection": {
        "zh": ("目标集合", "包含需要生成焊缝的相交物体的集合"),
        "en": (
            "Target Collection",
            "Collection containing intersecting source meshes to weld",
        ),
    },
    "Use Exact Solver": {
        "zh": (
            "高精度布尔",
            "焊接复杂物体及非流形物体时启用，精度更高，但性能消耗更大，请在应用前保存",
        ),
        "en": (
            "Use Exact Solver",
            "Enable when welding complex or non-manifold objects for higher precision, but with greater performance cost. Please save before applying",
        ),
    },
    "Sample Resolution": {
        "zh": ("焊缝采样精度", "调整采样精度以贴合物体间交线"),
        "en": (
            "Sample Resolution",
            "Adjust the sampling resolution to fit the intersection line between objects",
        ),
    },
    "Costume Bead": {
        "zh": ("替换焊点模型", "可自定义焊点模型，实例的+Z永远朝向焊缝夹角的中央"),
        "en": (
            "Costume Bead",
            "Custom weld point model supported; the instance's +Z always faces the center of the weld seam angle",
        ),
    },
    "Weld Scale": {
        "zh": ("焊缝缩放", "控制焊缝整体的粗细与尺寸比例"),
        "en": ("Weld Scale", "Overall thickness and scale of the weld bead"),
    },
    "Bead Density": {
        "zh": ("焊鳞密度", "控制沿交界线分布的焊鳞颗粒密集程度"),
        "en": ("Bead Density", "Density of weld ripples along the intersection curve"),
    },
    "Blend Edge": {
        "zh": ("边缘羽化范围", "控制焊缝边缘向母材过渡透明融合的宽度"),
        "en": ("Blend Edge", "Width of the transparent edge blending transition"),
    },
    "Weld Material": {
        "zh": (
            "焊缝材质",
            "指定焊缝网格所使用的自定义着色器材质，请在替换后手动使用材质融合进行边缘羽化",
        ),
        "en": (
            "Weld Material",
            "Custom shader material assigned to the weld bead, after replacing it, manually use material blending to feather the edges.",
        ),
    },
}


def is_chinese_locale():
    """判断当前 Blender 界面是否为中文环境"""
    try:
        lang = bpy.context.preferences.view.language
        if lang == "DEFAULT":
            lang = bpy.app.translations.locale
        return lang.startswith("zh_")
    except Exception:
        return False


def tr(en_text, zh_text):
    """用于动态提示消息 (self.report) 的快捷双语切换"""
    return zh_text if is_chinese_locale() else en_text


def localize_node_group_interface(ng):
    """根据当前界面语言，动态本地化几何节点暴露出的输入端口名称与悬停描述"""
    if not ng or not hasattr(ng, "interface"):
        return

    lang_key = "zh" if is_chinese_locale() else "en"
    for item in ng.interface.items_tree:
        if item.item_type == "SOCKET" and item.in_out == "INPUT":
            # 匹配原始英文名或已翻译过的中文名，支持随时切换语言
            for en_name, mapping in NODE_SOCKET_I18N.items():
                if item.name in (en_name, mapping["zh"][0], mapping["en"][0]):
                    new_name, new_desc = mapping[lang_key]
                    item.name = new_name
                    item.description = new_desc
                    break


# ==============================================================================
# 2. 核心资产与修改器工具函数
# ==============================================================================
def get_asset_filepath():
    addon_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(addon_dir, "assets", ASSET_FILE_NAME)


def ensure_node_group(group_name):
    """从 assets/weld_assets.blend 静默追加指定节点组"""
    ng = bpy.data.node_groups.get(group_name)
    if ng is not None:
        return ng

    filepath = get_asset_filepath()
    if not os.path.exists(filepath):
        return None

    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        if group_name in data_from.node_groups:
            data_to.node_groups = [group_name]

    return bpy.data.node_groups.get(group_name)


def get_active_weld_material(obj, mod):
    """通过 identifier 直接点取 Blender 5.3 的 mod.properties.inputs.<identifier>.value"""
    if mod and mod.node_group:
        for item in mod.node_group.interface.items_tree:
            if (
                item.item_type == "SOCKET"
                and item.in_out == "INPUT"
                and item.socket_type == "NodeSocketMaterial"
            ):
                ident = item.identifier
                if hasattr(mod, "properties") and hasattr(mod.properties, "inputs"):
                    inp = getattr(mod.properties.inputs, ident, None)
                    val = getattr(inp, "value", None)
                    if isinstance(val, bpy.types.Material):
                        return val.original if hasattr(val, "original") else val

                mat = getattr(item, "default_value", None)
                if isinstance(mat, bpy.types.Material):
                    return mat.original if hasattr(mat, "original") else mat

    if obj.active_material is not None:
        return (
            obj.active_material.original
            if hasattr(obj.active_material, "original")
            else obj.active_material
        )

    return None


# ==============================================================================
# 3. 算子与侧边栏面板定义
# ==============================================================================
class WELD_OT_CreateWeld(bpy.types.Operator):
    """Generate procedural weld bead along intersecting selected meshes"""

    bl_idname = "object.weld_create_from_selected"
    bl_label = "Create Weld"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        meshes = [o for o in context.selected_objects if o.type == "MESH"]
        return len(meshes) >= 2

    def execute(self, context):
        selected_meshes = [o for o in context.selected_objects if o.type == "MESH"]

        base_ng = ensure_node_group(GEO_NODE_NAME)
        if not base_ng:
            self.report(
                {"ERROR"},
                tr(
                    f"Node group '{GEO_NODE_NAME}' not found in assets/{ASSET_FILE_NAME}",
                    f"未在 assets/{ASSET_FILE_NAME} 中找到节点树 '{GEO_NODE_NAME}'",
                ),
            )
            return {"CANCELLED"}

        # 创建独立节点树副本并按当前语言更新端口名称与描述
        ng = base_ng.copy() if base_ng.users > 0 else base_ng
        localize_node_group_interface(ng)

        # 创建专属源集合
        idx = 1
        while f"Weld_Source_{idx:02d}" in bpy.data.collections:
            idx += 1
        col_name = f"Weld_Source_{idx:02d}"
        src_col = bpy.data.collections.new(col_name)
        context.scene.collection.children.link(src_col)

        for obj in selected_meshes:
            if obj.name not in src_col.objects:
                src_col.objects.link(obj)

        # 挂载给修改器前写入 Collection 默认值
        for item in ng.interface.items_tree:
            if (
                item.item_type == "SOCKET"
                and item.in_out == "INPUT"
                and item.socket_type == "NodeSocketCollection"
            ):
                item.default_value = src_col
                break

        weld_mesh = bpy.data.meshes.new(f"Weld_Bead_{idx:02d}_Mesh")
        weld_obj = bpy.data.objects.new(f"Weld_Bead_{idx:02d}", weld_mesh)
        weld_obj.location = (0.0, 0.0, 0.0)
        weld_obj.rotation_euler = (0.0, 0.0, 0.0)
        weld_obj.scale = (1.0, 1.0, 1.0)
        weld_obj.hide_select = (
            True  # 默认禁止视口框选，防止移动母材时误拖动焊缝导致偏移
        )
        context.scene.collection.objects.link(weld_obj)

        mod = weld_obj.modifiers.new(name="ProceduralWeld", type="NODES")
        mod.node_group = ng

        weld_obj.update_tag()
        context.view_layer.update()

        bpy.ops.object.select_all(action="DESELECT")
        weld_obj.select_set(True)
        context.view_layer.objects.active = weld_obj

        self.report(
            {"INFO"},
            tr(
                f"Created {weld_obj.name}, source collection: {col_name}",
                f"已生成 {weld_obj.name}，源集合：{col_name}",
            ),
        )
        return {"FINISHED"}


class WELD_OT_ApplyEdgeFade(bpy.types.Operator):
    """Inject edge transparency feathering node group into active weld material"""

    bl_idname = "object.weld_apply_edge_fade"
    bl_label = "Apply Edge Fade"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == "MESH"
            and any(m.type == "NODES" for m in obj.modifiers)
        )

    def execute(self, context):
        obj = context.active_object
        mod = next(
            (m for m in obj.modifiers if m.type == "NODES" and m.node_group), None
        )
        if not mod:
            self.report(
                {"WARNING"},
                tr(
                    "No weld Geometry Nodes modifier found",
                    "当前物体未挂载焊缝几何节点修改器",
                ),
            )
            return {"CANCELLED"}

        target_mat = get_active_weld_material(obj, mod)
        if not target_mat:
            self.report(
                {"WARNING"},
                tr("No weld material detected", "未检测到焊缝材质，请先指定一个材质"),
            )
            return {"CANCELLED"}

        if not target_mat.use_nodes or not target_mat.node_tree:
            target_mat.use_nodes = True

        fade_ng = ensure_node_group(FADE_NODE_GROUP_NAME)
        if not fade_ng:
            self.report(
                {"ERROR"},
                tr(
                    f"Shader group '{FADE_NODE_GROUP_NAME}' not found",
                    f"未在资产包中找到着色器组 '{FADE_NODE_GROUP_NAME}'",
                ),
            )
            return {"CANCELLED"}

        nt = target_mat.node_tree
        nodes = nt.nodes
        links = nt.links

        output_node = next(
            (n for n in nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output),
            None,
        )
        if not output_node:
            output_node = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
        if not output_node:
            self.report(
                {"WARNING"},
                tr(
                    f"Material '{target_mat.name}' has no Material Output node",
                    f"材质 '{target_mat.name}' 中缺少 Material Output 节点",
                ),
            )
            return {"CANCELLED"}

        surface_input = output_node.inputs.get("Surface")
        if not surface_input or not surface_input.is_linked:
            self.report(
                {"WARNING"},
                tr(
                    f"Surface socket of '{target_mat.name}' is not linked",
                    f"材质 '{target_mat.name}' 的 Surface 端口未连接任何着色器",
                ),
            )
            return {"CANCELLED"}

        from_socket = surface_input.links[0].from_socket
        if from_socket.node.type == "GROUP" and from_socket.node.node_tree == fade_ng:
            self.report(
                {"INFO"},
                tr(
                    f"Edge fade already applied to '{target_mat.name}'",
                    f"材质 '{target_mat.name}' 已应用边缘羽化，无需重复添加",
                ),
            )
            return {"FINISHED"}

        fade_node = nodes.new(type="ShaderNodeGroup")
        fade_node.node_tree = fade_ng
        fade_node.name = "Weld_Edge_Fade_Injected"
        fade_node.label = "Weld Edge Fade"
        fade_node.location = (output_node.location.x - 220, output_node.location.y)

        in_shader = fade_node.inputs.get("Shader") or next(
            (s for s in fade_node.inputs if s.type == "SHADER"), None
        )
        out_shader = fade_node.outputs.get("Shader") or next(
            (s for s in fade_node.outputs if s.type == "SHADER"), None
        )

        if not in_shader or not out_shader:
            nodes.remove(fade_node)
            self.report(
                {"ERROR"},
                tr(
                    f"'{FADE_NODE_GROUP_NAME}' lacks Shader input or output socket",
                    f"'{FADE_NODE_GROUP_NAME}' 缺少 Shader 输入或输出端口",
                ),
            )
            return {"CANCELLED"}

        links.remove(surface_input.links[0])
        links.new(from_socket, in_shader)
        links.new(out_shader, surface_input)

        nt.update_tag()
        target_mat.update_tag()

        self.report(
            {"INFO"},
            tr(
                f"Successfully applied edge fade to '{target_mat.name}'",
                f"已成功为材质 '{target_mat.name}' 注入边缘透明羽化",
            ),
        )
        return {"FINISHED"}


class WELD_OT_ConvertToMesh(bpy.types.Operator):
    """Bake procedural weld into static mesh while preserving vertex attributes and materials"""

    bl_idname = "object.weld_convert_to_mesh"
    bl_label = "Convert to Mesh"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == "MESH"
            and any(m.type == "NODES" for m in obj.modifiers)
        )

    def execute(self, context):
        obj = context.active_object

        context.view_layer.update()
        depsgraph = context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)

        new_mesh = bpy.data.meshes.new_from_object(
            eval_obj,
            preserve_all_data_layers=True,
            depsgraph=depsgraph,
        )

        if len(new_mesh.vertices) == 0:
            bpy.data.meshes.remove(new_mesh)
            self.report(
                {"WARNING"},
                tr(
                    "Weld geometry is empty, cannot convert",
                    "当前焊缝几何体为空，无法转换为静态网格",
                ),
            )
            return {"CANCELLED"}

        old_mesh = obj.data
        new_mesh.name = old_mesh.name
        obj.data = new_mesh
        obj.modifiers.clear()
        obj.hide_select = False  # 烘焙为静态网格后恢复视口可选中状态

        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)

        self.report(
            {"INFO"},
            tr(
                f"Baked to static mesh ({len(new_mesh.vertices)} vertices)",
                f"成功烘焙为静态网格（共 {len(new_mesh.vertices)} 个顶点）",
            ),
        )
        return {"FINISHED"}


class WELD_PT_MainPanel(bpy.types.Panel):
    """3D Viewport N-Panel UI"""

    bl_label = "Procedural Welder"
    bl_idname = "WELD_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Welder"

    def draw(self, context):
        layout = self.layout

        # 顶部：创建区
        box_create = layout.box()
        box_create.label(text="Create & Manage", icon="PLUS")
        row = box_create.row()
        row.scale_y = 1.4
        row.operator(WELD_OT_CreateWeld.bl_idname, icon="MOD_BUILD")

        obj = context.active_object
        if not obj:
            return

        mod = next(
            (m for m in obj.modifiers if m.type == "NODES" and m.node_group), None
        )

        # 如果当前选中的不是焊缝物体，但属于某个 Weld_Source 集合，提示其关联的焊缝物体名称
        if not mod:
            weld_cols = [
                c for c in obj.users_collection if c.name.startswith("Weld_Source_")
            ]
            if weld_cols:
                info_box = layout.box()
                info_box.label(
                    text=tr(
                        "Linked to weld collection (select in Outliner to edit):",
                        "当前母材已绑定焊缝（可在大纲视图选中焊缝调节）：",
                    ),
                    icon="INFO",
                )
                for c in weld_cols:
                    info_box.label(text=f"• {c.name}", icon="OUTLINER_COLLECTION")
            return

        # 中部：参数控制区（附带视口锁定小箭头开关，随时可切换）
        box_params = layout.box()
        header = box_params.row()
        header.label(
            text=bpy.app.translations.pgettext("Parameter Control") + f": {obj.name}",
            icon="PREFERENCES",
        )
        header.prop(
            obj,
            "hide_select",
            text="",
            icon="RESTRICT_SELECT_ON" if obj.hide_select else "RESTRICT_SELECT_OFF",
            emboss=False,
        )

        mod_inputs = getattr(getattr(mod, "properties", None), "inputs", None)
        for item in mod.node_group.interface.items_tree:
            if item.item_type == "SOCKET" and item.in_out == "INPUT":
                if item.socket_type == "NodeSocketGeometry":
                    continue
                ident = item.identifier
                label_text = bpy.app.translations.pgettext(item.name)
                inp = (
                    getattr(mod_inputs, ident, None) if mod_inputs is not None else None
                )
                if inp is not None and hasattr(inp, "value"):
                    box_params.prop(inp, "value", text=label_text)
                elif hasattr(item, "default_value"):
                    box_params.prop(item, "default_value", text=label_text)

        # 材质羽化区
        box_mat = layout.box()
        box_mat.label(text="Material Blending", icon="NODE_MATERIAL")
        row_fade = box_mat.row()
        row_fade.scale_y = 1.3
        row_fade.operator(WELD_OT_ApplyEdgeFade.bl_idname, icon="SHADING_RENDERED")

        # 底部：烘焙导出区
        box_export = layout.box()
        box_export.operator(WELD_OT_ConvertToMesh.bl_idname, icon="MESH_DATA")


classes = (
    WELD_OT_CreateWeld,
    WELD_OT_ApplyEdgeFade,
    WELD_OT_ConvertToMesh,
    WELD_PT_MainPanel,
)


def register():
    bpy.app.translations.register(__name__, TRANSLATIONS_DICT)
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.app.translations.unregister(__name__)


if __name__ == "__main__":
    register()
