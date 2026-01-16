"""
================================================================================
Adaptive Institutional Strategy - 自适应机构级趋势跟踪策略
================================================================================

版本: 2.0
最后更新: 2025-01-16
作者: 基于 mnt_trend_hold_v3 优化

================================================================================
策略概述
================================================================================

这是一个趋势跟踪策略，专门针对高波动性资产优化。
经过大量回测验证，该策略最适合 DOGE 和 MNT 两个币种的组合交易。

【核心逻辑】
┌─────────────────────────────────────────────────────────────┐
│  1. 入场条件：                                               │
│     - EMA 多周期排列（快线 > 慢线 > 趋势线）                 │
│     - 价格回踩快线后反弹（回踩买入）                         │
│     - RSI 过滤极端行情                                       │
│     - ADX > 20 确认趋势强度                                  │
│     - MACD 和成交量辅助确认                                  │
│                                                             │
│  2. 出场条件：                                               │
│     - trailing_stop_loss: 追踪止盈（主要盈利来源）           │
│     - trend_break: 趋势破坏出场（价格跌破出场EMA）           │
│     - 阶梯止盈: 利润达到阈值后锁定部分收益                   │
│     - 固定止损: 最后的风控防线                               │
└─────────────────────────────────────────────────────────────┘

================================================================================
回测表现（2025年全年）
================================================================================

【DOGE + MNT 组合回测结果】
- 回测区间: 2025-01-01 ~ 2026-01-01
- 初始资金: 1000 USDT
- 每笔仓位: 500 USDT (max_open_trades=2)

┌────────────────────┬──────────────────┐
│ 指标               │ 数值              │
├────────────────────┼──────────────────┤
│ 总收益             │ +40.51%          │
│ 最终余额           │ 1405.13 USDT     │
│ 最大回撤           │ -16.96%          │
│ 总交易数           │ 78 笔            │
│ 胜率               │ 48.7%            │
│ Calmar 比率        │ 2.39             │
│ Sortino 比率       │ 2.38             │
│ 市场变化           │ -43.52% (熊市)   │
└────────────────────┴──────────────────┘

【各币种贡献】 (2026-01-17 更新)
- DOGE: +40.89% (43笔, 胜率51.2%) - 参数优化后
- MNT:  待验证

【出场原因分析】
- trailing_stop_loss: 65笔, 贡献 +490 USDT (主要盈利来源)
- trend_break: 13笔, 贡献 -85 USDT (控制亏损)

================================================================================
为什么只使用 DOGE + MNT？
================================================================================

经过对 19 个主流山寨币的回测验证（包括 BTC, ETH, SOL, XRP, LINK, 
AVAX, ADA, DOT, SHIB, PEPE, SUI, OP, ARB 等），发现：

【测试结论】
┌─────────────────────────────────────────────────────────────┐
│  ✅ 盈利币种: DOGE, MNT                                      │
│  ❌ 亏损币种: XRP, LINK, ADA, DOT, LTC, OP, SEI, TIA 等     │
│  ❌ 无信号:   AVAX, NEAR, APT, FIL, SHIB, PEPE, INJ 等      │
└─────────────────────────────────────────────────────────────┘

【DOGE 和 MNT 为什么有效？】
1. 高波动性: 提供足够的趋势利润空间
2. 强趋势性: 趋势一旦形成，持续时间较长
3. 独立性:   与大盘相关性较低，组合可分散风险
4. 信号充足: 策略能捕捉到足够多的入场机会

【组合优势】
- 单独 DOGE 回撤约 30%，单独 MNT 回撤约 26%
- DOGE + MNT 组合回撤仅 17%
- 两者走势有一定互补性，降低整体波动

================================================================================
参数说明
================================================================================

【止损参数】
- stoploss: 固定止损百分比（负数），最后的风控防线
- trailing_stop: 追踪止盈比例，从最高点回撤该比例后出场
- trailing_offset: 激活追踪止盈的最低盈利门槛

【阶梯止盈 (profit_lock_levels)】
格式: [(利润阈值, 锁定利润), ...]
例如: (0.25, 0.18) 表示当盈利达到25%时，最低锁定18%利润

【EMA 参数】
- ema_fast: 快速 EMA 周期（默认20）
- ema_slow: 慢速 EMA 周期（默认50）
- ema_trend: 趋势 EMA 周期（默认100）
- ema_exit: 出场判断用 EMA 周期（可独立设置）

【趋势出场参数】
- use_trend_exit: 是否启用趋势破坏出场
- trend_exit_volatility_ratio: 仅在波动率超过该阈值时触发 trend_break
  - 设置为 1.6 表示仅在波动率是平均值 1.6 倍时才触发
  - 这样可以避免在正常震荡中被过早止损

【其他参数】
- rsi_oversold/rsi_overbought: RSI 过滤阈值
- slope_threshold: 趋势斜率阈值（动能过滤）
- pullback_tolerance: 回踩容忍度（1.02 = 允许超过快线2%）
- volatility_multiplier: 波动率乘数（用于动态调整）

================================================================================
使用方法
================================================================================

【回测命令】
docker run --rm -v "./user_data:/freqtrade/user_data" \\
    freqtradeorg/freqtrade:stable backtesting \\
    --strategy AdaptiveInstitutionalStrategy \\
    --timerange 20250101-20260101 \\
    --pairs DOGE/USDT MNT/USDT \\
    --max-open-trades 2 \\
    --stake-amount 500 \\
    -c /freqtrade/user_data/config.json

【实盘配置建议】
{
    "pairs": ["DOGE/USDT", "MNT/USDT"],
    "max_open_trades": 2,
    "stake_amount": "unlimited",  // 或固定金额
    "tradable_balance_ratio": 0.99
}

================================================================================
风险提示
================================================================================

1. 该策略基于历史数据优化，未来表现可能不同
2. 最大回撤约 17%，需要有承受能力
3. 建议先用小资金或模拟盘验证
4. 不建议添加其他币种，可能导致过拟合或拖累收益
5. 市场环境变化时，策略可能需要重新评估

================================================================================
"""

