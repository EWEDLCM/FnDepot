# FnDepot 外部应用源 V2 编写说明

> 外部源由用户自行添加，仅在用户本地客户端中生效。FnDepot 不对外部源的应用代码、安装包安全性或运行稳定性做审核、担保或背书。
本规范需等待客户端＞0.0.7方可使用

> 注意，由于飞牛已采用httponly，旧版客户端将无法继续使用，新版本已完成适配
## 1. 快速开始

一个最小可用的 V2 源只需要：

1. 在源文件根节点填写字符串 `"schema_version": "2"`。
2. 提供 `source_info.name`、`source_info.author`。
3. 在 `apps` 中为每个应用提供必填元数据和至少一个可用安装包。
4. 发布真实可访问的 `fnpack.json` 和 FPK 文件。

最小文件如下，实际发布文件必须是严格 JSON，不得包含注释或尾逗号：

```json
{
  "schema_version": "2",
  "source_info": {
    "name": "示例应用源",
    "author": "示例源作者"
  },
  "apps": {
    "sample.app": {
      "display_name": "示例应用",
      "desc": "一个示例应用。",
      "platform": ["all"],
      "categories": ["系统工具"],
      "icon_url": "https://example.com/assets/sample.png",
      "run_as": "package",
      "install_type": "",
      "is_docker": false,
      "releases": {
        "1.0.0": {
          "packages": {
            "all": {
              "download_url": "https://example.com/packages/sample.app-1.0.0.fpk"
            }
          }
        }
      }
    }
  }
}
```

## 2. 源地址与文件名

### 2.1 JSON 直链

用户可以添加任意文件名的 HTTP/HTTPS JSON 直链，例如：

```text
https://example.com/fnpack.json
https://cdn.example.com/releases/source-v2.json
```

直链模式不强制 URL 的文件名，但内容必须符合 V1 或 V2 结构。建议仍使用 `fnpack.json`，便于维护者和用户识别。

### 2.2 GitHub 仓库地址

用户也可以直接添加 GitHub 仓库根地址：

```text
https://github.com/example/FnDepot
```

GitHub 仓库模式有固定要求：

- 根目录必须存在名称完全匹配的 `fnpack.json`。
- 文件名大小写必须完全正确。
- 客户端优先使用仓库默认分支；GitHub API 暂不可用时兼容尝试 `main`、`master`。
- 客户端不会探测 `fndepot.json` 或其他索引文件名。
- 如果必须使用其他文件名或其他目录，应向用户提供该 JSON 文件的直链，而不是仓库根地址。

目录结构没有强制要求。客户端只按 `fnpack.json`（及可选 `details_url`）中的 JSON 内容解析，不扫描、不依赖任何固定目录布局；所有资源与 FPK 均由 JSON 内 URL 定位（绝对或相对）。因此可以直接沿用 V1 时代的目录习惯，也可以按个人喜好组织仓库，只要 JSON 中的相对 URL 与仓库实际布局一致即可。

以下两种布局都只是示例，选择其一或自行调整均可：

示例一：按应用分目录（FPK 与资源跟随应用集中存放）

```text
FnDepot/
|-- fnpack.json
|-- app1/
|   |-- fpk/
|   |   |-- app1-1.0.0-x86.fpk
|   |   `-- app1-1.0.0-arm.fpk
|   |-- icons/
|   `-- previews/
`-- app2/
    |-- fpk/
    |-- icons/
    `-- previews/
```

示例二：集中式（各应用 FPK 统一存放，便于批量检查与脚本处理）

```text
FnDepot/
|-- fnpack.json
|-- apps/
|   `-- sample.app.json
|-- assets/
|   |-- icons/
|   `-- previews/
`-- packages/
    |-- sample.app-1.0.0-x86.fpk
    `-- sample.app-1.0.0-arm.fpk
```

V1 和 V2 共用 `fnpack.json`。客户端根据 JSON 内容识别格式，而不是根据文件名识别格式。

## 3. V2 顶层结构

