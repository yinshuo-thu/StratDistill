# StratDistill

Hyperliquid 公开策略 / Vault 跟踪、评分、分群与可视化项目（public-data first）。

## 1) 目标

- 持续发现并跟踪可公开获取信息的策略/vault
- 产出可复用原始快照、结构化表、排名结果、分群分析和图表
- 用统一命令幂等刷新，支持小时级自动化

## 2) 数据源

### 官方公开接口
- `POST https://api.hyperliquid.xyz/info`
  - `type=vaultSummaries`：当前实测多次返回 `[]`
  - `type=vaultDetails`：可返回单 vault 详细字段（portfolio、commission、withdrawable 等）

### 公开 stats 端点
- `GET https://stats-data.hyperliquid.xyz/Mainnet/vaults`
  - 当前 discovery 主来源（可获取 summary/apr/pnls）

> 不使用私有接口，不伪造不可公开字段。

## 3) 目录结构

- `src/stratdistill/`
  - `client.py` 请求客户端（重试/超时）
  - `pipeline.py` 基础刷新与评分
  - `enrich.py` 详情抓取、扩展特征、可视化
  - `clustering.py` 分群分析与群组画像
- `scripts/refresh.py` 基础刷新
- `scripts/update_all.py` 全链路刷新（推荐）
- `data/raw/` 原始快照
- `data/processed/` 结构化结果
- `reports/` 文本报告与图表

## 4) 安装

```bash
python3 -m pip install -r requirements.txt
```

## 5) 运行

### 基础刷新
```bash
cd "/Users/yinshuo/Documents/code-iCloud/strategy distillation"
PYTHONPATH=src python3 scripts/refresh.py --max-vaults 300 --top-n 50
```

### 全量更新（推荐）
```bash
cd "/Users/yinshuo/Documents/code-iCloud/strategy distillation"
PYTHONPATH=src python3 scripts/update_all.py --max-vaults 400 --top-n 100 --details-top-k 250 --cluster-k 5
```

## 6) 前端可视化网站（收益时序 + action proxy）

生成网站数据：

```bash
cd "/Users/yinshuo/Documents/code-iCloud/strategy distillation"
python3 scripts/build_web_data.py --top-n 80 --max-fills-per-strategy 1200
```

本地启动：

```bash
cd "/Users/yinshuo/Documents/code-iCloud/strategy distillation/web"
python3 -m http.server 8080
# 浏览器打开 http://127.0.0.1:8080
```

页面能力：
- 可选策略（Top N）
- 可切换 day/week/month/allTime 收益序列
- 可查看 action proxy 点位（全部 / 开仓类 / 平仓类）

## 7) 输出

- 原始：
  - `data/raw/vaults_stats_*.json`
  - `data/raw/vault_details/details_top*_*.json`
- 结构化：
  - `data/processed/vault_master.csv`
  - `data/processed/strategy_registry.csv`
  - `data/processed/strategy_ranked_extended.csv`
  - `data/processed/strategy_cluster_assignments.csv`
  - `data/processed/strategy_cluster_summary.csv`
  - `data/processed/timeseries/*.csv`
- 报告与图：
  - `reports/latest_report.md`
  - `reports/analysis_extended.md`
  - `reports/cluster_report.md`
  - `reports/figures/*.png`

## 7) 排名与分群逻辑

### 扩展评分（extended_score）
- 在基础 `composite_score` 上加入：
  - 佣金友好度（commission 低更好）
  - 可提取比例（maxWithdrawable/maxDistributable 高更好）
  - 历史深度（all-time account value 点数）

### 分群（KMeans）
- 使用标准化后的特征：APR、TVL、PnL、回撤、稳定性、extended_score、历史深度、commission
- 输出 cluster assignments + cluster summary + cluster 可视化

## 8) 已知限制

- `vaultSummaries` 仍为空，发现环节依赖公开 stats 端点
- 某些字段覆盖不均（如 followers）
- 分群是 cohort 分析，不代表“官方策略类别”

## 9) 自动化（OpenClaw cron）

当前可用（已实配）思路：isolated session + agentTurn。

示例：
```bash
openclaw cron add \
  --name stratdistill-hourly \
  --every 1h \
  --session isolated \
  --agent main \
  --message "执行 StratDistill 全量更新：cd '/Users/yinshuo/Documents/code-iCloud/strategy distillation' && PYTHONPATH=src python3 scripts/update_all.py --max-vaults 400 --top-n 100 --details-top-k 250 --cluster-k 5；随后汇报新增raw、ranking、cluster与图表更新。"
```

## 10) Git 同步

```bash
git add .
git commit -m "feat: update distillation outputs"
git push origin master
```
