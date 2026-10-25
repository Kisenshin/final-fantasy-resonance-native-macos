# FINAL FANTASY RESONANCE Native macOS

[简体中文](README.md) | [English](README.en.md)

最终幻想：共鸣 — 基于 nxnative 的实验性 Apple Silicon macOS 适配

基于 [nxnative](https://github.com/seedds/nxnative) 的源码适配项目。用户自行提供游戏文件与从自己的主机导出的密钥，在本机生成 Mac 应用。仓库只提供适配源码、补丁、标识表和脚本，不提供游戏本体或可直接游玩的应用。

> **状态：本机适配已在 M1 Pro / macOS 26.5.1 上运行；此处新整理的构建入口尚未完成从零到应用的端到端验证，也没有其他机型的独立复现结果。** 现阶段适合愿意处理构建问题的测试者，不能承诺一键成功或全流程通关。

语言链接切换的是项目文档；当前启动器仍默认简体中文，本次未新增游戏内语言选择器。

## 当前支持范围

- 港版基础标题 ID：`0100B8A026F14000`；更新 ID：`0100B8A026F14800`。
- 游戏更新：**1.0.1**；`main` build ID：`b7f965b9d7227db8e29f04e84ea7331b`。其他版本和地区尚未验证，脚本会拒绝不匹配的模块。
- 简体中文、声音、窗口／全屏、键盘、Xbox 和 Switch Pro 的输入映射与设备提示。
- 原游戏「系统菜单 → 选项 → 画面设置 → 帧率」中的 **30／60 帧**切换；60 帧属于实验功能。
- 可选 DLC：测试过索引 `2` 的「見習騎士起步衝刺包」挂载；具体礼包领取流程未单独验证。
- 已验证标题、开场、起始场景、基本移动和存档读取；并非所有章节、战斗和功能均已测试。

## 已知限制

部分火焰／透明粒子仍存在黑色闪烁或显示异常。战斗特效首次出现可能卡顿，预热清单只覆盖已经记录的部分场景。不同系统、GPU、工具链上的结果可能不同。实体手柄仍需要更多测试；现有映射通过虚拟快照检查。

发布目录采用现场 GPU 采样实验之前保存的运行时源码，**不包含尚未验证的实时 GPU 采样改动**。没有用停画某个粒子材质的方式作为正式修复。

## 用 AI 协助构建

把本仓库链接交给具有本机终端和文件访问能力的 AI，可以减少查找流程和排错的工作。还需要用户自己的游戏文件、密钥路径、Mac 环境和足够的磁盘空间；这不是提供链接即可保证成功的一键转译服务。

[给 AI 的构建指南与可复制提示词](docs/AI_BUILD_GUIDE.md) · [键盘／Xbox／Switch Pro 与 30／60 帧详细操作](docs/CONTROLS_AND_FPS.md)

## 自备输入与依赖

1. 自己的港版本体 NSP、1.0.1 更新 NSP，以及自己的 `prod.keys` 路径；可选自有 DLC。
2. Apple Silicon Mac、原生 arm64 Python 3.12 或更高版本，以及 **macOS 26 或更新版本**。目前仅上述 M1 Pro 环境有运行记录。
3. Xcode 开发工具及其 Metal 工具链。`xcrun -sdk macosx --find metal` 和 `metallib` 必须成功；需要 `clang`、`make`、`codesign`、`sips` 和 `iconutil`。
4. .NET **10 SDK**、`spirv-cross`、`zstd`、Git，以及下列 Python 依赖。脚本不自动下载或寻找密钥。
5. 完整重建建议准备约 **100～120 GiB 空余空间**。这是根据现有构建产物估算的预算，尚未实测此入口的峰值；优先使用外置 APFS SSD。

解包和补丁都在私有构建目录中处理，不修改原始 NSP。该目录、密钥和运行时 checkout 都应放在此源码仓库之外。生成的 `.app` 包含用户自己的游戏内容，仅供其个人使用，不要作为本项目的 GitHub Release 上传。

## 构建步骤（实验入口，未做完整重建验证）

先创建 Python 环境并安装依赖。以下路径都是示例，请替换；不要直接把密钥值输入命令行。

```sh
git clone https://github.com/Kisenshin/final-fantasy-resonance-native-macos.git
cd final-fantasy-resonance-native-macos
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

准备固定版本的运行时。此操作联网拉取 nxnative 的指定提交并应用本仓库的源码补丁；不会读取游戏文件。

```sh
python scripts/prepare_runtime.py --destination ../ffr-runtime
```

先查看构建计划。默认模式不解密、不构建、不下载，也不启动游戏。

```sh
python scripts/build_mac.py
```

真正构建时显式加入 `--build`：

```sh
python scripts/build_mac.py \
  --runtime ../ffr-runtime \
  --base /path/to/owned-base.nsp \
  --update /path/to/owned-update-1.0.1.nsp \
  --keys /path/to/your-own/prod.keys \
  --work /Volumes/BuildSSD/FFR-private-build \
  --jobs 4 \
  --build
```

索引 2 的自有 DLC 可在同一命令中增加 `--dlc '2=/path/to/owned-dlc.nsp'`。其标题 ID 会与港版和索引核对。支持 `--compiler-bin /path/to/metal-tools` 指定本机编译器目录，仍须通过 `xcrun` 检查。

默认输出位于私有构建目录的 `最终幻想共鸣.app`。脚本只打包和本地 ad-hoc 签名，不自动安装、不启动游戏、不修改系统安全设置。签名验证不等同于 Apple 公证。输出已存在时会停止，使用新的 `--output /path/to/new-name.app` 保留旧构建。

## 中断和排错

- 构建日志位于私有工作目录的 `logs/`；私有输入记录不包含密钥内容。分享日志前仍需检查用户名、路径及个人信息。
- 上游辅助函数可复用已完成的解包、模块重写和匹配的 shader 缓存；**完整中断恢复流程尚未在这个入口验证**。更换输入、依赖或遇到不完整提取时，优先使用新的私有工作目录并保留错误日志。
- `Source/profile mismatch` 表示运行时或配置不再对应此发布快照，应在新目录重新执行 `prepare_runtime.py`。不要强制忽略 build ID 或资源校验。
- Metal 编译器、.NET 和图形 API 都由本机环境提供；缺少某一工具应按错误提示准备依赖，不要关闭 SIP 或 Gatekeeper 来替代排错。
- 本项目的帧率菜单补丁必须从用户提取的 IoStore 中读取两个资源并验证哈希。仓库不附带 `.uasset` 或修改后的容器。

## 操作、手柄与游戏内 30／60 帧

- **Xbox 按字母映射：A 确认、B 返回**；Switch Pro 保留原布局。完整键盘／手柄表、连接与提示说明见 [详细操作指南](docs/CONTROLS_AND_FPS.md)。
- 最近使用的输入设备决定窗口底部提示栏；**原游戏内部的 Switch 按键图案仍保留**，并非每处图标都会自动变成 Xbox 或键盘样式。F1 打开对照表，F2 隐藏／显示底部提示。
- 帧率入口：**系统菜单 → 选项 → 画面设置 → 帧率 → 30／60 → Y 套用 →「是」→ A 确认**。键盘套用按 **I**，确认按 **J／空格**；设置保存后可在重启时恢复。标题页 `Option` 也可进入。
- 60 帧是实验性目标，不代表所有场景持续达到 60；顶部 `Performance` 显示目标档位，切换统一在原游戏选项中完成。
- 全屏：**Control＋Command＋F** 或窗口绿色按钮。存档位于 `~/Library/Application Support/FFRNative/0100B8A026F14000/save`，构建工具不读取或打包已有存档。

## 发布内容与验证状态

- `patches/runtime.patch`：应用到固定上游提交的运行时源码修改。
- `profile/0100B8A026F14000/`：港版配置、版本门控、shader 标识／反射事实和 PSO 状态清单；不含 shader 程序。
- `scripts/`：本机准备、实验构建、FPS 资源补丁和打包脚本。
- `launcher/`：启动器源码及键位说明。
- `upstream.json`、`release-files.json`：上游版本、源码哈希及发布文件清单。
- `docs/VALIDATION.md`：轻量检查结果与明确未验证的项目。

这里只将现有适配整理为可供复现尝试的源码入口。**整理完成、静态检查通过，不代表从零构建已经成功。** 错误报告请附机器型号、macOS／Xcode／Python／.NET 版本、游戏 build ID 和去除个人信息后的日志，勿上传密钥、游戏模块或资源。

## 许可证

适配脚本按 MIT 发布；运行时补丁保留 nxnative 的 MIT 许可与署名，见 `LICENSE-nxnative`。第三方依赖见 `THIRD_PARTY_NOTICES.md` 和运行时原始许可。这里的许可不授予游戏本身的复制或分发权。
