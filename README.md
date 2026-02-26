本帖最后由 wodepiqi 于 2026-2-24 19:14 编辑


IRext-Android-HA-Gateway
将你的闲置安卓手机变成专业级红外网关，完美接入 Home Assistant。

本项目包含两个部分：

Android 端网关应用：支持内置红外/耳机孔红外发射，内置 Magisk 模块注入及系统级保活。

Home Assistant 自定义组件：支持 UI 配置，自动同步设备，生成原生 Climate（空调）和 Media Player 实体。


✨ 核心特性
🚀 零配置接入：通过 HACS 插件直接搜 IP 添加，自动同步 App 内保存的设备。

❄️ 完美空调支持：自动生成 Climate 实体，支持模式切换、温度调节及状态记忆。

📺 媒体中心支持：电视、机顶盒自动映射为 Media Player，支持音量、静音及 0-9 数字键。

🎧 硬件全兼容：


支持手机内置红外发射器。

支持耳机孔红外配件（通过 19kHz 相位差音频算法合成 38kHz 信号）。


🛡️ 工业级保活：


Magisk 模式：App 可一键注入面具模块，化身系统级 Priv-App，免疫一切杀后台。

非 Root 模式：支持系统电池优化白名单引导。


☁️ 云端双策略：支持官方公有云及本地 Docker 私有云自建，断网也能控。


📱 Android App 安装与使用
下载并安装 latest APK。

连接服务器：


选择“公有云”或“私有云”。

若使用私有云，请输入你的 Docker 地址（如 http://192.168.1.100:8081）。


激活服务：点击“保存并启动网关”，记录屏幕显示的访问地址（如 http://192.168.1.5:8080）。

添加设备：


点击“添加设备”，进入智能匹配向导。

选类型、选品牌，点击测试按钮。

有反应后点确认并保存，取名后设备将存入手机本地数据库。


极客选项：


如果手机有 Root，点击“一键部署面具模块”，重启后服务将永不掉线。

如果使用耳机孔红外头，请勾选“强制音频发码”。



🏠 Home Assistant 插件部署手动安装
将本项目目录下的 custom_components/irext_gateway 文件夹拷贝到你的 HA 配置目录下的 custom_components 文件夹内。

重启 Home Assistant。

在 HA 界面：配置 -> 设备与服务 -> 添加集成。

搜索 "IRext Android Gateway" 并输入手机 IP 地址。


实体展示
空调：自动绑定为 climate 实体，带温度圆环。

电视/机顶盒：自动绑定为 media_player 实体。

开关类：自动绑定为 switch 实体。


🛠️ 开发者说明技术栈
Android: Java, NanoHTTPD (Web API), AudioTrack (PCM脉冲合成)。

Home Assistant: Python, DataUpdateCoordinator (实时状态同步)。

云端: 完美兼容 IRext Restful API 1.5.2 协议。


API 接口
网关默认监听 8080 端口，提供以下接口供三方调用：

GET /api/list: 获取已保存设备 JSON。

GET /api/tx: 发射红外指令。


参数：id (码库ID), c (类别), k (键码), p (电源), m (模式), t (温度枚举)。



🤝 致谢
码库索引支持：IRext

网页解析支持：NanoHTTPD


📄 许可证
MIT License
