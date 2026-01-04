"""
研发技术投入分析模块
分析公司的研发投入、技术创新能力、专利情况等
"""
import akshare as ak
import pandas as pd
from datetime import datetime
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class RDAnalysis:
    """研发投入分析器"""

    def __init__(self, stock_code: str):
        """
        初始化研发分析器

        Args:
            stock_code: 股票代码
        """
        self.stock_code = stock_code
        self.rd_data = None

    def get_rd_expenses(self) -> Dict:
        """
        获取研发费用数据

        Returns:
            研发费用数据字典
        """
        try:
            # 尝试从财务报表中获取研发费用
            df = ak.stock_profit_sheet_by_report_em(symbol=self.stock_code)

            if df.empty:
                return self._get_empty_rd()

            # 获取最近4个季度的数据
            recent = df.head(4)

            rd_dict = {
                'latest_rd': self._safe_float(recent.iloc[0].get('研发费用', 0)),
                'total_rd_4q': sum([self._safe_float(row.get('研发费用', 0)) for _, row in recent.iterrows()]),
                'report_dates': recent['报告期'].tolist()
            }

            self.rd_data = rd_dict
            return rd_dict
        except Exception as e:
            print(f"获取研发费用失败: {e}")
            return self._get_empty_rd()

    def calculate_rd_intensity(self) -> Dict:
        """
        计算研发强度（研发费用占营收比例）

        Returns:
            研发强度数据
        """
        try:
            # 获取利润表数据
            profit_df = ak.stock_profit_sheet_by_report_em(symbol=self.stock_code)

            if profit_df.empty:
                return {'rd_intensity': 0.0, 'trend': 'unknown'}

            latest = profit_df.iloc[0]
            rd_expense = self._safe_float(latest.get('研发费用', 0))
            revenue = self._safe_float(latest.get('营业总收入', 0))

            if revenue == 0:
                return {'rd_intensity': 0.0, 'trend': 'unknown'}

            rd_intensity = rd_expense / revenue

            # 计算历史趋势
            if len(profit_df) >= 4:
                rd_intensities = []
                for i in range(min(4, len(profit_df))):
                    row = profit_df.iloc[i]
                    rd = self._safe_float(row.get('研发费用', 0))
                    rev = self._safe_float(row.get('营业总收入', 0))
                    if rev > 0:
                        rd_intensities.append(rd / rev)

                if len(rd_intensities) >= 2:
                    if rd_intensities[0] > rd_intensities[-1]:
                        trend = 'increasing'
                    elif rd_intensities[0] < rd_intensities[-1]:
                        trend = 'decreasing'
                    else:
                        trend = 'stable'
                else:
                    trend = 'unknown'
            else:
                trend = 'unknown'

            return {
                'rd_intensity': rd_intensity,
                'trend': trend
            }
        except Exception as e:
            print(f"计算研发强度失败: {e}")
            return {'rd_intensity': 0.0, 'trend': 'unknown'}

    def analyze_rd_growth(self) -> Dict:
        """
        分析研发费用增长情况

        Returns:
            增长分析结果
        """
        try:
            df = ak.stock_profit_sheet_by_report_em(symbol=self.stock_code)

            if df.empty or len(df) < 2:
                return {'growth_rate': 0.0, 'consecutive_growth': 0}

            rd_expenses = []
            for _, row in df.head(4).iterrows():
                rd = self._safe_float(row.get('研发费用', 0))
                rd_expenses.append(rd)

            # 同比增长率
            if len(rd_expenses) >= 5:
                current_year = sum(rd_expenses[:4])
                previous_year = sum(rd_expenses[4:8]) if len(rd_expenses) >= 8 else 0

                if previous_year > 0:
                    growth_rate = (current_year - previous_year) / previous_year
                else:
                    growth_rate = 0.0
            else:
                growth_rate = 0.0

            # 连续增长季度数
            consecutive_growth = 0
            for i in range(len(rd_expenses) - 1):
                if rd_expenses[i] >= rd_expenses[i + 1] and rd_expenses[i] > 0:
                    consecutive_growth += 1
                else:
                    break

            return {
                'growth_rate': growth_rate,
                'consecutive_growth': consecutive_growth,
                'latest_rd': rd_expenses[0] if rd_expenses else 0.0
            }
        except Exception as e:
            print(f"分析研发增长失败: {e}")
            return {'growth_rate': 0.0, 'consecutive_growth': 0}

    def evaluate_technical_capability(self) -> Dict:
        """
        评估技术能力（基于研发投入的多维度分析）

        Returns:
            技术能力评估结果
        """
        rd_expenses = self.get_rd_expenses()
        intensity = self.calculate_rd_intensity()
        growth = self.analyze_rd_growth()

        # 研发投入评分
        score = 0.0

        # 1. 研发强度评分 (40分)
        rd_intensity = intensity.get('rd_intensity', 0)
        if rd_intensity >= 0.10:  # 10%以上
            score += 40
        elif rd_intensity >= 0.05:  # 5%-10%
            score += 30
        elif rd_intensity >= 0.03:  # 3%-5%
            score += 20
        elif rd_intensity > 0:
            score += 10

        # 2. 研发增长评分 (30分)
        growth_rate = growth.get('growth_rate', 0)
        if growth_rate >= 0.30:
            score += 30
        elif growth_rate >= 0.20:
            score += 25
        elif growth_rate >= 0.10:
            score += 20
        elif growth_rate >= 0:
            score += 10

        # 3. 研发投入持续性评分 (30分)
        consecutive_growth = growth.get('consecutive_growth', 0)
        if consecutive_growth >= 4:
            score += 30
        elif consecutive_growth >= 3:
            score += 25
        elif consecutive_growth >= 2:
            score += 20
        elif consecutive_growth >= 1:
            score += 10

        # 4. 绝对投入规模奖励分 (最高10分)
        latest_rd = rd_expenses.get('latest_rd', 0)
        if latest_rd >= 1000000:  # 10亿以上
            score += 10
        elif latest_rd >= 500000:  # 5-10亿
            score += 8
        elif latest_rd >= 100000:  # 1-5亿
            score += 5
        elif latest_rd >= 10000:  # 1000万-1亿
            score += 3

        score = min(score, 100.0)

        # 技术能力等级
        if score >= 80:
            level = '优秀'
        elif score >= 60:
            level = '良好'
        elif score >= 40:
            level = '一般'
        elif score >= 20:
            level = '较弱'
        else:
            level = '弱'

        return {
            'score': score,
            'level': level,
            'rd_intensity': rd_intensity,
            'growth_rate': growth_rate,
            'latest_rd': latest_rd
        }

    def compare_industry_rd(self, industry: str = None) -> Dict:
        """
        与行业平均水平对比

        Args:
            industry: 行业名称（可选）

        Returns:
            对比结果
        """
        # 这里简化处理，实际需要行业数据
        rd_intensity = self.calculate_rd_intensity().get('rd_intensity', 0)

        # 不同行业的研发强度基准
        industry_benchmarks = {
            '科技': 0.08,
            '医药': 0.05,
            '制造': 0.03,
            '消费': 0.02,
            '金融': 0.01
        }

        benchmark = 0.03  # 默认基准

        if industry:
            for key, value in industry_benchmarks.items():
                if key in industry:
                    benchmark = value
                    break

        ratio = rd_intensity / benchmark if benchmark > 0 else 1.0

        return {
            'company_rd_intensity': rd_intensity,
            'industry_benchmark': benchmark,
            'ratio': ratio,
            'above_industry': ratio >= 1.0
        }

    def _safe_float(self, value) -> float:
        """安全转换为浮点数"""
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace('-', '').strip()
                if value == '' or value == 'N/A':
                    return 0.0
            return float(value) if value else 0.0
        except:
            return 0.0

    def _get_empty_rd(self) -> Dict:
        """返回空的研发数据结构"""
        return {
            'latest_rd': 0.0,
            'total_rd_4q': 0.0,
            'report_dates': []
        }

    def generate_rd_report(self) -> str:
        """
        生成研发分析报告

        Returns:
            文本报告
        """
        rd_expenses = self.get_rd_expenses()
        intensity = self.calculate_rd_intensity()
        growth = self.analyze_rd_growth()
        capability = self.evaluate_technical_capability()

        trend_desc = {
            'increasing': '持续提升',
            'decreasing': '持续下降',
            'stable': '保持稳定',
            'unknown': '趋势不明'
        }

        report = f"""
研发技术投入分析报告 - {self.stock_code}
{'=' * 50}

【研发投入规模】
最新研发费用: {rd_expenses.get('latest_rd', 0):,.0f} 万元
近4季度累计: {rd_expenses.get('total_rd_4q', 0):,.0f} 万元

【研发强度】
研发费用占营收比: {intensity.get('rd_intensity', 0):.2%}
趋势: {trend_desc.get(intensity.get('trend', 'unknown'), '未知')}
"""

        if intensity.get('rd_intensity', 0) >= 0.05:
            report += "评价: 研发强度较高，技术创新投入积极\n"
        elif intensity.get('rd_intensity', 0) >= 0.03:
            report += "评价: 研发强度适中\n"
        elif intensity.get('rd_intensity', 0) > 0:
            report += "评价: 研发强度较低，需关注技术竞争力\n"
        else:
            report += "评价: 研发数据缺失或无研发投入\n"

        report += f"""
【研发增长情况】
同比增长率: {growth.get('growth_rate', 0):.2%}
连续增长季度: {growth.get('consecutive_growth', 0)} 季度

【技术能力评估】
综合评分: {capability.get('score', 0):.1f}/100
能力等级: {capability.get('level', 'N/A')}

【投资建议】
"""

        score = capability.get('score', 0)
        if score >= 70:
            report += "该公司研发投入积极，技术创新能力强，具备长期竞争优势。\n"
        elif score >= 50:
            report += "该公司研发投入适中，技术能力良好，需持续关注研发进展。\n"
        elif score >= 30:
            report += "该公司研发投入较低，技术能力一般，建议观察后续研发投入变化。\n"
        else:
            report += "该公司研发投入不足，技术竞争力可能存在风险，建议谨慎投资。\n"

        return report
