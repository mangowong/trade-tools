"""
API辅助模块 - 提供安全的API调用封装
"""
import akshare as ak
import warnings
warnings.filterwarnings('ignore')


def safe_api_call(func, *args, **kwargs):
    """
    安全地调用akshare API

    Args:
        func: API函数
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        API返回结果，如果失败返回None
    """
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        # 静默失败，返回None
        return None


def safe_get_dataframe(func, *args, **kwargs):
    """
    安全获取DataFrame

    Returns:
        DataFrame或空DataFrame（如果失败）
    """
    import pandas as pd
    try:
        result = func(*args, **kwargs)
        if result is None:
            return pd.DataFrame()
        return result
    except Exception:
        return pd.DataFrame()
