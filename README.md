# FnDepot 应用源构建规范

版本: 1.1.1
更新日期: 2026-02-25
更新内容:
- 新增多架构（Multi-Arch）原生支持。
- 扩展 fndepot.json 字段支持按架构定义版本、大小、描述及下载地址。
- 优化 FPK 安装包命名规则，支持架构自动识别。
- 保持对旧版单架构配置的完全向下兼容。
1. 概述 (Overview)
FnDepot 是运行于 FNOS 上的去中心化第三方应用管理器。本文档定义了 FnDepot 应用源的构建规范、目录结构及元数据标准。开发者需严格遵循本规范，以确保应用源能被 FnDepot 客户端正确解析、索引。

2. 仓库规范 (Repository Standards)
为了保证解析效率与编写方便，项目在制作时尽可能采用了飞牛官方开发文档的键名，方便开发者识别和同步，应用源仓库必须满足以下硬性条件：

| 项目 | 要求 | 说明 |
| --- | --- | --- |
| 托管平台 | GitHub | 仅支持 GitHub 托管的仓库。 |
| 仓库可见性 | Public | 仓库必须设为公开，私有仓库无法被客户端索引。 |
| 仓库命名 | FnDepot | [强制] 仓库名称必须严格命名为 FnDepot。 |
| 分支策略 | main | 客户端默认拉取默认分支的内容。 |

3. 目录结构 (Directory Structure)
FnDepot 采用扁平化的目录结构。仓库根目录必须包含全局索引文件 fndepot.json，每个应用拥有独立的子目录。
```
FnDepot/                      # [Root] 仓库根目录
│
├── fndepot.json              # [Core] 全局元数据索引文件
│
├── {app_name}/               # [Dir] 应用目录 (需与 fndepot.json 中的app_name一致)
│   ├── ICON.PNG              # [Asset] 应用图标 (强制全大写)
│   ├── {app_name}_{arch}.fpk  # [Bin] 多架构安装包 (推荐: 如 fntermx_arm.fpk)
│   ├── {app_name}.fpk        # [Bin] 兼容模式安装包 (文件名须与目录名一致)
│   ├── README.md             # [Doc] 应用详情文档 (Markdown)
│   └── Preview/              # [Asset] 预览图目录
│       ├── 01.png
│       └── 02.jpg
│
└── ... (其他应用目录)
```
3.1 命名约定
- 应用唯一标识 (app_name)：
  - 仅允许使用小写字母 (a-z)、数字 (0-9) 和 连字符 (-)。
- 应用目录名称必须与 fndepot.json 中的键名（Key）完全一致。
- 大小写敏感：Linux 文件系统对大小写敏感，请严格遵守文件名规范。

4. 元数据规范 (fndepot.json)
fndepot.json 是应用源的核心数据库，位于仓库根目录。它是一个标准的 JSON 对象，其键（Key）为应用的 app_name。

4.1 数据结构
```
{
  "app_name": {
    "display_name": "String",
    "platform": "String | Array",
    "version": "String",
    "desc": "String",
    "labels": "String",
    "author": "String",
    "author_url": "String",
    "bug_report_url": "String",
    "isdocker": "String",
    "install_type": "Enum",
    "size": "String",
    "download_url": "String",
    "changelog": "String",
    "arch_diff": "Object"
  }
}
```
4.2 字段定义表

