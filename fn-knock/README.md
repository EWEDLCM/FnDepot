# 敲门knock

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/kci-lnk/fn-knock-turborepo)
[![Platform](https://img.shields.io/badge/platform-飞牛OS-orange.svg)](https://www.fnnas.com/)
[![Arch](https://img.shields.io/badge/arch-x86__64%20%7C%20arm64-lightgrey.svg)](https://github.com/kci-lnk/fn-knock-turborepo)

**敲门knock** 是一款面向飞牛OS的安全防护软件，聚焦家庭和轻量服务器场景下的访问安全治理，内置防火墙控制与反代安全能力，帮助用户更直观地管理入口暴露面和访问策略。

## 核心功能

- 防火墙控制：对外暴露端口进行集中管理，减少不必要的开放面。
- 反代安全：针对反向代理场景提供额外的安全防护能力。
- 双架构支持：同时提供 x86_64 与 arm64 安装包，便于不同硬件平台使用。
- 飞牛OS 集成：以 FPK 形式发布，适配飞牛OS 的应用安装与运行方式。

## 应用信息

- 应用名称：敲门knock
- 当前版本：1.2.0
- 开发者：kci-lnk
- 官网：[https://www.fnknock.cn/](https://www.fnknock.cn/)
- 项目页：[https://github.com/kci-lnk/fn-knock-turborepo](https://github.com/kci-lnk/fn-knock-turborepo)
- 问题反馈：[https://github.com/kci-lnk/fn-knock-turborepo/issues](https://github.com/kci-lnk/fn-knock-turborepo/issues)
- 默认服务端口：7999
- 安装类型：系统空间

## 依赖与兼容性

- 支持架构：x86_64、arm64
- x86_64 包依赖：Node.js v20、Redis
- arm64 包依赖：Node.js v20
- 运行权限：root

## 安装说明

1. 在 FnDepot 中同步应用源。
2. 找到 **敲门knock** 并安装与当前设备架构匹配的版本。
3. 安装完成后，通过飞牛OS 应用入口打开应用。
4. 如需进一步配置，请结合官网或项目页中的说明进行设置。

## 使用提示

- 在启用防火墙或反代相关策略前，建议先确认当前设备的管理入口与必要业务端口，避免误封。
- 若网络访问策略较复杂，建议先在低风险环境测试后再应用到生产设备。
- 若遇到安装或运行问题，可优先到项目 Issues 页面反馈。
