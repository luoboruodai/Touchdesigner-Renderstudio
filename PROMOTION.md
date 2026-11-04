# RenderStudio 宣发文案 / Launch Kit

用于分享 **RenderStudio 1.4** 的中英文公开文案。请保留下载链接、验证边界、原创许可范围与第三方声明。

- 仓库 / Repository：https://github.com/luoboruodai/Touchdesigner-Renderstudio
- 下载 / Download：https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.4.0
- 主图 / Hero image：[TouchDesigner 原生面板](preview/RenderStudio_1.4.png)
- 中文说明：[README](README.md) · English: [README_EN](README_EN.md)

## 中文

### 一句话介绍

**RenderStudio 是一个全新原创的 TouchDesigner 渲染组件：原生 COMP 面板、FFmpeg 首次自动下载配置、离线逐帧音频合成，以及 11 种容器 / 39 项编码配置。**

### 推荐发布文案

这次把 TouchDesigner 的导出工作流做成了一个全新原创组件：**RenderStudio 1.4**。

它不仅支持实时录制、帧范围渲染和离线逐帧音频合成，还解决了首次使用时的编码环境配置：当本机没有可用 FFmpeg 时，插件会在后台自动下载并配置 **FFmpeg 9.0.2 + ffprobe**，固定版本与 SHA-256，校验签名和依赖，无需手动安装，也不需要管理员权限。

主要能力：
- 11 种容器、39 项编码／档位／实现配置；
- 原生编码搜索与分页、8-bit / EXR16 中间路径；
- 非时间切片音频逐帧合成，短缺源尾部补静音；
- 活动取消、完成状态恢复与同名不覆盖；
- macOS arm64 / amd64 自动配置，已有 FFmpeg 直接复用。

原创插件源码与独立 TOX 采用 **MIT License**，可免费使用、修改和再分发，包括商业用途。开发中参考了 SkyFengStudio_MovieFileOut_2023X_RC 的工作流，但这不是 SkyFeng 官方版本或其续作；独立插件不含 Legacy 组件。代码雨及历史素材不随插件重新授权。

当前验证环境为 macOS / TouchDesigner 2025.31550。纯规则 31/31；真实下载、受管路径导出、二次复用及未覆盖范围见测试报告。

仓库：https://github.com/luoboruodai/Touchdesigner-Renderstudio
下载：https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.4.0

### 短版

**不用再手动装 FFmpeg。** RenderStudio 1.4：全新原创 TD 渲染组件，首次需要时自动下载配置 FFmpeg 9.0.2 + ffprobe，支持离线逐帧音频合成、11 容器 / 39 编码配置。原创插件 MIT 开源，欢迎试用与反馈。

https://github.com/luoboruodai/Touchdesigner-Renderstudio

### 推荐话题

`#TouchDesigner` `#CreativeCoding` `#RenderStudio` `#FFmpeg` `#MotionGraphics` `#OpenSource` `#代码雨`

## English

### One-liner

**RenderStudio is a new, original TouchDesigner export component with a native COMP panel, first-run FFmpeg setup, offline frame-based audio, and 11 containers / 39 codec configurations.**

### Suggested launch post

I built a new TouchDesigner export component from scratch: **RenderStudio 1.4**.

It supports real-time recording, frame-range rendering and offline frame-based audio assembly—and it also removes the first-run encoding setup burden. If no usable FFmpeg is found, the component downloads and configures **FFmpeg 9.0.2 + ffprobe** in the background with pinned versions and SHA-256 hashes, code-signature and dependency checks. No manual installation or administrator access is required.

Highlights:
- 11 containers and 39 codec, quality-tier and implementation configurations;
- Native codec search and pagination, plus 8-bit / EXR16 intermediate paths;
- Offline audio from non-time-sliced CHOPs, with silence padding for short sources;
- Active cancellation, completion-state recovery and non-overwriting output names;
- Automatic setup on macOS arm64 / amd64, with existing FFmpeg installations reused.

The original plugin source and independent TOX are **MIT licensed** for free use, modification and redistribution, including commercial use. The workflow references SkyFengStudio_MovieFileOut_2023X_RC, but this is not an official SkyFeng release or a continuation of that plugin; the independent component contains no Legacy node. Companion artwork and historical material are not relicensed.

Validation currently covers macOS / TouchDesigner 2025.31550. Pure-rule checks pass 31/31. Real downloads, managed-path export, second-run reuse and uncovered cases are documented in the test report.

Repository: https://github.com/luoboruodai/Touchdesigner-Renderstudio
Download: https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.4.0

### Short version

**No manual FFmpeg install.** RenderStudio 1.4 is a new, original TD export component that automatically downloads and configures FFmpeg 9.0.2 + ffprobe when first needed. It includes offline frame-based audio and 11 containers / 39 codec configurations. Original plugin code is MIT licensed.

https://github.com/luoboruodai/Touchdesigner-Renderstudio

### Suggested tags

`#TouchDesigner` `#CreativeCoding` `#RenderStudio` `#FFmpeg` `#MotionGraphics` `#OpenSource` `#VFX`

## 分享时的必要说明 / Required context

- 使用真实原生面板截图，不将静态截图描述为交互录像。
- “31/31”“真实下载”“自动配置”只对应文档中列明的环境与测试，不扩展为所有平台均通过。
- MIT 仅覆盖原创插件源码与独立 TOX，不覆盖代码雨、历史素材、SkyFeng 或单独下载的 FFmpeg。
- FFmpeg 9.0.2 的实际构建为 GPLv3；受管安装目录保存许可、源码与构建信息。
- 不声称 Windows、旧版 TD 或全部格式组合已验证。
- Release 附件才是安装入口；GitHub 自动 Source code 用于源码审查。
