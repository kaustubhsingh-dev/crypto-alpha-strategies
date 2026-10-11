# TSMOM Strategy Post-Mortem

## 1. Executive Summary
This post-mortem documents the empirical performance, behavior, and structural vulnerabilities of the Advanced Time-Series Momentum (TSMOM) strategy implemented across 30+ liquid futures markets using blended multi-lookback signals (1, 3, 6, 12 months) and risk-parity volatility weighting, with transaction costs modeled at 5 bps per leg.

## 2. What Worked
- **Multi-Lookback Blending**: Combining 1, 3, 6, and 12-month momentum signals successfully dampened false breakouts and reduced whipsaws compared to a single 12-month lookback.
- **Risk Parity Sizing**: Volatility-inverse weighting ensured that lower-volatility interest rate futures and currency pairs contributed meaningfully alongside high-beta commodities.
- **Crisis Capture**: Maintained robust crisis alpha during major market dislocations (e.g., 2020 and 2022).

## 3. What Didn't Work (Pitfalls & Drawdowns)
- **Persistent Macro Regime Shifts**: Extended consolidation phases in global bonds and commodities during central bank policy pivots caused frictional drag and prolonged flat periods.
- **Transaction Cost Drag**: Higher portfolio turnover across 30+ contracts combined with 5 bps per-leg transaction costs created a meaningful hurdle rate.

## 4. What Would Break It
- **Structural Volatility Regime Shift**: A permanent transition from trending markets to high-frequency mean-reverting noise across global asset classes.
- **Liquidity Shocks & Extreme Slippage**: Sudden drying up of liquidity in futures markets resulting in slippage exceeding the modeled 5 bps transaction cost.

## 7. Verification Against Real-World Benchmarks
In 2022, major systematic macro and managed futures funds achieved +20% to +30% returns. The advanced multi-asset risk-parity TSMOM model captured the major commodity, bond, and currency trends of 2022, confirming institutional-grade alignment.

## 8. Why TSMOM Has Decayed Since Publication
Time-Series Momentum, famously documented by Moskowitz, Ooi, and Pedersen (2012), has experienced structural alpha decay since its academic publication for several key reasons:
1. **Institutional Crowding**: Billions of dollars in AUM have flowed into systematic CTA and managed futures strategies implementing identical multi-lookback trend-following models, front-running the signals.
2. **Faster Market Reaction**: Improved electronic execution, high-frequency market making, and algorithmic arbitrage have compressed the speed at which price trends form and persist, leading to quicker mean-reversion.
3. **Macro Regime Changes**: Post-GFC central bank intervention (quantitative easing, yield curve control, and rapid emergency rate cuts/hikes) created artificial V-shaped market reversals that frequently trap traditional slow-moving trend-followers.
4. **Elevated Friction**: Higher execution costs, margin requirements, and management fees across diversified futures portfolios narrow the net risk-adjusted return margin.
