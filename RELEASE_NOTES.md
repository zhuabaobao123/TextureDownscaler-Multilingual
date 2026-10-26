# TextureDownscaler - 多语言整合版（Multilingual Localization）

> 基于 TextureDownscaler v2.6.0（Nexus 187049，作者 RoseEden30）的本地化版本。
> 游戏内菜单（MCM）支持 8 种语言，**窗口标题、标签页、按钮、提示、帮助全文都本地化**，
> 安装 FOMOD 时单选一种。

---

## 语言列表 / Languages

| 代码 | 语言 | 菜单窗口标题 |
|------|------|--------------|
| en | English（默认，不装语言文件即英文） | TextureDownscaler |
| zh-CN | 简体中文 | 纹理降频器 |
| ja | 日本語 | テクスチャダウンスケーラ |
| ko | 한국어 | 텍스처 다운스케일러 |
| ru | Русский | Даунскейлер текстур |
| fr | Français | Réducteur de textures |
| de | Deutsch | Textur-Downscaler |
| es | Español | Reductor de texturas |

## 安装方式 / Install

1. 用 MO2（或支持 FOMOD 的任意管理器）安装本包。
2. 在安装向导的语言步骤里选择一种语言（单选）。
3. 安装后确保本模组已启用、排在你原 TextureDownscaler 的位置。

### 需求 / Requirements
- 原版 TextureDownscaler 2.6.0 的安装前提（SKSE、对应游戏版本 AE/SE 1.5.97）依旧适用。
- 中文/日文/韩文字形由 **SKSE Menu Framework（SMF 共享 ImGui 上下文）** 的主字体设置决定。本包不内置字体，如果游戏里显示为方框「□」，在 SMF 的字体设置里把 `PrimaryFont` 换成一个包含 CJK 字形的字体（并确认已启用「允许非拉丁字形」之类选项），无需我这个 DLL 做任何改动。

## 本地化机制 / How the localization works

- DLL 内保留英文原文，从不硬编码本地化文本；语言包全部外置为 JSON 对照词条。
- 语言文件位于 `SKSE\Plugins\TextureDownscaler.json`（与 DLL 同目录、同名替换扩展名）。DLL 启动时自动读取它；**删掉这个 .json 即恢复英文**，随时可还原。
- 翻译只覆盖界面显示文本（含窗口标题）；**配置键名（schema / 预设 / ini 键）保持英文**，与官方 ini 完全兼容。卸载本语言包不会影响你已调好的 `TextureDownscaler.ini`（本包不附带、不覆盖任何 ini/preset）。
- 帮助页里的 ini 语法示例（`\weapons\silver\ 2048`、`1. Normal …`、`2. Any … Full size`）故意不翻译，那是要照着输入 ini 的语法。

## 文件清单 / Files

```
SKSE\Plugins\TextureDownscaler.dll   （含本地化支持的插件）
SKSE\Plugins\TextureDownscaler.pdb   （崩溃日志符号，可选保留）
SKSE\Plugins\TextureDownscaler.json  （所选语言；删除即恢复英文）
```

## 发布物 / Package

- `E:\TextureDownscaler-src-2.6\TextureDownscaler-Multilingual-2.6.0.7z`（FOMOD，4.77 MB）
- `E:\TextureDownscaler-src-2.6\TextureDownscaler-Multilingual-2.6.0.zip`（同内容 ZIP 版，7.22 MB；Windows 资源管理器可直接打开）
- FOMOD 语言选项使用**逐文件显式声明**（`<file source=... destination=...>`），不依赖空 destination 的 folder 复制，避免部分安装器装出空文件夹。
- 上传前请把 `fomod\info.xml` 里的 Author 改成你自己的 N 网 ID。

## 许可 / License

- 本包基于 RoseEden30 的 TextureDownscaler，遵循 **GPL-3.0-or-later + Modding Exception** 授权，可自由再分发（标注来源、附源代码链接即可）。
- 源码（原版 + 本地化改造与生成工具）：
  - 原仓库：<https://github.com/RoseEden30/TextureDownscaler>
  - 本地化支持源码与本包生成脚本：<https://github.com/zhuabaobao123/TextureDownscaler-Multilingual>
- 翻译词条为社区贡献，欢迎到发布页面提交改进（尤其俄/法/德/西/韩/日，属社区初译）。

## 致谢 / Credits

- 本体：RoseEden30（TextureDownscaler）
- 本地化支持、中文词条与多语言打包：本人
- 各语言初译：社区贡献者