| 字段 | 类型 | 必填 | 描述与约束 |
| --- | --- | :---: | --- |
| Key | String | ✅ | 应用唯一标识。必须与应用文件夹名称完全一致。 |
| display_name | String | ✅ | 客户端展示的应用名称（页面显示用）。 |
| platform | String / Array | - | 应用所属平台架构。<br>- String: "all" 或 "x86"等<br>- Array: ["all", "x86", "arm"]<br>- 缺少该platform字段时: 视为旧版写法默认识别为"x86"。 |
| version | String | ✅ | 当前版本号（通用版本）。 |
| desc | String | ✅ | 应用简介。支持 \n 换行。 |
| labels | String | ✅ | 分类标签。多个标签使用半角逗号 , 分隔。 |
| download_url | String | - | 下载地址（通用地址）。留空或缺失时自动从目录拼接路径获取。 |
| distributor | String | ✅ | 应用发布者名称。优先使用此字段，向下兼容 author 字段。 |
| distributor_url | String | ✅ | 发布者网站或仓库链接 (HTTP/HTTPS)。优先使用此字段，向下兼容 author_url 字段。 |
| author | String | - | (已废弃) 应用作者名称。建议使用 distributor 字段。 |
| author_url | String | - | (已废弃) 作者网站。建议使用 distributor_url 字段。 |
| bug_report_url | String | ✅ | 问题反馈链接/允许第三方链接。 |
| install_type | String | ✅ | 安装目标路径类型。"系统空间" 或 "存储空间"。 |
| isdocker | String | - | true或false，不填或缺失默认false。 |
| size | String | ✅ | 安装包大小，允许携带单位，不携带默认为 MB。 |
| changelog | String | ✅ | 本次版本更新内容（通用更新内容）。 |
| arch_diff | Object | - | 架构差异配置。用于覆盖通用字段或直接定义架构特定字段。<br>- 结构: {"x86": {...}, "arm": {...}, "all": {...}}<br>- 支持的字段: version, desc, size, download_url, changelog<br>- 优先级: arch_diff[arch] > 通用字段<br>- 注意：当存在 arch_diff 时，允许上层通用字段缺少对应字段，可直接在 arch_diff 中定义 |

4.3 项目运行逻辑与匹配规则
新版本以platform字段为主导，当该字段被定义时，客户端处理逻辑如下：
1. 检测客户端所在系统架构；
2. 在同步源时进行判定，筛选 "platform": "all" 以及与系统架构对应的应用信息进行录入，不满足条件的应用不会录入也不会被显示在客户端中；
3. 在满足以上前置条件的前提下，字段解析逻辑如下：
   - 首先检查 arch_diff 中是否存在当前架构的配置
   - 如果存在，则优先使用 arch_diff[arch] 中定义的字段值
   - 对于 arch_diff[arch] 中未定义的字段，使用通用字段的值
   - 如果 arch_diff 中不存在当前架构的配置，则全部使用通用字段的值
4. download_url为空时，回退为采用目录拼接路径获取；
5. 若仍未找到，视该应用信息不全或不适用于客户端所在系统，不进行录入。
注：当platform没有被定义或缺失时，视该应用信息没有被更新，按旧版本规则作为x86应用进行匹配。

5. 资源文件规范 (Assets Specification)
5.1 图标 (ICON.PNG)
- 路径: /{app_name}/ICON.PNG
- 格式: PNG
- 尺寸: 建议 256x256 
- 注意: 文件名必须为 ICON.PNG（全大写），否则客户端无法获取。
  
5.2 安装包 (.fpk)
- 路径与优先级: 
  1. 系统优先查找架构专用包: /{app_name}/{app_name}_{arch}.fpk (如 fntermx_arm.fpk)
  2. 若未找到，查找通用包: /{app_name}/{app_name}_all.fpk
  3. 若仍未找到且platform没有被定义或缺失，回退查找: /{app_name}/{app_name}.fpk (旧版结构)
- 外部下载: 若 download_url 已填写，则忽略仓库内对应应用的文件。
- 注意: 文件名必须严格匹配上述规则。

5.3 预览图 (Preview/)
- 路径: /{app_name}/Preview/
- 支持格式: .png, .jpg, .jpeg, .webp 等。
6. 完整配置示例 (Configuration Example)

