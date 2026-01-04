# A股投资分析工具

一个全面的A股股票交易投资分析系统，支持资金流动分析、基本面评估和技术指标分析。

## 功能特性

### 1. 资金流动分析
- 主力资金流入流出监测
- 超大单、大单、中单资金追踪
- 累计资金流趋势分析
- 资金流向评级

### 2. 基本面分析
- **估值分析**: 市盈率(P/E)、市净率(P/B)、市销率(P/S)
- **盈利能力**: ROE、ROA等关键指标
- **成长性**: 营收增长率、利润增长率
- **财务健康**: 资产负债率、流动比率、速动比率
- 综合基本面评分

### 3. 技术分析
- **趋势指标**: 移动平均线(MA5/10/20/30/60)、MACD
- **动量指标**: RSI、KDJ
- **波动指标**: 布林带(BOLL)、ATR
- **成交量分析**: 成交量均线、量价关系
- 综合技术面评分

### 4. 报告生成
- 详细的文字分析报告
- 可视化图表(K线、MACD、RSI、KDJ、成交量)
- 投资建议和风险提示
- 批量监控汇总报告

## 安装

### 环境要求
- Python 3.7+
- pandas, numpy, matplotlib, seaborn

### 安装依赖

```bash
pip install -r requirements.txt
```

### 注意事项

#### Windows用户安装TA-Lib
```bash
# 下载预编译的whl文件
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib-0.4.28-cpXX-cpXX-win_amd64.whl
```

#### Linux/Mac用户安装TA-Lib
```bash
# 先安装系统依赖
# Ubuntu/Debian:
sudo apt-get install build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# Mac:
brew install ta-lib

# 然后安装Python包
pip install ta-lib
```

## 使用方法

### 方式一: 使用免费数据源 (推荐新手)

无需任何配置，直接使用Akshare免费数据源：

```bash
# 监控默认股票列表
python stock_monitor.py

# 批量监控
python stock_monitor.py --batch

# 监控指定股票
python stock_monitor.py --stock 000001.SZ

# 指定分析天数
python stock_monitor.py --stock 600519.SH --days 120
```

### 方式二: 使用Tushare数据源

需要申请Tushare Token: https://tushare.pro/register

```bash
# 使用Token
python stock_monitor.py --token your_token_here --stock 000001.SZ

# 设置环境变量
export TUSHARE_TOKEN=your_token_here
python stock_monitor.py
```

## 配置说明

编辑 `config.py` 自定义配置：

```python
# 监控股票列表
DEFAULT_STOCKS = [
    '000001.SZ',  # 平安银行
    '600519.SH',  # 贵州茅台
    # 添加更多...
]

# 技术指标参数
MA_PERIODS = [5, 10, 20, 30, 60]  # 均线周期

# 评分权重
FUNDAMENTAL_WEIGHTS = {
    'pe_ratio': 0.2,
    'pb_ratio': 0.15,
    'roe': 0.25,
    # ...
}
```

## 输出文件

运行后会在 `output/` 目录生成：

```
output/
├── 000001.SZ_report_20240115.txt          # 分析报告
├── 000001.SZ_price_ma.png                  # 价格与均线图
├── 000001.SZ_macd.png                      # MACD图
├── 000001.SZ_rsi_kdj.png                   # RSI和KDJ图
├── 000001.SZ_volume.png                    # 成交量图
└── summary_report_20240115_143022.txt     # 汇总报告
```

## 股票代码格式

- 深交所: `股票代码.SZ` (如: `000001.SZ`)
- 上交所: `股票代码.SH` (如: `600000.SH`)

## 分析报告示例

```
================================================================================
A股投资分析报告 - 600519.SH
生成时间: 2024-01-15 14:30:22
================================================================================

【综合评分】
----------------------------------------
综合评分: 78.5/100
投资评级: 买入
技术面评分: 82.0/100
基本面评分: 75.0/100
资金流评分: 72.0/100

【技术分析】
----------------------------------------
趋势: UP
趋势强度: 4
趋势描述: 短期多头排列, 长期上升趋势, MACD金叉
RSI: 58.32 (NEUTRAL)
KDJ: K=58.20, D=55.40, J=63.80

【投资建议】
----------------------------------------
1. 技术面呈上升趋势，可考虑逢低买入
2. 基本面良好，具备中长期投资价值
3. 资金持续流入，市场关注度较高
```

## 项目结构

```
trade-tools/
├── stock_monitor.py          # 主程序
├── config.py                 # 配置文件
├── data_fetcher.py           # 数据获取模块
├── technical_analysis.py     # 技术分析模块
├── fundamental_analysis.py   # 基本面分析模块
├── money_flow_analysis.py    # 资金流分析模块
├── report_generator.py       # 报告生成模块
├── requirements.txt          # 依赖列表
└── README.md                 # 本文档
```

## 技术指标说明

### MACD (Moving Average Convergence Divergence)
- 快线: EMA(12) - EMA(26)
- 信号线: EMA(MACD, 9)
- 柱状图: MACD - 信号线
- 金叉: MACD上穿信号线 (买入信号)
- 死叉: MACD下穿信号线 (卖出信号)

### RSI (Relative Strength Index)
- 范围: 0-100
- >70: 超买区 (可能回调)
- <30: 超卖区 (可能反弹)
- 50为中性区

### KDJ
- K、D、J三条线
- K>D>70: 超买
- K<D<30: 超卖
- J线为敏感指标

### 布林带 (BOLL)
- 上轨: 中轨 + 2倍标准差
- 中轨: 20日均线
- 下轨: 中轨 - 2倍标准差
- 价格触及上下轨可能反转

## 评分体系

### 综合评分计算
- 技术面权重: 40%
- 基本面权重: 30%
- 资金流权重: 30%

### 投资评级
- **强烈买入**: 评分 ≥ 75
- **买入**: 评分 65-74
- **持有**: 评分 45-64
- **卖出**: 评分 35-44
- **强烈卖出**: 评分 < 35

## 风险提示

⚠️ **重要声明**:
1. 本工具仅供学习参考，不构成投资建议
2. 股市有风险，投资需谨慎
3. 历史数据不代表未来表现
4. 请结合多方面信息做出投资决策
5. 使用本工具所产生的任何损失，开发者不承担责任

## 常见问题

### Q: 为什么获取不到数据?
A:
1. 检查网络连接
2. 确认股票代码格式正确 (000001.SZ 或 600000.SH)
3. Tushare用户检查Token是否正确
4. 尝试使用免费数据源 (不填token)

### Q: TA-Lib安装失败怎么办?
A: 可以在 `technical_analysis.py` 中注释掉需要TA-Lib的部分，或使用纯pandas实现

### Q: 如何添加自定义股票?
A: 修改 `config.py` 中的 `DEFAULT_STOCKS` 列表

## 更新日志

### v1.0.0 (2024-01-15)
- ✨ 初始版本发布
- 📊 支持技术分析、基本面分析、资金流分析
- 📈 自动生成可视化图表
- 📝 生成详细分析报告
- 🔄 支持批量监控

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/mangowong/trade-tools
- Issues: https://github.com/mangowong/trade-tools/issues

---

**免责声明**: 本项目仅用于学习和研究目的，不构成任何投资建议。投资有风险，入市需谨慎。
