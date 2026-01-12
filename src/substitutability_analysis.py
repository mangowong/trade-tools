"""
替代性分析模块
分析产品替代性、市场竞争格局、行业地位等
"""
import akshare as ak
import pandas as pd
from datetime import datetime
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class SubstitutabilityAnalysis:
    """替代性分析器"""

    def __init__(self, stock_code: str):
        """
        初始化替代性分析器

        Args:
            stock_code: 股票代码
        """
        self.stock_code = stock_code
        self.company_info = None
        self.industry_data = None

    def get_industry_peers(self) -> List[Dict]:
        """
        获取同行业可比公司

        Returns:
            同行业公司列表
        """
        try:
            # 获取公司基本信息
            company_df = ak.stock_individual_info_em(symbol=self.stock_code)
            industry = None

            for _, row in company_df.iterrows():
                if row['item'] == '行业':
                    industry = row['value']
                    break

            if not industry:
                return []

            # 获取行业成分股
            try:
                # 尝试获取行业板块数据
                sector_stocks = self._get_sector_stocks(industry)

                if not sector_stocks:
                    return []

                # 获取前10只同行业股票的基本信息
                peers = []
                for stock in sector_stocks[:10]:
                    if stock != self.stock_code:
                        try:
                            peer_info = ak.stock_individual_info_em(symbol=stock)
                            peer_dict = {'code': stock}

                            for _, row in peer_info.iterrows():
                                peer_dict[row['item']] = row['value']

                            # 获取PE数据
                            try:
                                peer_df = ak.stock_financial_analysis_indicator(symbol=stock)
                                if not peer_df.empty:
                                    latest = peer_df.iloc[0]
                                    peer_dict['pe_ratio'] = self._safe_float(latest.get('市盈率-动态', 0))
                                    peer_dict['pb_ratio'] = self._safe_float(latest.get('市净率', 0))
                            except:
                                peer_dict['pe_ratio'] = 0.0
                                peer_dict['pb_ratio'] = 0.0

                            peers.append(peer_dict)
                        except:
                            continue

                return peers[:5]  # 返回前5个同行

            except Exception as e:
                print(f"获取行业成分股失败: {e}")
                return []

        except Exception as e:
            print(f"获取行业同行失败: {e}")
            return []

    def _get_sector_stocks(self, industry: str) -> List[str]:
        """
        获取行业成分股代码

        Args:
            industry: 行业名称

        Returns:
            股票代码列表
        """
        try:
            # 简化处理：根据行业返回一些常见的股票代码
            # 实际应用中应该调用相应的行业板块API

            industry_keywords = {
                '银行': ['600036', '600000', '601398', '601939', '000001'],
                '医药': ['000858', '600276', '000538', '600521', '002007'],
                '电子': ['000858', '002415', '300750', '002049', '688981'],
                '食品': ['600519', '000858', '600887', '002304', '603288'],
                '地产': ['000002', '600048', '001979', '000656', '600383']
            }

            for key, stocks in industry_keywords.items():
                if key in industry:
                    return stocks

            # 默认返回一些常见股票
            return ['600036', '600000', '600519', '000858', '600276']

        except Exception as e:
            print(f"获取行业股票失败: {e}")
            return []

    def analyze_market_position(self) -> Dict:
        """
        分析市场地位

        Returns:
            市场地位分析结果
        """
        try:
            company_df = ak.stock_individual_info_em(symbol=self.stock_code)

            market_cap = 0.0
            for _, row in company_df.iterrows():
                if row['item'] == '总市值':
                    # 处理市值字符串（如 "5000亿"）
                    cap_str = str(row['value']).replace('万亿', '0000').replace('亿', '00')
                    market_cap = self._safe_float(cap_str)
                    break

            # 获取同行数据
            peers = self.get_industry_peers()

            if not peers:
                return {
                    'market_cap': market_cap,
                    'position': 'unknown',
                    'cap_rank': 'N/A'
                }

            # 计算市值排名
            peer_caps = []
            for peer in peers:
                if '总市值' in peer:
                    cap_str = str(peer['总市值']).replace('万亿', '0000').replace('亿', '00')
                    peer_caps.append(self._safe_float(cap_str))

            peer_caps.append(market_cap)
            peer_caps.sort(reverse=True)

            rank = peer_caps.index(market_cap) + 1
            total = len(peer_caps)

            if rank == 1:
                position = '行业龙头'
            elif rank <= total / 3:
                position = '行业领先'
            elif rank <= 2 * total / 3:
                position = '行业中游'
            else:
                position = '行业跟随'

            return {
                'market_cap': market_cap,
                'position': position,
                'cap_rank': f"{rank}/{total}"
            }

        except Exception as e:
            print(f"分析市场地位失败: {e}")
            return {
                'market_cap': 0.0,
                'position': 'unknown',
                'cap_rank': 'N/A'
            }

    def compare_valuation_with_peers(self) -> Dict:
        """
        与同行进行估值对比

        Returns:
            估值对比结果
        """
        try:
            # 获取目标公司估值
            target_df = ak.stock_financial_analysis_indicator(symbol=self.stock_code)

            if target_df.empty:
                return {'comparison': 'unavailable'}

            target_pe = self._safe_float(target_df.iloc[0].get('市盈率-动态', 0))
            target_pb = self._safe_float(target_df.iloc[0].get('市净率', 0))

            # 获取同行估值
            peers = self.get_industry_peers()

            if not peers:
                return {
                    'target_pe': target_pe,
                    'target_pb': target_pb,
                    'comparison': 'no_peers'
                }

            peer_pes = [p.get('pe_ratio', 0) for p in peers if p.get('pe_ratio', 0) > 0]
            peer_pbs = [p.get('pb_ratio', 0) for p in peers if p.get('pb_ratio', 0) > 0]

            if not peer_pes:
                return {
                    'target_pe': target_pe,
                    'target_pb': target_pb,
                    'comparison': 'insufficient_data'
                }

            avg_peer_pe = sum(peer_pes) / len(peer_pes)
            avg_peer_pb = sum(peer_pbs) / len(peer_pbs) if peer_pbs else 0

            pe_premium = (target_pe - avg_peer_pe) / avg_peer_pe if avg_peer_pe > 0 else 0
            pb_premium = (target_pb - avg_peer_pb) / avg_peer_pb if avg_peer_pb > 0 else 0

            # 估值判断
            if pe_premium < -0.2:
                valuation_status = '显著低估'
            elif pe_premium < -0.1:
                valuation_status = '相对低估'
            elif pe_premium < 0.1:
                valuation_status = '估值合理'
            elif pe_premium < 0.2:
                valuation_status = '相对高估'
            else:
                valuation_status = '显著高估'

            return {
                'target_pe': target_pe,
                'target_pb': target_pb,
                'avg_peer_pe': avg_peer_pe,
                'avg_peer_pb': avg_peer_pb,
                'pe_premium': pe_premium,
                'pb_premium': pb_premium,
                'valuation_status': valuation_status,
                'comparison': 'available'
            }

        except Exception as e:
            print(f"估值对比失败: {e}")
            return {'comparison': 'error'}

    def analyze_substitutability_risk(self) -> Dict:
        """
        分析替代性风险

        Returns:
            替代性风险评估
        """
        position = self.analyze_market_position()
        valuation = self.compare_valuation_with_peers()

        risk_score = 0.0
        risk_factors = []

        # 1. 市场地位风险 (40分)
        if position['position'] == '行业跟随':
            risk_score += 40
            risk_factors.append('市场地位较低，面临被替代风险')
        elif position['position'] == '行业中游':
            risk_score += 25
            risk_factors.append('市场地位一般，竞争压力大')
        elif position['position'] == '行业领先':
            risk_score += 10
            risk_factors.append('市场地位较好，但仍需保持竞争力')
        elif position['position'] == '行业龙头':
            risk_score += 0
            risk_factors.append('行业龙头地位稳固')

        # 2. 估值风险 (30分)
        if valuation.get('comparison') == 'available':
            if valuation['valuation_status'] == '显著高估':
                risk_score += 30
                risk_factors.append('估值显著高于同行，存在回调风险')
            elif valuation['valuation_status'] == '相对高估':
                risk_score += 20
                risk_factors.append('估值偏高，需注意风险')

        # 3. 竞争风险 (30分) - 基于同行数量
        peers = self.get_industry_peers()
        if len(peers) > 10:
            risk_score += 30
            risk_factors.append('竞争激烈，需持续关注市场变化')
        elif len(peers) > 5:
            risk_score += 20
            risk_factors.append('竞争较为激烈')

        risk_level = '高' if risk_score >= 60 else '中' if risk_score >= 30 else '低'

        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'market_position': position.get('position', 'unknown'),
            'valuation_status': valuation.get('valuation_status', 'unknown')
        }

    def _safe_float(self, value) -> float:
        """安全转换为浮点数"""
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace('-', '').strip()
                if value == '' or value == 'N/A':
                    return 0.0
            return float(value) if value else 0.0
        except:
            return 0.0

    def generate_substitutability_report(self) -> str:
        """
        生成替代性分析报告

        Returns:
            文本报告
        """
        position = self.analyze_market_position()
        valuation = self.compare_valuation_with_peers()
        risk = self.analyze_substitutability_risk()

        report = f"""
替代性分析报告 - {self.stock_code}
{'=' * 50}

【市场地位】
总市值: {position.get('market_cap', 0):,.0f} 万元
市场排名: {position.get('cap_rank', 'N/A')}
市场地位: {position.get('position', '未知')}

【同行估值对比】
"""

        if valuation.get('comparison') == 'available':
            report += f"""目标公司PE: {valuation.get('target_pe', 0):.2f}
同行平均PE: {valuation.get('avg_peer_pe', 0):.2f}
PE溢价率: {valuation.get('pe_premium', 0):.2%}

目标公司PB: {valuation.get('target_pb', 0):.2f}
同行平均PB: {valuation.get('avg_peer_pb', 0):.2f}
PB溢价率: {valuation.get('pb_premium', 0):.2%}

估值评估: {valuation.get('valuation_status', '未知')}
"""
        else:
            report += "同行对比数据暂不可用\n"

        report += f"""
【替代性风险评估】
风险评分: {risk.get('risk_score', 0)}/100
风险等级: {risk.get('risk_level', '未知')}

主要风险因素:
"""
        for factor in risk.get('risk_factors', []):
            report += f"  - {factor}\n"

        report += "\n【投资建议】\n"

        if risk.get('risk_level') == '低':
            report += "替代性风险较低，公司在行业内具有一定优势，可适当关注。\n"
        elif risk.get('risk_level') == '中':
            report += "存在一定替代性风险，建议结合公司核心竞争力综合评估。\n"
        else:
            report += "替代性风险较高，建议谨慎投资并密切关注行业竞争变化。\n"

        return report
