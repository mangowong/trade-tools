# -*- coding: utf-8 -*-
"""
基本面分析模块
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FundamentalAnalyzer:
    """基本面分析类"""

    def __init__(self, config):
        self.config = config
        self.weights = config.FUNDAMENTAL_WEIGHTS

    def analyze(self, fundamental_data, current_price=None):
        """综合分析基本面"""
        if fundamental_data is None:
            return self._get_default_analysis()

        analysis = {}

        # 分析各个维度
        analysis['valuation'] = self._analyze_valuation(fundamental_data)
        analysis['profitability'] = self._analyze_profitability(fundamental_data)
        analysis['growth'] = self._analyze_growth(fundamental_data)
        analysis['financial_health'] = self._analyze_financial_health(fundamental_data)

        # 计算综合评分
        analysis['overall_score'] = self._calculate_overall_score(analysis)

        return analysis

    def _analyze_valuation(self, data):
        """估值分析"""
        score = 0
        details = {}

        try:
            basic = data.get('basic')
            if basic is not None and not basic.empty:
                latest = basic.iloc[-1]

                # 市盈率分析
                pe = latest.get('pe', 0)
                if pd.notna(pe) and pe > 0:
                    details['pe_ratio'] = round(pe, 2)
                    if pe < 15:
                        score += 100
                    elif pe < 30:
                        score += 75
                    elif pe < 50:
                        score += 50
                    else:
                        score += 25

                # 市净率分析
                pb = latest.get('pb', 0)
                if pd.notna(pb) and pb > 0:
                    details['pb_ratio'] = round(pb, 2)
                    if pb < 1.5:
                        score += 100
                    elif pb < 3:
                        score += 75
                    elif pb < 5:
                        score += 50
                    else:
                        score += 25

                # 市销率分析
                ps = latest.get('ps', 0)
                if pd.notna(ps) and ps > 0:
                    details['ps_ratio'] = round(ps, 2)

        except Exception as e:
            logger.error(f"估值分析失败: {e}")

        avg_score = score / 2 if details else 50
        return {
            'score': round(avg_score, 2),
            'details': details,
            'level': self._get_score_level(avg_score)
        }

    def _analyze_profitability(self, data):
        """盈利能力分析"""
        score = 50
        details = {}

        try:
            financial = data.get('financial')
            if financial is not None and not financial.empty:
                latest = financial.iloc[-1]

                # ROE分析
                roe = latest.get('roe', 0)
                if pd.notna(roe):
                    details['roe'] = round(roe, 2)
                    if roe > 20:
                        score = 100
                    elif roe > 15:
                        score = 85
                    elif roe > 10:
                        score = 70
                    elif roe > 5:
                        score = 50
                    else:
                        score = 30

        except Exception as e:
            logger.error(f"盈利能力分析失败: {e}")

        return {
            'score': round(score, 2),
            'details': details,
            'level': self._get_score_level(score)
        }

    def _analyze_growth(self, data):
        """成长性分析"""
        score = 50
        details = {}

        try:
            financial = data.get('financial')
            if financial is not None and len(financial) >= 2:
                # 比较最近两个季度的数据
                recent = financial.iloc[0]
                previous = financial.iloc[1]

                # 这里可以根据实际数据字段计算增长率
                # 暂时给出中性评分
                details['revenue_growth'] = 'N/A'

        except Exception as e:
            logger.error(f"成长性分析失败: {e}")

        return {
            'score': round(score, 2),
            'details': details,
            'level': self._get_score_level(score)
        }

    def _analyze_financial_health(self, data):
        """财务健康分析"""
        score = 50
        details = {}

        try:
            financial = data.get('financial')
            if financial is not None and not financial.empty:
                latest = financial.iloc[-1]

                # 资产负债率分析
                debt_ratio = latest.get('debt_to_assets', 0)
                if pd.notna(debt_ratio):
                    details['debt_ratio'] = round(debt_ratio, 2)
                    if debt_ratio < 30:
                        score = 100
                    elif debt_ratio < 50:
                        score = 85
                    elif debt_ratio < 70:
                        score = 60
                    else:
                        score = 30

                # 流动比率
                current_ratio = latest.get('current_ratio', 0)
                if pd.notna(current_ratio):
                    details['current_ratio'] = round(current_ratio, 2)

        except Exception as e:
            logger.error(f"财务健康分析失败: {e}")

        return {
            'score': round(score, 2),
            'details': details,
            'level': self._get_score_level(score)
        }

    def _calculate_overall_score(self, analysis):
        """计算综合评分"""
        weights = self.weights

        scores = {
            'pe_ratio': analysis['valuation']['score'],
            'pb_ratio': analysis['valuation']['score'],
            'roe': analysis['profitability']['score'],
            'revenue_growth': analysis['growth']['score'],
            'debt_ratio': analysis['financial_health']['score']
        }

        total_score = sum(scores[key] * weights[key] for key in weights)

        return round(total_score, 2)

    def _get_score_level(self, score):
        """获取评分等级"""
        if score >= 80:
            return 'EXCELLENT'
        elif score >= 60:
            return 'GOOD'
        elif score >= 40:
            return 'FAIR'
        else:
            return 'POOR'

    def _get_default_analysis(self):
        """返回默认分析结果"""
        return {
            'valuation': {'score': 50, 'details': {}, 'level': 'FAIR'},
            'profitability': {'score': 50, 'details': {}, 'level': 'FAIR'},
            'growth': {'score': 50, 'details': {}, 'level': 'FAIR'},
            'financial_health': {'score': 50, 'details': {}, 'level': 'FAIR'},
            'overall_score': 50.0
        }