```text
{
  "schema_version": "2",
  "source_info": { ... },
  "apps": {
    "<appname>": { ... }
  }
}
```

### 3.1 `schema_version`

| 字段 | 类型 | 要求 |
| --- | --- | --- |
| `schema_version` | 字符串 | V2 源发布时必须填写精确值 `"2"`。 |

必须使用字符串，以下写法均不符合 V2 规范：

```text
{"schema_version": 2}
{"schema_version": "2.0"}
{"schema_version": "2.1"}
```

客户端只接受字符串 `"2"`，不会接受 `"2.1"`、`"2.2"` 或其他次版本写法。

### 3.2 `source_info`

| 字段 | 类型 | 要求 |
| --- | --- | --- |
| `name` | 字符串 | 必填，源在客户端中的显示名称。 |
| `author` | 字符串 | 必填，源作者或源维护者名称。 |
| `homepage` | URL 字符串 | 可选，源或作者主页。 |
| `description` | 字符串 | 可选，源的简介。 |
| `i18n` | 对象 | 可选，源名称和简介的多语言内容。 |

`source_info.author` 只表示“这个源由谁维护”，不会替代应用的开发者或发布者名称。

以来源身份由用户实际添加的 URL 管理。对于 GitHub 来源，客户端使用仓库 API 的真实仓库信息、Fork 血缘和应用内容重叠情况进行识别。

## 4. 应用字段

`apps` 是对象，键名必须与 FPK manifest 中的 `appname` 一致。应用名允许大小写混合，并且区分大小写；只能使用字母、数字、点、下划线和短横线，且必须以字母或数字开头。

### 4.1 常用字段

| 字段 | 类型 | 要求 |
| --- | --- | --- |
| `display_name` | 字符串 | 合并后必填，应用显示名称。 |
| `desc` | 字符串 | 合并后必填，应用简介。支持 HTML 文本；客户端会清理危险内容，简介中的图片不用于应用卡片。 |
| `platform` | 字符串或字符串数组 | 合并后必填，只允许 `all`、`x86`、`arm`。 |
| `categories` | 字符串数组 | 合并后必填，至少一个固定分类，可填写多个。 |
| `icon_url` | URL 字符串 | 合并后必填，应用图标。 |
| `preview_urls` | URL 字符串数组 | 可选，应用预览图，最多读取前 8 张。 |
| `readme_url` | URL 字符串 | 可选，外部来源详情页中的 README 分页入口。 |
| `bug_report_url` | URL 字符串 | 可选，详情页中“问题反馈”按钮的跳转地址。 |
| `details_url` | URL 字符串 | 可选，拆分模式的应用详情 JSON 地址。 |
| `details_updated_at` | 字符串 | 可选，只能放在应用节点，用于说明应用详情更新时间。 |
| `maintainer` | 字符串 | 可选，开发者或开发团队名称。 |
| `maintainer_url` | URL 字符串 | 可选，开发者网站或联系方式。 |
| `distributor` | 字符串 | 可选，发布者名称；与开发者不同才填写。 |
| `distributor_url` | URL 字符串 | 可选，发布者网站或联系方式。 |
| `run_as` | 字符串 | 合并后必填，只允许 `package` 或 `root`。 |
| `install_type` | 字符串 | 合并后必填；空字符串表示存储空间，`root` 表示系统空间。 |
| `is_docker` | 布尔值 | 合并后必填，是否为 Docker 应用。 |
| `service_port` | 字符串 | 可选，默认服务端口；无端口时填写空字符串。 |
| `releases` | 对象 | 单文件模式必填，版本集合。 |


### 4.2 固定分类

`categories` 只能使用以下值，不能自行创造分类名称：

```text
影音娱乐、系统工具、编程开发、AI赋能、生活服务、智能智控、教育学习、游戏地带、硬件驱动
```

可以同时填写多个分类【不超过两个】，例如：

```text
"categories": ["编程开发", "AI赋能"]
```

