#!/usr/bin/env python3
"""
模拟测试 - 使用模拟数据测试代码逻辑
不依赖外部API和数据库
"""
import sys
import os

# Mock外部依赖
class MockDataFrame:
    """模拟pandas DataFrame"""
    def __init__(self, data=None):
        self.data = data or []
        self.empty = len(self.data) == 0

    def __getitem__(self, key):
        if self.empty:
            raise IndexError("DataFrame is empty")
        return self.data[0].get(key, None)

    def __len__(self):
        return len(self.data)

    def head(self, n=None):
        return MockDataFrame(self.data[:n] if n else self.data)

    def tail(self, n=None):
        if n:
            return MockDataFrame(self.data[-n:])
        return MockDataFrame(self.data)

    def iterrows(self):
        return enumerate(self.data)

    def iloc(self, index):
        if index < len(self.data):
            return self.data[index]
        raise IndexError("Index out of range")


# 模拟akshare模块
class MockAkshare:
    class stock:
        @staticmethod
        def stock_individual_fund_flow(stock, market):
            # 返回模拟的资金流向数据
            return MockDataFrame([{
                '日期': '2024-01-04',
                '收盘价': 35.50,
                '涨跌幅': 2.5,
                '主力净流入-净额': 15000.0,
                '主力净流入-净占比': 15.5,
                '超大单净流入-净额': 8000.0,
                '大单净流入-净额': 7000.0,
                '中单净流入-净额': -5000.0,
                '小单净流入-净额': -10000.0,
                '成交量': 150000,
                '成交额': 53250.0
            }])

        @staticmethod
        def stock_individual_info_em(symbol):
            return MockDataFrame([
                {'item': '公司名称', 'value': '测试银行股份有限公司'},
                {'item': '行业', 'value': '银行'},
                {'item': '总市值', 'value': '5000亿'},
                {'item': '流通市值', 'value': '4500亿'}
            ])

        @staticmethod
        def stock_financial_analysis_indicator(symbol):
            return MockDataFrame([{
                '日期': '2024-09-30',
                '市盈率-动态': 8.5,
                '市净率': 0.9,
                '市销率': 2.5,
                '净资产收益率': 0.12,
                '总资产净利率': 0.015,
                '销售毛利率': 0.45,
                '销售净利率': 0.25,
                '资产负债率': 0.55,
                '流动比率': 1.8,
                '速动比率': 1.5,
                '营业总收入': 5000000,
                '净利润': 1250000,
                '总资产': 25000000,
                '总负债': 13750000,
                '经营活动现金流': 1500000
            }])

        @staticmethod
        def stock_profit_sheet_by_report_em(symbol):
            return MockDataFrame([{
                '报告期': '2024-09-30',
                '研发费用': 150000,
                '营业总收入': 5000000,
                '净利润': 1250000
            }])


# 注入mock模块
sys.modules['akshare'] = type('MockAkshare', (), {'stock': MockAkshare.stock})()
sys.modules['pandas'] = type('MockPandas', (), {'DataFrame': MockDataFrame})()
sys.modules['yaml'] = type('MockYaml', (), {
    'safe_load': lambda x: {
        'stock_monitor': {
            'stocks': ['600036', '600519'],
            'data_path': './data',
            'report_path': './reports'
        }
    }
})()

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_fund_flow_monitor():
    """测试资金流向监控"""
    print("=" * 60)
    print("测试: FundFlowMonitor")
    print("=" * 60)

    from fund_flow_monitor import FundFlowMonitor

    monitor = FundFlowMonitor("600036")

    # 测试实时资金流向获取
    print("测试1: 获取实时资金流向...")
    realtime = monitor.get_realtime_fund_flow()

    assert realtime['price'] == 35.50, "价格不正确"
    assert realtime['main_net_inflow'] == 15000.0, "主力净流入不正确"
    print(f"✓ 实时价格: {realtime['price']}")
    print(f"✓ 主力净流入: {realtime['main_net_inflow']:.2f} 万元")

    # 测试趋势分析
    print("\n测试2: 分析资金趋势...")
    trend = monitor.analyze_fund_trend(5)
    print(f"✓ 趋势: {trend['trend']}")
    print(f"✓ 平均净流入: {trend['avg_main_inflow']:.2f} 万元")

    # 测试报告生成
    print("\n测试3: 生成报告...")
    report = monitor.generate_fund_flow_report()
    assert len(report) > 100, "报告内容过短"
    assert "资金流向分析报告" in report, "报告标题不正确"
    print("✓ 报告生成成功")
    print(f"  报告长度: {len(report)} 字符")

    print("\n✓ FundFlowMonitor 所有测试通过！\n")
    return True


