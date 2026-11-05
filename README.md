<div align="center">
  <h1>RenderStudio</h1>
  <p><strong>全新原创的 TouchDesigner 渲染组件，让画面、音轨和编码环境一起就绪。</strong></p>
  <p>独立 COMP 插件 · Windows / macOS FFmpeg 自动配置 · 离线逐帧音频合成</p>
  <p>
    <a href="README_EN.md"><strong>English</strong></a> ·
    <a href="README.md"><strong>中文</strong></a> ·
    <a href="https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.5.0"><strong>下载 v1.5.0</strong></a> ·
    <a href="PROMOTION.md">宣发文案</a>
  </p>
  <p>
    <a href="https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.5.0"><img src="https://img.shields.io/badge/release-v1.5.0-7C6FF0?style=for-the-badge" alt="Release v1.5.0"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2E9E6B?style=for-the-badge" alt="MIT License"></a>
    <img src="https://img.shields.io/badge/TouchDesigner-2025.31550-222222?style=for-the-badge" alt="TouchDesigner 2025.31550">
    <img src="https://img.shields.io/badge/FFmpeg-9.0.2%20auto-orange?style=for-the-badge" alt="FFmpeg 9.0.2 automatic setup">
  </p>
</div>

<p align="center">
  <a href="preview/RenderStudio_1.5.png"><img src="preview/RenderStudio_1.5.png" alt="RenderStudio 1.5 的 TouchDesigner 原生面板" width="1000"></a>
  <br>
  <sub>RenderStudio 1.5 的真实 TD 原生面板；不是网页概念图或合成演示。</sub>
</p>

> [!IMPORTANT]
> 本发布**只提供独立渲染插件**，不再附带代码雨整合工程。Windows x86_64 与 macOS arm64 / amd64 均可在首次需要时自动下载并配置 **FFmpeg 9.0.2 + ffprobe**，无需手动安装或管理员权限。原创插件代码与独立 TOX 采用 **MIT License**；历史素材及第三方项目不随之重新授权。

## 下载与安装

| 目标 | 附件 | 使用方式 |
|---|---|---|
| 在自己的 TD 工程中使用插件 | [`RenderStudio_1.5_TD2025.tox`](https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/download/v1.5.0/RenderStudio_1.5_TD2025.tox) | 拖入 TouchDesigner 工程 |
| 核对发布文件 | [`SHA256SUMS`](https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/download/v1.5.0/SHA256SUMS) | 校验对应 Release 的成员与附件 |

GitHub 自动生成的 **Source code** 用于审查源码，不替代上述可安装附件。**没有代码雨 TOE 下载项。**

### 环境准备

1. 安装 **TouchDesigner 2025.31550**。
2. **无需手动安装 FFmpeg。** 首次检查设置或开始导出时，如果没有可用安装，插件会在后台自动下载、校验并配置；已有安装直接复用。
3. 下载 TOX，先用短样本验证自己的工程。

### 开始导出

1. 将最终 TOP 接入插件端口，或在「源 TOP」中填写节点；同级节点可直接填 `out1`，留空则跟随端口。
2. 选择输出目录与文件名。默认 `./renders` 相对当前 TOE，重名自动编号，不覆盖旧文件。
3. 设置宽高、帧范围与 FPS，选择容器、编码器和速度档。
4. 如需音轨，在「音频 CHOP（可选）」中填入符合下述约定的 CHOP。
5. 点击「检查设置」，确认后开始渲染或录制。

## 1.5：Windows 也能自动配置 FFmpeg

| 平台 | 固定分发包与验证 |
|---|---|
| Windows x86_64 | BtbN `ffmpeg-n9.0.2-47-gb204e94e90-win64-gpl-9.0.zip`，固定字节数与 SHA-256，检查 PE x86_64，并在 Windows runner 上执行版本、编码器和真实编码／解码测试 |
| macOS arm64 / amd64 | Martin Riedl 9.0.2 ZIP，固定字节数与 SHA-256，检查苹果代码签名、系统动态依赖和真实编码／解码 |