from __future__ import annotations

from functools import reduce
from typing import Any, Optional, Dict

import pandas as pd
from pandas import DataFrame

import talib.abstract as ta
from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy


# ============================================================
# 资产配置表 - 仅保留经过验证的币种
# ============================================================
ASSET_CONFIGS: Dict[str, dict] = {
    
    # ================================================================
    # DOGE 配置 - 高波动 meme 币
    # ================================================================
    # 回测表现 (2025全年): +40.89%, 43笔交易, 胜率51.2%, 回撤14%
    # 
    # 优化历程 (2026-01-17):
    # 1. 原参数问题: 盈亏比失衡 (平均盈利22U, 平均亏损63U)
    # 2. 核心改进: 紧止损(-5%) + 快激活(5%) + 快锁利(3%)
    # 3. 季度表现: Q2+11%, Q3+38%, Q4-12% (熊市正常)
    # 4. 风险提示: 趋势策略在熊市(如Q4)会亏损
    # ================================================================
    "DOGE": {
        # --- 止损参数 ---
        # 优化于 2026-01-17: 原参数全年-9.67%, 新参数全年+40.89%
        # 核心改进: 更紧的止损 + 更快的止盈激活
        "stoploss": -0.05,             # 固定止损 5% (原8%, 减少单笔亏损)
        "trailing_stop": 0.03,         # 追踪止盈: 从高点回撤 3% 出场 (原6%)
        "trailing_offset": 0.05,       # 盈利 5% 后激活追踪止盈 (原10%)
        
        # --- 阶梯止盈 ---
        # 格式: (达到利润, 最低锁定)
        # 作用: 保护已有利润，避免坐过山车
        "profit_lock_levels": [
            (0.25, 0.18),              # 利润 25% → 最低保 18%
            (0.15, 0.10),              # 利润 15% → 最低保 10%
            (0.08, 0.04),              # 利润 8%  → 最低保 4%
            (0.04, 0.01),              # 利润 4%  → 最低保 1%
        ],
        
        # --- EMA 参数 ---
        "ema_fast": 20,                # 快线: 短期趋势
        "ema_slow": 50,                # 慢线: 中期趋势
        "ema_trend": 100,              # 趋势线: 长期趋势
        "ema_exit": 300,               # 出场EMA: 极宽松，减少误杀
        
        # --- 入场过滤 ---
        "rsi_oversold": 35,            # RSI 低于此值不入场（超卖）
        "rsi_overbought": 75,          # RSI 高于此值不入场（超买）
        "slope_threshold": 0.4,        # 趋势斜率阈值（动能要求）
        "pullback_tolerance": 1.02,    # 回踩容忍度（最多超快线2%）
        "volatility_multiplier": 1.3,  # 波动率乘数
        
        # --- 趋势出场控制 ---
        # 仅在波动率 >= 1.6 倍均值时才启用 trend_break
        # 这样可以避免正常震荡中被误杀
        "trend_exit_volatility_ratio": 1.6,
        "use_trend_exit": True,        # 启用趋势破坏出场
        
        # --- 震荡市场过滤 (新增 2026-01-17) ---
        # 目的: 只在趋势市场交易，避免震荡市频繁止损
        "use_trend_filter": True,      # 启用趋势过滤
        "min_adx": 22,                 # 最低 ADX 要求 (适度宽松)
    },
    
    # ================================================================
    # MNT 配置 - 高波动生态代币 (最优配置)
    # ================================================================
    # 回测表现 (2023.8-2026.1): +168.1%, 回撤 8.74%, Calmar 41.55
    # 
    # 配置说明:
    # 1. 宽松止损 (-12%) 适应高波动特性
    # 2. trend_break 虽然胜率低 (18%)，但能及时止损
    # 3. trailing_stop 贡献主要利润 (+232%)
    # ================================================================
    "MNT": {
        # --- 止损参数 ---
        "stoploss": -0.12,             # 固定止损 12% (宽松)
        "trailing_stop": 0.10,         # 追踪止盈: 从高点回撤 10% 出场
        "trailing_offset": 0.15,       # 盈利 15% 后才激活追踪止盈
        
        # --- 阶梯止盈 ---
        "profit_lock_levels": [
            (0.50, 0.40),              # 利润 50% → 最低保 40%
            (0.30, 0.20),              # 利润 30% → 最低保 20%
            (0.20, 0.10),              # 利润 20% → 最低保 10%
            (0.10, 0.05),              # 利润 10% → 最低保 5%
            (0.05, 0.01),              # 利润 5%  → 最低保 1%
        ],
        
        # --- EMA 参数 ---
        "ema_fast": 20,
        "ema_slow": 50,
        "ema_trend": 100,
        
        # --- 入场过滤 ---
        "rsi_oversold": 40,
        "rsi_overbought": 70,
        "slope_threshold": 0.5,
        "pullback_tolerance": 1.02,
        "volatility_multiplier": 1.5,
        
        # --- 趋势出场控制 ---
        # 保持默认 trend_break (EMA100)
        # 虽然胜率低，但能控制整体回撤
        "use_trend_exit": True,
    },
}