数组第一项作为主分类。客户端的“全部”是界面筛选项，不要把“全部”写入 `categories`。

### 4.3 开发者、发布者和源作者

三者职责不同：

- `source_info.author`：维护这个外部应用源的人或组织。
- `maintainer`：实际开发应用的个人、团队或组织。
- `distributor`：发布、打包或分发应用的人或组织；如果与 `maintainer` 相同，可以省略。

应用详情页会分别展示开发者和发布者。不要把 `source_info.author` 写入应用的 `maintainer`，除非两者确实是同一个主体。

## 5. 版本与安装包

### 5.1 版本结构

`releases` 的键是可比较的版本号，推荐使用 SemVer：

```text
1.0.0
1.2.3
2.0.0-beta.1
```

版本节点可以包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `changelog` | 字符串 | 版本更新说明。 |
| `updated_at` | 字符串 | 版本更新时间，建议 ISO 8601。 |
| `os_min_version` | 字符串 | 最低系统版本；为空或缺失表示不限制。 |
| `os_max_version` | 字符串 | 最高系统版本；为空或缺失表示不限制。 |
| `run_as` | 字符串 | 覆盖应用级值。 |
| `install_type` | 字符串 | 覆盖应用级值。 |
| `is_docker` | 布尔值 | 覆盖应用级值。 |
| `service_port` | 字符串 | 覆盖应用级值。 |
| `packages` | 对象 | 必填，按架构提供安装包。 |

客户端先按当前设备架构和系统版本过滤，再选择最高可用版本。版本号不能使用“latest”或日期文字替代。

### 5.2 `packages`

`packages` 的架构键只允许：

```text
all、x86、arm
```

每个安装包分支支持以下字段：

| 字段 | 类型 | 要求 |
| --- | --- | --- |
| `download_url` | URL 字符串 | 必填，FPK 下载地址。 |
| `sha256` | 字符串 | 强烈建议，64 位十六进制 SHA256；存在时客户端强制校验。 |
| `size` | 非负整数 | 建议填写，单位为 Bytes；不能写成 `"20 MB"`。 |
| `changelog` | 字符串 | 可覆盖版本级更新说明。 |
| `i18n` | 对象 | 可覆盖安装包级更新说明。 |
| `updated_at` | 字符串 | 可覆盖版本级更新时间。 |
| `os_min_version` | 字符串 | 可覆盖版本级最低系统版本。 |
| `os_max_version` | 字符串 | 可覆盖版本级最高系统版本。 |
| `run_as` | 字符串 | 可覆盖上层值。 |
| `install_type` | 字符串 | 可覆盖上层值。 |
| `is_docker` | 布尔值 | 可覆盖上层值。 |
| `service_port` | 字符串 | 可覆盖上层值。 |

最稳妥的写法是让每个包含 `download_url` 的分支同时填写自己的 `sha256` 和 `size`。

### 5.3 架构选择和 `all` 回退

应用级 `platform` 用于判断应用是否适用于当前设备，安装包级 `packages` 用于选择实际下载文件。

以 x86 设备为例，下载顺序为：

1. `packages.x86`。
2. `packages.x86` 缺失或信息无效时回退到 `packages.all`。
3. 两者都不可用时，该版本不可安装。

arm 设备同理。`all` 表示通用安装包或通用字段层。

如果应用声明 `platform: ["all"]`，推荐直接使用 `packages.all` 表示多架构合一包。V2 不应使用 `universal` 之类的自定义架构键：

```json
{
  "platform": ["all"],
  "releases": {
    "1.0.0": {
      "packages": {
        "all": {
          "download_url": "https://example.com/sample-1.0.0.fpk"
        }
      }
    }
  }
}
```

如果 V2 的 `platform` 声明包含 `all`，而 `packages` 只有一个合法分支，客户端也会将该分支作为通用包处理；为了避免歧义，仍建议把该分支命名为 `all`。`packages` 中除 `all`、`x86`、`arm` 外的架构键会使版本校验失败。

