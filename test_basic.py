#!/usr/bin/env python3
"""
基础测试脚本 - 验证代码结构和逻辑
不依赖外部数据源，只测试代码逻辑
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试所有模块能否成功导入"""
    print("=" * 60)
    print("测试1: 模块导入测试")
    print("=" * 60)

    try:
        from fund_flow_monitor import FundFlowMonitor
        print("✓ fund_flow_monitor.py 导入成功")
    except Exception as e:
        print(f"✗ fund_flow_monitor.py 导入失败: {e}")
        return False

    try:
        from fundamental_analysis import FundamentalAnalysis
        print("✓ fundamental_analysis.py 导入成功")
    except Exception as e:
        print(f"✗ fundamental_analysis.py 导入失败: {e}")
        return False

    try:
        from rd_analysis import RDAnalysis
        print("✓ rd_analysis.py 导入成功")
    except Exception as e:
        print(f"✗ rd_analysis.py 导入失败: {e}")
        return False

    try:
        from substitutability_analysis import SubstitutabilityAnalysis
        print("✓ substitutability_analysis.py 导入成功")
    except Exception as e:
        print(f"✗ substitutability_analysis.py 导入失败: {e}")
        return False

    try:
        from stock_monitor import StockMonitor
        print("✓ stock_monitor.py 导入成功")
    except Exception as e:
        print(f"✗ stock_monitor.py 导入失败: {e}")
        return False

    print("\n所有模块导入成功！\n")
    return True


def test_class_instantiation():
    """测试类能否正常实例化"""
    print("=" * 60)
    print("测试2: 类实例化测试")
    print("=" * 60)

    test_stock = "600036"

    try:
        from fund_flow_monitor import FundFlowMonitor
        monitor = FundFlowMonitor(test_stock)
        print(f"✓ FundFlowMonitor 实例化成功 (股票代码: {test_stock})")
        assert monitor.stock_code == test_stock
        print(f"✓ 股票代码属性正确: {monitor.stock_code}")
    except Exception as e:
        print(f"✗ FundFlowMonitor 实例化失败: {e}")
        return False

    try:
        from fundamental_analysis import FundamentalAnalysis
        analyzer = FundamentalAnalysis(test_stock)
        print(f"✓ FundamentalAnalysis 实例化成功")
        assert analyzer.stock_code == test_stock
        print(f"✓ 股票代码属性正确: {analyzer.stock_code}")
    except Exception as e:
        print(f"✗ FundamentalAnalysis 实例化失败: {e}")
        return False

    try:
        from rd_analysis import RDAnalysis
        analyzer = RDAnalysis(test_stock)
        print(f"✓ RDAnalysis 实例化成功")
        assert analyzer.stock_code == test_stock
        print(f"✓ 股票代码属性正确: {analyzer.stock_code}")
    except Exception as e:
        print(f"✗ RDAnalysis 实例化失败: {e}")
        return False

    try:
        from substitutability_analysis import SubstitutabilityAnalysis
        analyzer = SubstitutabilityAnalysis(test_stock)
        print(f"✓ SubstitutabilityAnalysis 实例化成功")
        assert analyzer.stock_code == test_stock
        print(f"✓ 股票代码属性正确: {analyzer.stock_code}")
    except Exception as e:
        print(f"✗ SubstitutabilityAnalysis 实例化失败: {e}")
        return False

    print("\n所有类实例化成功！\n")
    return True


def test_config_loading():
    """测试配置文件加载"""
    print("=" * 60)
    print("测试3: 配置文件加载测试")
    print("=" * 60)

    try:
        # 测试配置文件是否存在
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        if not os.path.exists(config_path):
            print(f"✗ 配置文件不存在: {config_path}")
            return False

        print(f"✓ 配置文件存在: {config_path}")

        # 尝试读取配置
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✓ 配置文件读取成功 (大小: {len(content)} 字节)")

        # 验证配置内容
        required_keys = ['stock_monitor', 'analysis']
        for key in required_keys:
            if key in content:
                print(f"✓ 配置包含必需的键: {key}")
            else:
                print(f"✗ 配置缺少必需的键: {key}")
                return False

        print("\n配置文件加载测试通过！\n")
        return True

    except Exception as e:
        print(f"✗ 配置文件加载失败: {e}")
        return False


