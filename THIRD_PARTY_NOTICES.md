# Third-party notices / 第三方声明

## RenderStudio 的原创与参考边界

RenderStudio 1.4 是全新原创的 TouchDesigner 渲染组件，开发过程中参考了 **SkyFengStudio_MovieFileOut_2023X_RC** 的工作流。它不是 SkyFeng 官方版本，也不表述为原插件续作。

独立 `RenderStudio_1.4_TD2025.tox` 不包含旧版中的 `Legacy_2023_original` 组件。原创插件源码与独立 TOX 采用根目录 `LICENSE` 中的 **MIT License**，允许免费使用、修改和再分发，包括商业用途。

`原作者声明.txt` 仅用于记录参考来源及历史工程的原始条款。代码雨整合工程、历史版本或艺术素材中如含第三方内容，这些内容仍遵循各自原许可，**不纳入 RenderStudio 原创部分的 MIT 授权**。

## 自动下载的 FFmpeg / FFprobe

当本机没有可用 FFmpeg 且用户未手动指定路径时，插件会下载以下独立可执行程序：

- FFmpeg / ffprobe **9.0.2**
- 分发方：Martin Riedl's FFmpeg Build Server
- 构建页：https://ffmpeg.martin-riedl.de/
- 构建脚本：https://git.martin-riedl.de/ffmpeg/build-script
- 上游精确源码：https://ffmpeg.org/releases/ffmpeg-9.0.2.tar.xz
- 上游源码仓库标签：https://github.com/FFmpeg/FFmpeg/tree/n9.0.2

实际构建使用 `--enable-gpl` 与 `--enable-version3`，因此该 FFmpeg 构建按 **GNU General Public License v3** 提供。插件在受管安装目录保存 `share/COPYING.GPLv3`、`share/versions.txt` 和含固定 URL、字节数及 SHA-256 的 `NOTICE.txt`。

FFmpeg 是独立执行的命令行程序，不与 RenderStudio 链接，也不并入 MIT 授权。其许可、源码和构建信息均属于 FFmpeg 及相应第三方库作者。

### 固定的 macOS 包

| 架构 | 文件 | SHA-256 |
|---|---|---|
| arm64 | ffmpeg.zip | `c8ed4c4e6978a03c485edbfe4e0a5dc2380f8a30bba5150531b31b094492d924` |
| arm64 | ffprobe.zip | `fcbe839537485eaee7a7a8bc5cbc0f90d53617e80943e8a5b2e31cb851197ea6` |
| amd64 | ffmpeg.zip | `7c6b4125b191cbf773832dc51f424cf2b6bb7da43007d1e066f95909e47cacd4` |
| amd64 | ffprobe.zip | `2322438ed2f6319a691291b247d09c69dcaa3a982460d1f269a7e1af335cfdfd` |

完整 URL、文件大小、版本信息哈希和许可文件哈希见 `source/export_core.py` 的 `FFMPEG_MANIFEST`、`FFMPEG_LICENSE_URL` 与 `ffmpeg_resources()`。下载器拒绝非白名单地址、非 HTTPS、大小或哈希不符的文件，并校验苹果代码签名和非系统动态依赖。

当前自动配置仅覆盖 macOS arm64 与 amd64；其他平台使用系统 FFmpeg，是否可用需另行验证。