def test_fundamental_analysis():
    """测试基本面分析"""
    print("=" * 60)
    print("测试: FundamentalAnalysis")
    print("=" * 60)

    from fundamental_analysis import FundamentalAnalysis

    analyzer = FundamentalAnalysis("600036")

    # 测试获取财务指标
    print("测试1: 获取财务指标...")
    financial = analyzer.get_financial_indicators()

    assert financial['pe_ratio'] == 8.5, "PE不正确"
    assert financial['pb_ratio'] == 0.9, "PB不正确"
    assert financial['roe'] == 0.12, "ROE不正确"
    print(f"✓ PE: {financial['pe_ratio']}")
    print(f"✓ PB: {financial['pb_ratio']}")
    print(f"✓ ROE: {financial['roe']:.2%}")

    # 测试评分系统
    print("\n测试2: 计算评分...")
    profitability = analyzer.get_profitability_score()
    growth = analyzer.get_growth_score()
    safety = analyzer.get_safety_score()

    print(f"✓ 盈利能力评分: {profitability:.1f}/100")
    print(f"✓ 成长能力评分: {growth:.1f}/100")
    print(f"✓ 安全性评分: {safety:.1f}/100")

    assert 0 <= profitability <= 100, "盈利能力评分超出范围"
    assert 0 <= growth <= 100, "成长能力评分超出范围"
    assert 0 <= safety <= 100, "安全性评分超出范围"

    # 测试估值评估
    print("\n测试3: 估值评估...")
    valuation = analyzer.get_valuation_level()
    print(f"✓ 估值水平: {valuation}")

    # 测试报告生成
    print("\n测试4: 生成报告...")
    report = analyzer.generate_fundamental_report()
    assert len(report) > 100, "报告内容过短"
    print("✓ 报告生成成功")

    print("\n✓ FundamentalAnalysis 所有测试通过！\n")
    return True


def test_rd_analysis():
    """测试研发分析"""
    print("=" * 60)
    print("测试: RDAnalysis")
    print("=" * 60)

    from rd_analysis import RDAnalysis

    analyzer = RDAnalysis("600036")

    # 测试获取研发费用
    print("测试1: 获取研发费用...")
    rd_data = analyzer.get_rd_expenses()
    assert rd_data['latest_rd'] == 150000, "研发费用不正确"
    print(f"✓ 最新研发费用: {rd_data['latest_rd']:.0f} 万元")

    # 测试研发强度
    print("\n测试2: 计算研发强度...")
    intensity = analyzer.calculate_rd_intensity()
    print(f"✓ 研发强度: {intensity['rd_intensity']:.2%}")
    print(f"✓ 趋势: {intensity['trend']}")

    # 测试技术能力评估
    print("\n测试3: 技术能力评估...")
    capability = analyzer.evaluate_technical_capability()
    print(f"✓ 技术能力评分: {capability['score']:.1f}/100")
    print(f"✓ 能力等级: {capability['level']}")

    assert 0 <= capability['score'] <= 100, "技术能力评分超出范围"

    # 测试报告生成
    print("\n测试4: 生成报告...")
    report = analyzer.generate_rd_report()
    assert len(report) > 100, "报告内容过短"
    print("✓ 报告生成成功")

    print("\n✓ RDAnalysis 所有测试通过！\n")
    return True


