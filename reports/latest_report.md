# Hyperliquid Strategy Distillation Report

Generated at (UTC): 2026-03-08T03:01:57.562475+00:00

## Data Sources
- Official Info API: `POST https://api.hyperliquid.xyz/info`
- Public stats dataset used for discovery: `GET https://stats-data.hyperliquid.xyz/Mainnet/vaults`

## Source Validation
- info type=vaultSummaries response size: 1
- stats vault records fetched: 9199

## Known Limits
- `vaultSummaries` currently returned empty array in test; discovery currently relies on public stats endpoint.
- Public dataset does not consistently expose all follower/flow dimensions for each vault.
- PnL/account value granularity depends on available `pnls` arrays; no private trade-level fields are assumed.

## Scoring Assumptions
- Composite score uses multi-factor ranking (apr/tvl/followers/pnl/drawdown/stability/data quality).
- If some factors are mostly missing, weights are dynamically renormalized over available factors.
- Closed vaults receive a fixed score penalty of 0.10.
- Discovery uses public stats endpoint while official vaultSummaries remains empty in observed tests.

## Top 20 by Composite Score

| Rank | Name | Vault | APR | TVL | PnL(all time) | Max Drawdown | Stability(std ΔPnL) | Score |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | +convexity | `0x5661a070eb13c7c55ac3210b2447d4bea426cbf5` | -0.050814 | 494966.27 | 62591.81 | -38513.83 | 24590.9078 | 0.5529 |
| 2 | Flagship by Fire Labs | `0x632df0dbe24f3dac3e1c4e0596c96a0adc3ba86a` | -0.019042 | 17830.62 | 2916.06 | -49531.62 | 32203.1525 | 0.5484 |
| 3 | [ Systemic Strategies ] ♾️ HyperGrowth ♾️ | `0xd6e56265890b76413d1d527eb9b75e334c0c5b42` | -0.080267 | 6826346.30 | 1914173.58 | -1317750.43 | 926243.9979 | 0.5441 |
| 4 | ski lambo beach  | `0x66e541024ca4c50b8f6c0934b8947c487d211661` | -0.183559 | 93310.20 | 90388.75 | -38679.37 | 20850.5264 | 0.5404 |
| 5 | Crypto Trading Channel | `0x51b62b4bf8df6f2795b3da30cb46aa47f9f230a8` | -0.058440 | 88760.53 | 17160.14 | -5268.14 | 4036.1162 | 0.5211 |
| 6 | BTC/ETH CTA | AIM | `0xbeebbbe817a69d60dd62e0a942032bc5414dae1c` | -0.076430 | 96762.41 | 550.98 | -21288.09 | 9045.5388 | 0.5184 |
| 7 | Abstract TrendETH, 2x leverage | `0x5c29944d5a39a452d282f1bc5f1702a9007cb36b` | -0.016137 | 7275.06 | 1786.96 | -2196.11 | 1216.2822 | 0.5130 |
| 8 | HLP Strategy A | `0x010461c14e146ac35fe42271bdc1134ee31c703a` | -0.000559 | 121382616.10 | 4891177.37 | -7014131.28 | 3127715.0486 | 0.5065 |
| 9 | Overdose | `0xe67dbf2d051106b42104c1a6631af5e5a458b682` | -0.041790 | 497138.20 | 173285.35 | -56031.61 | 51720.4523 | 0.5063 |
| 10 | 22Cap | `0xba939edf38c0ae0cc689c98b492e0535f43e4550` | -0.070486 | 126634.43 | 51370.78 | -14997.03 | 7818.5741 | 0.4984 |
| 11 | JizzJazz | `0x82eba5dc675279cb5967952f0c4b5184505eb17c` | -0.000408 | 147341.55 | 26016.27 | -15315.84 | 8125.1418 | 0.4942 |
| 12 | emas | `0x8d4b1f07c630d7cc1d0ea0bf519c61f2885f46a5` | -0.011868 | 2595.51 | 538.58 | -3226.39 | 1116.1648 | 0.4940 |
| 13 | TB10 (Top and Bottom 10) | `0xd8bc568c79e9a75563910e82e528596b49065cc9` | -0.034360 | 7513.64 | 195.70 | -502.70 | 228.7877 | 0.4929 |
| 14 | HighFDV | `0x78ab93343554d9b9fc7260f44844fad8f36d3d79` | -0.062162 | 2713.30 | 2019.94 | -1561.72 | 883.1002 | 0.4802 |
| 15 | Super Saiyan 孫悟空 | `0x7c5885d2974457eafb1a3a4d848c358111f0714d` | -0.196283 | 45286.93 | 170944.19 | -106114.57 | 69616.6187 | 0.4796 |
| 16 | Momentum Edge | `0xc1703054b55bfa1ac6dbaf25cb1c783ca133181f` | -0.000479 | 6736.23 | 1538.85 | -294.65 | 479.8306 | 0.4773 |
| 17 | Goon Edging | `0x2431edfcb662e6ff6deab113cc91878a0b53fb0f` | -0.295345 | 70583.13 | 20487.41 | -36582.06 | 15059.3359 | 0.4768 |
| 18 | Jade Lotus Capital | `0xbc5bf88fd012612ba92c5bd96e183955801b7fdc` | -0.091498 | 208711.90 | 185668.95 | -123330.25 | 70187.1260 | 0.4767 |
| 19 | Bitcoin Moving Average Long/Short | `0xb1505ad1a4c7755e0eb236aa2f4327bfc3474768` | -0.056777 | 3510764.74 | 414418.54 | -451197.39 | 244882.0312 | 0.4764 |
| 20 | Loop Fund | `0xfeab64de8cdf9dcebc0f49812499e396273efc06` | -0.163664 | 57624.64 | 65893.76 | -55567.74 | 23048.9987 | 0.4761 |