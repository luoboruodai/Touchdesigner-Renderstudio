# RenderStudio 项目上下文（公开续工版）

更新：2026-11-05 · 当前产品：**RenderStudio 1.5.0**

这份文档从项目交接与已验证记录中提炼公开信息，供用户和 coding agent 续工。它不是私有项目目录或聊天记录的完整镜像；隐私与素材边界见 [公开交接与隐私边界](docs/PUBLIC_HANDOFF.md)。

## 1. 产品目标与当前契约

RenderStudio 是原创 TouchDesigner 渲染／导出 COMP 插件，用原生面板管理实时录制、帧范围渲染、音轨、格式、速度、精度和取消／恢复流程。

- 当前发布只提供独立 `RenderStudio_1.5_TD2025.tox` 和 `SHA256SUMS`，不附带代码雨整合 TOE。
- 原创插件源码与独立 TOX采用 [MIT](LICENSE)；代码雨、历史素材、第三方参考和单独下载的 FFmpeg 不随之重新授权。
- 默认输出 `./renders`，相对当前 TOE；同名自动编号，不覆盖旧文件。
- 插件优先使用有效手动 FFmpeg 路径，其次是系统安装，最后才在需要时下载受管副本。不修改系统 PATH，不要求管理员权限。
- 当前自动包平台：Windows x86_64、macOS arm64 / amd64。Windows ARM64 和其他操作系统没有自动包。
- [v1.5.0 Release](https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.5.0) 的 TOX SHA-256 为 `633c071c1738dad867bd0356a4de7010019af56a27db5e1a0cd402d3d58e845e`。

## 2. 目录与任务索引

| 路径 | 职责 |
|---|---|
| `source/catalog.py` | 容器、编码器／档位／实现变体与兼容规则 |
| `source/encoding.py` | 能力检测、平台编码器要求、后台配置、缓存、编码与进程收尾 |
| `source/engine.py` | 渲染状态机、配置续接、取消竞态、时间线恢复和 UI 路由 |
| `source/sources.py` | 来源同步、轻量空闲路径、尺寸接管与恢复 |
| `source/determinism.py` | 支持的源进行固定起点／种子与固定步长适配 |
| `source/chooser.py` | 8 槽复用、搜索、分页和本机能力入口 |
| `source/export_core.py` | 无 TD 依赖的路径／范围校验、固定包下载、平台身份验证、原子安装与清理 |
| `source/help.txt` | 嵌入 TOX 的帮助 DAT 文本 |
| `scripts/apply_source.py` | 将公开源码、版本和帮助写入展开后的 TOX；无私有路径和测试钩子 |
| `format_catalog.json` / `FORMAT_CATALOG.md` | 11 种容器、39 项编码／档位／实现配置及其说明 |
| `dev/*.json` | 已去路径化的宿主验收结果，不是可执行测试驱动 |
| `preview/` | 当前真实面板与编码器搜索截图 |
| `docs/DEVELOPMENT.md` | 构建、测试和修改入口 |
| `docs/TROUBLESHOOTING.md` | 已定位堵点、修复与证据边界 |
| `TEST_REPORT.md` / `TEST_SUMMARY.json` | 当前与历史验证证据 |

## 3. 运行与状态约定

1. 插件从输入端口或「源 TOP」取得最终画面；音频按工作模式校验完整缓存或 Time Slice。
2. 参数是界面与导出的单一状态来源。容器变化会同步重建兼容编码器菜单。
3. 渲染开始前保存时间线、来源和尺寸接管状态；成功、取消和错误都要走对应收尾与恢复。
4. 帧范围渲染使用独立时间参考推进，不能依赖已暂停的全局时间线继续触发普通帧回调。
5. 外部 FFmpeg 配置分阶段执行：主线程取得 TD 对象与编码器清单，后台线程只做纯 Python 下载／校验／安装，完成后回主线程续接检查或导出。
6. 活动任务不得被重复 `initialize()` 清空。编码完成后的取消不得误报活动取消；取消和失败保留约定的中间素材。
7. 离线音轨按累计整数样本边界合成，源不足按约定补静音。Audio File In 在当前实测 TD build 中恒为时间切片，离线使用前须转换。
8. TOX 内七个模块必须与 `source/` 对应字节一致。最终包不含 Legacy 节点、私有测试驱动或自动执行钩子。

## 4. FFmpeg 固定分发

| 平台 | 当前分发与检查 |
|---|---|
| Windows x86_64 | 固定 BtbN `ffmpeg-n9.0.2-47-gb204e94e90-win64-gpl-9.0.zip`；预期 195111884 字节及 SHA-256；只提取白名单 EXE，兼容 bin／根目录／发布子目录布局，检查 PE `0x8664`、版本、构建参数和 29 项必需编码器 |
| macOS arm64 / amd64 | 固定 Martin Riedl 9.0.2 ZIP、预期字节数及 SHA-256；检查苹果代码签名、系统动态依赖和 31 项必需编码器 |

两种构建都按实际 `--enable-gpl` 与 `--enable-version3` 保存 GPLv3、版本、上游源码和构建入口。FFmpeg 是独立可执行程序，不与插件链接，也不纳入插件 MIT 授权。

受管根目录由 `export_core.managed_root()` 决定，可用 `RENDERSTUDIO_FFMPEG_HOME` 隔离测试。不要根据平台名称猜测或静默迁移用户已有安装。

## 5. 已验证范围

- `source/test_rules.py`：38/38。
- GitHub Actions run [41993984310](https://github.com/luoboruodai/Touchdesigner-Renderstudio/actions/runs/41993984310)：Windows x86_64 和 macOS arm64 的真实下载、安装、版本／编码器检查、三帧 H.264+AAC 编码／解码与第二次复用均成功。
- macOS / TouchDesigner 2025.31550：独立 TOX 换父容器、改名、相对源引用、受管 FFmpeg 路径和真实三帧解码通过；`dev/host_tox_results.json` 为 `overall_pass=true`。
- 最终 TOX 模块与源码逐字节一致，无 Legacy、无测试钩子；公开附件已经无凭据下载核对。
- 旧证据：1.2 的格式与原生交互、1.3 的离线音频、1.4 的 macOS 自动配置保留在 `TEST_REPORT.md`，不把它们冒充当前新增平台的覆盖。

## 6. 未覆盖与下一步

1. 在物理 Windows / TouchDesigner 中验证完整 UI、检查设置与导出；当前 Windows 证据是 CI runner 的 FFmpeg 原生执行，不是 TD UI。
2. 用真实指针验证下载中的取消；目前只有规则、清理和恢复证据。
3. 按需扩展 Windows ARM64、其他操作系统、旧版 TD、原生 Intel Mac；没有实测前不写成支持。
4. 长片压力、磁盘写满、全部格式交叉组合、网络异常和完整广播规范仍待覆盖。
5. 首次无系统 FFmpeg 时需要联网；离线环境应预置有效手动路径、系统安装或已配置目录。

## 7. 版本脉络（不含私有材料）

| 版本 | 已交付能力 |
|---|---|
| 1.2 | 格式能力拆分、原生搜索／分页、编码取消竞态和状态恢复 |
| 1.3 | 离线逐帧音频合成、双模式音频校验、EXR16 与音轨共存 |
| 1.4 | 原创独立 TOX 的 MIT 边界、macOS FFmpeg 自动配置与宿主续接 |
| 1.5 | 当前仅插件发布、win64 自动配置、跨平台真实 smoke 与公开续工入口 |

历史代码雨、旧工程和原始设计参考不进入当前公开树。旧 Release 是历史交付记录，不应被删除或静默改写。