def test_helper_methods():
    """测试辅助方法"""
    print("=" * 60)
    print("测试4: 辅助方法测试")
    print("=" * 60)

    try:
        from fundamental_analysis import FundamentalAnalysis
        analyzer = FundamentalAnalysis("600036")

        # 测试 _safe_float 方法
        test_cases = [
            ("100", 100.0),
            ("1,234.56", 1234.56),
            ("-50", -50.0),
            ("", 0.0),
            ("N/A", 0.0),
            (None, 0.0),
        ]

        for input_val, expected in test_cases:
            result = analyzer._safe_float(input_val)
            if result == expected:
                print(f"✓ _safe_float({input_val!r}) = {result}")
            else:
                print(f"✗ _safe_float({input_val!r}) = {result}, 期望 {expected}")
                return False

        print("\n辅助方法测试通过！\n")
        return True

    except Exception as e:
        print(f"✗ 辅助方法测试失败: {e}")
        return False


def test_empty_data_structures():
    """测试空数据结构生成"""
    print("=" * 60)
    print("测试5: 空数据结构测试")
    print("=" * 60)

    try:
        from fund_flow_monitor import FundFlowMonitor
        from fundamental_analysis import FundamentalAnalysis
        from rd_analysis import RDAnalysis

        fund_monitor = FundFlowMonitor("600036")
        empty_fund = fund_monitor._get_empty_fund_flow()

        required_keys = ['date', 'price', 'main_net_inflow', 'volume']
        for key in required_keys:
            if key in empty_fund:
                print(f"✓ 空资金流向数据包含键: {key}")
            else:
                print(f"✗ 空资金流向数据缺少键: {key}")
                return False

        fundamental = FundamentalAnalysis("600036")
        empty_financial = fundamental._get_empty_financial()

        required_keys = ['pe_ratio', 'pb_ratio', 'roe', 'debt_ratio']
        for key in required_keys:
            if key in empty_financial:
                print(f"✓ 空财务数据包含键: {key}")
            else:
                print(f"✗ 空财务数据缺少键: {key}")
                return False

        rd = RDAnalysis("600036")
        empty_rd = rd._get_empty_rd()

        required_keys = ['latest_rd', 'total_rd_4q']
        for key in required_keys:
            if key in empty_rd:
                print(f"✓ 空研发数据包含键: {key}")
            else:
                print(f"✗ 空研发数据缺少键: {key}")
                return False

        print("\n空数据结构测试通过！\n")
        return True

    except Exception as e:
        print(f"✗ 空数据结构测试失败: {e}")
        return False


def test_stock_monitor_init():
    """测试StockMonitor初始化"""
    print("=" * 60)
    print("测试6: StockMonitor初始化测试")
    print("=" * 60)

    try:
        from stock_monitor import StockMonitor

        # 测试无配置文件初始化
        monitor = StockMonitor(config_path=None)
        print("✓ StockMonitor 初始化成功（无配置文件）")

        # 验证默认配置
        if 'stock_monitor' in monitor.config:
            print("✓ 默认配置加载成功")
        else:
            print("✗ 默认配置加载失败")
            return False

        # 测试添加股票
        monitor.add_stock("600036")
        if "600036" in monitor.monitors:
            print("✓ 添加股票成功")
        else:
            print("✗ 添加股票失败")
            return False

        # 测试移除股票
        monitor.remove_stock("600036")
        if "600036" not in monitor.monitors:
            print("✓ 移除股票成功")
        else:
            print("✗ 移除股票失败")
            return False

        print("\nStockMonitor初始化测试通过！\n")
        return True

    except Exception as e:
        print(f"✗ StockMonitor初始化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("       A股股票分析工具 - 基础功能测试")
    print("=" * 60 + "\n")

    tests = [
        ("模块导入", test_imports),
        ("类实例化", test_class_instantiation),
        ("配置加载", test_config_loading),
        ("辅助方法", test_helper_methods),
        ("空数据结构", test_empty_data_structures),
        ("StockMonitor初始化", test_stock_monitor_init),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 发生异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 打印测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {name}")

    print("\n" + "-" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    print("-" * 60 + "\n")

    if passed == total:
        print("🎉 所有测试通过！代码基础逻辑正确。")
        print("\n注意事项:")
        print("1. 由于当前环境限制，无法安装外部依赖（akshare等）")
        print("2. 在实际运行前，请确保安装 requirements.txt 中的依赖")
        print("3. 数据获取功能需要网络连接和有效的API接口")
        print("4. 建议在完整Python环境中进行实际数据测试")
        return 0
    else:
        print("⚠️  部分测试失败，请检查代码。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
