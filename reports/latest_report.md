# Hyperliquid Strategy Distillation Report

Generated at (UTC): 2026-03-11T07:32:58.940020+00:00

## Data Sources
- Official Info API: `POST https://api.hyperliquid.xyz/info`
- Public stats dataset used for discovery: `GET https://stats-data.hyperliquid.xyz/Mainnet/vaults`

## Source Validation
- info type=vaultSummaries response size: 2
- stats vault records fetched: 9212

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
| 1 | Jade Lotus Capital | `0xbc5bf88fd012612ba92c5bd96e183955801b7fdc` | -0.248950 | 319928.92 | 192080.16 | -116919.04 | 69231.2338 | 0.5637 |
| 2 | Equinox · Blackalgo | `0x7048b287889c5913d59f812795d7fd5d724be77a` | -0.043627 | 1070486.70 | 6131.87 | -82602.59 | 42265.7852 | 0.5445 |
| 3 | C.A.T | `0xdfb729b4b789de6d13d6ad7ac8e2750909360af9` | -0.204618 | 6902.54 | 101.39 | -3448.44 | 1578.4045 | 0.5429 |
| 4 | Sentiment Edge  | `0xb7e7d0fdeff5473ed6ef8d3a762d096a040dbb18` | -0.027105 | 165749.67 | 46184.91 | -33191.74 | 18015.1686 | 0.5340 |
| 5 | OnDitMerciQui? | `0x057236927e2e2c8b3cd595746a051687ba40d1cc` | -0.101157 | 1222.45 | 176.21 | -2424.51 | 743.8513 | 0.5337 |
| 6 | BTC/ETH CTA | AIM | `0xbeebbbe817a69d60dd62e0a942032bc5414dae1c` | -0.082126 | 96289.18 | 77.75 | -21288.09 | 9052.4905 | 0.5304 |
| 7 | 22Cap | `0xba939edf38c0ae0cc689c98b492e0535f43e4550` | -0.015333 | 128812.18 | 56023.26 | -10344.55 | 6803.1218 | 0.5220 |
| 8 | DH-Funding Rate | `0xa6b72ea0ef4542d520aa78f8d749ab4f2714b63d` | -0.011681 | 9746.61 | 4408.58 | -1822.68 | 1085.0837 | 0.5194 |
| 9 | Storm | `0xae08a2282d969bd0c4bf63a626ab8f8e6200022d` | -0.027282 | 30789.17 | 789.17 | -3024.42 | 994.9112 | 0.5156 |
| 10 | Flagship by Fire Labs | `0x632df0dbe24f3dac3e1c4e0596c96a0adc3ba86a` | -0.008497 | 17679.12 | 2764.56 | -49531.62 | 32203.3217 | 0.5136 |
| 11 | Bitcoin Moving Average Long/Short | `0xb1505ad1a4c7755e0eb236aa2f4327bfc3474768` | -0.006385 | 3385434.56 | 265341.55 | -360419.11 | 231885.5408 | 0.5048 |
| 12 | Loop Fund | `0xfeab64de8cdf9dcebc0f49812499e396273efc06` | -0.072140 | 66272.74 | 74851.87 | -36529.51 | 15167.8595 | 0.5048 |
| 13 | Loong | `0x3daa34fb415e55fc5091df17f5c88cd552f88e46` | -0.000001 | 2759.33 | 143741.88 | -25785.74 | 37933.5022 | 0.5029 |
| 14 | [ Sidelined ] Market Neutral 1 | `0xf4ab2cb15b7b3fa298555b801e9f5772ba8f8891` | -0.002660 | 35192.67 | 4160.84 | -1787.81 | 1449.7069 | 0.5020 |
| 15 | Follow the Money | `0x0405e04a717fae31cd3d19242976aa2ffe1ed791` | -0.035849 | 4267.92 | 472.62 | -819.41 | 412.9039 | 0.5007 |
| 16 | JizzJazz | `0x82eba5dc675279cb5967952f0c4b5184505eb17c` | -0.003691 | 143828.12 | 21697.15 | -34727.36 | 14838.7303 | 0.5002 |
| 17 | TB10 (Top and Bottom 10) | `0xd8bc568c79e9a75563910e82e528596b49065cc9` | -0.043258 | 5591.64 | 178.23 | -258.51 | 126.5469 | 0.4948 |
| 18 | Orange Coin Green PNL | `0x58428d381ee757303234b75545b3fddd6884de0f` | -0.070724 | 2935.21 | 833.97 | -409.89 | 334.9020 | 0.4887 |
| 19 | Sentiment Edge | `0x026a2e082a03200a00a97974b7bf7753ce33540f` | -0.027903 | 109504.08 | 26135.78 | -7276.01 | 4078.1391 | 0.4876 |
| 20 | [ Broadcraft Capital ] Tradewinds | `0xe76c9c59157c993ac3cb405defb7992661b57fed` | -0.067700 | 2447.01 | 324.19 | -260.02 | 199.8370 | 0.4841 |