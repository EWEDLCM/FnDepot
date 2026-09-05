# PicoClaw

PicoClaw 是一款超轻量级个人 AI 助手，支持多种 LLM 提供商，强调轻量、快速与安全。

## 应用信息

- 应用名：PicoClaw
- 包名：`picoclaw`
- 当前版本：`0.3.1`
- 发布者：EWEDL
- 上游项目：<https://github.com/sipeed/picoclaw>
- 问题反馈：<https://github.com/sipeed/picoclaw/issues>

## 简介

皮皮虾，超轻量级个人 AI 助手，支持多种 LLM 提供商，比小龙虾更小、更轻快、更安全。

## 安装说明

从 FnDepot 安装后即可使用。当前仓库内提供 `picoclaw.fpk` 安装包。

## 更新说明

#### 🚀 新特性 (New Features)
- 模型提供商 (Provider)：新增 NEAR AI Cloud 支持
- 自动化与任务：新增可配置远程定时任务命令 (remote cron commands)
- 通道设置：新增更灵活的 Channel 频道配置项

#### ✨ 体验优化与增强 (Enhancements)
- 错误处理：改进模型/Provider 错误处理机制
- 搜索诊断：优化原生搜索处理逻辑及 Brave/Web 网页搜索诊断反馈
- 网关日志：改善 Gateway 启动时的日志报告机制

#### 🐛 核心修复 (Fixes)
- Evolution：修复 heartbeat 心跳跳过冷启动路径，使用 CompareAndSwap 实现 lockStoreFile 原子级文件锁并增加类型断言检查
- 网络与清理：修复 WebSocket 拨号清理路径中 resp.Body.Close() 错误，修复 Agent 代理 Base64 编码器在 io.Copy 报错时未正确关闭
- 平台特性：修复 Telegram 论坛话题 (forum topics) 与 Gemini 思考签名 (thought signatures)
- 安全加固：加固入站媒体文件与 Web 抓取处理，修复媒体清理路径

---
*上次更新：2026-09-05*
