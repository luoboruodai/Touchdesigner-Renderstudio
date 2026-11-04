# RenderStudio 宣发文案 / Launch Kit

用于分享 **RenderStudio 1.3** 的中英文公开文案。产品能力、验证范围和使用限制以仓库文档为准；分享时请保留下载链接与原作者使用边界。

- 仓库 / Repository：https://github.com/luoboruodai/Touchdesigner-Renderstudio
- 下载 / Download：https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.3.0
- 主图 / Hero image：[TouchDesigner 原生面板](preview/RenderStudio_1.3.png)
- 中文说明：[README](README.md) · English: [README_EN](README_EN.md)

## 中文

### 一句话介绍

**RenderStudio 是一个原生 TouchDesigner 渲染／导出组件，把帧范围渲染、离线逐帧音频合成和扩展格式库放进同一个 COMP 面板。**

### 推荐发布文案

最近把 TouchDesigner 里繁琐的导出与音轨对齐流程，整理成了原生组件 **RenderStudio 1.3**。

它支持：
- 实时录制与帧范围渲染；
- 离线逐帧音频合成，源不足时自动补静音；
- 11 种容器、39 项编码／档位／实现配置；
- 8-bit / EXR16 中间路径、编码搜索与分页；
- 活动取消、完成状态恢复与同名不覆盖。

配套代码雨工程已适配固定起点，原生 MOV/ProRes 实测中的音频脉冲定位误差为 0 个样本。当前验证环境是 macOS / TouchDesigner 2025.31550，宿主用例 9/9、纯规则 25/25；未覆盖范围和音频限制已在测试报告中列明。

插件与整合工程均可从 Release 下载。按原声明，仅限个人或非商业用途；这不是 SkyFeng 官方版本。

仓库：https://github.com/luoboruodai/Touchdesigner-Renderstudio
下载：https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.3.0

### 短版

**把 TD 画面和音轨一起交付。** RenderStudio 1.3：原生 COMP 面板、帧范围渲染、离线逐帧音频合成、11 容器 / 39 编码配置。macOS / TD 2025.31550 已实测，下载与验证边界见仓库。

https://github.com/luoboruodai/Touchdesigner-Renderstudio

### 推荐话题

`#TouchDesigner` `#CreativeCoding` `#RenderStudio` `#FFmpeg` `#MotionGraphics` `#代码雨`

## English

### One-liner

**RenderStudio is a native TouchDesigner export component that brings frame-range rendering, offline frame-based audio assembly and an extended codec catalog into one COMP panel.**

### Suggested launch post

I recently turned a repetitive TouchDesigner export and audio-alignment workflow into a native component: **RenderStudio 1.3**.

It includes:
- Real-time recording and frame-range rendering;
- Offline frame-based audio assembly with silence padding for short sources;
- 11 containers and 39 codec, quality-tier and implementation configurations;
- 8-bit / EXR16 intermediate paths, native codec search and pagination;
- Active cancellation, completion-state recovery and non-overwriting output names.

The companion code-rain project supports a fixed start and fixed-step progression. In the native MOV/ProRes host test, the decoded audio impulse landed at the expected sample with zero-sample offset.

Validation currently covers macOS / TouchDesigner 2025.31550: 9/9 host cases and 25/25 pure-rule checks. The test report lists the uncovered platforms, audio limitations and test boundaries.

The TOX component and integrated TOE are available from the Release. Under the original declaration, use is limited to personal or non-commercial purposes. This is not an official SkyFeng release.

Repository: https://github.com/luoboruodai/Touchdesigner-Renderstudio
Download: https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.3.0

### Short version

**Deliver TouchDesigner visuals and audio together.** RenderStudio 1.3 combines a native COMP panel, frame-range rendering, offline frame-based audio assembly, and 11 containers / 39 codec configurations. Tested on macOS / TD 2025.31550; downloads and validation boundaries are in the repository.

https://github.com/luoboruodai/Touchdesigner-Renderstudio

### Suggested tags

`#TouchDesigner` `#CreativeCoding` `#RenderStudio` `#FFmpeg` `#MotionGraphics` `#VFX`

## 分享时的必要说明 / Required context

- 使用真实原生面板截图，不将静态截图描述为交互录像。
- “9/9”“25/25”“零样本偏移”只对应文档中列明的测试，不扩展为所有环境均通过。
- 不使用“全平台”“全部格式组合”“商业许可”“官方 SkyFeng 版本”等未经证实表述。
- Release 附件才是安装入口；GitHub 自动 Source code 用于源码审查。
- 保留个人／非商业使用限制与原作者声明链接。
