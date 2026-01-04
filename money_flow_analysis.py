# -*- coding: utf-8 -*-
"""
资金流分析模块
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class MoneyFlowAnalyzer:
    """资金流分析类"""

    def __init__(self, config):
        self.config = config
        self.weights = config.MONEY_FLOW_WEIGHTS

    def analyze(self, money_flow_data):
        """分析资金流"""
        if money_flow_data is None or money_flow_data.empty:
            return self._get_default_analysis()

        analysis = {
            'latest': self._analyze_latest(money_flow_data),
            'trend': self._analyze_trend(money_flow_data),
            'accumulation': self._analyze_accumulation(money_flow_data)
        }

        # 计算综合评分
        analysis['overall_score'] = self._calculate_overall_score(analysis)

        return analysis

    def _analyze_latest(self, df):
        """分析最新交易日资金流"""
        if df.empty:
            return {}

        latest = df.iloc[-1]

        try:
            # Tushare格式
            return {
                'date': str(latest.get('trade_date', '')),
                'buy_elg_vol': round(latest.get('buy_elg_vol', 0), 2),
                'sell_elg_vol': round(latest.get('sell_elg_vol', 0), 2),
                'buy_lg_vol': round(latest.get('buy_lg_vol', 0), 2),
                'sell_lg_vol': round(latest.get('sell_lg_vol', 0), 2),
                'buy_md_vol': round(latest.get('buy_md_vol', 0), 2),
                'sell_md_vol': round(latest.get('sell_md_vol', 0), 2),
                'net_mf_vol': round(latest.get('net_mf_vol', 0), 2),
                'net_mf_amount': round(latest.get('net_mf_amount', 0), 2)
            }
        except Exception as e:
            logger.error(f"分析最新资金流失败: {e}")
            return {}

    def _analyze_trend(self, df):
        """分析资金流趋势"""
        if len(df) < 5:
            return {'trend': 'UNKNOWN', 'strength': 0}

        # 最近5天资金流
        recent = df.tail(5)
        net_flow = recent['net_mf_vol'] if 'net_mf_vol' in recent.columns else [0] * 5

        # 计算趋势
        positive_days = (net_flow > 0).sum()
        total_net = net_flow.sum()

        trend_score = 0
        trend_desc = []

        if positive_days >= 4:
            trend_score += 3
            trend_desc.append("连续净流入")
        elif positive_days >= 3:
            trend_score += 1
            trend_desc.append("多数净流入")
        elif positive_days <= 1:
            trend_score -= 3
            trend_desc.append("连续净流出")
        elif positive_days <= 2:
            trend_score -= 1
            trend_desc.append("多数净流出")

        # 总流入/流出
        if total_net > 0:
            trend_score += 2
            trend_desc.append(f"累计净流入{abs(total_net)/10000:.2f}万手")
        elif total_net < 0:
            trend_score -= 2
            trend_desc.append(f"累计净流出{abs(total_net)/10000:.2f}万手")

        if trend_score >= 4:
            trend = 'STRONG_INFLOW'
        elif trend_score >= 1:
            trend = 'INFLOW'
        elif trend_score <= -4:
            trend = 'STRONG_OUTFLOW'
        elif trend_score <= -1:
            trend = 'OUTFLOW'
        else:
            trend = 'BALANCED'

        return {
            'trend': trend,
            'strength': abs(trend_score),
            'description': ', '.join(trend_desc) if trend_desc else '资金平衡',
            'recent_avg': round(net_flow.mean(), 2)
        }

    def _analyze_accumulation(self, df):
        """分析资金累计"""
        if df.empty:
            return {}

        # 近5日、10日、20日累计
        periods = [5, 10, 20]
        accumulation = {}

        for period in periods:
            if len(df) >= period:
                recent = df.tail(period)
                net = recent['net_mf_vol'].sum() if 'net_mf_vol' in recent.columns else 0
                accumulation[f'{period}day_net'] = round(net, 2)

        return accumulation

    def _calculate_overall_score(self, analysis):
        """计算资金流综合评分"""
        score = 50

        # 基于趋势评分
        trend = analysis['trend'].get('trend', 'BALANCED')
        trend_scores = {
            'STRONG_INFLOW': 100,
            'INFLOW': 75,
            'BALANCED': 50,
            'OUTFLOW': 25,
            'STRONG_OUTFLOW': 0
        }
        score = trend_scores.get(trend, 50)

        # 基于最新净流入调整
        latest = analysis.get('latest', {})
        net_flow = latest.get('net_mf_vol', 0)
        if net_flow > 0:
            score = min(score + 10, 100)
        elif net_flow < 0:
            score = max(score - 10, 0)

        return round(score, 2)

    def _get_default_analysis(self):
        """返回默认分析结果"""
        return {
            'latest': {},
            'trend': {'trend': 'UNKNOWN', 'strength': 0, 'description': '无数据'},
            'accumulation': {},
            'overall_score': 50.0
        }
