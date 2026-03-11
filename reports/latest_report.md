# Hyperliquid Strategy Distillation Report

Generated at (UTC): 2026-03-08T03:41:02.587703+00:00

## Data Sources
- Official Info API: `POST https://api.hyperliquid.xyz/info`
- Public stats dataset used for discovery: `GET https://stats-data.hyperliquid.xyz/Mainnet/vaults`

## Source Validation
- info type=vaultSummaries response size: 1
- stats vault records fetched: 9200

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
| 1 | Flagship by Fire Labs | `0x632df0dbe24f3dac3e1c4e0596c96a0adc3ba86a` | -0.019042 | 17830.62 | 2916.06 | -49531.62 | 32203.1525 | 0.5669 |
| 2 | BTC/ETH CTA | AIM | `0xbeebbbe817a69d60dd62e0a942032bc5414dae1c` | -0.078655 | 96528.09 | 316.66 | -21288.09 | 9044.5641 | 0.5530 |
| 3 | +convexity | `0x5661a070eb13c7c55ac3210b2447d4bea426cbf5` | -0.050814 | 494966.27 | 62591.81 | -38513.83 | 24590.9078 | 0.5519 |
| 4 | [ Systemic Strategies ] ♾️ HyperGrowth ♾️ | `0xd6e56265890b76413d1d527eb9b75e334c0c5b42` | -0.079572 | 6831503.02 | 1919330.30 | -1317750.43 | 926030.4584 | 0.5427 |
| 5 | ski lambo beach  | `0x66e541024ca4c50b8f6c0934b8947c487d211661` | -0.187276 | 92626.94 | 89705.49 | -39362.63 | 20903.2091 | 0.5391 |
| 6 | Crypto Trading Channel | `0x51b62b4bf8df6f2795b3da30cb46aa47f9f230a8` | -0.055935 | 88997.47 | 17397.08 | -5268.14 | 4039.3196 | 0.5360 |
| 7 | HighFDV | `0x78ab93343554d9b9fc7260f44844fad8f36d3d79` | -0.062162 | 2713.30 | 2019.94 | -1561.72 | 883.1002 | 0.5271 |
| 8 | Delta Neutral | R Tech | `0xf182de5226dc4fe2f134c9b375281a6f50309416` | -0.408411 | 14008.78 | 113.89 | -10394.55 | 4631.1639 | 0.5252 |
| 9 | Ethos Intel - Mvault | `0x79d3b973bd5bc4c6a98f5d2e0ee6e285910945ae` | -0.000449 | 7801.17 | 3082.59 | -1809.75 | 1046.3358 | 0.5198 |
| 10 | Super Saiyan 孫悟空 | `0x7c5885d2974457eafb1a3a4d848c358111f0714d` | -0.209851 | 44520.13 | 170177.39 | -106881.37 | 69634.2544 | 0.5117 |
| 11 | Jade Lotus Capital | `0xbc5bf88fd012612ba92c5bd96e183955801b7fdc` | -0.110346 | 202813.68 | 179770.73 | -129228.46 | 70650.0105 | 0.5093 |
| 12 | Delta_01 | `0x3005fade4c0df5e1cd187d7062da359416f0eb8e` | -0.061170 | 488925.55 | 404495.40 | -270497.09 | 141850.8776 | 0.5082 |
| 13 | Loop Fund | `0xfeab64de8cdf9dcebc0f49812499e396273efc06` | -0.164493 | 57467.88 | 65737.00 | -55724.50 | 23053.7224 | 0.5081 |
| 14 | [ Sidelined ] Market Neutral 1 | `0xf4ab2cb15b7b3fa298555b801e9f5772ba8f8891` | -0.006916 | 36060.73 | 3538.26 | -2022.92 | 1428.3901 | 0.5048 |
| 15 | HLP Strategy A | `0x010461c14e146ac35fe42271bdc1134ee31c703a` | -0.000758 | 121358406.69 | 4866967.96 | -7014131.28 | 3128752.8616 | 0.5040 |
| 16 | Overdose | `0xe67dbf2d051106b42104c1a6631af5e5a458b682` | -0.046775 | 494241.95 | 170389.10 | -56031.61 | 51929.4835 | 0.5039 |
| 17 | しねやボケェ！！！ | `0x7f9571cc340883ff8781dca34afd8d07e3c8147c` | -0.097891 | 4214.53 | 707.89 | -915.11 | 467.6553 | 0.5035 |
| 18 | Octavious Maximus | `0x45c42fbd450b5506f8dc819d46036630fe75b81e` | -0.182914 | 16933.81 | 10394.61 | -8056.70 | 3577.5710 | 0.4960 |
| 19 | TB10 (Top and Bottom 10) | `0xd8bc568c79e9a75563910e82e528596b49065cc9` | -0.034535 | 7512.17 | 194.23 | -502.70 | 228.5726 | 0.4914 |
| 20 | emas | `0x8d4b1f07c630d7cc1d0ea0bf519c61f2885f46a5` | -0.007287 | 2615.17 | 558.24 | -3226.39 | 1116.5076 | 0.4906 |