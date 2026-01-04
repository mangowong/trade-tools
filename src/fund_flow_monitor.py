"""
资金流动监控模块
监测主力资金、散户资金流向和成交量变化
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class FundFlowMonitor:
    """资金流动监控器"""

    def __init__(self, stock_code: str):
        """
        初始化资金流动监控器

        Args:
            stock_code: 股票代码（如 '600036'）
        """
        self.stock_code = stock_code
        self.data = None

    def get_realtime_fund_flow(self) -> Dict:
        """
        获取实时资金流向数据

        Returns:
            包含资金流向信息的字典
        """
        try:
            # 获取个股资金流向
            df = ak.stock_individual_fund_flow(stock=self.stock_code, market="sh" if self.stock_code.startswith('6') else "sz")

            if df.empty:
                return self._get_empty_fund_flow()

            latest = df.iloc[0]

            return {
                'date': latest.get('日期', datetime.now().strftime('%Y-%m-%d')),
                'price': float(latest.get('收盘价', 0)),
                'change_pct': float(latest.get('涨跌幅', 0)),
                'main_net_inflow': float(latest.get('主力净流入-净额', 0)),
                'main_net_inflow_pct': float(latest.get('主力净流入-净占比', 0)),
                'super_large_net_inflow': float(latest.get('超大单净流入-净额', 0)),
                'large_net_inflow': float(latest.get('大单净流入-净额', 0)),
                'medium_net_inflow': float(latest.get('中单净流入-净额', 0)),
                'small_net_inflow': float(latest.get('小单净流入-净额', 0)),
                'volume': 0.0,  # akshare当前不提供此数据
                'turnover': 0.0  # akshare当前不提供此数据
            }
        except Exception as e:
            # API调用失败，返回空数据
            return self._get_empty_fund_flow()

    def get_historical_fund_flow(self, days: int = 30) -> pd.DataFrame:
        """
        获取历史资金流向数据

        Args:
            days: 获取天数

        Returns:
            历史资金流向DataFrame
        """
        try:
            df = ak.stock_individual_fund_flow(
                stock=self.stock_code,
                market="sh" if self.stock_code.startswith('6') else "sz"
            )

            if df is None or df.empty:
                return pd.DataFrame()

            df['日期'] = pd.to_datetime(df['日期'])
            df = df.tail(days)

            return df
        except Exception as e:
            # 静默失败，返回空DataFrame
            return pd.DataFrame()

    def analyze_fund_trend(self, days: int = 5) -> Dict:
        """
        分析资金流向趋势

        Args:
            days: 分析天数

        Returns:
            趋势分析结果
        """
        df = self.get_historical_fund_flow(days)

        if df.empty:
            return {
                'trend': 'unknown',
                'avg_main_inflow': 0,
                'total_main_inflow': 0,
                'consecutive_days': 0
            }

        main_inflows = df['主力净流入-净额'].astype(float)

        avg_main_inflow = main_inflows.mean()
        total_main_inflow = main_inflows.sum()

        # 计算连续净流入/流出天数
        consecutive_days = 0
        for i in range(len(main_inflows)):
            if main_inflows.iloc[i] > 0:
                consecutive_days += 1
            else:
                break

        trend = 'inflow' if avg_main_inflow > 0 else 'outflow'

        return {
            'trend': trend,
            'avg_main_inflow': avg_main_inflow,
            'total_main_inflow': total_main_inflow,
            'consecutive_days': consecutive_days,
            'latest_inflow': main_inflows.iloc[0] if len(main_inflows) > 0 else 0
        }

    def get_volume_ratio(self) -> float:
        """
        计算量比（当前成交量与过去5日平均成交量之比）

        Returns:
            量比值
        """
        try:
            df = self.get_historical_fund_flow(10)

            if df.empty or len(df) < 5:
                return 1.0

            # 检查是否有成交量列
            if '成交量' not in df.columns:
                return 1.0

            latest_volume = df.iloc[0]['成交量']
            avg_volume = df.iloc[1:6]['成交量'].astype(float).mean()

            if avg_volume == 0:
                return 1.0

            return float(latest_volume) / avg_volume
        except Exception:
            # 如果计算失败，返回默认值
            return 1.0

    def calculate_turnover_rate(self) -> float:
        """
        计算换手率

        Returns:
            换手率
        """
        realtime = self.get_realtime_fund_flow()

        if realtime['turnover'] == 0:
            return 0.0

        # 这里简化计算，实际需要流通市值数据
        return 0.0

    def _get_empty_fund_flow(self) -> Dict:
        """返回空的资金流向数据结构"""
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'price': 0.0,
            'change_pct': 0.0,
            'main_net_inflow': 0.0,
            'main_net_inflow_pct': 0.0,
            'super_large_net_inflow': 0.0,
            'large_net_inflow': 0.0,
            'medium_net_inflow': 0.0,
            'small_net_inflow': 0.0,
            'volume': 0.0,
            'turnover': 0.0
        }

    def generate_fund_flow_report(self) -> str:
        """
        生成资金流向分析报告

        Returns:
            文本报告
        """
        realtime = self.get_realtime_fund_flow()
        trend = self.analyze_fund_trend(5)
        volume_ratio = self.get_volume_ratio()

        report = f"""
资金流向分析报告 - {self.stock_code}
{'=' * 50}

【实时数据】
日期: {realtime['date']}
最新价: {realtime['price']:.2f} 元
涨跌幅: {realtime['change_pct']:.2f}%
成交量: {realtime['volume']:,.0f} 手
成交额: {realtime['turnover']:,.0f} 万元

【资金流向】
主力净流入: {realtime['main_net_inflow']:,.0f} 万元 ({realtime['main_net_inflow_pct']:.2f}%)
  - 超大单: {realtime['super_large_net_inflow']:,.0f} 万元
  - 大单: {realtime['large_net_inflow']:,.0f} 万元
  - 中单: {realtime['medium_net_inflow']:,.0f} 万元
  - 小单: {realtime['small_net_inflow']:,.0f} 万元

【趋势分析】
近期趋势: {'资金净流入' if trend['trend'] == 'inflow' else '资金净流出'}
5日平均净流入: {trend['avg_main_inflow']:,.0f} 万元
5日累计净流入: {trend['total_main_inflow']:,.0f} 万元
连续净流入天数: {trend['consecutive_days']} 天
量比: {volume_ratio:.2f}

【风险提示】
{'主力资金持续流入，值得关注' if trend['trend'] == 'inflow' else '主力资金持续流出，注意风险'}
"""
        return report
