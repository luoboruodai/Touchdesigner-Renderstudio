# 格式与编码配置目录 · 1.2

共 **11 种容器、39 项编码/配置**。包括硬件变体和专业档位，并非声称有39种独立编码标准。先选容器，菜单只列兼容配置；输入名称后按Enter筛选。

## 容器

| 容器 | 扩展名 | 默认外部音频编码 | 可选编码配置数 |
|---|---|---|---|
| MP4 · 通用 / 网络 | `.mp4` | aac | 8 |
| MOV · QuickTime / 后期 | `.mov` | pcm_s16le | 27 |
| MKV · 多编码 / 归档 | `.mkv` | flac | 27 |
| WebM · 网页视频 | `.webm` | libopus | 3 |
| AVI · 传统 / 无损 | `.avi` | pcm_s16le | 9 |
| MXF · 广播交换 | `.mxf` | pcm_s16le | 7 |
| MPEG · MPG 节目流 | `.mpg` | mp2 | 2 |
| MPEG-TS · 传输流 | `.ts` | aac | 7 |
| FLV · 兼容输出 | `.flv` | aac | 3 |
| WMV / ASF · Windows兼容 | `.wmv` | wmav2 | 1 |
| GIF · 动图 | `.gif` | 无音轨 | 1 |

## 编码/配置

| 配置 | 兼容容器 | 默认后端 | 精度参考 | Alpha能力 |
|---|---|---|---|---|
| H.264 / AVC | mp4, mov, mkv, ts, flv | FFmpeg | 8 bit | 不支持 |
| H.264 · VideoToolbox 硬件 | mp4, mov, mkv, ts, flv | FFmpeg | 8 bit | 不支持 |
| H.264 RGB · 4:4:4 | mp4, mov, mkv | FFmpeg | 8 bit | 不支持 |
| H.265 / HEVC | mp4, mov, mkv, ts | FFmpeg | 8 bit | 不支持 |
| H.265 · VideoToolbox 硬件 | mp4, mov, mkv, ts | FFmpeg | 8 bit | 不支持 |
| HEVC Main 10 · 10-bit | mp4, mov, mkv, ts | FFmpeg | 10 bit | 不支持 |
| AV1 · SVT-AV1 | mp4, mkv, webm | FFmpeg | 8 bit | 不支持 |
| VP8 · WebM | webm, mkv | FFmpeg | 8 bit | 不支持 |
| VP9 · WebM | webm, mkv | FFmpeg | 8 bit | 不支持 |
| MPEG-4 Part 2 | mp4, mov, avi, mkv | TD原生 | 8 bit | 不支持 |
| ProRes 422 Proxy | mov, mkv | TD原生 | 10 bit | 不支持 |
| ProRes 422 LT | mov, mkv | TD原生 | 10 bit | 不支持 |
| ProRes 422 | mov, mkv | TD原生 | 10 bit | 不支持 |
| ProRes 422 HQ | mov, mkv | TD原生 | 10 bit | 不支持 |
| ProRes 4444 · Alpha | mov, mkv | TD原生 | 12 bit | 默认启用 |
| ProRes 4444 XQ · Alpha | mov, mkv | TD原生 | 12 bit | 默认启用 |
| DNXHR LB | mov, mkv, mxf | FFmpeg | 8 bit | 不支持 |
| DNXHR SQ | mov, mkv, mxf | FFmpeg | 8 bit | 不支持 |
| DNXHR HQ | mov, mkv, mxf | FFmpeg | 8 bit | 不支持 |
| DNXHR HQX | mov, mkv, mxf | FFmpeg | 10 bit | 不支持 |
| DNXHR 444 | mov, mkv, mxf | FFmpeg | 10 bit | 不支持 |
| GoPro CineForm · 10/12-bit | mov, avi | TD原生 | 12 bit（后端相关） | 可选 |
| Animation / QuickTime RLE · 无损 | mov | TD原生 | 8 bit | 可选 |
| Hap · GPU 播放 | mov | TD原生 | 8 bit | 可选 |
| Hap Q · GPU 播放 | mov | TD原生 | 8 bit | 可选 |
| Motion JPEG / MJPEG | mov, avi, mkv | TD原生 | 8 bit | 不支持 |
| JPEG 2000 | mov, mkv | FFmpeg | 8 bit | 不支持 |
| FFV1 v3 · 无损归档 | mkv, avi | FFmpeg | 8 bit | 可选 |
| FFV1 · 16-bit 无损 | mkv | FFmpeg | 16 bit | 可选 |
| HuffYUV · 无损 | avi, mkv | FFmpeg | 8 bit | 可选 |
| Ut Video · 无损 | avi, mkv | FFmpeg | 8 bit | 可选 |
| Uncompressed 4:2:2 · 10-bit | mov, avi | FFmpeg | 10 bit | 不支持 |
| Uncompressed RGB / RGBA | mov, avi | FFmpeg | 8 bit | 可选 |
| MPEG-1 Video | mpg | FFmpeg | 8 bit | 不支持 |
| MPEG-2 Video | mpg, ts, mxf | FFmpeg | 8 bit | 不支持 |
| MPEG-2 4:2:2 · 50 Mb/s | mxf, mov, ts | FFmpeg | 8 bit | 不支持 |
| FLV / Sorenson Spark | flv | FFmpeg | 8 bit | 不支持 |
| Windows Media Video 8 | wmv, avi | FFmpeg | 8 bit | 不支持 |
| GIF · 调色板动图 | gif | TD原生 | 8 bit | 不支持 |

## 约束与选择

- H.264 / HEVC / VPx 等抽样格式需偶数宽高；DNxHR至少256×120。广播编码/MXF可能要求标准帧率和HD尺寸，预检会提示。
- VideoToolbox是本机macOS硬件路径，当前已实际编码验证；其他设备的硬件可用性仍取决于系统。
- 高位深外部配置自动使用EXR16半浮点中间序列，减少8-bit缓存截断；这不等于完整HDR/色彩管理认证，也不为8-bit源创造细节。
- EXR16高位深中间序列本身不内嵌音频；1.3起离线逐帧音频合成会在成片阶段混入音轨，两者可共存。实时录制的音轨仍走8-bit缓存路径。
- 短TS片段可能无法被自动探测；本轮3帧片段指定MPEG-TS后可解码，另有30帧正常自动探测测试。GIF时序受其时间单位限制，不适合精确任意FPS交付。
- Alpha保留的是源通道，不自动抠掉背景。原生/外部不同编码路径的全Alpha组合未穷举。
- 未包含所有Media Encoder专业封装、商业插件或授权编码器，也不伪造本机不存在的能力。
