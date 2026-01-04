# -*- coding: utf-8 -*-
"""
技术分析模块
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """技术分析类"""

    def __init__(self, config):
        self.config = config

    def calculate_all_indicators(self, df):
        """计算所有技术指标"""
        if df is None or df.empty:
            return None

        result = df.copy()

        # 移动平均线
        for period in self.config.MA_PERIODS:
            result[f'MA{period}'] = result['close'].rolling(window=period).mean()

        # 成交量移动平均
        for period in self.config.VOLUME_MA_PERIODS:
            result[f'VOL_MA{period}'] = result['vol'].rolling(window=period).mean()

        # MACD
        macd_data = self.calculate_macd(result['close'])
        result['MACD'] = macd_data['MACD']
        result['MACD_SIGNAL'] = macd_data['SIGNAL']
        result['MACD_HIST'] = macd_data['HIST']

        # RSI
        result['RSI'] = self.calculate_rsi(result['close'])

        # 布林带
        boll = self.calculate_bollinger(result['close'])
        result['BOLL_UPPER'] = boll['UPPER']
        result['BOLL_MIDDLE'] = boll['MIDDLE']
        result['BOLL_LOWER'] = boll['LOWER']

        # KDJ
        kdj = self.calculate_kdj(result)
        result['KDJ_K'] = kdj['K']
        result['KDJ_D'] = kdj['D']
        result['KDJ_J'] = kdj['J']

        # ATR (真实波幅)
        result['ATR'] = self.calculate_atr(result)

        # 成交量变化率
        result['VOL_CHANGE'] = result['vol'].pct_change()

        # 价格动量
        result['MOMENTUM'] = result['close'].pct_change(5)

        return result

    def calculate_macd(self, close_prices, fast=None, slow=None, signal=None):
        """计算MACD指标"""
        if fast is None:
            fast = self.config.MACD_FAST
        if slow is None:
            slow = self.config.MACD_SLOW
        if signal is None:
            signal = self.config.MACD_SIGNAL

        ema_fast = close_prices.ewm(span=fast, adjust=False).mean()
        ema_slow = close_prices.ewm(span=slow, adjust=False).mean()

        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return {
            'MACD': macd,
            'SIGNAL': signal_line,
            'HIST': histogram
        }

    def calculate_rsi(self, close_prices, period=None):
        """计算RSI指标"""
        if period is None:
            period = self.config.RSI_PERIOD

        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_bollinger(self, close_prices, period=None, std=None):
        """计算布林带"""
        if period is None:
            period = self.config.BOLLINGER_PERIOD
        if std is None:
            std = self.config.BOLLINGER_STD

        middle = close_prices.rolling(window=period).mean()
        upper = middle + (close_prices.rolling(window=period).std() * std)
        lower = middle - (close_prices.rolling(window=period).std() * std)

        return {
            'UPPER': upper,
            'MIDDLE': middle,
            'LOWER': lower
        }

    def calculate_kdj(self, df, n=9, m1=3, m2=3):
        """计算KDJ指标"""
        low_list = df['low'].rolling(window=n, min_periods=1).min()
        high_list = df['high'].rolling(window=n, min_periods=1).max()

        rsv = (df['close'] - low_list) / (high_list - low_list) * 100

        k = rsv.ewm(com=m1 - 1, adjust=False).mean()
        d = k.ewm(com=m2 - 1, adjust=False).mean()
        j = 3 * k - 2 * d

        return {'K': k, 'D': d, 'J': j}

    def calculate_atr(self, df, period=14):
        """计算ATR (真实波幅)"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    def analyze_trend(self, df):
        """分析趋势"""
        if df is None or len(df) < 20:
            return {'trend': 'UNKNOWN', 'strength': 0}

        latest = df.iloc[-1]

        # 基于均线判断趋势
        ma5 = latest['MA5'] if pd.notna(latest['MA5']) else 0
        ma10 = latest['MA10'] if pd.notna(latest['MA10']) else 0
        ma20 = latest['MA20'] if pd.notna(latest['MA20']) else 0
        ma60 = latest['MA60'] if pd.notna(latest['MA60']) else 0

        current_price = latest['close']

        trend_score = 0
        trend_desc = []

        # 价格与均线关系
        if current_price > ma5 > ma10 > ma20:
            trend_score += 3
            trend_desc.append("短期多头排列")
        elif current_price < ma5 < ma10 < ma20:
            trend_score -= 3
            trend_desc.append("短期空头排列")

        # 长期趋势
        if ma20 > ma60:
            trend_score += 2
            trend_desc.append("长期上升趋势")
        elif ma20 < ma60:
            trend_score -= 2
            trend_desc.append("长期下降趋势")

        # MACD信号
        if pd.notna(latest['MACD']) and pd.notna(latest['MACD_SIGNAL']):
            if latest['MACD'] > latest['MACD_SIGNAL'] and latest['MACD_HIST'] > 0:
                trend_score += 1
                trend_desc.append("MACD金叉")
            elif latest['MACD'] < latest['MACD_SIGNAL'] and latest['MACD_HIST'] < 0:
                trend_score -= 1
                trend_desc.append("MACD死叉")

        # 判断趋势方向
        if trend_score >= 4:
            trend = 'STRONG_UP'
        elif trend_score >= 1:
            trend = 'UP'
        elif trend_score <= -4:
            trend = 'STRONG_DOWN'
        elif trend_score <= -1:
            trend = 'DOWN'
        else:
            trend = 'SIDEWAYS'

        return {
            'trend': trend,
            'strength': abs(trend_score),
            'description': ', '.join(trend_desc) if trend_desc else '震荡'
        }

    def analyze_momentum(self, df):
        """分析动量"""
        if df is None or len(df) < 14:
            return {}

        latest = df.iloc[-1]

        # RSI分析
        rsi = latest['RSI'] if pd.notna(latest['RSI']) else 50
        rsi_signal = 'NEUTRAL'
        if rsi > 70:
            rsi_signal = 'OVERBOUGHT'
        elif rsi < 30:
            rsi_signal = 'OVERSOLD'

        # KDJ分析
        k = latest['KDJ_K'] if pd.notna(latest['KDJ_K']) else 50
        d = latest['KDJ_D'] if pd.notna(latest['KDJ_D']) else 50
        j = latest['KDJ_J'] if pd.notna(latest['KDJ_J']) else 50

        kdj_signal = 'NEUTRAL'
        if k > 80 and d > 80:
            kdj_signal = 'OVERBOUGHT'
        elif k < 20 and d < 20:
            kdj_signal = 'OVERSOLD'

        # 动量评分
        momentum_score = 0
        if 30 < rsi < 70:
            momentum_score += 1
        if k > d:
            momentum_score += 1
        if j > k:
            momentum_score += 1

        return {
            'rsi': round(rsi, 2),
            'rsi_signal': rsi_signal,
            'kdj_k': round(k, 2),
            'kdj_d': round(d, 2),
            'kdj_j': round(j, 2),
            'kdj_signal': kdj_signal,
            'momentum_score': momentum_score
        }

    def calculate_technical_score(self, trend_analysis, momentum_analysis):
        """计算技术面综合评分"""
        score = 0

        # 趋势得分 (权重40%)
        trend = trend_analysis.get('trend', 'SIDEWAYS')
        trend_scores = {
            'STRONG_UP': 100,
            'UP': 70,
            'SIDEWAYS': 50,
            'DOWN': 30,
            'STRONG_DOWN': 10
        }
        score += trend_scores.get(trend, 50) * 0.4

        # 动量得分 (权重30%)
        momentum_score = momentum_analysis.get('momentum_score', 0)
        score += (momentum_score / 3 * 100) * 0.3

        # RSI得分 (权重15%)
        rsi = momentum_analysis.get('rsi', 50)
        if 40 <= rsi <= 60:
            rsi_score = 100
        elif 30 <= rsi < 40 or 60 < rsi <= 70:
            rsi_score = 75
        elif 20 <= rsi < 30 or 70 < rsi <= 80:
            rsi_score = 50
        else:
            rsi_score = 25
        score += rsi_score * 0.15

        # MACD得分 (权重15%)
        score += 50 * 0.15  # 中性值

        return round(score, 2)
