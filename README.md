# 自动维护的备用节点池

这套配置从多个公开订阅源抓取节点，交给 `subs-check` 做协议级测活、实际 HTTP 请求、去重和有限测速，每两小时更新一次 Clash/Mihomo 订阅。它面向“固定节点失效时的临时备份”，不应替代可信的自建节点。

## 快速启动

前提：Docker Desktop 已启动。

```bash
cd /Users/log/Documents/代理节点
make bootstrap
make test
make up
make logs
```

首次运行需要拉取容器镜像并检测大量候选节点，可能耗时数分钟。日志出现检测完成后，可使用：

- 当前通过检测的 Clash 节点：`http://127.0.0.1:8199/sub/all.yaml`
- 最近一次有效结果：`http://127.0.0.1:8199/sub/last-good.yaml`
- 带规则的 Mihomo 配置：`http://127.0.0.1:8199/sub/mihomo.yaml`
- Base64 订阅：`http://127.0.0.1:8199/sub/base64.txt`
- 本地管理页：`http://127.0.0.1:8199/admin`

管理页 API Key 保存在本机 `.env`，该文件已被 Git 忽略。Compose 只把 8199/8299 绑定到 `127.0.0.1`，局域网和公网默认无法访问。

## 修改数据源

编辑 `config/sources.txt`：

```text
https://example.com/subscription | 来源名称
```

然后重新生成并重启：

```bash
make config
make restart
```

不要把带私人 token 的订阅地址提交到 Git；如果必须加入私有源，先确认这个目录不会被公开同步。

## 自动维护逻辑

1. 首次启动立即检测，之后每两小时重新下载数据源。
2. 聚合并去重候选节点。
3. 使用真实代理连接请求 `https://www.gstatic.com/generate_204`。
4. 淘汰延迟超过 6 秒或速度低于 128 KB/s 的节点。
5. 最多保留约 120 个通过节点。
6. 最近 7 天成功过的节点会被重新加入候选池，但仍需重新通过检测。
7. 每次有效结果复制到 `output/last-good.yaml`，并在 `output/snapshots/` 保留 14 天快照。

`last-good.yaml` 的意义是：某轮上游拉取或检测异常时，旧的有效订阅不会被覆盖。它不保证节点此刻仍然在线，客户端仍应开启自动延迟测试。

## 常用命令

```bash
make status   # 容器状态和输出文件
make logs     # 实时日志
make restart  # 修改配置后重建容器
make pull     # 手动拉取最新版 subs-check 镜像
make down     # 停止服务
```

## 安全边界

公开免费节点的运营者可以观察未端到端加密的流量，也可能记录连接元数据。仅用于临时访问公开内容；不要用于邮箱、银行、交易所、主力 AI 账号、工作系统或任何包含敏感信息的服务。

上游项目：<https://github.com/beck-8/subs-check>
