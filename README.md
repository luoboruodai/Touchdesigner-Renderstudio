<div align="center">
  <h1>RenderStudio</h1>
  <p><strong>全新原创的 TouchDesigner 渲染组件，让画面、音轨和编码环境一起就绪。</strong></p>
  <p>原生 COMP 面板 · FFmpeg 自动下载配置 · 离线逐帧音频合成 · 11 种容器 / 39 项编码配置</p>
  <p>
    <a href="README_EN.md"><strong>English</strong></a> ·
    <a href="README.md"><strong>中文</strong></a> ·
    <a href="https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.4.0"><strong>下载 v1.4.0</strong></a> ·
    <a href="PROMOTION.md">宣发文案</a>
  </p>
  <p>
    <a href="https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.4.0"><img src="https://img.shields.io/badge/release-v1.4.0-7C6FF0?style=for-the-badge" alt="Release v1.4.0"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2E9E6B?style=for-the-badge" alt="MIT License"></a>
    <img src="https://img.shields.io/badge/TouchDesigner-2025.31550-222222?style=for-the-badge" alt="TouchDesigner 2025.31550">
    <img src="https://img.shields.io/badge/FFmpeg-9.0.2%20auto-orange?style=for-the-badge" alt="FFmpeg 9.0.2 automatic setup">
  </p>
</div>

<p align="center">
  <a href="preview/RenderStudio_1.4.png"><img src="preview/RenderStudio_1.4.png" alt="RenderStudio 1.4 的 TouchDesigner 原生面板" width="1000"></a>
  <br>
  <sub>RenderStudio 1.4 的真实 TD 原生面板；不是网页概念图或合成演示。</sub>
</p>

> [!IMPORTANT]
> 当前验证环境为 **macOS / TouchDesigner 2025.31550**。首次需要 FFmpeg 时，插件会自动下载并配置 **FFmpeg 9.0.2 + ffprobe**，无需用户手动安装，也不需要管理员权限。原创插件代码与独立 TOX 采用 **MIT License**；代码雨、历史素材及第三方项目不随之重新授权，详见[第三方声明](THIRD_PARTY_NOTICES.md)。

## 下载与安装

| 你的目标 | 应下载的附件 | 使用方式 |
|---|---|---|
| 在自己的 TD 工程中使用插件 | [`RenderStudio_1.4_TD2025.tox`](https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/download/v1.4.0/RenderStudio_1.4_TD2025.tox) | 拖入 TouchDesigner 工程 |
| 打开配套代码雨工程 | [`RenderStudio_1.4_TD2025_code-rain.toe`](https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/download/v1.4.0/RenderStudio_1.4_TD2025_code-rain.toe) | 用 TD 2025.31550 打开 |
| 核对发布文件 | [`SHA256SUMS`](https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/download/v1.4.0/SHA256SUMS) | 校验对应 Release 的成员与附件 |

GitHub 自动生成的 **Source code** 用于审查源码，不替代上述可安装附件。

### 环境准备

1. 安装 **TouchDesigner 2025.31550（macOS）**。
2. **无需手动安装 FFmpeg。** 首次检查设置或开始导出时，如果本机没有可用安装，插件会在后台自动下载、校验并配置；已有可用安装时直接复用。
3. 下载 TOX 或 TOE，先用短样本验证自己的工程。

### 开始导出

1. 将最终 TOP 接入插件端口，或在「源 TOP」中填写节点；同级节点可直接填 `out1`，留空则跟随端口。
2. 选择输出目录与文件名。默认 `./renders` 相对当前 TOE，重名自动编号，不覆盖旧文件。
3. 设置宽高、帧范围与 FPS，选择容器、编码器和速度档。
4. 如需音轨，在「音频 CHOP（可选）」中填入符合下述约定的 CHOP。
5. 点击「检查设置」，确认后开始渲染或录制。

## 1.4 新增：FFmpeg 自动配置

- **按需触发**：只有当前工作流确实需要 FFmpeg 且没有找到可用安装时才下载，不主动替换已有环境。
- **后台执行**：下载阶段显示进度并支持取消，完成后自动继续原检查／导出动作。
- **尊重手动路径**：高级页中有效的手动路径优先；无效路径会明确提示，留空才进入自动查找与配置。
- **固定供应链**：macOS arm64 / amd64 分别使用固定 ZIP、字节数与 SHA-256；同时校验苹果代码签名、系统动态依赖和项目所需的 31 项视频／音频编码器。
- **私有安装**：写入当前用户的 RenderStudio 目录，不修改系统 PATH，不要求 sudo，不把 FFmpeg 二进制塞进 TOX。
- **失败可恢复**：校验失败或取消会清理暂存，不创建输出文件、不改变时间线；第二次使用直接复用已验证安装。
- **许可随附**：受管目录保存 GPLv3 原文、版本信息、精确源码与构建脚本入口。FFmpeg 是独立可执行程序，许可与插件 MIT 分开说明。

