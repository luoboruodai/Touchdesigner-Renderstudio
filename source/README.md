# 维护源码
这些模块已嵌入插件DAT；正常使用不依赖本目录。

- `catalog.py`：容器、编码/档位、兼容与参数规则。
- `encoding.py`：FFmpeg能力检测、8-bit/EXR16缓存、编码进度和进程收尾。
- `engine.py`：渲染状态机、取消竞态处理、时间线恢复及UI路由。
- `sources.py`：来源同步、轻量空闲路径、尺寸接管/恢复、合并更新。
- `determinism.py`：当前代码雨固定状态适配。
- `chooser.py`：8槽复用、搜索和分页。
- `export_core.py`：纯命名/范围/路径校验。
- `test_rules.py`：在本目录执行 `python3 test_rules.py`；不启动TD。

宿主模块需在TD DAT环境中运行。重载模块前先停止任务；删除导出器前释放接管。FFmpeg可执行文件不在本包内。
