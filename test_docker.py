#!/usr/bin/env python3
"""
Docker环境测试脚本
测试在完整依赖环境下代码是否能够正常导入和初始化
"""
import sys
import os

sys.path.insert(0, '/app/src')

def test_imports_with_deps():
    """测试带依赖的模块导入"""
    print("=" * 70)
    print("测试: 在Docker环境中导入所有模块")
    print("=" * 70)

    results = []

    # 测试第三方库
    print("\n1. 测试第三方依赖库...")
    try:
        import pandas
        print(f"   ✓ pandas {pandas.__version__}")
    except ImportError as e:
        print(f"   ✗ pandas 导入失败: {e}")
        results.append(False)

    try:
        import numpy
        print(f"   ✓ numpy {numpy.__version__}")
    except ImportError as e:
        print(f"   ✗ numpy 导入失败: {e}")
        results.append(False)

    try:
        import yaml
        print(f"   ✓ pyaml {yaml.__version__}")
    except ImportError as e:
        print(f"   ✗ yaml 导入失败: {e}")
        results.append(False)

    try:
        import akshare
        print(f"   ✓ akshare {akshare.__version__}")
    except ImportError as e:
        print(f"   ✗ akshare 导入失败: {e}")
        results.append(False)

    # 测试项目模块
    print("\n2. 测试项目模块导入...")
    try:
        from fund_flow_monitor import FundFlowMonitor
        print("   ✓ fund_flow_monitor 导入成功")

        # 测试实例化
        monitor = FundFlowMonitor("600036")
        print(f"   ✓ FundFlowMonitor 实例化成功 (股票: {monitor.stock_code})")
        results.append(True)
    except Exception as e:
        print(f"   ✗ fund_flow_monitor 失败: {e}")
        results.append(False)

    try:
        from fundamental_analysis import FundamentalAnalysis
        print("   ✓ fundamental_analysis 导入成功")

        analyzer = FundamentalAnalysis("600036")
        print(f"   ✓ FundamentalAnalysis 实例化成功")
        results.append(True)
    except Exception as e:
        print(f"   ✗ fundamental_analysis 失败: {e}")
        results.append(False)

    try:
        from rd_analysis import RDAnalysis
        print("   ✓ rd_analysis 导入成功")

        analyzer = RDAnalysis("600036")
        print(f"   ✓ RDAnalysis 实例化成功")
        results.append(True)
    except Exception as e:
        print(f"   ✗ rd_analysis 失败: {e}")
        results.append(False)

    try:
        from substitutability_analysis import SubstitutabilityAnalysis
        print("   ✓ substitutability_analysis 导入成功")

        analyzer = SubstitutabilityAnalysis("600036")
        print(f"   ✓ SubstitutabilityAnalysis 实例化成功")
        results.append(True)
    except Exception as e:
        print(f"   ✗ substitutability_analysis 失败: {e}")
        results.append(False)

    try:
        from stock_monitor import StockMonitor
        print("   ✓ stock_monitor 导入成功")

        monitor = StockMonitor()
        print(f"   ✓ StockMonitor 实例化成功")
        results.append(True)
    except Exception as e:
        print(f"   ✗ stock_monitor 失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(False)

    # 测试配置文件
    print("\n3. 测试配置文件...")
    try:
        import yaml
        with open('/app/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            print(f"   ✓ 配置文件加载成功")
            print(f"   ✓ 监控股票数量: {len(config['stock_monitor']['stocks'])}")
            results.append(True)
    except Exception as e:
        print(f"   ✗ 配置文件加载失败: {e}")
        results.append(False)

    # 测试数据目录
    print("\n4. 测试目录结构...")
    dirs = ['/app/data', '/app/reports']
    for dir_path in dirs:
        if os.path.exists(dir_path):
            print(f"   ✓ {dir_path} 存在")
        else:
            print(f"   ✗ {dir_path} 不存在")
            results.append(False)

    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total} 项测试")

    if passed == total:
        print("\n✅ 所有测试通过！代码可以在Docker环境中正常运行。")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 项测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(test_imports_with_deps())
