# Procedural Welder

**One-Click Intersection Weld Bead Generator for Blender 4.2 – 5.3+**  
**适用于 Blender 4.2 – 5.3+ 的一键程序化焊缝生成器**

[English](#english) | [简体中文](#简体中文)

---

## English

**Procedural Welder** is a lightweight, non-destructive Geometry Nodes add-on for Blender that generates realistic weld beads along intersecting mesh seams in one click—complete with automatic shader edge feathering and game-ready static mesh baking.

### Key Features

- **One-Click Intersection Detection:** Automatically isolates selected intersecting meshes into dedicated source collections (`Weld_Source_XX`) and generates weld beads strictly along their intersection seams.
- **Non-Destructive Real-Time Controls:** Adjust weld scale, ripple density, exact/fast boolean solver mode, and edge feathering directly in the 3D Viewport N-Panel (`Welder` tab).
- **One-Click Shader Edge Feathering:** Assign any custom PBR material in the **Weld Material** slot and click **Apply Edge Fade** to automatically inject a non-destructive transparency feathering node group (`NG_Weld_Edge_Fade`) for seamless surface blending.
- **Game & Engine Ready Baking:** Click **Convert to Mesh** to bake the procedural modifier into a clean static mesh while preserving material slots and vertex attributes (`edge_blend`) for FBX/GLB export.
- **Native Bilingual UI:** Automatically adapts all labels, buttons, and tooltips between English and Simplified Chinese based on your Blender language settings.

### Installation

1. Go to the [Releases](https://github.com/ReplicaStudio/blender-procedural-welder/releases) page and download the latest `procedural_welder_v1.0.0.zip` (**do not unzip**).
2. Open Blender (`4.2 – 5.3+`) and navigate to **Edit > Preferences > Get Extensions** (or **Add-ons**).
3. Click the top-right dropdown arrow (`v`) and select **Install from Disk...**.
4. Select the downloaded `.zip` file to install and enable **Procedural Welder**.

### Quick Workflow

1. Select **two or more intersecting mesh objects** in the 3D Viewport.
2. Press `N` to open the sidebar, switch to the **Welder** tab, and click **Create Weld**.
3. Fine-tune **Weld Scale**, **Bead Density**, and **Blend Edge**. Optionally assign a custom material and click **Apply Edge Fade** for smooth transparency transitions in Cycles/EEVEE.
4. Click **Convert to Mesh** when ready to finalize or export to external game engines.

### License

Licensed under the **GNU General Public License v3.0 (GPL-3.0-or-later)**. See [LICENSE](LICENSE) for details.

---

## 简体中文

**Procedural Welder** 是一款基于 Blender 几何节点与现代 Extensions 扩展架构开发的轻量化效率插件。只需框选相互穿插的模型并点击一次按钮，即可沿交界线实时生成高细节程序化焊缝，并支持自定义材质边缘透明羽化融合与一键静态网格烘焙。

### 核心功能

- **一键相交识别与独立集合管理：** 自动将选中的相交母材归入独立源集合（`Weld_Source_XX`），沿模型交界线实时生成焊缝，多条焊缝之间互不串扰。
- **自定义材质 + 一键边缘羽化融合：** 在 **Weld Material** 槽位指定任意自定义金属/PBR材质后，点击 **「应用边缘羽化」** 即可自动向着色器节点树注入边缘透明过渡节点组，消除焊缝与母材之间的生硬穿插感。
- **高精度布尔切换：** 内置快速/高精度布尔求解器开关，轻松应对复杂结构与非流形拓扑模型。
- **一键烘焙静态网格：** 点击 **「转为静态网格」** 即可将程序化修改器烘焙为纯净静态网格，完整保留边缘羽化顶点属性（`edge_blend`）与材质槽。
- **原生中英双语界面：** 自动跟随 Blender 偏好设置切换全套界面按钮、参数滑块与悬停提示。

### 安装方法

1. 前往本仓库右侧 [Releases](https://github.com/ReplicaStudio/blender-procedural-welder/releases) 页面下载最新的 `procedural_welder_v1.0.0.zip`（**无需解压**）。
2. 打开 Blender（`4.2 – 5.3+`），进入 **编辑 (Edit) > 偏好设置 (Preferences) > 获取扩展 (Get Extensions)**。
3. 点击右上角下拉箭头（`v`），选择 **从磁盘安装 (Install from Disk...)**。
4. 选中下载的 `.zip` 压缩包并启用插件即可。

### 四步使用流程

1. 在 3D 视口中框选两个或多个**相互穿插（相交）**的网格物体。
2. 按 `N` 打开右侧边栏 **`Welder`** 标签页，点击 **「生成焊缝」**。
3. 实时调节焊缝缩放、焊鳞密度与边缘羽化范围；替换自定义材质后点击 **「应用边缘羽化」** 即可在渲染模式下获得自然熔接过渡。
4. 确认效果后点击 **「转为静态网格」** 完成烘焙导出。

### 开源协议

本项目基于 **GNU General Public License v3.0 (GPL-3.0-or-later)** 协议开源，详见 [LICENSE](LICENSE)。
