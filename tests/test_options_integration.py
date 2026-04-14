"""期权功能集成测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import Mock

# 简化的集成测试 - 直接测试关键功能
from backend.options_utils import format_option_symbol, calculate_market_value_with_multiplier


class TestOptionsIntegration:
    """测试期权功能的完整集成"""

    def test_end_to_end_options_processing(self):
        """端到端测试期权处理流程"""
        # 创建模拟的期权合约
        option_contract = Mock()
        option_contract.symbol = "SPY"
        option_contract.secType = "OPT"
        option_contract.strike = 580.0
        option_contract.right = "P"
        option_contract.lastTradeDateOrContractMonth = "20260523"
        option_contract.multiplier = "100"

        # 测试期权名称格式化
        formatted_name = format_option_symbol(option_contract)
        expected_name = "SPY-580-PUT-20260523"
        assert formatted_name == expected_name, f"Expected {expected_name}, got {formatted_name}"

        # 测试期权市值计算（裸卖1张$1.50期权）
        position = -1.0  # 卖出1张
        market_price = 1.50
        market_value = calculate_market_value_with_multiplier(position, market_price, option_contract)
        expected_value = -150.0  # -1 * 1.50 * 100
        assert market_value == expected_value, f"Expected {expected_value}, got {market_value}"

        print(f"✅ 期权名称格式化: {formatted_name}")
        print(f"✅ 期权市值计算: {market_value}")

    def test_stock_vs_option_processing(self):
        """对比测试股票和期权处理的区别"""
        # 股票合约
        stock_contract = Mock()
        stock_contract.symbol = "AAPL"
        stock_contract.secType = "STK"

        # 期权合约
        option_contract = Mock()
        option_contract.symbol = "SPY"
        option_contract.secType = "OPT"
        option_contract.strike = 580.0
        option_contract.right = "PUT"
        option_contract.lastTradeDateOrContractMonth = "20260523"
        option_contract.multiplier = "100"

        # 相同的持仓和价格
        position = 1.0
        price = 10.0

        # 股票市值（模拟原始计算）
        stock_value = position * price  # 1.0 * 10.0 = 10.0

        # 期权市值（使用新函数）
        option_value = calculate_market_value_with_multiplier(position, price, option_contract)  # 1.0 * 10.0 * 100 = 1000.0

        assert stock_value == 10.0, "股票市值计算错误"
        assert option_value == 1000.0, "期权市值计算错误"

        print(f"✅ 股票市值（无乘数）: ${stock_value}")
        print(f"✅ 期权市值（含乘数）: ${option_value}")

        # 验证期权和股票的区别
        assert option_value == stock_value * 100, "期权市值应该是股票市值的100倍（包含乘数）"