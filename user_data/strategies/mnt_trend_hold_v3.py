"""
MNT Trend Hold V3 Strategy
MNT 趋势持有策略 V3 版本

历史回测表现: +293.68% (2024-2025)

核心特点:
1. EMA 多周期趋势跟踪 (20/50/100)
2. 回踩买入策略
3. 宽松追踪止盈 (10% 回撤, 15% 激活)
4. 阶梯式利润保护
"""

from __future__ import annotations

from functools import reduce
from typing import Any, Optional

import pandas as pd
from pandas import DataFrame

import talib.abstract as ta
from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy


class MntTrendHoldV3Strategy(IStrategy):
    """
    MNT 趋势持有策略 V3
    
    专为 MNT 优化的趋势跟踪策略
    回测收益: +293.68% (2024-2025)
    """

    INTERFACE_VERSION = 3

    # 基础配置
    timeframe = "1h"
    can_short = False
    process_only_new_candles = True
    startup_candle_count = 200

    # 止损配置
    stoploss = -0.12                    # 固定止损 12%
    use_custom_stoploss = True          # 使用自定义止损
    minimal_roi = {"0": 0.80}           # 80% 止盈（基本不触发）

    # 追踪止盈配置 - V3 核心改动
    trailing_stop = True
    trailing_stop_positive = 0.10       # 从高点回撤 10% 触发
    trailing_stop_positive_offset = 0.15  # 盈利 15% 后激活
    trailing_only_offset_is_reached = True

    # 出场信号
    use_exit_signal = True
    exit_profit_only = False

    # EMA 参数
    ema_fast = 20
    ema_slow = 50
    ema_trend = 100

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """计算技术指标"""
        # EMA 指标
        dataframe["ema20"] = ta.EMA(dataframe, timeperiod=self.ema_fast)
        dataframe["ema50"] = ta.EMA(dataframe, timeperiod=self.ema_slow)
        dataframe["ema100"] = ta.EMA(dataframe, timeperiod=self.ema_trend)
        
        # RSI
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        
        # ATR (波动率)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)

        # 上升趋势判断: 快线 > 慢线 > 趋势线，价格在快线上方
        dataframe["uptrend"] = (
            (dataframe["ema20"] > dataframe["ema50"]) &
            (dataframe["ema50"] > dataframe["ema100"]) &
            (dataframe["close"] > dataframe["ema20"])
        )

        # 趋势斜率 (10根K线变化率)
        dataframe["ema50_slope"] = (
            dataframe["ema50"] - dataframe["ema50"].shift(10)
        ) / dataframe["ema50"].shift(10) * 100

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """入场信号 - 严格条件"""
        conditions = [
            # 趋势确认
            dataframe["uptrend"],
            
            # 趋势动能 > 0.5%
            dataframe["ema50_slope"] > 0.5,
            
            # 回踩买入: 最低价触及 EMA20 附近 (容忍 2%)
            dataframe["low"] <= dataframe["ema20"] * 1.02,
            
            # 收盘价仍在 EMA20 上方
            dataframe["close"] > dataframe["ema20"],
            
            # RSI 过滤
            dataframe["rsi"] < 70,  # 不追高
            dataframe["rsi"] > 40,  # 不抄底
        ]

        valid = dataframe["ema20"].notna() & dataframe["rsi"].notna()
        dataframe.loc[reduce(lambda x, y: x & y, conditions) & valid, "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """出场信号 - 趋势破坏"""
        # 连续两根K线收于 EMA100 下方
        dataframe.loc[
            (dataframe["close"] < dataframe["ema100"]) &
            (dataframe["close"].shift(1) < dataframe["ema100"].shift(1)),
            "exit_long"
        ] = 1
        return dataframe

    def custom_stoploss(
        self, 
        pair: str, 
        trade: Trade, 
        current_time: pd.Timestamp,
        current_rate: float, 
        current_profit: float, 
        **kwargs: Any
    ) -> Optional[float]:
        """
        阶梯式利润保护
        
        盈利越高，锁定的利润越多
        """
        # 50% 利润 → 锁定 40%
        if current_profit >= 0.50:
            return -(current_profit - 0.40)
        
        # 30% 利润 → 锁定 20%
        if current_profit >= 0.30:
            return -(current_profit - 0.20)
        
        # 20% 利润 → 锁定 10%
        if current_profit >= 0.20:
            return -(current_profit - 0.10)
        
        # 10% 利润 → 锁定 5%
        if current_profit >= 0.10:
            return -(current_profit - 0.05)
        
        # 5% 利润 → 锁定 1%
        if current_profit >= 0.05:
            return -(current_profit - 0.01)
        
        # 未盈利，使用固定止损
        return self.stoploss