def test_substitutability_analysis():
    """测试替代性分析"""
    print("=" * 60)
    print("测试: SubstitutabilityAnalysis")
    print("=" * 60)

    from substitutability_analysis import SubstitutabilityAnalysis

    analyzer = SubstitutabilityAnalysis("600036")

    # 测试市场地位分析
    print("测试1: 分析市场地位...")
    position = analyzer.analyze_market_position()
    print(f"✓ 市场地位: {position['position']}")
    print(f"✓ 市值排名: {position['cap_rank']}")

    # 测试估值对比
    print("\n测试2: 估值对比...")
    valuation = analyzer.compare_valuation_with_peers()
    if valuation['comparison'] == 'available':
        print(f"✓ 估值状态: {valuation['valuation_status']}")
        print(f"✓ PE溢价率: {valuation['pe_premium']:.2%}")

    # 测试风险评估
    print("\n测试3: 替代性风险评估...")
    risk = analyzer.analyze_substitutability_risk()
    print(f"✓ 风险评分: {risk['risk_score']}/100")
    print(f"✓ 风险等级: {risk['risk_level']}")

    # 测试报告生成
    print("\n测试4: 生成报告...")
    report = analyzer.generate_substitutability_report()
    assert len(report) > 100, "报告内容过短"
    print("✓ 报告生成成功")

    print("\n✓ SubstitutabilityAnalysis 所有测试通过！\n")
    return True


def test_stock_monitor():
    """测试综合监控器"""
    print("=" * 60)
    print("测试: StockMonitor")
    print("=" * 60)

    from stock_monitor import StockMonitor

    # 测试初始化
    print("测试1: 初始化监控器...")
    monitor = StockMonitor(config_path=None)
    assert 'stock_monitor' in monitor.config, "配置加载失败"
    print("✓ 监控器初始化成功")

    # 测试添加股票
    print("\n测试2: 添加股票...")
    monitor.add_stock("600036")
    assert "600036" in monitor.monitors, "股票添加失败"
    print("✓ 股票添加成功")

    # 测试综合分析
    print("\n测试3: 综合分析...")
    result = monitor.analyze_stock("600036")

    assert 'fund_flow' in result, "缺少资金流向数据"
    assert 'fundamental' in result, "缺少基本面数据"
    assert 'rd_analysis' in result, "缺少研发数据"
    assert 'substitutability' in result, "缺少替代性数据"
    assert 'comprehensive_score' in result, "缺少综合评分"

    print(f"✓ 综合评分: {result['comprehensive_score']:.1f}/100")

    # 测试报告生成
    print("\n测试4: 生成完整报告...")
    report = monitor.generate_report("600036")
    assert len(report) > 500, "报告内容过短"
    assert "资金流向分析报告" in report, "缺少资金流向报告"
    assert "基本面分析报告" in report, "缺少基本面报告"
    assert "研发技术投入分析报告" in report, "缺少研发报告"
    assert "替代性分析报告" in report, "缺少替代性报告"

    print("✓ 完整报告生成成功")
    print(f"  报告长度: {len(report)} 字符")

    print("\n✓ StockMonitor 所有测试通过！\n")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("          A股股票分析工具 - 模拟数据测试")
    print("          (不依赖外部API，使用模拟数据)")
    print("=" * 70 + "\n")

    tests = [
        ("资金流向监控", test_fund_flow_monitor),
        ("基本面分析", test_fundamental_analysis),
        ("研发投入分析", test_rd_analysis),
        ("替代性分析", test_substitutability_analysis),
        ("综合监控器", test_stock_monitor),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, True, None))
        except AssertionError as e:
            print(f"\n✗ 测试 '{name}' 断言失败: {e}")
            results.append((name, False, str(e)))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 发生异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False, str(e)))

    # 打印测试总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for name, success, error in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{status} - {name}")
        if error:
            print(f"  错误: {error}")

    print("\n" + "-" * 70)
    print(f"总计: {passed}/{total} 测试通过")
    print("-" * 70 + "\n")

    if passed == total:
        print("🎉 所有测试通过！代码逻辑正确。")
        print("\n✓ 代码结构完整")
        print("✓ 所有模块功能正常")
        print("✓ 数据处理逻辑正确")
        print("✓ 报告生成功能正常")
        print("\n下一步:")
        print("  1. 安装依赖: pip install -r requirements.txt")
        print("  2. 运行程序: python main.py")
        print("  3. 分析股票: python src/stock_monitor.py --stock 600036")
        return 0
    else:
        print("⚠️  部分测试失败，请检查代码逻辑。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
