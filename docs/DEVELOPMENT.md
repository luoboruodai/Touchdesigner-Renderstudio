# 公开开发与构建指南

本指南从公开仓库根目录开始。维护者若使用包含多个历史版本的工作区，应先阅读其私有 `PROJECT.md`，进入当前 1.5 活跃线；不要重建或上传整个历史目录。

## 1. 环境

- 当前宿主验证：TouchDesigner **2025.31550**。
- 纯规则、公开构建脚本和 CI smoke：Python **3.11**（GitHub Actions 当前配置）。
- 离线 TOX 编辑：TouchDesigner 安装目录自带的 `toeexpand` / `toecollapse`。
- FFmpeg 运行与 CI：首次无可用安装时需要联网。Windows smoke 的固定包约 195 MB，不要把真实下载当成无网络单元测试。

公开脚本不需要安装额外 pip 包，不调用 TouchDesigner API，不保存用户打开的工程，也不注入测试钩子。

## 2. 修改前定位

| 修改目标 | 主要入口 | 必看约束 |
|---|---|---|
| 容器、编码器、菜单兼容 | `source/catalog.py`、`source/chooser.py` | 39 项包含档位与实现变体，不等于 39 种标准 |
| FFmpeg 下载、架构、安装 | `source/export_core.py`、`source/encoding.py` | 平台编码器、固定包、TLS、PE／签名、原子安装 |
| 渲染、取消、恢复 | `source/engine.py`、`source/encoding.py` | 独立时间参考、活动任务、进程回收、实际解码 |
| 来源、尺寸接管 | `source/sources.py` | 保存／恢复真实所有权，不覆盖用户后续改动 |
| 离线音频 | `source/engine.py`、`source/encoding.py` | 完整缓存、累计整数样本边界、AAC 延迟与实际音轨 |
| UI 与参数 | 展开后的 `.parm` / `.cparm`、相关 DAT | 真实面板、回调时序、含空格文案引号、最终 TOX 重导入 |
| 帮助与版本 | `source/help.txt`、`source/export_core.py` | `VERSION` 为完整版本；帮助页标题使用显示版本 |

七个模块的规范来源是 `source/`。`scripts/apply_source.py` 还读取 `source/help.txt`，同步版本标签与帮助 DAT；其他 UI 几何和用户工程不被脚本重建。

## 3. 规则与真实 smoke

```bash
python3 source/test_rules.py
```

当前基线为 **38/38**。它覆盖渲染规则、win64 清单、解包布局、PE 架构、安装复用、取消和失败清理，不启动 TouchDesigner。

真实跨平台 smoke 入口：

```bash
python3 source/test_bootstrap_smoke.py
```

该脚本在临时目录设置 `RENDERSTUDIO_FFMPEG_HOME`，真实下载并安装固定 FFmpeg，执行版本／编码器检查，生成 320×180、30fps 三帧 H.264+AAC，使用 ffprobe 核对三帧、AAC 48kHz 双声道，再验证第二次复用。它会访问上游大文件；失败要按实际网络、哈希、布局、身份或执行错误处理，不能改成假通过。