- **按需触发**：只有当前工作流需要 FFmpeg 且没有找到可用安装时才下载。
- **后台执行**：显示进度并支持取消，完成后自动继续检查／导出。
- **尊重环境**：有效手动路径优先，系统安装其次，不修改系统 PATH，不要求 sudo。
- **固定供应链**：不可变 URL、预期字节数和 SHA-256；Windows 包只提取白名单中的 `bin/ffmpeg.exe` 与 `bin/ffprobe.exe`。
- **失败可恢复**：取消或校验失败会清理暂存，不创建输出文件、不改变时间线；第二次使用直接复用。
- **许可随附**：保存 GPLv3 原文、版本信息、精确上游源码与构建入口。FFmpeg 独立执行，不与插件链接，也不纳入插件的 MIT 授权。

Windows ARM64、其他操作系统及旧版 TD 不在当前自动包范围内，请手动指定系统 FFmpeg；不要把这些平台写成已验证支持。

## 保留的渲染能力

| 能力 | 当前实现 |
|---|---|
| 双模式导出 | 实时录制与帧范围渲染；摄像头、麦克风等实时输入仍走实时录制 |
| 离线逐帧音频合成 | 按帧范围与 FPS 累计整数样本边界取样，源不足时尾部补静音，成片阶段混入音轨 |
| 扩展格式库 | 11 种容器、39 项编码／档位／实现配置；39 项不等于 39 种独立编码标准 |
| 原生搜索与分页 | 容器与编码器分离，8 个条目控件复用，支持搜索、分页与本机能力重新检测 |
| 8-bit / EXR16 中间路径 | 普通输出可使用无损 MOV；高位深路径使用 EXR16，成片阶段仍可与音轨共存 |
| 来源与尺寸控制 | 同步来源引用，接管相关输出尺寸；释放接管或删除组件时恢复已记录状态 |
| 相同起点适配 | 支持的源可使用固定起点／种子与固定步长；第三方源可通过 Reset DAT 自行适配 |
| 取消与恢复 | 区分活动取消和已完成任务；保留取消／失败时的中间素材，成功时按约定清理 |

## 音频约定

| 工作模式 | 音频源要求 |
|---|---|
| 帧范围渲染 | 含完整数据的**非时间切片** CHOP，例如 Wave CHOP、Script CHOP 或缓存录制结果 |
| 实时录制 | 开启 **Time Slice** 的音频 CHOP |

本机实测中，Audio File In CHOP 在 TD 2025.31550 恒为时间切片，不能直接作为离线渲染音频源，请先转换。离线合成固定使用 16-bit PCM WAV 中间文件，不包含重采样、变速变调或多轨混音。

## 验证与 CI

- **纯规则 35/35**：既有渲染规则、win64 清单、bundle 解包、PE 架构、安装复用、取消与失败清理。
- **真实 macOS smoke**：下载、安装、版本与编码器验证、三帧 H.264+AAC 编码／解码、第二次复用全部通过。
- **独立 TOX**：换父容器、改名重导入、相对源引用和真实三帧解码通过。
- **Windows runner**：GitHub Actions 的 `bootstrap-smoke` 工作流执行真实下载、安装、版本／编码器验证和三帧编码／解码；精确提交与结果见仓库 **Actions**。
- **最终产物**：TOX 模块与源码逐字节一致，无 Legacy、无测试钩子。

详细证据见 **[测试报告](TEST_REPORT.md)** 与 **[结构化摘要](TEST_SUMMARY.json)**。Windows runner 通过不等同于每一种 Windows 物理机、GPU、旧版 TD 或所有格式组合均已验证。

## 文档入口

- **[English README](README_EN.md)**
- **[格式目录](FORMAT_CATALOG.md)**
- **[更新记录](CHANGELOG.md)**
- **[测试报告](TEST_REPORT.md)**
- **[MIT License](LICENSE)**
- **[第三方声明](THIRD_PARTY_NOTICES.md)**
- **[宣发文案 / Launch Kit](PROMOTION.md)**

## 原创与参考

RenderStudio 是全新原创的渲染组件，开发中参考了 **SkyFengStudio_MovieFileOut_2023X_RC** 的工作流，不是 SkyFeng 官方版本，也不表述为其续作。独立 TOX 不包含 `Legacy_2023_original`。

原创插件源码与独立 TOX 采用 **[MIT License](LICENSE)**，支持免费使用、修改和再分发，包括商业用途。代码雨、历史版本或艺术素材中的第三方内容仍遵循各自原许可，不纳入该 MIT 授权；原声明仅作为参考与历史记录保留。

如果 RenderStudio 对你的工作流有帮助，欢迎 Star 或分享给 TouchDesigner 创作者。反馈问题请附上 **TD build、操作系统、源类型、格式配置、短样本与可复现步骤**。
