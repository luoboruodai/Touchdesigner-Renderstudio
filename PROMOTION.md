# RenderStudio 宣发文案 / Launch Kit

用于分享 **RenderStudio 1.5** 的中英文公开文案。请保留下载链接、验证边界、原创许可范围与第三方声明。

- 仓库 / Repository：https://github.com/luoboruodai/Touchdesigner-Renderstudio
- 下载 / Download：https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.5.0
- 主图 / Hero image：[TouchDesigner 原生面板](preview/RenderStudio_1.5.png)
- 中文说明：[README](README.md) · English: [README_EN](README_EN.md)

## 中文

### 一句话介绍

**RenderStudio 是一个全新原创的独立 TouchDesigner 渲染插件：Windows / macOS 首次自动配置 FFmpeg、离线逐帧音频合成，以及 11 种容器 / 39 项编码配置。**

### 推荐发布文案

这次把 TouchDesigner 的导出工作流做成了全新原创组件：**RenderStudio 1.5**。

本版只提供独立插件，不再附带代码雨工程。Windows x86_64 和 macOS arm64 / amd64 都能在首次需要时自动下载并配置 **FFmpeg 9.0.2 + ffprobe**，固定版本与 SHA-256，无需手动安装，也不需要管理员权限。

主要能力：
- 实时录制、帧范围渲染与离线逐帧音频合成；
- 11 种容器、39 项编码／档位／实现配置；
- 原生编码搜索与分页、8-bit / EXR16 中间路径；
- 活动取消、完成状态恢复与同名不覆盖；
- Windows 固定 BtbN 包与 PE 架构检查，macOS 固定签名包与依赖检查；
- Windows / macOS runner 的真实安装、编码和解码验证。

原创插件源码与独立 TOX 采用 **MIT License**，可免费使用、修改和再分发，包括商业用途。工作流参考 SkyFengStudio_MovieFileOut_2023X_RC，但这不是 SkyFeng 官方版本或其续作；独立插件不含 Legacy 组件，历史素材不随插件重新授权。

仓库：https://github.com/luoboruodai/Touchdesigner-Renderstudio
下载：https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.5.0

### 短版

**Windows 也不用再手动装 FFmpeg。** RenderStudio 1.5：全新原创独立 TD 渲染插件，Windows / macOS 首次自动配置 FFmpeg 9.0.2 + ffprobe，支持离线逐帧音频合成、11 容器 / 39 编码配置。原创插件 MIT 开源。

https://github.com/luoboruodai/Touchdesigner-Renderstudio

### 推荐话题

`#TouchDesigner` `#CreativeCoding` `#RenderStudio` `#FFmpeg` `#MotionGraphics` `#OpenSource` `#Windows`

## English

### One-liner

**RenderStudio is a new, original standalone TouchDesigner export component with automatic FFmpeg setup on Windows and macOS, offline frame-based audio, and 11 containers / 39 codec configurations.**

### Suggested launch post

I built a new TouchDesigner export component from scratch: **RenderStudio 1.5**.

This release contains only the independent plugin—no code-rain project is bundled. On Windows x86_64 and macOS arm64 / amd64, it downloads and configures **FFmpeg 9.0.2 + ffprobe** when first needed, with pinned versions and SHA-256 hashes. No manual installation or administrator access is required.

Highlights:
- Real-time recording, frame-range rendering and offline frame-based audio assembly;
- 11 containers and 39 codec, quality-tier and implementation configurations;
- Native codec search and pagination, plus 8-bit / EXR16 intermediate paths;
- Active cancellation, completion-state recovery and non-overwriting output names;
- A pinned BtbN package and PE architecture check on Windows, and signed, dependency-checked packages on macOS;
- Real installation, encoding and decoding tests on Windows and macOS runners.

The original plugin source and independent TOX are **MIT licensed** for free use, modification and redistribution, including commercial use. The workflow references SkyFengStudio_MovieFileOut_2023X_RC, but this is not an official SkyFeng release or a continuation of that plugin; the independent component contains no Legacy node. Historical material is not relicensed.

Repository: https://github.com/luoboruodai/Touchdesigner-Renderstudio
Download: https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.5.0

### Short version

**No manual FFmpeg install on Windows either.** RenderStudio 1.5 is a new, original standalone TD export component that automatically downloads and configures FFmpeg 9.0.2 + ffprobe on Windows and macOS. It includes offline frame-based audio and 11 containers / 39 codec configurations. Original plugin code is MIT licensed.

https://github.com/luoboruodai/Touchdesigner-Renderstudio

### Suggested tags

`#TouchDesigner` `#CreativeCoding` `#RenderStudio` `#FFmpeg` `#MotionGraphics` `#OpenSource` `#Windows`

## 分享时的必要说明 / Required context

- 使用真实原生面板截图，不将静态截图描述为交互录像。
- MIT 仅覆盖原创插件源码与独立 TOX，不覆盖代码雨、历史素材、SkyFeng 或单独下载的 FFmpeg。
- Windows 支持指 Windows x86_64；Windows ARM64 和其他平台没有当前自动包，不写成全部平台已验证。
- 原生 UI、CI runner、实际解码和物理设备是不同证据层，不互相冒充。
- Release 附件才是安装入口；GitHub 自动 Source code 用于源码审查。
