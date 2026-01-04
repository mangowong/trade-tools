# -*- coding: utf-8 -*-
"""
A股监控系统 - 主程序
"""
import sys
import os
from datetime import datetime, timedelta
import logging
import argparse

from config import config
from data_fetcher import get_data_fetcher
from technical_analysis import TechnicalAnalyzer
from fundamental_analysis import FundamentalAnalyzer
from money_flow_analysis import MoneyFlowAnalyzer
from report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class StockMonitor:
    """股票监控主类"""

    def __init__(self, token=None):
        logger.info("=" * 60)
        logger.info("A股投资分析工具启动")
        logger.info("=" * 60)

        # 初始化组件
        self.fetcher = get_data_fetcher(token or config.TUSHARE_TOKEN)
        self.technical_analyzer = TechnicalAnalyzer(config)
        self.fundamental_analyzer = FundamentalAnalyzer(config)
        self.money_flow_analyzer = MoneyFlowAnalyzer(config)
        self.report_generator = ReportGenerator(config)

        # 创建数据目录
        os.makedirs(config.DATA_DIR, exist_ok=True)

    def monitor_stock(self, stock_code, days=60):
        """监控单只股票"""
        logger.info(f"\n开始分析股票: {stock_code}")
        logger.info("-" * 40)

        # 计算日期范围
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

        # 1. 获取数据
        logger.info("正在获取数据...")
        stock_data = self.fetcher.get_stock_data(stock_code, start_date, end_date)
        money_flow = self.fetcher.get_money_flow(stock_code, start_date, end_date)
        fundamental = self.fetcher.get_fundamental(stock_code)

        if stock_data is None or stock_data.empty:
            logger.error(f"无法获取{stock_code}的数据，跳过分析")
            return None

        logger.info(f"获取数据成功: 行情{len(stock_data)}条, 资金流{len(money_flow) if money_flow is not None else 0}条")

        # 2. 技术分析
        logger.info("正在进行技术分析...")
        stock_data = self.technical_analyzer.calculate_all_indicators(stock_data)
        trend_analysis = self.technical_analyzer.analyze_trend(stock_data)
        momentum_analysis = self.technical_analyzer.analyze_momentum(stock_data)
        technical_score = self.technical_analyzer.calculate_technical_score(trend_analysis, momentum_analysis)

        technical_data = {
            'trend': trend_analysis,
            'momentum': momentum_analysis,
            'technical_score': technical_score
        }
        logger.info(f"技术面评分: {technical_score}/100 - {trend_analysis['description']}")

        # 3. 基本面分析
        logger.info("正在进行基本面分析...")
        fundamental_analysis = self.fundamental_analyzer.analyze(fundamental)
        logger.info(f"基本面评分: {fundamental_analysis.get('overall_score', 0)}/100")

        # 4. 资金流分析
        logger.info("正在进行资金流分析...")
        money_flow_analysis = self.money_flow_analyzer.analyze(money_flow)
        logger.info(f"资金流评分: {money_flow_analysis.get('overall_score', 0)}/100 - {money_flow_analysis.get('trend', {}).get('description', '')}")

        # 5. 整合分析结果
        analysis_data = {
            'technical': technical_data,
            'fundamental': fundamental_analysis,
            'money_flow': money_flow_analysis
        }

        # 6. 生成报告
        logger.info("正在生成分析报告...")
        report = self.report_generator.generate_daily_report(stock_code, analysis_data)

        # 7. 生成图表
        logger.info("正在生成图表...")
        chart_files = self.report_generator.generate_charts(stock_code, stock_data, analysis_data)
        report['charts'] = chart_files

        # 8. 保存报告
        report_file = self.report_generator.save_report(report)
        report['report_file'] = report_file

        # 打印摘要
        self._print_summary(report)

        logger.info(f"✓ {stock_code} 分析完成!")
        return report

    def monitor_batch(self, stock_codes=None, days=60):
        """批量监控股票"""
        if stock_codes is None:
            stock_codes = config.DEFAULT_STOCKS

        logger.info(f"\n批量监控 {len(stock_codes)} 只股票")
        logger.info("=" * 60)

        results = {}
        for stock_code in stock_codes:
            try:
                result = self.monitor_stock(stock_code, days)
                if result:
                    results[stock_code] = result
            except Exception as e:
                logger.error(f"分析{stock_code}时出错: {e}")
                continue

        # 生成汇总报告
        if results:
            self._generate_summary_report(results)

        return results

    def _print_summary(self, report):
        """打印分析摘要"""
        summary = report['summary']
        print(f"\n{'='*60}")
        print(f"【{report['stock_code']}】分析摘要")
        print(f"{'='*60}")
        print(f"综合评分: {summary['overall_score']}/100")
        print(f"投资评级: {summary['rating']}")
        print(f"- 技术面: {summary['technical_score']}/100 ({report['technical']['trend']['description']})")
        print(f"- 基本面: {summary['fundamental_score']}/100")
        print(f"- 资金流: {summary['money_flow_score']}/100 ({report['money_flow']['trend']['description']})")
        print(f"\n投资建议:")
        for i, rec in enumerate(report['recommendation'][:3], 1):
            print(f"  {i}. {rec}")
        print(f"{'='*60}\n")

    def _generate_summary_report(self, results):
        """生成汇总报告"""
        filename = f"{config.OUTPUT_DIR}/summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("A股批量监控汇总报告\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"监控股票数: {len(results)}\n")
                f.write("=" * 80 + "\n\n")

                # 按评分排序
                sorted_results = sorted(
                    results.items(),
                    key=lambda x: x[1]['summary']['overall_score'],
                    reverse=True
                )

                for stock_code, report in sorted_results:
                    summary = report['summary']
                    f.write(f"{stock_code}:\n")
                    f.write(f"  综合评分: {summary['overall_score']}/100\n")
                    f.write(f"  投资评级: {summary['rating']}\n")
                    f.write(f"  技术面: {summary['technical_score']}/100\n")
                    f.write(f"  基本面: {summary['fundamental_score']}/100\n")
                    f.write(f"  资金流: {summary['money_flow_score']}/100\n")
                    f.write("\n")

            logger.info(f"汇总报告已保存: {filename}")
        except Exception as e:
            logger.error(f"保存汇总报告失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='A股投资分析工具')
    parser.add_argument('--stock', type=str, help='股票代码 (如: 000001.SZ)')
    parser.add_argument('--token', type=str, help='Tushare Token (可选，不填则使用免费数据源)')
    parser.add_argument('--days', type=int, default=60, help='分析天数 (默认60天)')
    parser.add_argument('--batch', action='store_true', help='批量监控模式')

    args = parser.parse_args()

    # 创建监控器
    monitor = StockMonitor(token=args.token)

    if args.batch:
        # 批量监控
        monitor.monitor_batch(days=args.days)
    elif args.stock:
        # 单只股票
        monitor.monitor_stock(args.stock, days=args.days)
    else:
        # 默认批量监控
        monitor.monitor_batch(days=args.days)


if __name__ == '__main__':
    main()
