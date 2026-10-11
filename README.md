# Crypto Alpha Strategies

A collection of quantitative research strategies for crypto markets, including Time-Series Momentum (TSMOM) and Liquidation Signal generation.

## Modules
- **`tsmom_strategy/`**: A Time-Series Momentum backtesting engine. Includes a full post-mortem analysis and performance results.
- **`liquidation_strategy/`**: A live signal logger designed to capture liquidation cascades, complete with daily logging and research memos.
- **`rules.md`**: Project governance and strategy rules.

## How to Run
1. Navigate to the desired strategy folder.
2. Install dependencies: `pip install -r ../requirements.txt`
3. Run the backtest: `python backtest_tsmom.py` (for TSMOM) or `python signal_logger.py` (for Liquidation).