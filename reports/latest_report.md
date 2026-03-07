# Hyperliquid Strategy Distillation Report

Generated at (UTC): 2026-03-07T21:34:53.354418+00:00

## Data Sources
- Official Info API: `POST https://api.hyperliquid.xyz/info`
- Public stats dataset used for discovery: `GET https://stats-data.hyperliquid.xyz/Mainnet/vaults`

## Source Validation
- info type=vaultSummaries response size: 0
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
| 1 | [ Systemic Strategies ] ♾️ HyperGrowth ♾️ | `0xd6e56265890b76413d1d527eb9b75e334c0c5b42` | -0.062630 | 6492305.40 | 1878956.33 | -1317750.43 | 927769.9945 | 0.5463 |
| 2 | Flagship by Fire Labs | `0x632df0dbe24f3dac3e1c4e0596c96a0adc3ba86a` | -0.023726 | 17830.62 | 2916.06 | -49531.62 | 32203.1525 | 0.5210 |
| 3 | Satori Quantum HF Vault | `0xbbf7d7a9d0eaeab4115f022a6863450296112422` | -0.107020 | 568720.55 | 278171.16 | -213742.76 | 138422.8599 | 0.5176 |
| 4 | HighFDV | `0x78ab93343554d9b9fc7260f44844fad8f36d3d79` | -0.062162 | 2713.30 | 2019.94 | -1561.72 | 883.1002 | 0.5149 |
| 5 | TrendPilot | `0x72255024cded9e6edf856a2a24318b9411a37695` | -0.040056 | 8832.64 | 2207.83 | -12845.01 | 5294.8551 | 0.5123 |
| 6 | HLP Strategy A | `0x010461c14e146ac35fe42271bdc1134ee31c703a` | -0.000843 | 121353748.59 | 4862309.86 | -7014131.28 | 3128954.4399 | 0.5107 |
| 7 | Ethos Intel - Mvault | `0x79d3b973bd5bc4c6a98f5d2e0ee6e285910945ae` | -0.000449 | 7801.17 | 3082.59 | -1809.75 | 1046.3358 | 0.5069 |
| 8 | HyperTwin - Blue Whale | `0x9a3006e0b7ffacf11729103098ff16fa6e17bd24` | -0.143132 | 14221.12 | 2180.31 | -4674.56 | 2408.3683 | 0.5031 |
| 9 | [ Sidelined ] Market Neutral 2: BTC Maxi | `0x257acedf61ffd72abfcde8332a13a1d015930051` | -0.020426 | 31910.39 | 1332.96 | -3943.81 | 1634.6774 | 0.4931 |
| 10 | ● MONO BLACK TOKYO「ISHI 石」 | `0x395f50a09d7bc2e2883c9e427d36896264a6ee8f` | -0.040856 | 2189.21 | 1811.18 | -1572.67 | 1193.8733 | 0.4872 |
| 11 | Super Saiyan 孫悟空 | `0x7c5885d2974457eafb1a3a4d848c358111f0714d` | -0.290393 | 45846.53 | 171503.79 | -105554.97 | 69604.1529 | 0.4826 |
| 12 | Jade Lotus Capital | `0xbc5bf88fd012612ba92c5bd96e183955801b7fdc` | -0.210668 | 211403.56 | 188360.61 | -120638.58 | 69989.7374 | 0.4803 |
| 13 | [ Sidelined ] Market Neutral 1 | `0xf4ab2cb15b7b3fa298555b801e9f5772ba8f8891` | -0.021237 | 36007.30 | 3484.83 | -2022.92 | 1430.1932 | 0.4803 |
| 14 | Delta_01 | `0x3005fade4c0df5e1cd187d7062da359416f0eb8e` | -0.156938 | 492228.74 | 407798.59 | -270497.09 | 141807.4591 | 0.4802 |
| 15 | Aquila Chrysaetos | `0x50e2fe552727a4b8692c192b4f96d1a6b0d44394` | -0.008078 | 73271.63 | 11692.44 | -2355.93 | 2676.0757 | 0.4795 |
| 16 | Loop Fund | `0xfeab64de8cdf9dcebc0f49812499e396273efc06` | -0.260997 | 57406.40 | 65675.52 | -55785.97 | 23055.5989 | 0.4794 |
| 17 | Goon Edging | `0x2431edfcb662e6ff6deab113cc91878a0b53fb0f` | -0.137235 | 70424.26 | 20328.54 | -36740.94 | 15069.4664 | 0.4765 |
| 18 | ski lambo beach  | `0x66e541024ca4c50b8f6c0934b8947c487d211661` | -0.222475 | 94153.92 | 91232.47 | -37835.65 | 20787.8486 | 0.4765 |
| 19 | OnDitMerciQui? | `0x057236927e2e2c8b3cd595746a051687ba40d1cc` | -0.176824 | 1143.42 | 97.18 | -2503.54 | 715.5954 | 0.4745 |
| 20 | しねやボケェ！！！ | `0x7f9571cc340883ff8781dca34afd8d07e3c8147c` | -0.032842 | 4207.37 | 700.73 | -915.11 | 467.2572 | 0.4743 |