# A股股票交易投资分析工具

一个全面的A股股票投资分析工具，提供资金流向、基本面、研发投入和替代性分析等多维度评估。

## 功能特性

### 1. 资金流向监控
- 实时主力资金流向追踪
- 大单、中单、小单资金分析
- 资金流入流出趋势判断
- 量比和换手率计算

### 2. 基本面分析
- 关键财务指标获取（PE、PB、ROE等）
- 盈利能力评分
- 成长能力评分
- 财务安全性评分
- 估值水平评估

### 3. 研发技术投入分析
- 研发费用追踪
- 研发强度计算（研发费用占营收比例）
- 研发增长率分析
- 技术能力综合评估

### 4. 替代性分析
- 市场地位评估
- 同行估值对比
- 替代性风险评估
- 竞争格局分析

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式一：交互式界面

```bash
python main.py
```

### 方式二：命令行参数

```bash
# 分析单只股票
python src/stock_monitor.py --stock 600036

# 批量分析
python src/stock_monitor.py --batch

# 指定配置文件
python src/stock_monitor.py --config config.yaml --batch
```

## 配置文件

编辑 `config.yaml` 文件来自定义监控参数：

```yaml
stock_monitor:
  stocks:
    - "600036"  # 招商银行
    - "600519"  # 贵州茅台
  update_interval: 30
  data_path: "./data"
  report_path: "./reports"

analysis:
  fund_flow:
    main_net_inflow_threshold: 100000000
  fundamentals:
    pe_ratio_max: 50
    roe_min: 0.08
  rd_analysis:
    rd_ratio_min: 0.03
```

## 项目结构

```
trade-tools/
├── main.py                          # 主入口文件
├── config.yaml                      # 配置文件
├── requirements.txt                 # 依赖包列表
├── src/
│   ├── __init__.py
│   ├── stock_monitor.py             # 综合监控器
│   ├── fund_flow_monitor.py         # 资金流向监控
│   ├── fundamental_analysis.py      # 基本面分析
│   ├── rd_analysis.py               # 研发投入分析
│   └── substitutability_analysis.py # 替代性分析
├── data/                            # 数据存储目录
└── reports/                         # 报告输出目录
```

## 示例输出

程序会生成详细的分析报告，包括：

1. **资金流向分析报告**
   - 实时价格和涨跌幅
   - 主力、超大单、大单资金流向
   - 量比和趋势判断

2. **基本面分析报告**
   - 估值指标（PE、PB、PS）
   - 盈利能力评分
   - 成长能力和安全性评分
   - 综合投资建议

3. **研发投入分析报告**
   - 研发费用规模
   - 研发强度和趋势
   - 技术能力评估

4. **替代性分析报告**
   - 市场地位
   - 同行对比
   - 风险评估

## 技术栈

- Python 3.7+
- akshare: A股数据获取
- pandas: 数据处理
- numpy: 数值计算
- pyyaml: 配置文件解析

## 注意事项

1. 数据来源于公开接口，可能存在延迟
2. 本工具仅供学习参考，不构成投资建议
3. 投资有风险，决策需谨慎

## 开发者

- Version: 1.0.0
- License: MIT

## 更新日志

### v1.0.0 (2024-01-04)
- 初始版本发布
- 实现四大核心分析模块
- 支持单股票和批量分析