## 保留的渲染能力

| 能力 | 当前实现 |
|---|---|
| 双模式导出 | 实时录制与帧范围渲染；摄像头、麦克风等实时输入仍走实时录制 |
| 离线逐帧音频合成 | 按帧范围与 FPS 累计整数样本边界取样，源不足时尾部补静音，成片阶段混入音轨 |
| 扩展格式库 | 11 种容器、39 项编码／档位／实现配置；39 项不等于 39 种独立编码标准 |
| 原生搜索与分页 | 容器与编码器分离，8 个条目控件复用，支持搜索、分页与本机能力重新检测 |
| 8-bit / EXR16 中间路径 | 普通输出可使用无损 MOV；高位深路径使用 EXR16，成片阶段仍可与音轨共存 |
| 可控的来源与尺寸 | 同步来源引用，接管相关输出尺寸；释放接管或删除组件时恢复已记录状态 |
| 相同起点适配 | 配套代码雨使用固定起点／种子与固定步长；第三方源可通过 Reset DAT 自行适配 |
| 取消与恢复 | 区分活动取消和已完成任务；保留取消／失败时的中间素材，成功时按约定清理 |

## 音频约定

| 工作模式 | 音频源要求 |
|---|---|
| 帧范围渲染 | 含完整数据的**非时间切片** CHOP，例如 Wave CHOP、Script CHOP 或缓存录制结果 |
| 实时录制 | 开启 **Time Slice** 的音频 CHOP |

本机实测中，Audio File In CHOP 在 TD 2025.31550 恒为时间切片，不能直接作为离线渲染音频源，请先转换。离线合成固定使用 16-bit PCM WAV 中间文件，不包含重采样、变速变调或多轨混音。

原生 MOV/ProRes 路径可直接复制视频流并混入 PCM；外部编码路径由 FFmpeg 合成。1.3 既有宿主测试中，原生 MOV/ProRes 的音频脉冲定位误差为 **0 个样本**。

## 格式与工作流

支持 MP4、MOV、MKV、WebM、AVI、MXF、MPEG/MPG、MPEG-TS、FLV、WMV/ASF、GIF，以及 H.264、HEVC、AV1、VP8/VP9、ProRes、DNxHR、CineForm、Hap、FFV1 等配置。

完整兼容关系、档位与精度说明见 **[格式目录](FORMAT_CATALOG.md)**。检测到编码器不代表所有硬件、素材和参数组合都已验证。

<p align="center">
  <a href="preview/编码器搜索.png"><img src="preview/编码器搜索.png" alt="RenderStudio 原生编码器搜索与分页" width="800"></a>
</p>

## 验证与边界

- **纯规则 31/31**：既有命名／范围／音频规则，以及下载清单、重复安装、失败清理、取消、ZIP 成员与协议白名单。
- **真实下载**：两种 macOS 架构包均核验 SHA-256、代码签名与依赖；实际 H.264+AAC 编码及 ffprobe 解码通过。
- **既有宿主证据**：1.3 离线音频相关 9/9；1.2 的 39 项编码配置解码样本在同源模块上复用。
- **1.4 新增验收**：自动配置、受管路径真实导出、第二次复用及最终 TOX/TOE 身份，详见[测试报告](TEST_REPORT.md)与结构化结果。

**未覆盖**：Windows、旧版 TD、长片压力、磁盘写满、所有分辨率／色彩／Alpha 交叉组合及完整广播交付规范。自动下载目前仅提供 macOS arm64 / amd64 包；其他架构和平台需另行验证。

## 文档入口

- **[English README](README_EN.md)**
- **[格式目录](FORMAT_CATALOG.md)**
- **[更新记录](CHANGELOG.md)**
- **[测试报告](TEST_REPORT.md)**
- **[MIT License](LICENSE)**
- **[第三方声明](THIRD_PARTY_NOTICES.md)**
- **[宣发文案 / Launch Kit](PROMOTION.md)**

## 原创与参考

RenderStudio 是全新原创的渲染组件，开发中参考了 **SkyFengStudio_MovieFileOut_2023X_RC** 的工作流，不是 SkyFeng 官方版本，也不表述为其续作。独立 1.4 TOX 不包含 `Legacy_2023_original`。

原创插件源码与独立 TOX 采用 **[MIT License](LICENSE)**，支持免费使用、修改和再分发，包括商业用途。代码雨整合工程、历史版本或艺术素材中的第三方内容仍遵循各自原许可，不纳入该 MIT 授权；原声明仅作为参考与历史记录保留。

如果 RenderStudio 对你的工作流有帮助，欢迎 Star 或分享给 TouchDesigner 创作者。反馈问题请附上 **TD build、操作系统、源类型、格式配置、短样本与可复现步骤**。