```json
{
  "example1": {
    "display_name": "示例一",
    "platform": ["x86", "arm"],
    "version": "1.0.0",
    "desc": "这是一个示例",
    "distributor": "EWEDL",
    "distributor_url": "https://github.com/EWEDLCM",
    "bug_report_url": "https://github.com/EWEDLCM/FnDepot/issues",
    "labels": "工具,效率",
    "size": "15",
    "download_url": "https://example.com/example1.fpk",
    "install_type": "系统空间",
    "changelog": "全架构适配"
  },
  // 解析结果：
  // - x86架构：version: 1.0.0, size: 15, desc: 这是一个示例, download_url: https://example.com/example1.fpk
  // - arm架构：version: 1.0.0, size: 15, desc: 这是一个示例, download_url: https://example.com/example1.fpk

  "example2": {
    "display_name": "示例二",
    "platform": "all",
    "version": "1.0.0",
    "desc": "这是一个示例",
    "distributor": "EWEDL",
    "distributor_url": "https://github.com/EWEDLCM",
    "bug_report_url": "https://github.com/EWEDLCM/FnDepot/issues",
    "labels": "工具,效率",
    "size": "15",
    "download_url": "https://example.com/example2.fpk",
    "install_type": "系统空间",
    "changelog": "全架构适配"
  },
  // 解析结果：
  // - 所有架构：version: 1.0.0, size: 15, desc: 这是一个示例, download_url: https://example.com/example2.fpk

  "example3": {
    "display_name": "示例三",
    "platform": ["x86", "arm"],
    "version": "1.0.0",
    "desc": "这是一个示例",
    "distributor": "EWEDL",
    "distributor_url": "https://github.com/EWEDLCM",
    "bug_report_url": "https://github.com/EWEDLCM/FnDepot/issues",
    "labels": "工具,效率",
    "size": "20",
    "download_url": "",
    "install_type": "系统空间",
    "changelog": "通用更新内容",
    "arch_diff": {
      "arm": {
        "version": "1.0.1",
        "size": "25",
        "desc": "ARM架构优化版本",
        "download_url": "https://example.com/example3_arm.fpk"
      }
    }
  },
  // 解析结果：
  // - x86架构：version: 1.0.0, size: 20, desc: 这是一个示例, download_url: 目录查找对应的 example3_x86.fpk 或 example3_all.fpk 文件, changelog: 通用更新内容
  // - arm架构：version: 1.0.1, size: 25, desc: ARM架构优化版本, download_url: https://example.com/example3_arm.fpk, changelog: 通用更新内容

  "example4": {
    "display_name": "示例四",
    "platform": ["x86", "arm"],
    "version": "1.0.0",
    "desc": "通用描述",
    "distributor": "EWEDL",
    "distributor_url": "https://github.com/EWEDLCM",
    "bug_report_url": "https://github.com/EWEDLCM/FnDepot/issues",
    "labels": "工具,效率",
    "size": "20",
    "install_type": "系统空间",
    "changelog": "通用更新内容",
    "arch_diff": {
      "x86": {
        "download_url": "https://example.com/example4_x86.fpk",
        "size": "25"
      },
      "arm": {
        "version": "1.0.1",
        "size": "30",
        "desc": "ARM架构优化版本",
        "download_url": "https://example.com/example4_arm.fpk",
        "changelog": "ARM架构适配"
      }
    }
  },
  // 解析结果：
  // - x86架构：version: 1.0.0, size: 25, desc: 通用描述, download_url: https://example.com/example4_x86.fpk, changelog: 通用更新内容
  // - arm架构：version: 1.0.1, size: 30, desc: ARM架构优化版本, download_url: https://example.com/example4_arm.fpk, changelog: ARM架构适配

  "example5": {
    "display_name": "示例五",
    "version": "1.0.0",
    "desc": "旧版单架构配置，无 platform 字段默认为 x86",
    "size": "10",
    "changelog": "x86 适配"
  }
  // 解析结果：
  // - x86架构：version: 1.0.0, size: 10, desc: 旧版单架构配置，无 platform 字段默认为 x86, download_url: 目录查找 example5.fpk 文件, changelog: x86 适配
}
```

**示例说明：**

- **示例一**：多架构通用，x86和arm架构使用相同的配置
- **示例二**：全架构通用，platform为"all"，所有架构使用相同的配置
- **示例三**：部分字段有差异，ARM架构有独立的版本、大小、描述和下载地址
- **示例四**：多个字段都有差异，x86和ARM架构都有独立的配置
- **示例五**：兼容模式，旧版写法，无platform字段默认为x86

7. FnDepot 的维护与更新 (Maintenance)
FnDepot 客户端包含自动同步机制。开发者只需对 GitHub 仓库进行常规的 Git 操作即可完成发布：
1. 更新安装包文件：替换对应的 .fpk 文件。
2. 更新元数据：修改 fndepot.json 中的相关字段内容。
3. 推送 (Push)：将更改推送到 GitHub 的默认分支。
客户端会在同步源信息时检测到 version 字段变更，正确响应状态。

8. 法律与免责声明 (Disclaimer)
- 责任限制：FnDepot 仅提供索引服务并调用系统安装命令。不提供收集和分发功能，应用开发者需对其提交的代码安全性、稳定性及版权合规性负全部责任。
- 安全合规：严禁在应用源中包含恶意代码、后门程序或未经授权的侵权内容。违规仓库将被 FnDepot 索引服务拉黑并在项目中公示。
- 数据安全：开发者应在文档中明确告知用户应用的权限要求及潜在风险。

---
FnDepot Protocol Version 1.1.1
