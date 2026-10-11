# Research Memo: Crypto Liquidation Cascade Fading ("Remora Fish" Strategy)

## 1. Data Sources
To capture positioning extremes and liquidation cascades without relying on lagging retail indicators, we require high-frequency derivatives market data. Below is the breakdown of free API availability across major exchanges and aggregators:

- **Binance Futures API**:
  - **Open Interest (OI)**: Available via `/fapi/v1/openInterest` (current) and `/futures/data/openInterestHist` (historical historical intervals: 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d). Completely free.
  - **Funding Rates**: Real-time (`/fapi/v1/premiumIndex`) and historical funding rate archives (`/fapi/v1/fundingRate`). Completely free.
  - **Liquidation Volumes**: Real-time WebSocket stream (`<symbol>@forceOrder`) for individual liquidation events, and historical aggregated liquidation data via Binance Futures data archives.
  - **Long/Short Ratios**: Account-level and position-level long/short ratios (`/futures/data/globalLongShortAccountRatio`, `/futures/data/topLongShortPositionRatio`) updated periodically. Free.
  - **Heatmaps**: Binance does not natively provide visual order book liquidation heatmaps via public REST endpoints, but order book depth snapshots can be queried to construct local depth walls.

- **Bybit V5 API**:
  - **Open Interest**: `/v5/market/open-interest` supports historical interval queries (5m, 15m, 30m, 1h, 4h, 1d). Free.
  - **Funding Rates**: `/v5/market/funding/history` provides historical funding rate records. Free.
  - **Liquidation Volumes**: `/v5/market/liquidation` provides recent public liquidation history (symbol, side, size, price). Free.
  - **Long/Short Ratios**: `/v5/market/account-ratio` gives historical global and top trader account ratios. Free.
  - **Heatmaps**: Not provided natively via API.

- **OKX V5 API**:
  - **Open Interest**: `/api/v5/public/open-interest` provides current and historical OI. Free.
  - **Funding Rates**: `/api/v5/public/funding-rate-history` provides historical funding rates. Free.
  - **Liquidation Volumes**: `/api/v5/public/liquidation-orders` returns historical liquidation orders across instruments. Free.
  - **Long/Short Ratios**: `/api/v5/rubik/stat/market/long-short-account-ratio` provides historical sentiment metrics. Free.
  - **Heatmaps**: Not provided natively via API.

- **Coinglass API & Web**:
  - **Aggregated Data**: Coinglass aggregates OI, funding, and liquidations across all major exchanges. However, their granular historical liquidation history and historical heatmaps require a paid tier (Enterprise/API keys range from $100+/month). For a free-first approach, we can directly ingest and aggregate raw REST/WebSocket feeds from Binance, Bybit, and OKX rather than relying on Coinglass paid APIs.

---

## 2. The Signal: Liquidation Cascade Trigger
The strategy seeks to fade over-leveraged retail and momentum crowds when positions become so crowded that a minor price reversal triggers a self-reinforcing liquidation cascade. 

### Precise Trigger Conditions (Short Fade of Long Squeeze):
1. **Funding Rate Extreme**: 8-hour funding rate across Binance/Bybit/OKX averages $\ge +0.10\%$ (annualized $>100\%$), indicating aggressive long leverage paying heavy carry.
2. **Open Interest Expansion**: Total Open Interest in USD terms has expanded by $\ge +15\%$ over the preceding 48 hours, confirming that new leveraged capital (rather than spot buying) is driving the advance.
3. **Top Trader vs. Retail Divergence**: Top trader long/short account ratio is $\le 0.8$ (smart money short/hedged) while retail account ratio is $\ge 2.0$ (crowd heavily long).
4. **Proximity to Liquidation Cluster**: Spot/Perp price is within $0.5\%$ of a dense structural liquidation wall (calculated via cumulative exchange order book depth or estimated via recent high-volume consolidation nodes where leveraged breakouts occurred).

### Entry Execution:
When all four conditions align, enter a short position at market. Conversely, mirror conditions apply for fading a short squeeze (funding $\le -0.10\%$, OI spike, retail short, price near heavy short liquidation wall).

---

## 3. The Cascade Exit
Cascades are violent, non-linear events. Holding too long turns a high-edge fade into a momentum trap. Exit conditions must be mechanical and fast:

1. **Open Interest Purge (Primary Exit)**: Exit when Open Interest drops by $\ge 8\%$ from its peak within a 4-hour window. A rapid drop in OI indicates that the leveraged cascade has flushed out the weak hands and forced liquidations are complete.
2. **Funding Normalization**: Exit when the weighted funding rate reverts from extreme levels back toward neutral ($| \text{Funding} | < 0.01\%$).
3. **Time-Based Stop / Exhaustion**: If the cascade does not materialize and liquidate open interest within 6 hours of entry, time-out and close the position to avoid carrying toxic carry costs.
4. **Hard Stop-Loss**: Maximum adverse excursion stop set at $1.5\%$ against the position (above the local liquidation cluster breakout level).

---

## 4. Backtest Feasibility
- **Is it backtestable for free?** **Partially, with caveats.**
  - **Binance Futures Data Archive**: Binance provides public historical daily and monthly CSV data for funding rates, open interest (aggregated), and klines via `data.binance.vision`. However, tick-level or minute-level historical liquidation order logs (`forceOrder`) are **not** provided as bulk free historical downloads by Binance or Bybit.
  - **Open Interest & Funding**: Easily backtestable historically using daily/hourly REST archives from Binance/Bybit.
  - **Liquidation Cascades**: True historical tick-level liquidation volume backtesting requires either recording live WebSocket streams over several months or purchasing Coinglass/Skew historical tick feeds. Therefore, an initial backtest must rely on proxy signals (Funding Rate extremes + OI expansions + volatility breakouts) rather than exact historical liquidation order book prints, unless built via forward-testing / live paper trading.

---

## 5. The Counterparty
- **Who is on the losing side?** 
  - **Retail Momentum Chasers & High-Leverage Margin Traders**: Speculators using 20x to 100x leverage on centralized exchanges (Binance, Bybit, OKX) who enter breakouts late, driven by FOMO and social media sentiment.
- **Why do they keep showing up?**
  - **Asymmetric Psychological Bias**: Retail traders suffer from lottery-ticket preference, anchoring bias, and loss aversion. They add margin to losing positions ("grid trading" or "averaging down") rather than cutting losses.
  - **Structural Incentive Design**: Exchange fee structures, high leverage availability, and perpetual swap funding mechanisms encourage aggressive directional speculation without expiration dates, ensuring a continuous supply of fresh, vulnerable liquidity.
