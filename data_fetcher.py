# -*- coding: utf-8 -*-
"""
数据获取模块 - 支持多数据源
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataFetcher:
    """数据获取基类"""

    def __init__(self, token=None):
        self.token = token

    def get_stock_data(self, stock_code, start_date, end_date):
        """获取股票数据"""
        raise NotImplementedError

    def get_money_flow(self, stock_code, start_date, end_date):
        """获取资金流数据"""
        raise NotImplementedError

    def get_fundamental(self, stock_code):
        """获取基本面数据"""
        raise NotImplementedError


class TushareFetcher(DataFetcher):
    """Tushare数据源"""

    def __init__(self, token):
        super().__init__(token)
        try:
            import tushare as ts
            ts.set_token(token)
            self.ts = ts.pro_api()
            logger.info("Tushare初始化成功")
        except Exception as e:
            logger.error(f"Tushare初始化失败: {e}")
            self.ts = None

    def get_stock_data(self, stock_code, start_date, end_date):
        """获取日线行情数据"""
        if not self.ts:
            return None

        try:
            df = self.ts.daily(
                ts_code=stock_code,
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', '')
            )
            if df is not None and not df.empty:
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df = df.sort_values('trade_date')
                logger.info(f"获取{stock_code}行情数据成功，共{len(df)}条")
                return df
        except Exception as e:
            logger.error(f"获取{stock_code}行情数据失败: {e}")
        return None

    def get_money_flow(self, stock_code, start_date, end_date):
        """获取资金流数据"""
        if not self.ts:
            return None

        try:
            df = self.ts.moneyflow(
                ts_code=stock_code,
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', '')
            )
            if df is not None and not df.empty:
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df = df.sort_values('trade_date')
                logger.info(f"获取{stock_code}资金流数据成功，共{len(df)}条")
                return df
        except Exception as e:
            logger.error(f"获取{stock_code}资金流数据失败: {e}")
        return None

    def get_fundamental(self, stock_code):
        """获取基本面数据"""
        if not self.ts:
            return None

        try:
            # 获取最新交易日基本信息
            basic = self.ts.daily_basic(
                ts_code=stock_code,
                fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,free_share,total_mv,circ_mv'
            )
            # 获取公司财务指标
            finan = self.ts.fina_indicator(
                ts_code=stock_code,
                fields='ts_code,ann_date,end_date,roe,roe_dt,roe_waa,roe_yearly,npta,assets,debt_to_assets,current_ratio,quick_ratio'
            )

            result = {'basic': basic, 'financial': finan}
            logger.info(f"获取{stock_code}基本面数据成功")
            return result
        except Exception as e:
            logger.error(f"获取{stock_code}基本面数据失败: {e}")
        return None


class AkshareFetcher(DataFetcher):
    """Akshare数据源 (免费，无需token)"""

    def __init__(self):
        super().__init__(None)
        try:
            import akshare as ak
            self.ak = ak
            logger.info("Akshare初始化成功")
        except Exception as e:
            logger.error(f"Akshare初始化失败: {e}")
            self.ak = None

    def get_stock_data(self, stock_code, start_date, end_date):
        """获取日线行情数据"""
        if not self.ak:
            return None

        try:
            # 转换股票代码格式 (000001.SZ -> sz000001)
            symbol = stock_code.replace('.SZ', '').replace('.SH', '').lower()
            exchange = 'sz' if 'SZ' in stock_code else 'sh'

            df = self.ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust=""
            )
            if df is not None and not df.empty:
                df = df.rename(columns={
                    '日期': 'trade_date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'vol',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '涨跌幅': 'pct_chg',
                    '涨跌额': 'change',
                    '换手率': 'turnover_rate'
                })
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df['ts_code'] = stock_code
                logger.info(f"获取{stock_code}行情数据成功，共{len(df)}条")
                return df
        except Exception as e:
            logger.error(f"获取{stock_code}行情数据失败: {e}")
        return None

    def get_money_flow(self, stock_code, start_date, end_date):
        """获取资金流数据"""
        if not self.ak:
            return None

        try:
            # Akshare资金流数据
            symbol = stock_code.replace('.SZ', '').replace('.SH', '')
            df = self.ak.stock_individual_fund_flow_rank(
                symbol=symbol,
                indicator="今日"
            )
            logger.info(f"获取{stock_code}资金流数据")
            return df
        except Exception as e:
            logger.error(f"获取{stock_code}资金流数据失败: {e}")
        return None

    def get_fundamental(self, stock_code):
        """获取基本面数据"""
        if not self.ak:
            return None

        try:
            symbol = stock_code.replace('.SZ', '').replace('.SH', '')

            # 获取股票基本信息
            basic = self.ak.stock_individual_info_em(symbol=symbol)

            # 获取财务数据
            financial = self.ak.stock_financial_analysis_indicator(symbol=symbol)

            result = {'basic': basic, 'financial': financial}
            logger.info(f"获取{stock_code}基本面数据成功")
            return result
        except Exception as e:
            logger.error(f"获取{stock_code}基本面数据失败: {e}")
        return None


def get_data_fetcher(token=None):
    """工厂函数：获取数据获取器"""
    if token and token != 'your_tushare_token_here':
        logger.info("使用Tushare数据源")
        return TushareFetcher(token)
    else:
        logger.info("使用Akshare数据源 (免费)")
        return AkshareFetcher()