```text
"packages": {
  "all": {
    "download_url": "https://example.com/sample-1.0.0.fpk"
  }
}
```

安装包选择顺序为：

```text
packages.[当前架构] -> packages.all
```

也就是说，当前架构分支优先使用；只有当前架构分支缺失或校验失败时，才回退到 `packages.all`。

在已经选定安装包后，字段合并顺序为：

```text
应用级 -> 版本级 -> packages.all -> packages.[当前架构]
```

这里的 `packages.all` 是通用默认字段层，`packages.[当前架构]` 是最后的架构专用覆盖层；这不会改变安装包的选择顺序。`download_url` 必须存在于最终选中的分支中，不能从其他分支继承。若专用架构包和 `all` 包是不同文件，请分别填写对应的哈希和大小。

## 6. 国际化 `i18n`

`i18n` 可出现在 `source_info`、应用节点、版本节点和安装包分支中：

```json
{
  "source_info": {
    "name": "示例应用源",
    "author": "Example",
    "i18n": {
      "en-US": {
        "name": "Example Source",
        "description": "An example source."
      }
    }
  },
  "apps": {
    "sample.app": {
      "display_name": "示例应用",
      "desc": "示例简介",
      "i18n": {
        "en-US": {
          "display_name": "Sample App",
          "desc": "A sample application."
        }
      },
      "releases": {
        "1.0.0": {
          "changelog": "修复问题。",
          "i18n": {
            "en-US": {
              "changelog": "Bug fixes."
            }
          },
          "packages": {
            "all": {
              "download_url": "https://example.com/sample.fpk"
            }
          }
        }
      }
    }
  }
}
```

可本地化字段：

| 层级 | 可用键 |
| --- | --- |
| `source_info.i18n[locale]` | `name`、`description` |
| `apps.<appname>.i18n[locale]` | `display_name`、`desc` |
| `releases.<version>.i18n[locale]` | `changelog` |
| `packages.<arch>.i18n[locale]` | `changelog` |

回退顺序为：

1. 精确匹配运行时语言，例如 `zh-TW`。
2. 同语系候选语言，例如 `zh-CN`。
3. `en-US`。
4. `zh-CN`。
5. 对应层级的基础字段。

每个字段独立回退。基础字段仍然必须填写，不能只填写 `i18n`。

运行时语言以 FnOS 环境变量 `TRIM_SYS_LANGUAGE` 为准，不以浏览器 Cookie 的 `language`、HTTP `Accept-Language` 或页面手动参数为准。客户端保存完整翻译映射，并在输出时选择语言，因此切换系统语言后不必重新编写源文件。

## 7. 拆分详情文件

应用较多时，可以让根目录 `fnpack.json` 只保存索引，把每个应用放在详情 JSON 中。

主源：

```json
{
  "schema_version": "2",
  "source_info": {
    "name": "示例应用源",
    "author": "示例作者"
  },
  "apps": {
    "sample.app": {
      "details_url": "apps/sample.app.json",
      "details_updated_at": "2026-08-05T12:00:00+08:00"
    }
  }
}
```

详情文件：

```json
{
  "app_name": "sample.app",
  "display_name": "示例应用",
  "desc": "一个示例应用。",
  "platform": ["all"],
  "categories": ["系统工具"],
  "icon_url": "../assets/sample.png",
  "run_as": "package",
  "install_type": "",
  "is_docker": false,
  "releases": {
    "1.0.0": {
      "packages": {
        "all": {
          "download_url": "../packages/sample.app-1.0.0.fpk",
          "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
          "size": 26633830
        }
      }
    }
  }
}
```

拆分规则：

- `details_url` 非空时，客户端按拆分模式拉取详情。
- 详情文件的 `app_name` 必须与 `apps` 的键名完全一致。
- 详情字段覆盖主索引中同名字段；合并后再进行必填字段校验。
- 详情文件中的资源相对 URL 相对于详情文件所在目录解析。
- 详情请求失败、超时、格式错误或校验失败时，本次跳过该应用，并保留本地已有的有效缓存。
- `details_updated_at` 只在应用节点使用，不要放进 `source_info`，也不要使用它代替 HTTP 缓存头。

