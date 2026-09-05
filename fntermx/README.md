# FntermX - 飞牛NAS终端模拟器

[![Version](https://img.shields.io/badge/version-1.1.9-blue.svg)](manifest)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-飞牛OS-orange.svg)](https://www.fnnas.com/)
[![Arch](https://img.shields.io/badge/arch-x86__64-lightgrey.svg)](manifest)

**FntermX** 是专为飞牛NAS平台打造的现代化Web终端应用，基于Vue3+FastAPI架构开发，提供强大的本地终端和远程SSH功能，在Web界面中呈现完整的命令行体验。

## 📝 近期更新（v1.1.9）

- 适配 fnOS 新版 HttpOnly 会话认证和官方网关 Header 管理策略。
- 修复本地终端打开后提示“认证失败”、无法建立 WebSocket 的问题。
- 修复 SSH 连接配置读取或保存时提示“网络错误”的问题。
- FntermX JWT 改用应用专用认证 Header，避免与官方网关的 `Authorization` 校验冲突。
- 保持 JWT 验签、过期校验、网关用户 UID 绑定和一次性 WebSocket 票据等安全措施。
- 改进非 JSON 网关错误响应处理，提供更准确的认证错误提示。

完整说明参见 [RELEASE_NOTES.md](RELEASE_NOTES.md)。

## ✨ 核心特性

### 🖥️ 双重终端支持
- **本地终端**：基于Tmux的本地Shell访问，支持完整的终端功能和会话持久化
- **远程终端**：基于 tmux+ssh 实现的远程连接，支持会话持久化和断线恢复
- **多会话管理**：同时管理多个终端会话，支持标签页切换和会话重命名
- **会话持久化**：本地和远程均基于Tmux实现，断网重连后终端状态完整保留，运行中的程序不受影响

### 🎨 主题与界面
- **12款护眼主题**：内置One Dark Pro、Dracula、Nord、Gruvbox、Solarized、Monokai、GitHub Dark、Atom Dark、Material Dark、Night Owl、Palenight、Cobalt2
- **背景透明度**：支持0-100%透明度调节，打造个性化视觉效果
- **响应式设计**：完美适配桌面和移动设备，支持悬浮侧边栏
- **流畅动画**：精心设计的过渡效果和微交互
- **暗色优化**：专为终端环境优化的深色界面

### 🔧 高级功能
- **实时同步**：基于WebSocket的实时终端I/O，低延迟响应
- **连接管理**：保存和管理多个SSH连接配置，支持一键连接
- **断网恢复**：Tmux会话持久化，断开重连后终端状态完整恢复
- **快捷指令**：内置常用命令快捷方式，自动添加 sudo 权限支持
- **安全认证**：完善的密码认证机制，强制首页认证，防止直接访问
- **配置持久化**：主题设置和连接配置自动保存到后端
- **自包含部署**：内置所有依赖库，无需系统额外安装

## 📋 应用信息

- **应用名称**：FntermX 终端
- **版本**：1.1.9（新版网关认证兼容版）
- **架构**：x86_64
- **服务端口**：5122
- **最低系统版本**：飞牛OS 0.9.26+
- **安装类型**：root权限安装
- **技术栈**：Vue 3 + FastAPI + xterm.js + Tmux
- **维护者**：EWEDL

## 🏗️ 项目结构

```
fntermx/
├── app/                         # 运行时应用文件
│   ├── server/                 # FastAPI后端服务
│   │   ├── main.py            # 主服务器应用
│   │   ├── theme_manager.py   # 主题管理模块
│   │   ├── tmux_manager.py    # Tmux本地终端管理
│   │   ├── tmux_remote_manager.py  # Tmux远程终端管理
│   │   ├── bin/               # 内置二进制文件（tmux、sshpass等）
│   │   └── lib/               # 内置共享库（libutempter.so.0等）
│   └── ui/                    # 构建的前端资源
├── frontend/                  # Vue 3前端源码
│   ├── src/
│   │   ├── components/       # Vue组件
│   │   │   ├── AuthModal.vue           # 认证弹窗
│   │   │   ├── PasswordChangeModal.vue # 密码修改弹窗
│   │   │   ├── SettingsModal.vue       # 首页设置弹窗
│   │   │   └── TerminalWorkspace.vue   # 终端工作区（主组件）
│   │   └── App.vue           # 主应用组件
│   ├── index.html           # 主页模板
│   ├── terminal.html        # 终端工作区模板
│   ├── package.json         # NPM依赖配置
│   └── vite.config.js       # Vite构建配置
├── cmd/                     # 应用生命周期管理脚本
│   └── main                # 启动/停止脚本
├── config/                  # 应用配置文件
│   ├── privilege           # 用户权限配置
│   └── resource           # 系统资源配置
├── wizard/                  # 安装向导配置
├── manifest                 # 应用元数据
├── ICON.png                # 应用图标（小）
├── ICON_256.png            # 应用图标（大）
└── README.md               # 项目说明文档
```

## 🚀 安装和使用

### 系统要求
- 飞牛OS 0.9.26 或更高版本
- x86_64 架构
- root 权限

### 安装步骤

1. **下载应用包**
```bash
# 获取fntermx.fpk文件
```

2. **通过飞牛应用中心安装**
```bash
# 方法1：使用appcenter-cli
appcenter-cli install fntermx.fpk

# 方法2：通过Web界面上传到应用中心
```

3. **启动应用**
```bash
# 命令行启动
appcenter-cli start fntermx

# 或通过应用中心界面启动
```

4. **访问应用**
- 打开浏览器，访问：`http://your-nas-ip:5122`
- 或通过飞牛OS应用中心访问

## 📱 功能使用

### 本地终端
1. 打开FntermX应用
2. 点击"本地终端"按钮
3. 即可访问本地Shell环境
4. 支持多标签页管理

### 远程终端
1. 点击"远程终端"按钮
2. 配置SSH连接信息（主机、端口、用户名、密码）
3. 保存连接配置
4. 建立连接并开始远程操作

### 会话管理
- 支持多个终端标签页同时运行
- 可重命名会话标签
- 支持会话的关闭和重新连接
- 配置信息自动保存

## ⚙️ 配置说明

### 环境变量
- `TRIM_APPDEST`：应用安装目录
- `TRIM_PKGVAR`：应用数据目录
- `TRIM_SERVICE_PORT`：服务端口（默认5122）
- `TRIM_USERNAME`：应用用户名

### 数据存储位置
- **应用日志**：`/usr/local/apps/@appdata/fntermx/fntermx.log`
- **系统日志**：`/var/log/apps/fntermx.log`
- **远程连接配置**：`{TRIM_PKGVAR}/fntermx_remote_configs.json`
- **主题配置**：`{TRIM_PKGVAR}/fntermx_theme_settings.json`
- **认证信息**：`{TRIM_PKGVAR}/fntermx_auth.json`
- **会话数据**：`{TRIM_PKGVAR}/fntermx_sessions.json`

### WebSocket端点
- `/ws/terminal`：本地Tmux终端WebSocket连接
- `/ws/remote-terminal`：远程SSH终端WebSocket连接

### API端点
**会话管理**
- `GET /api/sessions`：列出所有活跃的Tmux会话
- `DELETE /api/sessions/{session_id}`：删除指定的Tmux会话

**远程连接**
- `GET /api/remote-configs`：列出保存的远程SSH连接
- `POST /api/remote-configs`：创建新的远程连接配置
- `DELETE /api/remote-configs/{id}`：删除远程连接配置
- `POST /api/remote-configs/test`：测试远程连接可用性

**主题管理**
- `GET /api/theme/load`：加载用户主题配置
- `POST /api/theme/save`：保存用户主题配置
- `DELETE /api/theme/reset`：重置为默认主题

**认证管理**
- `POST /api/auth/verify`：验证访问密码
- `POST /api/auth/check`：检查认证状态
- `POST /api/auth/change-password`：修改访问密码

## 🛠️ 开发指南

### 本地开发环境
1. **克隆项目**
```bash
git clone <repository-url>
cd fntermx
```

2. **安装前端依赖**
```bash
cd frontend
npm install
```

3. **开发模式运行**
```bash
# 前端开发服务器
cd frontend
npm run dev

# 后端开发服务器
cd app/server
python main.py
```

4. **构建生产版本**
```bash
cd frontend
npm run build  # 生产环境会自动移除所有 console 日志
```

**注意事项**
- 生产构建会使用 Terser 自动移除所有 `console.*` 调试语句
- 开发时可以随意使用 `console.log` 等调试方法
- 构建后需要硬刷新浏览器（Ctrl+Shift+R）清除缓存

### 应用打包
```bash
# 创建应用包
appcenter-cli pack

# 本地安装测试
appcenter-cli install-local
```

## 🔍 故障排除

### 常见问题

**Q: 应用启动失败**
A: 检查系统版本是否满足要求，确认端口5122未被占用

**Q: WebSocket连接失败**
A: 检查防火墙设置，确保端口5122可访问

**Q: SSH连接超时**
A: 验证服务器地址、端口和认证信息是否正确

**Q: 本地终端无响应**
A: 检查系统权限和Shell路径配置

**Q: 提示 libutempter.so.0 缺失**
A: 应用已内置此库，确保使用完整的安装包，或检查 `app/server/lib/` 目录

**Q: 用户 home 目录不存在警告**
A: 应用会自动检测并切换到 `/vol1` 目录，无需手动处理

**Q: 直接访问终端页面被重定向**
A: 这是安全设计，所有终端页面访问都需要先通过首页认证

**Q: 浏览器缓存导致更新不生效**
A: 使用硬刷新（Ctrl+Shift+R）或清空缓存后重新访问

### 调试命令
```bash
# 检查应用状态
appcenter-cli status fntermx

# 查看应用日志
tail -f /usr/local/apps/@appdata/fntermx/fntermx.log

# 查看系统日志
tail -f /var/log/apps/fntermx.log

# 检查端口占用
netstat -tlnp | grep 5122

# 重启应用
appcenter-cli restart fntermx
```

### 重要文件
- `manifest`：应用元数据和配置
- `cmd/main`：应用启动/停止脚本
- `config/privilege`：用户权限配置
- `config/resource`：系统资源限制

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 代码规范
- 前端使用 Vue 3 + Vite + TypeScript
- 后端使用 FastAPI + Python
- 遵循飞牛OS应用开发规范
- 提交信息使用中文，格式清晰

## 📝 更新日志

### v1.0.4 (2025-10-22) - 远程终端架构重构

**重大更新**
- 🚀 **远程终端持久化**：远程SSH连接现在也支持会话持久化和断线恢复
- 🔧 **架构重构**：将远程终端从 Paramiko 迁移到 `tmux+ssh` 方案，统一本地和远程架构
- ✨ **代码复用**：通过继承 `TmuxTerminalManager` 实现，大幅简化远程终端代码
- 📦 **自包含部署**：内置 `sshpass` 工具，无需系统安装额外依赖

额外更新：
- 将通过cdn调用的css改为本地调用
- 重构终端界面TerminalWorkspace.vue中设置弹窗的各平台效果
- 更新终端界面新建会话时的下拉框样式
- 终端内容支持搜索、复制
- 新增终端界面主题系统，支持自定义背景图，支持自动取色，支持自定义界面、按钮、终端文本选中高亮颜色。
**功能改进**
- ✅ 远程终端断开后会话继续运行，重新连接后状态完整恢复
- ✅ 支持在远程服务器运行长时间任务（如编译、下载）而不受浏览器关闭影响
- ✅ 自动 SSH keepalive 配置（60秒间隔），防止连接超时断开
- ✅ 保留完整的 SSH 欢迎信息和 ANSI 颜色格式

**技术改进**
- 🔧 创建独立的 `tmux_remote_manager.py` 模块，架构更清晰
- 🔧 移除 Paramiko 依赖，减少依赖复杂度和维护成本
- 🔧 内置 `sshpass` 二进制文件到 `app/server/bin/`
- 🔧 优化错误提示，提供更友好的连接失败信息
- 🔧 代码复用率提升至 80%，远程终端继承本地终端的所有 tmux 操作逻辑

### v1.0.3 (2025-10-21) - 稳定性增强

**Bug 修复**
- 🐛 修复跨设备部署时 `libutempter.so.0` 缺失导致 tmux 无法启动的问题
- 🐛 修复用户 home 目录不存在时的 `su` 警告信息显示问题
- 🐛 修复直接访问 `/terminal/local` 或 `/terminal/remote` 绕过认证的安全漏洞
- 🐛 修复"仅连接"功能在无保存配置时显示错误页面的问题
- 🐛 移除硬编码的测试环境默认值，提高代码健壮性

**功能优化**
- ✨ 为需要管理员权限的快捷命令自动添加 `sudo` 前缀
- ✨ 生产环境自动移除所有 `console` 调试日志，提升性能和专业性
- ✨ 优化路由结构，删除无用的 `/remote-config` 和 `/help` 路由
- ✨ 智能检测用户 home 目录，不存在时自动使用 `/vol1` 作为工作目录
- ✨ 内置 `libutempter.so.0` 依赖库，实现完全自包含部署

**技术改进**
- 🔧 配置 Vite 使用 Terser 压缩，彻底移除生产环境调试代码
- 🔧 统一前端认证流程，强制所有终端页面通过首页认证
- 🔧 优化 `tmux` 启动命令，根据目录存在性选择最优方案
- 🔧 添加 `LD_LIBRARY_PATH` 环境变量配置，确保自带库优先加载

### v1.0.0 (2025-01-XX) - 首次发布

**核心功能**
- ✅ 支持本地终端（基于Tmux）和远程SSH连接管理
- ✅ 实现会话持久化，支持断网重连恢复
- ✅ 提供12款预设主题配色，支持背景透明度调节
- ✅ 现代化响应式界面，支持侧边栏浮动
- ✅ 完善的认证机制和密码管理
- ✅ 支持远程连接配置保存和一键连接

**主题系统**
- One Dark Pro - 经典护眼主题
- Dracula - 优雅深紫色主题
- Nord - 冷色调护眼主题
- Gruvbox Dark - 温暖复古色调
- Solarized Dark - 科学配色
- Monokai - 流行暗色主题
- GitHub Dark - GitHub风格深色
- Atom One Dark - Atom编辑器经典
- Material Dark - Material Design深色
- Night Owl - 夜猫子专属护眼
- Palenight - 淡紫夜色优雅
- Cobalt2 - 深蓝科技风

**技术特性**
- 基于Vue 3 + Vite构建的现代化前端
- FastAPI高性能异步后端
- xterm.js终端模拟器
- Tmux会话管理和持久化（本地+远程统一架构）
- tmux+ssh 远程连接实现，支持会话持久化
- sshpass 非交互式密码认证
- WebSocket实时通信
- 生产环境自动移除调试日志
- 自动依赖库管理（内置 libutempter、sshpass）
- 智能路径检测和兜底机制

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Vue.js](https://vuejs.org/) - 现代化前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能异步Web框架
- [xterm.js](https://xtermjs.org/) - 强大的Web终端模拟器
- [Tmux](https://github.com/tmux/tmux) - 终端复用器和会话管理
- [sshpass](https://sourceforge.net/projects/sshpass/) - 非交互式SSH密码认证工具
- [OpenSSH](https://www.openssh.com/) - 安全的远程连接协议
- [Vite](https://vitejs.dev/) - 新一代前端构建工具
- 飞牛OS团队提供的优秀应用开发框架

## 📞 技术支持

- **维护者**：EWEDL
- **社区支持**：[飞牛社区](https://club.fnnas.com/home.php?mod=space&uid=5411)
- **问题反馈**：请通过GitHub Issues提交问题
- **功能建议**：欢迎提交功能请求和建议

---

**FntermX** - 为飞牛NAS打造的现代化终端体验 🚀

> 让强大的命令行功能在Web界面中完美呈现
