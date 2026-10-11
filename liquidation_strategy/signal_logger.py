import os, requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

def fetch_binance_complete_data(symbol='BTCUSDT'):
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1h&limit=720"
        res = requests.get(url, timeout=15).json()
        if not isinstance(res, list) or len(res) == 0: return pd.DataFrame()
        df = pd.DataFrame(res, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['close'] = df['close'].astype(float)
        df['timestamp'] = pd.to_datetime(df['close_time'], unit='ms')
        oi_url = f"https://fapi.binance.com/futures/data/openInterestHist?symbol={symbol}&period=1h&limit=500"
        oi_res = requests.get(oi_url, timeout=15).json()
        if isinstance(oi_res, list) and len(oi_res) > 0:
            df_oi = pd.DataFrame(oi_res)
            df_oi['sumOpenInterest'] = df_oi['sumOpenInterest'].astype(float)
            df_oi['timestamp'] = pd.to_datetime(df_oi['timestamp'], unit='ms')
            df = pd.merge_asof(df.sort_values('timestamp'), df_oi[['timestamp', 'sumOpenInterest']].sort_values('timestamp'), on='timestamp', direction='nearest')
        fund_url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit=1000"
        fund_res = requests.get(fund_url, timeout=15).json()
        if isinstance(fund_res, list) and len(fund_res) > 0:
            df_fund = pd.DataFrame(fund_res)
            df_fund['fundingRate'] = df_fund['fundingRate'].astype(float)
            df_fund['timestamp'] = pd.to_datetime(df_fund['fundingTime'], unit='ms')
            df = pd.merge_asof(df.sort_values('timestamp'), df_fund[['timestamp', 'fundingRate']].sort_values('timestamp'), on='timestamp', direction='backward')
        top_url = f"https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol={symbol}&period=1h&limit=500"
        top_res = requests.get(top_url, timeout=15).json()
        if isinstance(top_res, list) and len(top_res) > 0:
            df_top = pd.DataFrame(top_res)
            df_top['top_ratio'] = df_top['longShortRatio'].astype(float)
            df_top['timestamp'] = pd.to_datetime(df_top['timestamp'], unit='ms')
            df = pd.merge_asof(df.sort_values('timestamp'), df_top[['timestamp', 'top_ratio']].sort_values('timestamp'), on='timestamp', direction='nearest')
        global_url = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period=1h&limit=500"
        global_res = requests.get(global_url, timeout=15).json()
        if isinstance(global_res, list) and len(global_res) > 0:
            df_global = pd.DataFrame(global_res)
            df_global['retail_ratio'] = df_global['longShortRatio'].astype(float)
            df_global['timestamp'] = pd.to_datetime(df_global['timestamp'], unit='ms')
            df = pd.merge_asof(df.sort_values('timestamp'), df_global[['timestamp', 'retail_ratio']].sort_values('timestamp'), on='timestamp', direction='nearest')
        return df.fillna(method='ffill')
    except: return pd.DataFrame()

def run_evaluation():
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    all_signals = []
    symbol_dfs = {}
    for sym in symbols:
        df = fetch_binance_complete_data(sym)
        if not df.empty and len(df) > 168:
            df['oi_chg_4h'] = df['sumOpenInterest'].pct_change(4) * 100
            df['oi_change_24h'] = df['sumOpenInterest'].pct_change(24) * 100
            symbol_dfs[sym] = df
    pos_active_until = {sym: pd.Timestamp(0) for sym in symbols}
    concurrent_positions = []
    sets = [set(df['timestamp']) for df in symbol_dfs.values()]
    all_ts = sorted(list(set().union(*sets)))
    for ts in all_ts:
        active = 0
        for sym, until in pos_active_until.items():
            if ts <= until: active += 1
        concurrent_positions.append(active)
        for sym, df in symbol_dfs.items():
            if ts <= pos_active_until[sym]: continue
            row_match = df[df['timestamp'] == ts]
            if row_match.empty: continue
            row = row_match.iloc[0]
            idx = row_match.index[0]
            if idx < 168 or idx >= len(df) - 24: continue
            window = df.iloc[idx-168 : idx]
            acc = window[window['oi_chg_4h'] > 2.0]
            cluster = acc['close'].mean() if not acc.empty else row['close']
            dist = abs(row['close'] - cluster) / row['close']
            if (row['fundingRate'] >= 0.001 and row['oi_change_24h'] >= 15.0 and row['top_ratio'] <= 0.8 and row['retail_ratio'] >= 2.0 and dist <= 0.005): signal = 'LONG_SQUEEZE_FADE'
            elif (row['fundingRate'] <= -0.001 and row['oi_change_24h'] >= 15.0 and row['top_ratio'] >= 1.2 and row['retail_ratio'] <= 0.5 and dist <= 0.005): signal = 'SHORT_SQUEEZE_FADE'
            else: continue
            fut = df.iloc[idx+1 : idx+25]
            if len(fut) < 24: continue
            casc = (fut['sumOpenInterest'].pct_change() <= -0.08).any()
            pnl = ((fut.iloc[-1]['close'] - row['close']) / row['close'] * 100) if signal == 'SHORT_SQUEEZE_FADE' else ((row['close'] - fut.iloc[-1]['close']) / row['close'] * 100)
            pos_active_until[sym] = fut.iloc[-1]['timestamp']
            all_signals.append({'ts': ts, 'sym': sym, 'sig': signal, 'pnl': pnl, 'casc': casc})
    df_sig = pd.DataFrame(all_signals)
    df_sig.to_csv('liquidation_strategy/signals_log.csv', index=False)
    count, casc = len(df_sig), (df_sig['casc'].sum() if not df_sig.empty else 0)
    pnl = df_sig['pnl'].mean() if not df_sig.empty else 0
    max_pos = max(concurrent_positions) if concurrent_positions else 0
    with open('liquidation_strategy/DAILY_LOG.md', 'w') as f:
        f.write(f"# Results: {count} signals, {casc} cascades, {pnl:.2f}% avg pnl, {max_pos} max concurrency.")

if __name__ == '__main__': run_evaluation()
