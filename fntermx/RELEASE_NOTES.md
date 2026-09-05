# FntermX v1.1.9 更新说明

## 更新概述

本版本主要适配 fnOS 新版 HttpOnly 会话认证与官方网关认证策略，修复升级 fnOS 后本地终端和远程 SSH 功能无法正常使用的问题。

## 问题修复

- 修复打开本地终端后提示“认证失败”，无法建立终端 WebSocket 连接的问题。
- 修复 SSH 连接配置读取、保存或测试时提示“网络错误”的问题。
- 修复受保护 API 被官方网关返回 `invalid token`，请求无法到达 FntermX 后端的问题。
- 改进网关纯文本和非 JSON 错误响应处理，避免将认证冲突错误显示为普通网络故障。

## 安全改进

fnOS 新版网关开始接管标准 `Authorization` Header。旧版本 FntermX 使用该 Header 传递应用 JWT，导致应用令牌被官方网关误判为 fnOS 令牌并提前拒绝。

v1.1.9 将应用 JWT 迁移至专用 Header：

```http
X-FntermX-Authorization: Bearer <FntermX JWT>
```

本次适配没有降低认证强度，以下安全措施保持启用：

- FntermX JWT 使用 HS256 签名并校验有效期。
- 每个受保护请求必须同时具备有效应用 JWT 和 fnOS 网关用户身份。
- JWT 中的用户 UID 必须与官方网关 `X-Trim-Userid` 一致。
- SSH 配置、主题、自定义命令和终端会话继续按 `owner_uid` 隔离。
- WebSocket 继续使用短期、一次性、绑定用途及会话 ID 的认证票据。
- 后端默认不接受标准 `Authorization` 作为应用 JWT，避免与官方网关再次发生认证冲突。

## 验证结果

已在 fnOS `1.2.0600` 测试环境完成以下回归：

- fnOS 登录和 FntermX 独立密码认证。
- 本地终端创建、WebSocket 建连和命令输入输出。
- SSH 配置读取、保存和删除。
- WebSocket 一次性票据签发。
- 伪造 JWT、过期 JWT、用户 UID 不一致及缺少网关身份时的拒绝行为。
- 浏览器受保护请求不再发送标准 `Authorization` Header。

## 升级建议

建议已升级新版 fnOS、且出现本地终端认证失败或 SSH 配置网络错误的用户升级到 v1.1.9。升级会保留现有认证信息、SSH 配置、主题、自定义命令和终端会话数据。
