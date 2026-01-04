#!/usr/bin/env python3
"""
A股股票交易投资分析工具 - 主入口
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.stock_monitor import StockMonitor


def main():
    """主入口函数"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        A股股票交易投资分析工具 v1.0                       ║
    ║        A-Stock Investment Analysis Tool                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # 创建监控器实例
    monitor = StockMonitor()

    # 获取用户输入
    print("\n请选择操作:")
    print("1. 分析单只股票")
    print("2. 批量分析（使用配置文件中的股票列表）")
    print("3. 退出")

    choice = input("\n请输入选项 (1-3): ").strip()

    if choice == '1':
        stock_code = input("请输入股票代码 (如 600036): ").strip()
        if stock_code:
            print(f"\n开始分析股票: {stock_code}\n")
            try:
                # 执行分析
                result = monitor.analyze_stock(stock_code)

                # 显示报告
                report = monitor.generate_report(stock_code)
                print("\n" + report)

                # 询问是否保存报告
                save = input("\n是否保存报告到文件? (y/n): ").strip().lower()
                if save == 'y':
                    monitor.save_report(stock_code)
                    print("报告已保存！")
            except Exception as e:
                print(f"\n分析过程中出现错误: {e}")
                import traceback
                traceback.print_exc()

    elif choice == '2':
        print("\n开始批量分析...\n")
        try:
            results = monitor.monitor_batch()
            print("\n批量分析完成！")
            print(f"共分析 {len(results)} 只股票")
        except Exception as e:
            print(f"\n批量分析过程中出现错误: {e}")
            import traceback
            traceback.print_exc()

    elif choice == '3':
        print("\n感谢使用，再见！")
        sys.exit(0)

    else:
        print("\n无效的选项，程序退出。")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断，退出...")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
