# SBS闲鱼助手桌面版

此分支为原有 FastAPI + Vue 应用增加 Electron 桌面外壳，并通过 GitHub Actions 生成：

- Windows x64 安装程序（EXE）
- macOS Apple Silicon 安装镜像（DMG，适用于 M1/M2/M3/M4）

## 在 GitHub 上生成安装包

1. 合并本 Pull Request 到 `master`。
2. 打开仓库顶部的 **Actions**。
3. 左侧选择 **Build desktop installers**。
4. 点击右侧 **Run workflow**，分支选择 `master`。
5. 等待 Windows 与 macOS 两项任务完成。
6. 打开本次运行页面，在页面底部 **Artifacts** 下载两个压缩包。

首次测试不需要创建 Release。确认安装包能正常启动后，可以在仓库右侧手动创建 Release，并上传测试通过的 EXE 和 DMG。

## 首次使用

- 默认登录账号：`admin`
- 默认登录密码：`admin123`
- AI接口在软件“系统设置”中填写。
- 闲鱼登录状态在“账号管理”中导入。
- 软件数据保存在系统用户数据目录，升级软件不会主动删除。

## 签名说明

当前测试包未进行代码签名：

- macOS 首次打开时可能需要在 Finder 中右键应用并选择“打开”，或在“隐私与安全性”中允许。
- Windows 可能显示 SmartScreen 提醒，需要选择“更多信息”后继续运行。

正式对外销售前建议配置 Apple Developer ID、公证和 Windows 代码签名证书。

## 安全说明

不要把商用 AI API Key 直接写入仓库或安装包。如果要统一收费，应让桌面客户端连接你自己的 API 中转服务。
