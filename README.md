# StratDistill

Hyperliquid 公开策略 / Vault 跟踪与表现蒸馏项目（public-data first）。

## 1) 项目目标

- 发现并跟踪 Hyperliquid 上可公开获取数据的 vault/strategy
- 定时抓取并保存原始快照（raw）
- 生成可复用的结构化表格（master/top/timeseries）
- 基于多因子打分逻辑输出“高表现策略”候选
- 产出文本报告，记录假设、限制与最新结果

## 2) 数据源（公开接口优先）

### 官方接口
- `POST https://api.hyperliquid.xyz/info`
  - 已验证：`{"type":"vaultSummaries"}` 在当前时点返回空数组 `[]`
  - 结论：官方该入口当前不足以独立完成完整 vault 发现

### 公开可访问 stats 数据
- `GET https://stats-data.hyperliquid.xyz/Mainnet/vaults`
  - 可获得：`summary`、`apr`、`pnls` 等字段
  - 当前用于发现 + 更新主流程

> 说明：本项目**不使用私有接口**，不伪造不可公开字段。

## 3) 项目结构

- `src/stratdistill/` 核心模块
  - `client.py` 抓取客户端（超时/重试）
  - `pipeline.py` 处理、评分、报告生成
  - `config.py` 路径与常量
- `scripts/refresh.py` 一键刷新入口（可传参数）
- `data/raw/` 原始快照
- `data/processed/` 处理后结构化结果
  - `vault_master.csv`
  - `vault_top_performers.csv`
  - `timeseries/*.csv`
- `reports/latest_report.md` 最新报告
- `logs/` 运行日志/元信息

## 4) 安装

```bash
python3 -m pip install -r requirements.txt
```

## 5) 一键刷新（统一入口）

```bash
cd "/Users/yinshuo/Documents/code-iCloud/strategy distillation"
PYTHONPATH=src python3 scripts/refresh.py --max-vaults 300 --top-n 50
```

## 6) 输出产物

- `data/raw/vaults_stats_*.json`：原始抓取快照
- `data/processed/vault_master.csv`：候选主表
- `data/processed/vault_top_performers.csv`：Top N 汇总
- `data/processed/timeseries/<vault>.csv`：每个 vault 的可用 PnL 序列
- `reports/latest_report.md`：分析摘要与限制说明

## 7) 评分逻辑（v1）

综合得分 `composite_score` 基于多因子排名（rank percentile）：

- APR（高更好）
- TVL（高更好）
- Followers（高更好；若公开数据缺失则动态降权）
- All-time PnL（高更好）
- 最大回撤（绝对值越小越好）
- 稳定性（`std(diff(all_time_pnl))` 越小越好）
- 数据完整性（`pnl_obs_count` 越高越好）

附加规则：
- `is_closed=true` 固定扣分 `0.10`
- 若某因子在当前批次几乎缺失（例如 followers），采用**动态权重重归一化**，避免空字段污染总分

候选过滤（v1）：
- 非关闭 vault
- `pnl_obs_count >= 20`
- `tvl > 1000`
- `pnl_all_time_last > 0`

## 8) 已知限制 / 数据缺口

- 官方 `vaultSummaries` 当前返回空数组，导致发现环节依赖 public stats 端点
- 当前公开数据未稳定提供完整 follower 维度
- 时间序列以 `pnls` 为主，非逐笔交易级

## 9) 每小时自动刷新（OpenClaw cron）

先确认语法：`openclaw cron add --help`

建议命令：

```bash
openclaw cron add \
  --name stratdistill-hourly \
  --every 1h \
  --session main \
  --message "在 /Users/yinshuo/Documents/code-iCloud/strategy distillation 执行：PYTHONPATH=src python3 scripts/refresh.py --max-vaults 300 --top-n 50；然后汇报结果与阻塞。"
```

> 如果你希望**自动提交并推送**，建议再增加一个独立 cron（先观察 1~2 天再开启）。

## 10) Git 同步

```bash
git add .
git commit -m "feat: refresh pipeline and scoring update"
git push origin master
```

如推送失败，优先检查：
- SSH key 是否已配置到 GitHub
- 本地分支与远端是否存在冲突
