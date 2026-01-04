# -*- coding: utf-8 -*-
"""
报告生成模块
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""

    def __init__(self, config):
        self.config = config
        plt.style.use(config.CHART_STYLE)

        # 创建输出目录
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    def generate_daily_report(self, stock_code, analysis_data):
        """生成日报"""
        report = {
            'stock_code': stock_code,
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': self._generate_summary(analysis_data),
            'technical': analysis_data.get('technical', {}),
            'fundamental': analysis_data.get('fundamental', {}),
            'money_flow': analysis_data.get('money_flow', {}),
            'recommendation': self._generate_recommendation(analysis_data)
        }

        return report

    def _generate_summary(self, analysis_data):
        """生成摘要"""
        technical = analysis_data.get('technical', {})
        fundamental = analysis_data.get('fundamental', {})
        money_flow = analysis_data.get('money_flow', {})

        # 获取各维度评分
        tech_score = technical.get('technical_score', 50)
        fund_score = fundamental.get('overall_score', 50)
        flow_score = money_flow.get('overall_score', 50)

        # 综合评分
        overall_score = round((tech_score * 0.4 + fund_score * 0.3 + flow_score * 0.3), 2)

        # 评级
        if overall_score >= 75:
            rating = '强烈买入'
        elif overall_score >= 65:
            rating = '买入'
        elif overall_score >= 45:
            rating = '持有'
        elif overall_score >= 35:
            rating = '卖出'
        else:
            rating = '强烈卖出'

        return {
            'overall_score': overall_score,
            'rating': rating,
            'technical_score': tech_score,
            'fundamental_score': fund_score,
            'money_flow_score': flow_score
        }

    def _generate_recommendation(self, analysis_data):
        """生成投资建议"""
        recommendations = []

        # 技术面建议
        technical = analysis_data.get('technical', {})
        trend = technical.get('trend', {}).get('trend', 'SIDEWAYS')
        momentum = technical.get('momentum', {})

        if trend in ['UP', 'STRONG_UP']:
            recommendations.append("技术面呈上升趋势，可考虑逢低买入")
        elif trend in ['DOWN', 'STRONG_DOWN']:
            recommendations.append("技术面呈下降趋势，建议谨慎或减仓")

        rsi = momentum.get('rsi', 50)
        if rsi > 70:
            recommendations.append("RSI超买，短期可能回调，注意风险")
        elif rsi < 30:
            recommendations.append("RSI超卖，可能存在反弹机会")

        # 基本面建议
        fundamental = analysis_data.get('fundamental', {})
        fund_score = fundamental.get('overall_score', 50)

        if fund_score >= 70:
            recommendations.append("基本面良好，具备中长期投资价值")
        elif fund_score <= 40:
            recommendations.append("基本面较弱，建议谨慎投资")

        # 资金流建议
        money_flow = analysis_data.get('money_flow', {})
        flow_trend = money_flow.get('trend', {}).get('trend', 'BALANCED')

        if flow_trend in ['INFLOW', 'STRONG_INFLOW']:
            recommendations.append("资金持续流入，市场关注度较高")
        elif flow_trend in ['OUTFLOW', 'STRONG_OUTFLOW']:
            recommendations.append("资金持续流出，需注意资金面风险")

        return recommendations if recommendations else ["综合分析中性，建议观望"]

    def save_report(self, report, filename=None):
        """保存报告"""
        if filename is None:
            stock_code = report['stock_code']
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"{self.config.OUTPUT_DIR}/{stock_code}_report_{date_str}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"A股投资分析报告 - {report['stock_code']}\n")
                f.write(f"生成时间: {report['report_date']}\n")
                f.write("=" * 80 + "\n\n")

                # 摘要
                f.write("【综合评分】\n")
                f.write("-" * 40 + "\n")
                summary = report['summary']
                f.write(f"综合评分: {summary['overall_score']}/100\n")
                f.write(f"投资评级: {summary['rating']}\n")
                f.write(f"技术面评分: {summary['technical_score']}/100\n")
                f.write(f"基本面评分: {summary['fundamental_score']}/100\n")
                f.write(f"资金流评分: {summary['money_flow_score']}/100\n\n")

                # 技术分析
                f.write("【技术分析】\n")
                f.write("-" * 40 + "\n")
                tech = report['technical']
                if 'trend' in tech:
                    trend_info = tech['trend']
                    f.write(f"趋势: {trend_info.get('trend', 'N/A')}\n")
                    f.write(f"趋势强度: {trend_info.get('strength', 0)}\n")
                    f.write(f"趋势描述: {trend_info.get('description', 'N/A')}\n")
                if 'momentum' in tech:
                    momentum = tech['momentum']
                    f.write(f"RSI: {momentum.get('rsi', 'N/A')} ({momentum.get('rsi_signal', 'N/A')})\n")
                    f.write(f"KDJ: K={momentum.get('kdj_k', 'N/A')}, D={momentum.get('kdj_d', 'N/A')}, J={momentum.get('kdj_j', 'N/A')}\n")
                f.write(f"\n技术面评分: {tech.get('technical_score', 'N/A')}/100\n\n")

                # 基本面分析
                f.write("【基本面分析】\n")
                f.write("-" * 40 + "\n")
                fund = report['fundamental']
                f.write(f"估值评级: {fund.get('valuation', {}).get('level', 'N/A')} ({fund.get('valuation', {}).get('score', 0)})\n")
                f.write(f"盈利能力: {fund.get('profitability', {}).get('level', 'N/A')} ({fund.get('profitability', {}).get('score', 0)})\n")
                f.write(f"成长性: {fund.get('growth', {}).get('level', 'N/A')} ({fund.get('growth', {}).get('score', 0)})\n")
                f.write(f"财务健康: {fund.get('financial_health', {}).get('level', 'N/A')} ({fund.get('financial_health', {}).get('score', 0)})\n")
                f.write(f"\n基本面综合评分: {fund.get('overall_score', 'N/A')}/100\n\n")

                # 资金流分析
                f.write("【资金流分析】\n")
                f.write("-" * 40 + "\n")
                flow = report['money_flow']
                if 'trend' in flow:
                    flow_trend = flow['trend']
                    f.write(f"资金流向: {flow_trend.get('trend', 'N/A')}\n")
                    f.write(f"流向描述: {flow_trend.get('description', 'N/A')}\n")
                f.write(f"\n资金流评分: {flow.get('overall_score', 'N/A')}/100\n\n")

                # 投资建议
                f.write("【投资建议】\n")
                f.write("-" * 40 + "\n")
                for i, rec in enumerate(report['recommendation'], 1):
                    f.write(f"{i}. {rec}\n")

                f.write("\n" + "=" * 80 + "\n")
                f.write("风险提示: 本报告仅供参考，不构成投资建议，投资有风险，入市需谨慎\n")
                f.write("=" * 80 + "\n")

            logger.info(f"报告已保存至: {filename}")
            return filename
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            return None

    def generate_charts(self, stock_code, df, analysis_data):
        """生成图表"""
        if df is None or df.empty:
            logger.warning(f"{stock_code}: 无数据生成图表")
            return []

        chart_files = []

        try:
            # 图1: K线图与均线
            fig1 = self._plot_price_and_ma(stock_code, df)
            if fig1:
                chart_file = f"{self.config.OUTPUT_DIR}/{stock_code}_price_ma.png"
                fig1.savefig(chart_file, dpi=150, bbox_inches='tight')
                plt.close(fig1)
                chart_files.append(chart_file)

            # 图2: MACD
            fig2 = self._plot_macd(stock_code, df)
            if fig2:
                chart_file = f"{self.config.OUTPUT_DIR}/{stock_code}_macd.png"
                fig2.savefig(chart_file, dpi=150, bbox_inches='tight')
                plt.close(fig2)
                chart_files.append(chart_file)

            # 图3: RSI和KDJ
            fig3 = self._plot_rsi_kdj(stock_code, df)
            if fig3:
                chart_file = f"{self.config.OUTPUT_DIR}/{stock_code}_rsi_kdj.png"
                fig3.savefig(chart_file, dpi=150, bbox_inches='tight')
                plt.close(fig3)
                chart_files.append(chart_file)

            # 图4: 成交量
            fig4 = self._plot_volume(stock_code, df)
            if fig4:
                chart_file = f"{self.config.OUTPUT_DIR}/{stock_code}_volume.png"
                fig4.savefig(chart_file, dpi=150, bbox_inches='tight')
                plt.close(fig4)
                chart_files.append(chart_file)

            logger.info(f"{stock_code}: 图表生成完成，共{len(chart_files)}个文件")
            return chart_files

        except Exception as e:
            logger.error(f"{stock_code}: 生成图表失败: {e}")
            return []

    def _plot_price_and_ma(self, stock_code, df):
        """绘制价格和均线图"""
        fig, axes = plt.subplots(2, 1, figsize=self.config.FIGSIZE,
                                 height_ratios=[3, 1], sharex=True)

        # 价格和均线
        ax1 = axes[0]
        ax1.plot(df['trade_date'], df['close'], label='Close Price', linewidth=2)

        for period in self.config.MA_PERIODS:
            if f'MA{period}' in df.columns:
                ax1.plot(df['trade_date'], df[f'MA{period}'],
                        label=f'MA{period}', alpha=0.7, linewidth=1)

        ax1.set_ylabel('Price (元)')
        ax1.set_title(f'{stock_code} - 价格走势与均线')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)

        # 成交量
        ax2 = axes[1]
        colors = ['red' if df['close'].iloc[i] >= df['open'].iloc[i] else 'green'
                 for i in range(len(df))]
        ax2.bar(df['trade_date'], df['vol'], color=colors, alpha=0.6)
        ax2.set_ylabel('Volume (手)')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def _plot_macd(self, stock_code, df):
        """绘制MACD图"""
        if 'MACD' not in df.columns:
            return None

        fig, ax = plt.subplots(figsize=self.config.FIGSIZE)

        ax.plot(df['trade_date'], df['MACD'], label='MACD', linewidth=2)
        ax.plot(df['trade_date'], df['MACD_SIGNAL'], label='Signal', linewidth=2)

        colors = ['red' if x >= 0 else 'green' for x in df['MACD_HIST']]
        ax.bar(df['trade_date'], df['MACD_HIST'], color=colors, alpha=0.3, label='Histogram')

        ax.set_ylabel('MACD')
        ax.set_title(f'{stock_code} - MACD指标')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def _plot_rsi_kdj(self, stock_code, df):
        """绘制RSI和KDJ图"""
        if 'RSI' not in df.columns or 'KDJ_K' not in df.columns:
            return None

        fig, axes = plt.subplots(2, 1, figsize=self.config.FIGSIZE, sharex=True)

        # RSI
        ax1 = axes[0]
        ax1.plot(df['trade_date'], df['RSI'], label='RSI', linewidth=2, color='purple')
        ax1.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Overbought')
        ax1.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Oversold')
        ax1.set_ylabel('RSI')
        ax1.set_title(f'{stock_code} - RSI & KDJ')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)

        # KDJ
        ax2 = axes[1]
        ax2.plot(df['trade_date'], df['KDJ_K'], label='K', linewidth=2)
        ax2.plot(df['trade_date'], df['KDJ_D'], label='D', linewidth=2)
        ax2.plot(df['trade_date'], df['KDJ_J'], label='J', linewidth=2, alpha=0.7)
        ax2.axhline(y=80, color='red', linestyle='--', alpha=0.3)
        ax2.axhline(y=20, color='green', linestyle='--', alpha=0.3)
        ax2.set_ylabel('KDJ')
        ax2.set_xlabel('Date')
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def _plot_volume(self, stock_code, df):
        """绘制成交量图"""
        fig, ax = plt.subplots(figsize=self.config.FIGSIZE)

        colors = ['red' if df['close'].iloc[i] >= df['open'].iloc[i] else 'green'
                 for i in range(len(df))]

        ax.bar(df['trade_date'], df['vol'], color=colors, alpha=0.6, label='Volume')

        # 成交量均线
        for period in self.config.VOLUME_MA_PERIODS:
            if f'VOL_MA{period}' in df.columns:
                ax.plot(df['trade_date'], df[f'VOL_MA{period}'],
                       label=f'VOL MA{period}', linewidth=2)

        ax.set_ylabel('Volume (手)')
        ax.set_xlabel('Date')
        ax.set_title(f'{stock_code} - 成交量分析')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig
