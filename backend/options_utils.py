"""期权处理工具函数模块"""
from datetime import datetime
from typing import Optional
from ib_insync import Contract


def format_option_symbol(contract: Contract) -> str:
    """
    格式化期权名称为用户期望格式：SPY-580-PUT-20260523
    采用最大努力原则：有什么字段放什么，缺失的跳过

    Args:
        contract: IB 期权合约对象

    Returns:
        格式化后的期权名称，如 "SPY-580-PUT-20260523"
        如果信息不完整则部分格式化，如 "SPY-PUT"
    """
    parts = []

    # 底层资产符号（必需）
    if hasattr(contract, 'symbol') and contract.symbol:
        parts.append(contract.symbol)
    else:
        return getattr(contract, 'symbol', "UNKNOWN")  # 兜底

    # 行权价（可选）
    if hasattr(contract, 'strike') and contract.strike is not None:
        try:
            strike = int(contract.strike) if float(contract.strike).is_integer() else float(contract.strike)
            parts.append(str(strike))
        except (ValueError, AttributeError):
            pass  # 跳过，不添加

    # 期权类型（可选）
    if hasattr(contract, 'right') and contract.right:
        right_name = "CALL" if contract.right.upper() == "C" else "PUT"
        parts.append(right_name)

    # 到期日期（可选）
    if hasattr(contract, 'lastTradeDateOrContractMonth') and contract.lastTradeDateOrContractMonth:
        try:
            # 确保是8位YYYYMMDD格式
            date_str = str(contract.lastTradeDateOrContractMonth)
            if len(date_str) == 8 and date_str.isdigit():
                parts.append(date_str)
            else:
                # 尝试解析和转换其他格式
                if len(date_str) == 6:  # YYMMDD格式
                    year = "20" + date_str[:2]
                    parts.append(year + date_str[2:])
        except (ValueError, AttributeError):
            pass  # 跳过，不添加

    return "-".join(parts)


def get_option_multiplier(contract: Contract) -> float:
    """
    获取期权合约乘数

    Args:
        contract: IB 合约对象

    Returns:
        乘数值，期权默认 100，其他类型默认 1
    """
    # 将在下一个任务中实现
    pass


def calculate_market_value_with_multiplier(position: float, price: float, contract: Contract) -> float:
    """
    计算包含乘数的期权市值

    Args:
        position: 持仓数量（可为负数，表示做空）
        price: 市场价格
        contract: 合约对象

    Returns:
        正确的期权市值（已应用乘数）
    """
    # 将在下一个任务中实现
    pass