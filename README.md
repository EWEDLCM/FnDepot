# FnDepot 外部应用源示例

本仓库是 FnDepot 外部应用源 V2 的单文件示例。用户在自己的 FnDepot 客户端中添加该仓库后，应用元数据、图标、预览图和安装包由客户端直接同步到本地；FnDepot 平台服务端不收集或记录这些外部源应用。

## 源入口

GitHub 仓库模式固定读取默认分支根目录的 `fnpack.json`：

```text
仓库根目录/
|-- fnpack.json
|-- app-name/
|   |-- ICON.PNG
|   |-- Preview/
|   `-- app-name.fpk
`-- ...
```

- 文件名大小写必须准确为 `fnpack.json`。
- 客户端优先通过 GitHub API 获取默认分支；API 不可用时依次尝试 `main`、`master`。
- 客户端不会探测或回退其他索引文件名。
- 直接添加 HTTP/HTTPS JSON URL 时，客户端读取用户填写的准确地址，文件名不受限制。
- V1 与 V2 都使用 `fnpack.json`，客户端根据 JSON 内容识别版本。

## 当前格式

本仓库采用 `schema_version: "2.0"`：

```json
{
  "schema_version": "2.0",
  "source_info": {
    "name": "示例应用源",
    "author": "示例作者",
    "homepage": "https://example.com"
  },
  "apps": {
    "sample-app": {
      "display_name": "示例应用",
      "desc": "一个示例应用",
      "platform": ["all"],
      "categories": ["系统工具"],
      "icon_url": "./sample-app/ICON.PNG",
      "run_as": "package",
      "install_type": "",
      "is_docker": false,
      "releases": {
        "1.0.0": {
          "changelog": "首次发布",
          "packages": {
            "all": {
              "download_url": "./sample-app/sample-app.fpk",
              "sha256": "64位十六进制SHA256",
              "size": 123456
            }
          }
        }
      }
    }
  }
}
```

`source_info` 只保存展示信息。源记录由用户实际添加的 URL 管理，GitHub Fork 血缘由 GitHub API 判断，不使用仓库内可随 Fork 复制的字段作为身份。

## 固定枚举

架构只允许：

```text
all, x86, arm
```

分类只允许：

```text
影音娱乐、系统工具、编程开发、AI赋能、生活服务、智能智控、教育学习、游戏地带、硬件驱动
```

`categories` 是字符串数组，至少填写一项，第一项作为主分类。FnDepot 不再使用自由标签。

安装与权限字段：

- `run_as`：`package` 或 `root`。
- `install_type`：空字符串表示默认存储空间，`root` 表示系统空间。
- `is_docker`：JSON 布尔值。
- `service_port`：可选的默认端口字符串，空字符串表示无。

## 版本与安装包

- `releases` 的键是应用版本号。
- 每个版本通过 `packages.all`、`packages.x86` 或 `packages.arm` 提供安装包。
- 当前架构有专用包时优先使用专用包，否则回退 `all`。
- `download_url` 可以是绝对 URL，也可以是相对于当前 JSON 文件的 URL。
- 强烈建议每个安装包同时填写准确的 `sha256` 和字节数 `size`。
- 已发布的“版本号 + 架构”安装包应保持不可变；内容变化时发布新版本、URL 和 SHA256。

计算文件信息：

```bash
sha256sum path/to/app.fpk
stat -c %s path/to/app.fpk
```

## 发布检查

1. `fnpack.json` 是不带注释和尾逗号的严格 JSON。
2. 应用键名与 FPK manifest 的 `appname` 一致。
3. 相对路径的大小写与仓库文件完全一致。
4. 当前设备架构存在专用包或 `all` 包。
5. 分类、架构、权限和安装位置使用固定枚举。
6. SHA256、字节数和实际 FPK 一致。
7. 图标、预览图及安装包可以从公开网络访问。

## V1 兼容

缺少 `schema_version` 且根节点为 `{appname: app_info}` 的文件会按历史 V1 格式解析。V1 仍兼容 `platform`、`arch_diff`、`labels`、字符串形式的 `isdocker`、旧作者字段和目录资源；新源应直接采用 V2。

## 责任边界

外部源由用户自主添加，其应用不代表 FnDepot 项目收录、推荐、审核或背书。源维护者和应用发布者应自行保证安装包的安全性、可用性、版权与许可合规性。
