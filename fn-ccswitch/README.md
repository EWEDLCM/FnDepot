# CC Switch for fnOS

把 [CC Switch](https://github.com/cp-yu/cc-switch-web) 的 Web 版打包成飞牛应用：在飞牛桌面窗口里直接管理
Claude Code / Codex / Gemini / OpenCode 的供应商配置，一键切换。

## 特点

- 桌面窗口内直接使用，通过飞牛**统一网关**接入（`/app/fn-ccswitch`），不额外对外开端口
- 内部服务只监听 `127.0.0.1`，访问控制交给 NAS 登录态
- 支持供应商切换、MCP 服务器、提示词、技能（Skills）、会话记录、配置导入导出
- 浅色 / 深色主题，中文 / English / 日本語 / 繁體中文
- 安装向导只需填一个内部端口（默认 `17666`），升级保留数据，卸载可选清空

## 使用

安装完成后，在飞牛桌面点应用图标即可打开，无需在浏览器里输入端口。

打开后的界面与上游 Web 版一致：

1. 点右上角 `+` 新增供应商（填名称、Base URL、API Key）；
2. 点卡片上的「启用」切换当前使用的供应商；
3. 顶部图标切换要管理的工具（Claude Code / Codex / Gemini / OpenCode 等）。

## 数据位置

| 内容 | 路径 |
| --- | --- |
| 数据库、设置 | `/vol1/@appdata/fn-ccswitch/data/` |
| HOME（`.claude`、`.codex` 等配置） | `/vol1/@apphome/fn-ccswitch/` |
| 运行日志 | `/vol1/@appdata/fn-ccswitch/log/` |

应用以包用户身份运行，管理的是**应用自己目录下**的配置，不会读写 NAS 用户的家目录。

## 已知限制

- 仅支持 x86_64（上游未提供 arm64 产物）
- 内部端口 `17666` 仅供本机使用，浏览器请一律通过 `/app/fn-ccswitch` 访问

## 来源与许可

- 上游：[cp-yu/cc-switch-web](https://github.com/cp-yu/cc-switch-web)（MIT）
- 打包与适配：[Maluslock/fn-ccswitch](https://github.com/Maluslock/fn-ccswitch)（MIT）
