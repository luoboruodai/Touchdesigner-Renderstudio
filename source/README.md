# 维护源码
这些模块已嵌入插件DAT；正常使用不依赖本目录。

- `catalog.py`：容器、编码/档位、兼容与参数规则。
- `encoding.py`：FFmpeg能力检测、受管路径选择、后台配置线程、8-bit/EXR16缓存、编码进度和进程收尾。线程启动前在主线程取得TD模块与编码器清单。
- `engine.py`：渲染状态机、FFmpeg自动配置阶段、取消竞态处理、时间线恢复及UI路由；活动任务不被重复初始化打断。
- `sources.py`：来源同步、轻量空闲路径、尺寸接管/恢复、合并更新。
- `determinism.py`：当前代码雨固定状态适配。
- `chooser.py`：8槽复用、搜索和分页。
- `export_core.py`：纯命名/范围/路径校验，以及无TD依赖的FFmpeg固定清单、TLS/CA、哈希校验、macOS签名与依赖验证、Windows PE架构验证、原子安装和取消清理。当前支持macOS arm64/amd64与Windows x86_64。
- `test_rules.py`：在本目录执行 `python3 test_rules.py`；不启动TD，当前37项。
- `test_bootstrap_smoke.py`：真实下载、安装、版本/编码器验证、三帧H.264+AAC编码与ffprobe解码、第二次复用；由 `.github/workflows/bootstrap-smoke.yml` 在Windows与macOS runner分别执行。

宿主模块需在TD DAT环境中运行。重载模块前先停止任务；删除导出器前释放接管。FFmpeg可执行文件不在本包内；首次需要且没有可用安装时按固定清单下载到当前用户的RenderStudio目录，许可与构建信息随附。
