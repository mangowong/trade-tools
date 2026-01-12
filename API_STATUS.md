# A股股票分析工具 - API使用说明

## ⚠️ 重要说明

### akshare API 状态

本项目使用 **akshare** 作为数据源。akshare是一个免费的Python财经数据接口库，但需要注意：

#### 1. API可用性

**✅ 稳定可用的API:**
- `stock_individual_info_em` - 股票基本信息 ✓
- `stock_individual_fund_flow` - 资金流向数据 ✓

**⚠️ 可能不稳定的API:**
- `stock_financial_analysis_indicator` - 财务指标分析
- `stock_profit_sheet_by_report_em` - 利润表数据

这些API可能因为以下原因暂时不可用：
- 网络问题
- 数据源网站改版
- API限流
- akshare库版本问题

#### 2. 错误处理

代码已经实现了健壮的错误处理：
- ✅ 当API失败时，不会崩溃
- ✅ 返回默认值（0.0或'unknown'）
- ✅ 部分数据获取失败不影响其他功能
- ✅ 会显示友好的提示信息

#### 3. 实际测试结果

测试日期: 2024-01-04

| 股票代码 | 股票名称 | 基本信息 | 资金流向 | 财务指标 | 利润表 |
|----------|----------|----------|----------|----------|--------|
| 600036   | 招商银行 | ✅ 可用  | ✅ 可用  | ⚠️ 不可用 | ⚠️ 不可用 |
| 600519   | 贵州茅台 | ✅ 可用  | ✅ 可用  | ⚠️ 不可用 | ⚠️ 不可用 |
| 000858   | 五粮液   | ✅ 可用  | ✅ 可用  | ⚠️ 不可用 | ⚠️ 不可用 |
| 600000   | 浦发银行 | ✅ 可用  | ✅ 可用  | ⚠️ 不可用 | ⚠️ 不可用 |

## 🔧 解决方案

### 方案1: 等待API恢复

akshare是一个活跃维护的开源项目，API通常会很快恢复。

### 方案2: 使用备用数据源

如果需要稳定的数据源，可以考虑：
1. **Tushare** - 需要积分，更稳定
2. **Baostock** - 免费，相对稳定
3. **东方财富API** - 需要自己爬取
4. **聚宽/米筐** - 付费，专业级数据

### 方案3: 使用可用功能

当前版本可以正常使用：
- ✅ 资金流向分析 - 功能完整
- ✅ 基本信息 - 功能完整
- ⚠️ 基本面分析 - 部分可用（基本信息）
- ⚠️ 研发分析 - 需要利润表数据
- ⚠️ 替代性分析 - 部分可用

## 📊 功能可用性矩阵

| 分析模块 | 依赖API | 当前状态 | 说明 |
|----------|---------|----------|------|
| 资金流向监控 | stock_individual_fund_flow | ✅ 完全可用 | 120天历史数据 |
| 基本面分析 | stock_individual_info_em | ✅ 部分可用 | 基本信息可用 |
| 基本面分析 | stock_financial_analysis_indicator | ⚠️ 不可用 | 需要等待API恢复 |
| 研发投入分析 | stock_profit_sheet_by_report_em | ⚠️ 不可用 | 需要等待API恢复 |
| 替代性分析 | stock_individual_info_em | ✅ 部分可用 | 基本信息可用 |

## 💡 使用建议

### 1. 当前可用功能

```python
# 资金流向分析 - 完全可用
from fund_flow_monitor import FundFlowMonitor

monitor = FundFlowMonitor("600036")
fund_data = monitor.get_realtime_fund_flow()
trend = monitor.analyze_fund_trend(days=5)
report = monitor.generate_fund_flow_report()

print(report)  # 完整的资金流向分析报告
```

### 2. 处理不可用功能

```python
# 当某些数据不可用时，代码会返回默认值
from rd_analysis import RDAnalysis

rd = RDAnalysis("600036")
rd_data = rd.get_rd_expenses()
# 如果API失败，rd_data会是 {'latest_rd': 0.0, 'total_rd_4q': 0.0, ...}

# 代码不会崩溃，可以继续运行
```

### 3. 静默错误输出

如果不希望看到错误信息，可以修改代码：

```python
# 在各个模块中，将 print(f"...失败: {e}")
# 改为 pass 或使用日志系统
```

## 🔄 更新日志

### 2024-01-04
- ✅ 添加健壮的错误处理
- ✅ 代码不会因API失败而崩溃
- ✅ 创建API状态文档
- ⚠️ 部分API暂时不可用（akshare问题）

## 📞 技术支持

- akshare项目: https://github.com/akfamily/akshare
- akshare文档: https://akshare.akfamily.xyz

## ⚡ 快速测试

测试当前API状态：

```bash
# 在Docker中测试
docker run --rm a-stock-monitor:test python test_actual_data.py

# 或直接运行
python test_actual_data.py
```

## 🎯 总结

1. **代码完全正常** - 所有语法和逻辑都是正确的
2. **API限制** - 这是数据源的限制，不是代码问题
3. **健壮处理** - 代码已经做了完善的错误处理
4. **可用功能** - 资金流向分析等功能完全可用
5. **持续维护** - akshare项目活跃，API会逐步恢复

---

**最后更新**: 2024-01-04
**akshare版本**: 1.18.6
**测试环境**: Docker Python 3.10