## 8. URL、缓存与资源要求

所有 URL 只能使用 `http` 或 `https`，支持绝对 URL 和相对 URL：

- 源级 URL、主源中的 `details_url` 和主源资源，相对主 JSON 所在地址解析。
- 详情 JSON 中的资源，相对详情 JSON 所在地址解析。
- 不允许 `file`、`ftp`、`data` 等协议，也不要在 URL 中放用户名、密码或长期令牌。

客户端会对主源和详情 JSON 做大小限制：

- 主源 JSON 最大约 2MB。
- 单个详情 JSON 最大约 512KB。
- 单个源最多 5000 个应用。
- 单个应用最多 100 个版本。
- 单个应用最多读取 8 张预览图。

源和详情请求会使用短时缓存、`ETag` 和 `Last-Modified` 条件请求。建议源服务器提供稳定 URL、`Content-Type: application/json; charset=utf-8`、`ETag` 或 `Last-Modified`。

建议：

- 图标优先 PNG/WebP，单张小于 500KB。
- 预览图单张尽量小于 2MB。
- README 尽量小于 1MB。
- FPK 提供准确的 `Content-Length`、`size` 和 `sha256`。
- FPK 服务支持 `Accept-Ranges: bytes`，方便客户端恢复下载。

外部源应用不统计或上报下载量、评分、评论和举报数据。

## 9. 校验失败和缓存行为

错误按四个粒度处理：

### 源级错误

JSON 语法错误、V2 顶层结构错误、`schema_version` 不支持、`source_info` 缺失、`apps` 类型错误等会使整个源同步失败。客户端不会用空结果覆盖已有源缓存。

### 应用级错误

单个应用的字段类型错误、分类非法、缺少必填元数据、详情 `app_name` 不匹配或没有可用版本时，只跳过该应用，不影响同源的其他应用。

### 版本和安装包级错误

没有有效 `packages`、URL 非法、哈希格式错误、大小类型错误或当前架构不可用时，只跳过对应版本或安装包分支。专用架构分支失败时，存在合法 `all` 分支则回退到 `all`。

### 缓存保留

单应用同步失败时，客户端保留该应用上一次有效缓存，避免一次网络波动导致整个外部源应用消失。只有源成功同步且应用键被明确从 `apps` 移除时，客户端才会清理对应未安装应用的旧缓存。

## 10. GitHub 来源、Fork 与重复源

`source_info.name`、`source_info.author` 和 `homepage` 不是唯一身份，名称相同或使用同一 CDN 不能证明两个源相同。

GitHub 源的血缘判断使用 GitHub 仓库 API 返回的真实信息，包括：

- 仓库 `full_name`。
- `fork` 状态。
- `parent.full_name`。
- `source.full_name`。

客户端结合仓库血缘和应用名、`appname|version` 重叠度识别高风险重复源，并可能停用后添加的重复 Fork。源作者不需要、也不应添加 `source_info.id` 试图规避或建立身份关系；该字段不参与客户端合并、去重或信任判断。

## 11. V1 兼容与迁移

新版客户端同时支持 V1 和 V2，但v1后续会取消兼容，请各位源作者尽可能完成迁移：

- V2：根节点包含 `schema_version`、`source_info`、`apps`。
- V1：没有 `schema_version`，根节点直接是应用名到应用信息的映射。
- 两种格式都使用 `fnpack.json`。
- JSON 直链可以使用任意文件名，但 GitHub 仓库固定读取根目录 `fnpack.json`。

V1 架构和安装包兼容规则必须保留：

1. 没有 `platform` 时，按历史规则默认目标为 x86。
2. 有架构标识的包优先匹配当前架构。
3. 未写架构的安装包视为全架构包，不要求文件名必须带 `_all`。
4. 旧源会按显式 `download_url`、架构命名包和通用命名包进行兼容回退；`{appname}.fpk` 也可以作为未标架构的通用包。

