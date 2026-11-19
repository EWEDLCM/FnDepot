# aiNVR

AI 增强小米摄像头 NVR —— 小米私有协议直连，无需开启 RTSP/ONVIF、无需刷固件、不依赖云录像。

- 画面变动侦测：ROI 排除区域、侦测时段计划、灰屏/糊屏过滤
- 本地 AI 识别（SSD-MobileNetV1，ONNX）：人形 / 车辆 / 宠物，完全离线
- 事件告警中心：快照大图、直达回放、批量处理
- 时间轴回放：分段无缝接续、0.5~16 倍速、循环播放
- 标准 RTSP 下行 + HLS 网页预览，多端共用一条摄像头连接
- 免登录共享大屏：4/9/6 宫格挂 Android TV，Webhook 驱动事件全屏
- 通知推送：Webhook（HMAC 验签）+ SMTP 邮件
- 访问安全：密码门禁、API 密钥、监控台深色/浅色双主题

以飞牛 fnOS 应用（fpk）交付，应用中心安装即用。GPL-2.0 开源（基于上游开源项目 i-nvr by IndSvr 二次开发并延续同许可发行）。

- 源码：https://github.com/zsunny6658/ai-nvr
- 官网：https://ainvr.zsunny.top
