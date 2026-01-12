"""
基本面分析模块
分析财务指标、估值水平、盈利能力等基本面数据
"""
import akshare as ak
import pandas as pd
from datetime import datetime
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class FundamentalAnalysis:
    """基本面分析器"""

    def __init__(self, stock_code: str):
        """
        初始化基本面分析器

        Args:
            stock_code: 股票代码
        """
        self.stock_code = stock_code
        self.company_info = None
        self.financial_data = None

    def get_company_info(self) -> Dict:
        """
        获取公司基本信息

        Returns:
            公司信息字典
        """
        try:
            # 获取股票基本信息
            df = ak.stock_individual_info_em(symbol=self.stock_code)

            if df.empty:
                return {}

            info = {}
            for _, row in df.iterrows():
                info[row['item']] = row['value']

            self.company_info = info
            return info
        except Exception as e:
            print(f"获取公司信息失败: {e}")
            return {}

    def get_financial_indicators(self) -> Dict:
        """
        获取关键财务指标

        Returns:
            财务指标字典
        """
        try:
            # 获取财务指标
            df = ak.stock_financial_analysis_indicator(symbol=self.stock_code)

            if df.empty:
                return self._get_empty_financial()

            latest = df.iloc[0]

            financial = {
                'report_date': latest.get('日期', ''),
                'pe_ratio': self._safe_float(latest.get('市盈率-动态', 0)),
                'pb_ratio': self._safe_float(latest.get('市净率', 0)),
                'ps_ratio': self._safe_float(latest.get('市销率', 0)),
                'roe': self._safe_float(latest.get('净资产收益率', 0)),
                'roa': self._safe_float(latest.get('总资产净利率', 0)),
                'gross_margin': self._safe_float(latest.get('销售毛利率', 0)),
                'net_margin': self._safe_float(latest.get('销售净利率', 0)),
                'debt_ratio': self._safe_float(latest.get('资产负债率', 0)),
                'current_ratio': self._safe_float(latest.get('流动比率', 0)),
                'quick_ratio': self._safe_float(latest.get('速动比率', 0)),
                'total_revenue': self._safe_float(latest.get('营业总收入', 0)),
                'net_profit': self._safe_float(latest.get('净利润', 0)),
                'total_assets': self._safe_float(latest.get('总资产', 0)),
                'total_liabilities': self._safe_float(latest.get('总负债', 0)),
                'operating_cash_flow': self._safe_float(latest.get('经营活动现金流', 0))
            }

            self.financial_data = financial
            return financial
        except Exception as e:
            print(f"获取财务指标失败: {e}")
            return self._get_empty_financial()

    def get_profitability_score(self) -> float:
        """
        计算盈利能力评分 (0-100)

        Returns:
            盈利能力评分
        """
        financial = self.get_financial_indicators()

        if not financial:
            return 0.0

        score = 0.0

        # ROE评分 (40分)
        roe = financial.get('roe', 0)
        if roe >= 0.20:
            score += 40
        elif roe >= 0.15:
            score += 35
        elif roe >= 0.10:
            score += 25
        elif roe >= 0.05:
            score += 15

        # 毛利率评分 (20分)
        gross_margin = financial.get('gross_margin', 0)
        if gross_margin >= 0.50:
            score += 20
        elif gross_margin >= 0.30:
            score += 15
        elif gross_margin >= 0.20:
            score += 10

        # 净利率评分 (20分)
        net_margin = financial.get('net_margin', 0)
        if net_margin >= 0.20:
            score += 20
        elif net_margin >= 0.10:
            score += 15
        elif net_margin >= 0.05:
            score += 10

        # ROA评分 (20分)
        roa = financial.get('roa', 0)
        if roa >= 0.10:
            score += 20
        elif roa >= 0.05:
            score += 15
        elif roa >= 0.03:
            score += 10

        return min(score, 100.0)

    def get_growth_score(self) -> float:
        """
        计算成长能力评分

        Returns:
            成长能力评分
        """
        try:
            df = ak.stock_financial_analysis_indicator(symbol=self.stock_code)

            if df.empty or len(df) < 2:
                return 0.0

            latest = df.iloc[0]
            previous = df.iloc[1]

            score = 0.0

            # 营收增长率 (50分)
            current_revenue = self._safe_float(latest.get('营业总收入', 0))
            previous_revenue = self._safe_float(previous.get('营业总收入', 0))

            if previous_revenue > 0:
                revenue_growth = (current_revenue - previous_revenue) / previous_revenue
                if revenue_growth >= 0.30:
                    score += 50
                elif revenue_growth >= 0.20:
                    score += 40
                elif revenue_growth >= 0.10:
                    score += 30
                elif revenue_growth >= 0.05:
                    score += 20
                elif revenue_growth >= 0:
                    score += 10

            # 利润增长率 (50分)
            current_profit = self._safe_float(latest.get('净利润', 0))
            previous_profit = self._safe_float(previous.get('净利润', 0))

            if previous_profit > 0:
                profit_growth = (current_profit - previous_profit) / previous_profit
                if profit_growth >= 0.30:
                    score += 50
                elif profit_growth >= 0.20:
                    score += 40
                elif profit_growth >= 0.10:
                    score += 30
                elif profit_growth >= 0.05:
                    score += 20
                elif profit_growth >= 0:
                    score += 10

            return min(score, 100.0)
        except Exception as e:
            print(f"计算成长性评分失败: {e}")
            return 0.0

    def get_safety_score(self) -> float:
        """
        计算安全性评分

        Returns:
            安全性评分
        """
        financial = self.get_financial_indicators()

        if not financial:
            return 0.0

        score = 0.0

        # 资产负债率 (40分) - 越低越好
        debt_ratio = financial.get('debt_ratio', 1.0)
        if debt_ratio <= 0.30:
            score += 40
        elif debt_ratio <= 0.50:
            score += 30
        elif debt_ratio <= 0.70:
            score += 20

        # 流动比率 (30分)
        current_ratio = financial.get('current_ratio', 0)
        if current_ratio >= 2.0:
            score += 30
        elif current_ratio >= 1.5:
            score += 25
        elif current_ratio >= 1.0:
            score += 15

        # 速动比率 (30分)
        quick_ratio = financial.get('quick_ratio', 0)
        if quick_ratio >= 1.5:
            score += 30
        elif quick_ratio >= 1.0:
            score += 25
        elif quick_ratio >= 0.5:
            score += 15

        return min(score, 100.0)

    def get_valuation_level(self) -> str:
        """
        评估估值水平

        Returns:
            估值水平描述
        """
        financial = self.get_financial_indicators()

        if not financial:
            return "未知"

        pe = financial.get('pe_ratio', 0)
        pb = financial.get('pb_ratio', 0)

        if pe == 0:
            return "无法评估"

        if pe < 10:
            level = "低估"
        elif pe < 20:
            level = "合理偏低"
        elif pe < 30:
            level = "合理"
        elif pe < 50:
            level = "偏高"
        else:
            level = "高估"

        if pb > 0:
            if pb < 1:
                level += " (破净)"
            elif pb > 5:
                level += " (PB偏高)"

        return level

    def _safe_float(self, value) -> float:
        """安全转换为浮点数"""
        try:
            if isinstance(value, str):
                value = value.replace('%', '').replace(',', '').strip()
                if value == '-' or value == '':
                    return 0.0
            return float(value) if value else 0.0
        except:
            return 0.0

    def _get_empty_financial(self) -> Dict:
        """返回空的财务数据结构"""
        return {
            'report_date': '',
            'pe_ratio': 0.0,
            'pb_ratio': 0.0,
            'ps_ratio': 0.0,
            'roe': 0.0,
            'roa': 0.0,
            'gross_margin': 0.0,
            'net_margin': 0.0,
            'debt_ratio': 0.0,
            'current_ratio': 0.0,
            'quick_ratio': 0.0,
            'total_revenue': 0.0,
            'net_profit': 0.0,
            'total_assets': 0.0,
            'total_liabilities': 0.0,
            'operating_cash_flow': 0.0
        }

    def generate_fundamental_report(self) -> str:
        """
        生成基本面分析报告

        Returns:
            文本报告
        """
        company_info = self.get_company_info()
        financial = self.get_financial_indicators()
        profitability_score = self.get_profitability_score()
        growth_score = self.get_growth_score()
        safety_score = self.get_safety_score()
        valuation = self.get_valuation_level()

        report = f"""
基本面分析报告 - {self.stock_code}
{'=' * 50}

【公司基本信息】
公司名称: {company_info.get('公司名称', 'N/A')}
行业: {company_info.get('行业', 'N/A')}
总市值: {company_info.get('总市值', 'N/A')}
流通市值: {company_info.get('流通市值', 'N/A')}

【估值指标】
市盈率(PE): {financial.get('pe_ratio', 0):.2f}
市净率(PB): {financial.get('pb_ratio', 0):.2f}
市销率(PS): {financial.get('ps_ratio', 0):.2f}
估值水平: {valuation}

【盈利能力】 (评分: {profitability_score:.1f}/100)
净资产收益率(ROE): {financial.get('roe', 0):.2%}
总资产净利率(ROA): {financial.get('roa', 0):.2%}
销售毛利率: {financial.get('gross_margin', 0):.2%}
销售净利率: {financial.get('net_margin', 0):.2%}

【成长能力】 (评分: {growth_score:.1f}/100)
营业总收入: {financial.get('total_revenue', 0):,.0f} 万元
净利润: {financial.get('net_profit', 0):,.0f} 万元

【财务安全】 (评分: {safety_score:.1f}/100)
资产负债率: {financial.get('debt_ratio', 0):.2%}
流动比率: {financial.get('current_ratio', 0):.2f}
速动比率: {financial.get('quick_ratio', 0):.2f}

【现金流】
经营活动现金流: {financial.get('operating_cash_flow', 0):,.0f} 万元

【综合评分】
总分: {(profitability_score * 0.4 + growth_score * 0.3 + safety_score * 0.3):.1f}/100
投资建议: {'具备投资价值' if (profitability_score + growth_score + safety_score) / 3 >= 60 else '需要谨慎观察'}
"""
        return report