迁移到 V2 时建议：

1. 保持仓库文件名为 `fnpack.json`。
2. 增加 `schema_version` 和 `source_info`。
3. 将 `labels` 整理为固定 `categories`。
4. 将版本信息整理到 `releases.<version>.packages.<arch>`。
5. 为每个 FPK 填写真实 `download_url`、`size`、`sha256`。
6. 用应用 FPK manifest 的 `appname`、版本和平台逐项核对 JSON。
7. 在 x86 和 arm 设备上分别测试包选择和安装流程。

旧版客户端无法解析 V2，迁移前请确认目标用户使用的是支持 V2 的 FnDepot 客户端，版本为v0.0.7以上。

## 12. 发布前检查清单

### JSON 检查

- [ ] 文件是 UTF-8 严格 JSON，无注释、尾逗号和未转义字符。
- [ ] `schema_version` 是字符串 `"2"`。
- [ ] `source_info.name` 和 `source_info.author` 非空。
- [ ] 每个应用键名与 FPK 的 `appname` 完全一致并保留大小写。
- [ ] `categories` 只使用九个固定分类。
- [ ] `platform` 只使用 `all`、`x86`、`arm`。
- [ ] `run_as`、`install_type`、`is_docker` 的类型和值正确。
- [ ] 应用级 `details_updated_at` 使用字符串，源级没有该字段。
- [ ] `i18n` 中的字段名与所在层级匹配，基础字段仍然存在。

### 安装包检查

- [ ] 每个目标设备至少有 `all` 或对应架构包。
- [ ] `download_url` 实际可访问，且相对 URL 的基准目录正确。
- [ ] `size` 等于实际 FPK 文件字节数。
- [ ] `sha256sum` 与 JSON 中的 `sha256` 一致。
- [ ] FPK 内 manifest 的 `appname`、`version`、`platform` 与源文件一致。
- [ ] 下载中断后可以恢复，下载完成后 SHA256 校验通过。

常用检查命令（`packages/` 路径对应"示例二：集中式"布局，其他布局请按实际目录调整）：

```bash
jq empty fnpack.json
sha256sum packages/sample.app-1.0.0-x86.fpk
stat -c '%s' packages/sample.app-1.0.0-x86.fpk
```

### 发布后检查

- [ ] 使用 JSON 直链或 GitHub 仓库地址添加源。
- [ ] 检查源同步状态和被跳过应用的错误详情。
- [ ] 分别检查 x86、arm 的应用展示和安装包选择。
- [ ] 检查简介、图标、预览图、README、开发者和发布者显示。
- [ ] 在 `TRIM_SYS_LANGUAGE=zh-CN`、`en-US` 等环境下检查 i18n 回退。
- [ ] 发布新版本时使用新的版本号、下载地址、大小和 SHA256，不要静默替换同版本 FPK。

## 13. 发布新版本和移除应用

发布新版本时，在 `releases` 下增加新的可比较版本键，并更新对应的 `updated_at`、下载地址、`size` 和 `sha256`。已经发布的“版本号 + 架构”文件应视为不可变；文件内容变更时必须发布新版本或新地址。

主动移除版本时，从 `releases` 删除对应版本；主动移除应用时，从 `apps` 删除应用键。下一次成功同步后，客户端会按源的明确删除结果清理未安装应用的缓存。

不要通过故意返回空文件、格式错误或临时网络失败来移除应用，因为这些情况会触发缓存保留策略。

## 14. 版本记录

### V2

- 使用 `fnpack.json` 作为 GitHub 根目录索引文件。
- 支持单文件和 `details_url` 拆分模式。
- 支持多版本、多架构、`all` 回退、系统版本范围和安装包校验。
- 支持源、应用、版本和安装包级 i18n。
- `source_info.id` 不具有身份语义，不属于 V2 必需字段。
- 单应用同步失败保留旧缓存，源级失败不清空已有数据。
