#!/usr/bin/env python3
"""
语法和结构测试脚本 - 不依赖外部库
"""
import ast
import os
import sys


def check_python_syntax(filepath):
    """检查Python文件语法是否正确"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)


def check_file_structure(filepath):
    """检查文件结构"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []

    # 检查是否有基本的类定义
    if 'class ' not in content and 'def ' not in content:
        issues.append("文件中既没有类定义也没有函数定义")

    # 检查是否有文档字符串
    if '"""' not in content and "'''" not in content:
        issues.append("缺少文档字符串")

    # 检查基本代码质量
    lines = content.split('\n')
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

    if len(code_lines) < 10:
        issues.append("代码行数过少")

    return issues


def test_all_python_files():
    """测试所有Python文件"""
    print("=" * 70)
    print("                Python代码语法和结构测试")
    print("=" * 70 + "\n")

    # 定义要测试的文件
    test_files = [
        'main.py',
        'src/__init__.py',
        'src/fund_flow_monitor.py',
        'src/fundamental_analysis.py',
        'src/rd_analysis.py',
        'src/substitutability_analysis.py',
        'src/stock_monitor.py',
    ]

    results = []
    total_lines = 0

    for filepath in test_files:
        if not os.path.exists(filepath):
            print(f"✗ 文件不存在: {filepath}")
            results.append((filepath, False, "文件不存在"))
            continue

        # 检查语法
        syntax_ok, syntax_error = check_python_syntax(filepath)

        if not syntax_ok:
            print(f"✗ {filepath}")
            print(f"  语法错误: {syntax_error}\n")
            results.append((filepath, False, syntax_error))
            continue

        # 检查结构
        structure_issues = check_file_structure(filepath)

        # 统计代码行数
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = len([l for l in f if l.strip()])

        total_lines += lines

        if structure_issues:
            print(f"⚠️  {filepath} ({lines} 行)")
            for issue in structure_issues:
                print(f"  - {issue}")
            print()
            results.append((filepath, True, "有警告"))
        else:
            print(f"✓ {filepath} ({lines} 行)")
            results.append((filepath, True, "无问题"))

    # 测试配置文件
    print("\n配置文件检查:")
    config_files = ['config.yaml', 'requirements.txt', '.gitignore', 'README.md']
    for config_file in config_files:
        if os.path.exists(config_file):
            size = os.path.getsize(config_file)
            print(f"✓ {config_file} ({size} 字节)")
        else:
            print(f"✗ {config_file} (缺失)")

    # 打印总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)

    for filepath, ok, msg in results:
        status = "✓" if ok else "✗"
        print(f"{status} {filepath:40s} - {msg}")

    print("\n" + "-" * 70)
    print(f"代码统计:")
    print(f"  总代码行数: {total_lines} 行")
    print(f"  文件数量: {len(test_files)} 个")
    print(f"  语法检查: {passed}/{total} 通过")
    print("-" * 70 + "\n")

    # 分析代码结构
    print("=" * 70)
    print("代码结构分析")
    print("=" * 70 + "\n")

    for filepath in test_files:
        if not os.path.exists(filepath):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 统计类和函数
        try:
            tree = ast.parse(content)
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            if classes or functions:
                print(f"\n{filepath}:")
                if classes:
                    print(f"  类定义 ({len(classes)}): {', '.join(classes[:3])}{'...' if len(classes) > 3 else ''}")
                if functions:
                    print(f"  函数定义 ({len(functions)}): {', '.join(functions[:5])}{'...' if len(functions) > 5 else ''}")
        except:
            pass

    print("\n" + "=" * 70)

    if passed == total:
        print("✓ 所有Python文件语法正确！")
        print("\n注意事项:")
        print("  1. 代码结构完整，包含所有必需的模块")
        print("  2. 在实际运行前需要安装依赖: pip install -r requirements.txt")
        print("  3. 需要Python 3.7+环境")
        print("  4. 数据获取依赖akshare库和网络连接")
        return 0
    else:
        print("✗ 部分文件存在语法错误")
        return 1


def check_imports():
    """检查导入语句"""
    print("\n" + "=" * 70)
    print("导入依赖分析")
    print("=" * 70 + "\n")

    import_counts = {}

    for filename in os.listdir('src'):
        if not filename.endswith('.py'):
            continue

        filepath = os.path.join('src', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        lib = alias.name.split('.')[0]
                        import_counts[lib] = import_counts.get(lib, 0) + 1
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        lib = node.module.split('.')[0]
                        import_counts[lib] = import_counts.get(lib, 0) + 1
        except:
            pass

    # 分析依赖
    standard_libs = {'os', 'sys', 'datetime', 'typing', 'warnings', 'pathlib'}
    external_libs = {k: v for k, v in import_counts.items() if k not in standard_libs}

    print("外部依赖库:")
    for lib, count in sorted(external_libs.items(), key=lambda x: -x[1]):
        print(f"  {lib:20s} - 使用 {count} 次")

    print("\n这些依赖需要在requirements.txt中定义")


if __name__ == '__main__':
    result = test_all_python_files()
    check_imports()
    sys.exit(result)