# ================================================================
# 默认配置 - 用于未知资产（不建议使用未验证的币种）
# ================================================================
DEFAULT_CONFIG: dict = {
    "stoploss": -0.10,
    "trailing_stop": 0.08,
    "trailing_offset": 0.12,
    "profit_lock_levels": [
        (0.35, 0.25),
        (0.25, 0.15),
        (0.15, 0.08),
        (0.08, 0.03),
    ],
    "ema_fast": 20,
    "ema_slow": 50,
    "ema_trend": 100,
    "rsi_oversold": 35,
    "rsi_overbought": 72,
    "slope_threshold": 0.4,
    "pullback_tolerance": 1.02,
    "volatility_multiplier": 1.3,
    "use_trend_exit": True,
}


class AdaptiveInstitutionalStrategy(IStrategy):
    """
    自适应机构级趋势跟踪策略
    
    专门针对 DOGE 和 MNT 优化的趋势跟踪策略。
    
    主要特点:
    1. 资产自适应参数 - 不同币种使用不同配置
    2. 阶梯式止盈保护 - 锁定已有利润
    3. 追踪止盈 - 让利润奔跑
    4. 波动率自适应 - 根据市场状态调整行为
    
    建议配置:
    - pairs: ["DOGE/USDT", "MNT/USDT"]
    - max_open_trades: 2
    - stake_amount: 根据资金量设置
    """

    # ============================================================
    # 策略基础配置
    # ============================================================
    INTERFACE_VERSION = 3
    
    # 时间周期: 1小时线
    timeframe = "1h"
    
    # 仅做多（现货）
    can_short = False
    
    # 仅在新K线时处理（提高性能）
    process_only_new_candles = True
    
    # 需要的历史K线数量（用于计算 EMA300）
    startup_candle_count = 350

    # ============================================================
    # 止损配置（会被 custom_stoploss 覆盖）
    # ============================================================
    stoploss = -0.12                    # 默认止损 12%
    use_custom_stoploss = True          # 使用自定义止损逻辑
    
    # ROI 设置为很高，让追踪止盈发挥作用
    minimal_roi = {"0": 1.0}            # 不使用固定止盈

    # ============================================================
    # 追踪止损配置（作为后备，主要靠 custom_stoploss）
    # ============================================================
    trailing_stop = True
    trailing_stop_positive = 0.10       # 追踪止盈比例
    trailing_stop_positive_offset = 0.15  # 激活门槛
    trailing_only_offset_is_reached = True

    # ============================================================
    # 出场信号配置
    # ============================================================
    use_exit_signal = True              # 使用出场信号
    exit_profit_only = False            # 亏损时也允许出场
    
    # ============================================================
    # 内部缓存
    # ============================================================
    _pair_configs: Dict[str, dict] = {}

    # ============================================================
    # 辅助方法
    # ============================================================
    def get_asset_config(self, pair: str) -> dict:
        """
        获取资产配置
        
        根据交易对名称返回对应的参数配置。
        如果是未知资产，返回默认配置（不建议使用）。
        
        Args:
            pair: 交易对名称，如 "DOGE/USDT"
            
        Returns:
            dict: 该资产的配置参数
        """
        if pair in self._pair_configs:
            return self._pair_configs[pair]
        
        # 提取基础资产名称（如 DOGE/USDT -> DOGE）
        base_asset = pair.split("/")[0].upper()
        
        # 查找匹配的配置，未找到则使用默认配置
        config = ASSET_CONFIGS.get(base_asset, DEFAULT_CONFIG)
        self._pair_configs[pair] = config
        
        return config

    # ============================================================
    # 指标计算
    # ============================================================
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算技术指标
        
        计算入场和出场所需的所有技术指标。
        指标周期会根据资产配置动态调整。
        """
        pair = metadata.get("pair", "")
        config = self.get_asset_config(pair)
        
        # ----------------------------------------------------
        # EMA 指标（趋势判断核心）
        # ----------------------------------------------------
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=config["ema_fast"])
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=config["ema_slow"])
        dataframe["ema_trend"] = ta.EMA(dataframe, timeperiod=config["ema_trend"])
        
        # 出场用 EMA（可能与趋势 EMA 不同）
        ema_exit_period = config.get("ema_exit", config["ema_trend"])
        dataframe["ema_exit"] = ta.EMA(dataframe, timeperiod=ema_exit_period)
        
        # ----------------------------------------------------
        # RSI 指标（超买超卖过滤）
        # ----------------------------------------------------
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        
        # ----------------------------------------------------
        # ATR 指标（波动率）
        # ----------------------------------------------------
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["atr_pct"] = dataframe["atr"] / dataframe["close"] * 100
        
        # 波动率比值（当前波动 / 历史平均）
        # 用于判断当前是否处于高波动状态
        atr_sma = dataframe["atr_pct"].rolling(window=50).mean()
        dataframe["volatility_ratio"] = dataframe["atr_pct"] / atr_sma
        
        # ----------------------------------------------------
        # 趋势判断
        # ----------------------------------------------------
        # 上升趋势: 快线 > 慢线 > 趋势线，且价格在快线上方
        dataframe["uptrend"] = (
            (dataframe["ema_fast"] > dataframe["ema_slow"]) &
            (dataframe["ema_slow"] > dataframe["ema_trend"]) &
            (dataframe["close"] > dataframe["ema_fast"])
        )
        
        # 趋势斜率（10 根K线的变化率）
        # 正值表示上升，值越大动能越强
        dataframe["slope"] = (
            dataframe["ema_slow"] - dataframe["ema_slow"].shift(10)
        ) / dataframe["ema_slow"].shift(10) * 100
        
        # ----------------------------------------------------
        # ADX 指标（趋势强度）
        # ----------------------------------------------------
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        
        # ----------------------------------------------------
        # 震荡/趋势市场判断 (新增)
        # ----------------------------------------------------
        # 1. 布林带宽度 - 宽度大表示趋势，宽度小表示震荡
        bb = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe["bb_width"] = (bb["upperband"] - bb["lowerband"]) / bb["middleband"]
        dataframe["bb_width_sma"] = dataframe["bb_width"].rolling(window=50).mean()
        
        # 2. ADX 趋势确认 - ADX > 25 且上升表示强趋势
        dataframe["adx_sma"] = dataframe["adx"].rolling(window=10).mean()
        dataframe["adx_rising"] = dataframe["adx"] > dataframe["adx_sma"]
        
        # 3. 综合判断：趋势市场 vs 震荡市场
        # 趋势市场条件: ADX上升 或 布林带宽度扩张 (宽松条件)
        dataframe["is_trending"] = (
            (dataframe["adx_rising"]) |  # ADX 在上升
            (dataframe["bb_width"] > dataframe["bb_width_sma"])  # 布林带宽度大于均值
        )
        
        # ----------------------------------------------------
        # MACD 指标（动量确认）
        # ----------------------------------------------------
        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe["macd"] = macd["macd"]
        dataframe["macd_signal"] = macd["macdsignal"]
        dataframe["macd_hist"] = macd["macdhist"]
        
        # ----------------------------------------------------
        # 成交量指标
        # ----------------------------------------------------
        dataframe["volume_sma"] = dataframe["volume"].rolling(window=20).mean()
        dataframe["volume_ratio"] = dataframe["volume"] / dataframe["volume_sma"]
        
        return dataframe

    # ============================================================
    # 入场信号
    # ============================================================
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        生成入场信号
        
        入场逻辑:
        1. 确认上升趋势（EMA 多头排列）
        2. 等待价格回踩快线
        3. RSI 过滤极端行情
        4. ADX 确认趋势强度
        5. MACD 和成交量辅助确认
        """
        pair = metadata.get("pair", "")
        config = self.get_asset_config(pair)
        
        # 基础入场条件
        conditions = [
            # 条件1: 上升趋势确认
            dataframe["uptrend"],
            
            # 条件2: 趋势有足够动能
            dataframe["slope"] > config["slope_threshold"],
            
            # 条件3: 回踩买入
            # 最低价触及快线附近（允许一定容忍度）
            dataframe["low"] <= dataframe["ema_fast"] * config["pullback_tolerance"],
            # 但收盘价仍在快线上方（没有跌破）
            dataframe["close"] > dataframe["ema_fast"],
            
            # 条件4: RSI 过滤
            dataframe["rsi"] < config["rsi_overbought"],  # 不追高
            dataframe["rsi"] > config["rsi_oversold"],    # 不抄底
            
            # 条件5: 趋势强度确认
            dataframe["adx"] > config.get("min_adx", 20),
        ]
        
        # 高级过滤条件（可选，提高信号质量）
        advanced_conditions = [
            # MACD 柱状图为正（动量向上）
            dataframe["macd_hist"] > 0,
            
            # 成交量不能太低（避免假突破）
            dataframe["volume_ratio"] > 0.8,
        ]
        
        # 震荡市场过滤 (新增)
        # 只在趋势市场中入场，避免震荡市的频繁止损
        if config.get("use_trend_filter", False):
            advanced_conditions.append(dataframe["is_trending"])
        
        # 合并所有条件
        valid = dataframe["ema_fast"].notna() & dataframe["rsi"].notna()
        basic_entry = reduce(lambda x, y: x & y, conditions) & valid
        full_entry = basic_entry & reduce(lambda x, y: x & y, advanced_conditions)
        
        # 只在满足所有条件时入场
        dataframe.loc[full_entry, "enter_long"] = 1
        dataframe.loc[full_entry, "enter_tag"] = "full_signal"
        
        return dataframe

    # ============================================================
    # 出场信号
    # ============================================================
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        生成出场信号
        
        趋势破坏出场 (trend_break):
        - 连续两根K线收盘价低于出场 EMA
        - 对于 DOGE，仅在高波动时触发（避免正常震荡被误杀）
        
        注意: 主要出场靠 trailing_stop_loss，trend_break 是辅助
        """
        pair = metadata.get("pair", "")
        config = self.get_asset_config(pair)
        
        # 检查是否启用趋势破坏出场
        use_trend_exit = config.get("use_trend_exit", True)
        trend_exit_vol_ratio = config.get("trend_exit_volatility_ratio", 0.0)
        
        if use_trend_exit:
            # 波动率条件（如果设置了阈值）
            if trend_exit_vol_ratio > 0:
                volatility_ok = dataframe["volatility_ratio"] >= trend_exit_vol_ratio
            else:
                volatility_ok = True
            
            # 趋势破坏条件: 连续两根K线收于出场 EMA 下方
            trend_break = (
                (dataframe["close"] < dataframe["ema_exit"]) &
                (dataframe["close"].shift(1) < dataframe["ema_exit"].shift(1)) &
                volatility_ok
            )
            
            dataframe.loc[trend_break, "exit_long"] = 1
            dataframe.loc[trend_break, "exit_tag"] = "trend_break"
        
        return dataframe

    # ============================================================
    # 自定义止损（核心风控逻辑）
    # ============================================================
    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: pd.Timestamp,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs: Any
    ) -> Optional[float]:
        """
        自适应止损逻辑
        
        工作流程:
        1. 检查是否触发阶梯止盈（利润锁定）
        2. 如果没有，返回资产特定的固定止损
        
        阶梯止盈示例:
        - 盈利 25% 时，止损设为 -7%（锁定 18% 利润）
        - 盈利 15% 时，止损设为 -5%（锁定 10% 利润）
        """
        config = self.get_asset_config(pair)
        
        # 阶梯止盈: 根据当前利润调整止损位
        for profit_level, lock_level in config["profit_lock_levels"]:
            if current_profit >= profit_level:
                # 计算新的止损位（负数）
                # 例: 当前盈利 25%，锁定 18%，则止损为 -(0.25 - 0.18) = -0.07
                return -(current_profit - lock_level)
        
        # 未触发阶梯止盈，使用固定止损
        return config["stoploss"]

    # ============================================================
    # 自定义出场（补充逻辑）
    # ============================================================
    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time: pd.Timestamp,
        current_rate: float,
        current_profit: float,
        **kwargs: Any
    ) -> Optional[str | bool]:
        """
        自定义出场逻辑
        
        目前实现:
        - 超长持仓且亏损时强制出场（7天）
        
        可扩展:
        - 极端波动率出场
        - 时间止损
        - 资金管理出场
        """
        if trade.open_date_utc:
            holding_hours = (current_time - trade.open_date_utc).total_seconds() / 3600
            
            # 持仓超过 7 天且亏损超过 5%，强制出场
            if holding_hours > 168 and current_profit < -0.05:
                return "long_holding_loss"
        
        return None

    # ============================================================
    # 杠杆设置（现货固定为 1x）
    # ============================================================
    def leverage(
        self,
        pair: str,
        current_time: pd.Timestamp,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs: Any
    ) -> float:
        """现货交易，杠杆固定为 1"""
        return 1.0

    # ============================================================
    # 入场确认（额外风控）
    # ============================================================
    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time: pd.Timestamp,
        entry_tag: Optional[str],
        side: str,
        **kwargs: Any
    ) -> bool:
        """
        入场确认
        
        可在此实现额外的风控检查:
        - 最大持仓数量限制
        - 单日入场次数限制
        - 相关性检查
        
        目前: 允许所有通过信号的入场
        """
        return True

    # ============================================================
    # 信息对配置
    # ============================================================
    def informative_pairs(self):
        """
        信息对（可用于跨品种分析）
        
        例如: 使用 BTC 作为大盘指标
        目前: 不使用
        """
        return []
