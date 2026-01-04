# -*- coding: utf-8 -*-
"""
A股监控分析工具 - 配置文件
"""
import os

class Config:
    """配置类"""

    # Tushare API配置 (需要申请token: https://tushare.pro/register)
    TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', 'your_tushare_token_here')

    # 默认监控股票列表 (股票代码)
    DEFAULT_STOCKS = [
        '000001.SZ',  # 平安银行
        '000002.SZ',  # 万科A
        '600000.SH',  # 浦发银行
        '600036.SH',  # 招商银行
        '600519.SH',  # 贵州茅台
    ]

    # 数据存储路径
    DATA_DIR = 'data'
    OUTPUT_DIR = 'output'

    # 分析参数
    MA_PERIODS = [5, 10, 20, 30, 60]  # 均线周期
    VOLUME_MA_PERIODS = [5, 10]  # 成交量均线周期

    # 技术指标参数
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9

    RSI_PERIOD = 14
    BOLLINGER_PERIOD = 20
    BOLLINGER_STD = 2

    # 基本面权重
    FUNDAMENTAL_WEIGHTS = {
        'pe_ratio': 0.2,      # 市盈率
        'pb_ratio': 0.15,     # 市净率
        'roe': 0.25,          # 净资产收益率
        'revenue_growth': 0.2, # 营收增长率
        'debt_ratio': 0.2,    # 资产负债率
    }

    # 资金流权重
    MONEY_FLOW_WEIGHTS = {
        'main_flow': 0.4,     # 主力资金流入
        'super_large': 0.3,   # 超大单
        'large': 0.2,         # 大单
        'medium': 0.1,        # 中单
    }

    # 技术面权重
    TECHNICAL_WEIGHTS = {
        'trend': 0.3,         # 趋势
        'momentum': 0.25,     # 动量
        'volume': 0.2,        # 成交量
        'volatility': 0.15,   # 波动率
        'macd': 0.1,          # MACD
    }

    # 日期配置
    START_DATE = '2023-01-01'
    END_DATE = None  # None表示使用当前日期

    # 图表配置
    CHART_STYLE = 'seaborn-v0_8-darkgrid'
    FIGSIZE = (14, 10)

config = Config()