`.github/workflows/bootstrap-smoke.yml` 在 `source/**` 或工作流变更时运行于 main push / PR，也可手动触发。矩阵为 Windows / macOS，权限仅为 `contents: read`。既有 run [41993984310](https://github.com/luoboruodai/Touchdesigner-Renderstudio/actions/runs/41993984310) 是历史证据，不是后续提交的自动通行证。

## 4. 可复现 TOX 构建

以下 macOS 命令已在当前发布 TOX 上实测。Windows 下可使用相同 Python 脚本和 TD 自带工具，但可执行文件位置与 shell 需按实际安装调整；当前未把 Windows 离线构建写成已验证。

```bash
# 在公开仓库根目录执行。
BUILD_DIR="$(mktemp -d)"
TD_BIN="/Applications/TouchDesigner.app/Contents/MacOS"
cp RenderStudio_1.5_TD2025.tox "$BUILD_DIR/RenderStudio.tox"
"$TD_BIN/toeexpand" "$BUILD_DIR/RenderStudio.tox"

# 展开结果为 RenderStudio.tox.dir，清单为 RenderStudio.tox.toc。
python3 scripts/apply_source.py "$BUILD_DIR/RenderStudio.tox.dir"

# 保留原始输入，再压回候选。
mv "$BUILD_DIR/RenderStudio.tox" "$BUILD_DIR/original.tox"
"$TD_BIN/toecollapse" "$BUILD_DIR/RenderStudio.tox.dir"
```

`toeexpand` 在已成功展开时也可能返回非零；不能仅凭退出码下结论，也不能因此忽略缺失文件。检查实际输出、`.toc` 和重新展开结果。

未修改运行输入时，候选应与原发布 TOX 完全一致：

```bash
shasum -a 256 "$BUILD_DIR/original.tox" "$BUILD_DIR/RenderStudio.tox"
cmp "$BUILD_DIR/original.tox" "$BUILD_DIR/RenderStudio.tox"
```

本次实测：连续两次 `apply_source.py` 后展开树 540 个文件的哈希不变；压回 TOX 为 46038 字节，SHA-256 与原发布文件同为 `633c071c1738dad867bd0356a4de7010019af56a27db5e1a0cd402d3d58e845e`。如果确实修改了源码、参数或 UI，则不要求与旧 TOX 相同，必须重新识别新产物并执行受影响验收。

### 版本升级时

1. 更新 `source/export_core.py` 的 `VERSION`、`source/help.txt` 的显示版本及相应功能说明。
2. 从当前公开 TOX 的独立副本展开，执行公开构建脚本；不要从私有代码雨 TOE 生成当前插件。
3. 若改变目标 TD 系列，先核对宿主兼容性，再调整脚本的 `TD_SERIES` 和全部文档，不能只换标签。
4. 重新展开候选，核对七个模块与 `source/`、帮助文本、参数、TOC 和必需根文件；确认无 Legacy、私有路径或测试钩子。
5. 换父容器并改名重导入最终 TOX，验证相对源引用、检查设置、受影响导出、实际解码、取消和状态恢复。
6. 更新双语文档、CHANGELOG、TEST_REPORT、TEST_SUMMARY、预览与 SHA256SUMS。新文件身份明确前不得覆盖旧有效交付物。
7. 只有用户明确授权时才推送或发布；只给验证通过的提交打新标签，不移动旧标签或静默替换旧附件。

## 5. 宿主验收最小集合

按改动面选择，不机械重跑全部历史矩阵：

- **模块／参数**：TD 实际加载、参数页完整、相关回调和原生面板；程序赋值不能冒充真实指针交互。
- **来源／尺寸**：换源、换父容器、改名、释放接管和删除组件后的状态恢复。
- **渲染／封装**：短样本实际解码帧数、首末帧、尺寸、FPS、Alpha／音轨，不能只看 manifest 或文件存在。
- **音频**：完整缓存与 Time Slice 的模式校验、非零起点、短缺补静音、分数 FPS／采样率，按需检查脉冲位置。
- **FFmpeg**：隔离受管目录的首次下载、身份验证、复用、失败／取消清理和受管路径实际导出。
- **取消**：分别覆盖进程确定活动与已经成功完成两种竞态，不通过延长等待冒充活动取消。

CI runner 的 FFmpeg 结果与物理机 TouchDesigner UI 是两层证据，缺失哪层就明确写哪层未覆盖。

## 6. 文档与隐私同步

行为、架构、构建或验证范围变化时，同步 `PROJECT_CONTEXT.md`、`docs/TROUBLESHOOTING.md`、两个 README 和 `CHANGELOG.md`。公开前先读 `docs/PUBLIC_HANDOFF.md`，只加入白名单文件，依次检查候选、Git 索引／历史与最终归档。

不要提交私有 `PROJECT.md`、会话、测试输出、真实用户素材、公司信息、密钥、凭据或本机绝对路径。忽略规则只是防误提交辅助，不代替内容审查。
