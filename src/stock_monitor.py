"""
股票监控主程序
整合所有分析模块，提供统一的监控接口
"""
import sys
import os
import yaml
from datetime import datetime
from pathlib import Path

# 添加src目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fund_flow_monitor import FundFlowMonitor
from fundamental_analysis import FundamentalAnalysis
from rd_analysis import RDAnalysis
from substitutability_analysis import SubstitutabilityAnalysis


class StockMonitor:
    """股票综合监控器"""

    def __init__(self, config_path: str = None):
        """
        初始化股票监控器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.monitors = {}

    def _load_config(self, config_path: str = None) -> dict:
        """加载配置文件"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {
                'stock_monitor': {
                    'stocks': ['600036'],
                    'data_path': './data',
                    'report_path': './reports'
                }
            }

    def add_stock(self, stock_code: str):
        """
        添加监控股票

        Args:
            stock_code: 股票代码
        """
        if stock_code not in self.monitors:
            self.monitors[stock_code] = {
                'fund_flow': FundFlowMonitor(stock_code),
                'fundamental': FundamentalAnalysis(stock_code),
                'rd_analysis': RDAnalysis(stock_code),
                'substitutability': SubstitutabilityAnalysis(stock_code)
            }
            print(f"已添加股票 {stock_code} 到监控列表")
        else:
            print(f"股票 {stock_code} 已在监控列表中")

    def remove_stock(self, stock_code: str):
        """
        移除监控股票

        Args:
            stock_code: 股票代码
        """
        if stock_code in self.monitors:
            del self.monitors[stock_code]
            print(f"已移除股票 {stock_code}")
        else:
            print(f"股票 {stock_code} 不在监控列表中")

    def analyze_stock(self, stock_code: str) -> dict:
        """
        全面分析指定股票

        Args:
            stock_code: 股票代码

        Returns:
            综合分析结果
        """
        if stock_code not in self.monitors:
            self.add_stock(stock_code)

        monitors = self.monitors[stock_code]

        print(f"\n{'='*60}")
        print(f"开始分析股票: {stock_code}")
        print(f"{'='*60}\n")

        # 1. 资金流向分析
        print("正在分析资金流向...")
        fund_flow_data = monitors['fund_flow'].get_realtime_fund_flow()
        fund_trend = monitors['fund_flow'].analyze_fund_trend(days=5)

        # 2. 基本面分析
        print("正在分析基本面...")
        fundamental_data = monitors['fundamental'].get_financial_indicators()
        profitability_score = monitors['fundamental'].get_profitability_score()
        growth_score = monitors['fundamental'].get_growth_score()
        safety_score = monitors['fundamental'].get_safety_score()

        # 3. 研发投入分析
        print("正在分析研发投入...")
        rd_capability = monitors['rd_analysis'].evaluate_technical_capability()
        rd_intensity = monitors['rd_analysis'].calculate_rd_intensity()

        # 4. 替代性分析
        print("正在分析替代性风险...")
        market_position = monitors['substitutability'].analyze_market_position()
        risk_assessment = monitors['substitutability'].analyze_substitutability_risk()

        # 综合评分计算
        comprehensive_score = self._calculate_comprehensive_score(
            profitability_score, growth_score, safety_score,
            rd_capability['score'], 100 - risk_assessment['risk_score']
        )

        result = {
            'stock_code': stock_code,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'fund_flow': {
                'data': fund_flow_data,
                'trend': fund_trend
            },
            'fundamental': {
                'data': fundamental_data,
                'profitability_score': profitability_score,
                'growth_score': growth_score,
                'safety_score': safety_score
            },
            'rd_analysis': {
                'capability': rd_capability,
                'intensity': rd_intensity
            },
            'substitutability': {
                'market_position': market_position,
                'risk': risk_assessment
            },
            'comprehensive_score': comprehensive_score
        }

        print(f"\n分析完成！综合评分: {comprehensive_score:.1f}/100\n")
        return result

    def _calculate_comprehensive_score(self, profitability: float, growth: float,
                                      safety: float, rd: float, anti_risk: float) -> float:
        """
        计算综合评分

        Args:
            profitability: 盈利能力评分
            growth: 成长能力评分
            safety: 安全性评分
            rd: 研发能力评分
            anti_risk: 抗风险能力评分

        Returns:
            综合评分
        """
        # 权重分配
        weights = {
            'profitability': 0.25,
            'growth': 0.25,
            'safety': 0.25,
            'rd': 0.10,
            'anti_risk': 0.15
        }

        score = (
            profitability * weights['profitability'] +
            growth * weights['growth'] +
            safety * weights['safety'] +
            rd * weights['rd'] +
            anti_risk * weights['anti_risk']
        )

        return score

    def generate_report(self, stock_code: str) -> str:
        """
        生成完整分析报告

        Args:
            stock_code: 股票代码

        Returns:
            完整报告文本
        """
        if stock_code not in self.monitors:
            self.add_stock(stock_code)

        monitors = self.monitors[stock_code]

        # 生成各模块报告
        fund_report = monitors['fund_flow'].generate_fund_flow_report()
        fundamental_report = monitors['fundamental'].generate_fundamental_report()
        rd_report = monitors['rd_analysis'].generate_rd_report()
        substitutability_report = monitors['substitutability'].generate_substitutability_report()

        # 组合报告
        full_report = f"""
{'#'*60}
{'#'*60}
{'#'*20} 股票投资分析报告 {'#'*20}
{'#'*20} {stock_code} {'#'*30}
{'#'*20} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {'#'*17}
{'#'*60}
{'#'*60}

{fund_report}

{'-'*60}

{fundamental_report}

{'-'*60}

{rd_report}

{'-'*60}

{substitutability_report}

{'='*60}
报告生成完毕
{'='*60}
"""

        return full_report

    def save_report(self, stock_code: str, report_path: str = None):
        """
        保存报告到文件

        Args:
            stock_code: 股票代码
            report_path: 报告保存路径
        """
        if report_path is None:
            report_path = self.config.get('stock_monitor', {}).get('report_path', './reports')

        # 确保目录存在
        Path(report_path).mkdir(parents=True, exist_ok=True)

        # 生成报告
        report = self.generate_report(stock_code)

        # 保存文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{stock_code}_analysis_{timestamp}.txt"
        filepath = os.path.join(report_path, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"报告已保存到: {filepath}")
        return filepath

    def monitor_batch(self, stock_codes: list = None):
        """
        批量监控股票

        Args:
            stock_codes: 股票代码列表
        """
        if stock_codes is None:
            stock_codes = self.config.get('stock_monitor', {}).get('stocks', ['600036'])

        results = {}

        for stock_code in stock_codes:
            print(f"\n{'#'*60}")
            print(f"正在监控股票: {stock_code}")
            print(f"{'#'*60}\n")

            try:
                result = self.analyze_stock(stock_code)
                results[stock_code] = result

                # 生成并保存报告
                self.save_report(stock_code)

            except Exception as e:
                print(f"分析股票 {stock_code} 时出错: {e}")
                results[stock_code] = {'error': str(e)}

        return results


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='A股股票投资分析工具')
    parser.add_argument('--stock', type=str, help='股票代码')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--batch', action='store_true', help='批量分析模式')
    parser.add_argument('--report', type=str, help='报告保存路径')

    args = parser.parse_args()

    # 创建监控器
    monitor = StockMonitor(config_path=args.config)

    if args.batch:
        # 批量分析模式
        results = monitor.monitor_batch()
        print("\n批量分析完成！")
    elif args.stock:
        # 单股票分析模式
        result = monitor.analyze_stock(args.stock)

        # 生成报告
        if args.report:
            monitor.save_report(args.stock, args.report)
        else:
            report = monitor.generate_report(args.stock)
            print(report)
    else:
        # 默认分析配置文件中的股票
        results = monitor.monitor_batch()
        print("\n分析完成！")


if __name__ == '__main__':
    main()
