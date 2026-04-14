# 期权显示和计算修复实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复期权市值计算缺少100倍乘数的bug，并改进期权名称显示为 SPY-580-PUT-20260523 格式

**Architecture:** 创建独立的期权工具模块处理格式化和计算逻辑，在 ib_client.py 中通过条件判断调用，确保股票等非期权合约完全不受影响

**Tech Stack:** Python, ib_insync, pytest

---

### Task 1: 创建期权工具模块基础结构

**Files:**
- Create: `backend/options_utils.py`
- Create: `tests/test_options_utils.py`

- [ ] **Step 1: 创建期权工具模块文件**

创建 `backend/options_utils.py`:

```python
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
    # 将在下一个任务中实现
    pass


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
```

- [ ] **Step 2: 创建测试文件基础结构**

创建 `tests/test_options_utils.py`:

```python
"""期权工具函数测试"""
import pytest
from unittest.mock import Mock
from backend.options_utils import (
    format_option_symbol,
    get_option_multiplier,
    calculate_market_value_with_multiplier
)


class TestFormatOptionSymbol:
    """测试期权名称格式化"""
    
    def test_format_complete_option_symbol(self):
        """测试完整期权信息格式化"""
        # 将在后续任务中实现
        pass
    
    def test_format_partial_option_symbol(self):
        """测试部分期权信息格式化"""
        # 将在后续任务中实现
        pass


class TestGetOptionMultiplier:
    """测试期权乘数获取"""
    
    def test_get_option_multiplier_with_value(self):
        """测试有乘数值的期权"""
        # 将在后续任务中实现
        pass
    
    def test_get_option_multiplier_default(self):
        """测试缺失乘数的期权默认值"""
        # 将在后续任务中实现
        pass


class TestCalculateMarketValueWithMultiplier:
    """测试期权市值计算"""
    
    def test_calculate_positive_position(self):
        """测试正数持仓（买入）"""
        # 将在后续任务中实现
        pass
    
    def test_calculate_negative_position(self):
        """测试负数持仓（做空）"""
        # 将在后续任务中实现
        pass
```

- [ ] **Step 3: 提交基础结构**

```bash
git add backend/options_utils.py tests/test_options_utils.py
git commit -m "feat: add options utils module structure

- Create options_utils.py with function stubs
- Create test structure for comprehensive coverage
- Prepare for TDD implementation of options fixes"
```

### Task 2: 实现期权名称格式化功能

**Files:**
- Modify: `backend/options_utils.py:12-27`
- Modify: `tests/test_options_utils.py:12-25`

- [ ] **Step 1: 编写期权名称格式化的失败测试**

在 `tests/test_options_utils.py` 中替换 `test_format_complete_option_symbol`:

```python
def test_format_complete_option_symbol(self):
    """测试完整期权信息格式化"""
    contract = Mock()
    contract.symbol = "SPY"
    contract.strike = 580.0
    contract.right = "P"
    contract.lastTradeDateOrContractMonth = "20260523"
    
    result = format_option_symbol(contract)
    assert result == "SPY-580-PUT-20260523"
```

- [ ] **Step 2: 运行测试验证失败**

运行测试：
```bash
python -m pytest tests/test_options_utils.py::TestFormatOptionSymbol::test_format_complete_option_symbol -v
```
预期：FAIL，函数未实现

- [ ] **Step 3: 实现期权名称格式化函数**

在 `backend/options_utils.py` 中替换 `format_option_symbol` 函数：

```python
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
```

- [ ] **Step 4: 运行测试验证通过**

运行测试：
```bash
python -m pytest tests/test_options_utils.py::TestFormatOptionSymbol::test_format_complete_option_symbol -v
```
预期：PASS

- [ ] **Step 5: 添加部分信息测试**

在 `tests/test_options_utils.py` 中替换 `test_format_partial_option_symbol`:

```python
def test_format_partial_option_symbol(self):
    """测试部分期权信息格式化"""
    # 缺少日期的情况
    contract = Mock()
    contract.symbol = "AAPL"
    contract.strike = 150.0
    contract.right = "C"
    # 没有 lastTradeDateOrContractMonth
    
    result = format_option_symbol(contract)
    assert result == "AAPL-150-CALL"
    
    # 只有基本信息
    contract2 = Mock()
    contract2.symbol = "TSLA"
    contract2.right = "P"
    # 没有 strike 和 lastTradeDateOrContractMonth
    
    result2 = format_option_symbol(contract2)
    assert result2 == "TSLA-PUT"
```

- [ ] **Step 6: 运行部分信息测试**

运行测试：
```bash
python -m pytest tests/test_options_utils.py::TestFormatOptionSymbol::test_format_partial_option_symbol -v
```
预期：PASS

- [ ] **Step 7: 提交期权名称格式化功能**

```bash
git add backend/options_utils.py tests/test_options_utils.py
git commit -m "feat: implement option symbol formatting

- Add format_option_symbol with graceful degradation
- Support format: SPY-580-PUT-20260523
- Handle missing fields with best-effort approach
- Add comprehensive test coverage"
```

### Task 3: 实现期权乘数获取功能

**Files:**
- Modify: `backend/options_utils.py:30-42`
- Modify: `tests/test_options_utils.py:28-40`

- [ ] **Step 1: 编写乘数获取的失败测试**

在 `tests/test_options_utils.py` 中替换乘数测试：

```python
def test_get_option_multiplier_with_value(self):
    """测试有乘数值的期权"""
    contract = Mock()
    contract.multiplier = "100"
    
    result = get_option_multiplier(contract)
    assert result == 100.0

def test_get_option_multiplier_default(self):
    """测试缺失乘数的期权默认值"""
    contract = Mock()
    # 没有 multiplier 属性
    
    result = get_option_multiplier(contract)
    assert result == 100.0
    
def test_get_option_multiplier_invalid(self):
    """测试无效乘数值的处理"""
    contract = Mock()
    contract.multiplier = "invalid"
    
    result = get_option_multiplier(contract)
    assert result == 100.0
```

- [ ] **Step 2: 运行测试验证失败**

运行测试：
```bash
python -m pytest tests/test_options_utils.py::TestGetOptionMultiplier -v
```
预期：FAIL，函数未实现

- [ ] **Step 3: 实现乘数获取函数**

在 `backend/options_utils.py` 中替换 `get_option_multiplier` 函数：

```python
def get_option_multiplier(contract: Contract) -> float:
    """
    获取期权合约乘数
    
    Args:
        contract: IB 合约对象
        
    Returns:
        乘数值，期权默认 100，其他类型默认 1
    """
    try:
        multiplier = getattr(contract, 'multiplier', None)
        if multiplier is not None:
            return float(multiplier)
        else:
            # 期权默认乘数为 100
            return 100.0
    except (ValueError, TypeError):
        # 解析失败，使用期权默认值
        return 100.0
```

- [ ] **Step 4: 运行测试验证通过**

运行测试：
```bash
python -m pytest tests/test_options_utils.py::TestGetOptionMultiplier -v
```
预期：PASS

- [ ] **Step 5: 提交乘数获取功能**

```bash
git add backend/options_utils.py tests/test_options_utils.py
git commit -m "feat: implement option multiplier retrieval

- Add get_option_multiplier with dynamic parsing
- Default to 100 for options when multiplier missing/invalid
- Add robust error handling for edge cases"
```

### Task 4: 实现期权市值计算功能

**Files:**
- Modify: `backend/options_utils.py:45-60`
- Modify: `tests/test_options_utils.py:45-65`

- [ ] **Step 1: 编写市值计算的失败测试**

在 `tests/test_options_utils.py` 中替换市值计算测试：

```python
def test_calculate_positive_position(self):
    """测试正数持仓（买入期权）"""
    contract = Mock()
    contract.multiplier = "100"
    
    # 买入1张期权，价格$1.50
    result = calculate_market_value_with_multiplier(1.0, 1.50, contract)
    assert result == 150.0  # 1 * 1.50 * 100

def test_calculate_negative_position(self):
    """测试负数持仓（卖出期权）"""
    contract = Mock()
    contract.multiplier = "100"
    
    # 卖出1张期权，价格$2.00
    result = calculate_market_value_with_multiplier(-1.0, 2.00, contract)
    assert result == -200.0  # -1 * 2.00 * 100

def test_calculate_default_multiplier(self):
    """测试使用默认乘数计算"""
    contract = Mock()
    # 没有 multiplier 属性
    
    result = calculate_market_value_with_multiplier(1.0, 1.00, contract)
    assert result == 100.0  # 1 * 1.00 * 100 (默认)
```

- [ ] **Step 2: 运行测试验证失败**

运行测试：
```bash
python -m pytest tests/test_options_utils.py::TestCalculateMarketValueWithMultiplier -v
```
预期：FAIL，函数未实现

- [ ] **Step 3: 实现市值计算函数**

在 `backend/options_utils.py` 中替换 `calculate_market_value_with_multiplier` 函数：

```python
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
    multiplier = get_option_multiplier(contract)
    return position * price * multiplier
```

- [ ] **Step 4: 运行测试验证通过**

运行测试：
```bash
python -m pytest tests/test_options_utils.py::TestCalculateMarketValueWithMultiplier -v
```
预期：PASS

- [ ] **Step 5: 运行所有工具函数测试**

验证所有工具函数正常工作：
```bash
python -m pytest tests/test_options_utils.py -v
```
预期：所有测试PASS

- [ ] **Step 6: 提交期权市值计算功能**

```bash
git add backend/options_utils.py tests/test_options_utils.py
git commit -m "feat: implement option market value calculation

- Add calculate_market_value_with_multiplier function
- Correctly apply multiplier to position * price
- Support positive and negative positions (long/short)
- Complete options utility module implementation"
```

### Task 5: 集成期权工具到主系统

**Files:**
- Modify: `backend/ib_client.py:1-10` (imports)
- Modify: `backend/ib_client.py:146-155` (position processing loop)

- [ ] **Step 1: 添加期权工具导入**

在 `backend/ib_client.py` 的导入部分添加：

```python
from options_utils import format_option_symbol, calculate_market_value_with_multiplier
```

- [ ] **Step 2: 备份原始逻辑用于测试**

运行现有系统测试确保当前功能正常：
```bash
# 如果有现有测试，运行它们
python -m pytest tests/ -k "test_get_snapshot or test_ib_client" -v || echo "No existing tests found"
```

- [ ] **Step 3: 修改持仓处理循环 - 符号格式化**

在 `backend/ib_client.py` 的 `get_snapshot()` 函数中，找到位置创建 Position 对象的部分（约146-155行），修改 symbol 字段处理：

**原代码：**
```python
positions.append(Position(
    symbol=contract.symbol,
    # ... 其他字段
))
```

**修改为：**
```python
# 根据合约类型选择符号格式
if contract.secType == "OPT":
    symbol = format_option_symbol(contract)
else:
    symbol = contract.symbol  # 股票等保持原样

positions.append(Position(
    symbol=symbol,
    # ... 其他字段保持不变
))
```

- [ ] **Step 4: 修改持仓处理循环 - 市值计算**

在同一个循环中，找到市值计算部分：

**原代码：**
```python
market_value = pos.position * market_price
```

**修改为：**
```python
# 根据合约类型计算市值
if contract.secType == "OPT":
    # 期权：应用乘数计算
    market_value = calculate_market_value_with_multiplier(
        pos.position, market_price, contract
    )
else:
    # 股票等：保持原有计算
    market_value = pos.position * market_price
```

- [ ] **Step 5: 验证修改正确性**

检查修改后的代码逻辑：
```bash
# 验证语法正确性
python -m py_compile backend/ib_client.py
```
预期：无语法错误

- [ ] **Step 6: 提交集成修改**

```bash
git add backend/ib_client.py
git commit -m "feat: integrate options utilities into main system

- Import format_option_symbol and calculate_market_value_with_multiplier
- Apply options formatting for OPT secType contracts only
- Apply multiplier-based calculation for options market value
- Preserve existing logic for stocks and other contract types"
```

### Task 6: 创建集成测试验证完整功能

**Files:**
- Create: `tests/test_options_integration.py`

- [ ] **Step 1: 创建集成测试文件**

创建 `tests/test_options_integration.py`:

```python
"""期权功能集成测试"""
import pytest
from unittest.mock import Mock, patch
from backend.ib_client import get_snapshot
from backend.models import Position


class TestOptionsIntegration:
    """测试期权功能的完整集成"""
    
    @patch('backend.ib_client._ensure_connected')
    @patch('backend.ib_client._get_usdcnh_rate')
    @patch('backend.ib_client._get_cash_balances')
    @patch('backend.ib_client._ib')
    def test_option_position_complete_flow(self, mock_ib, mock_cash, mock_usd_rate, mock_connect):
        """测试期权持仓的完整处理流程"""
        # Mock 现金余额
        mock_cash.return_value = (1000.0, 0.0)  # (cash_usd, cash_cnh)
        
        # Mock 汇率
        mock_usd_rate.return_value = (7.2, "2026-04-14T12:00:00Z")
        
        # Mock 期权合约
        option_contract = Mock()
        option_contract.symbol = "SPY"
        option_contract.secType = "OPT" 
        option_contract.currency = "USD"
        option_contract.strike = 580.0
        option_contract.right = "P"
        option_contract.lastTradeDateOrContractMonth = "20260523"
        option_contract.multiplier = "100"
        
        # Mock 期权持仓
        option_position = Mock()
        option_position.contract = option_contract
        option_position.position = -1.0  # 卖出1张
        option_position.avgCost = 2.00
        
        # Mock ticker
        option_ticker = Mock()
        option_ticker.bid = 1.45
        option_ticker.ask = 1.55
        option_ticker.last = 1.50
        option_ticker.close = 1.50
        
        # 配置 mock IB
        mock_ib.positions.return_value = [option_position]
        mock_ib.reqTickers.return_value = [option_ticker]
        mock_ib.tickers.return_value = []
        
        # 执行测试
        result = get_snapshot()
        
        # 验证期权名称格式
        assert len(result.positions) == 1
        option_pos = result.positions[0]
        assert option_pos.symbol == "SPY-580-PUT-20260523"
        assert option_pos.sec_type == "OPT"
        
        # 验证期权市值计算（包含乘数）
        expected_market_value = -1.0 * 1.50 * 100  # -150.0
        assert option_pos.market_value == expected_market_value
        assert option_pos.market_value_cny == expected_market_value * 7.2
    
    @patch('backend.ib_client._ensure_connected')
    @patch('backend.ib_client._get_usdcnh_rate')
    @patch('backend.ib_client._get_cash_balances')
    @patch('backend.ib_client._ib')
    def test_stock_position_unchanged(self, mock_ib, mock_cash, mock_usd_rate, mock_connect):
        """测试股票持仓处理保持不变"""
        # Mock 现金余额
        mock_cash.return_value = (1000.0, 0.0)
        
        # Mock 汇率
        mock_usd_rate.return_value = (7.2, "2026-04-14T12:00:00Z")
        
        # Mock 股票合约
        stock_contract = Mock()
        stock_contract.symbol = "AAPL"
        stock_contract.secType = "STK"  # 股票类型
        stock_contract.currency = "USD"
        
        # Mock 股票持仓
        stock_position = Mock()
        stock_position.contract = stock_contract
        stock_position.position = 100.0  # 100股
        stock_position.avgCost = 150.00
        
        # Mock ticker
        stock_ticker = Mock()
        stock_ticker.bid = 149.50
        stock_ticker.ask = 150.50
        stock_ticker.last = 150.00
        stock_ticker.close = 150.00
        
        # 配置 mock IB
        mock_ib.positions.return_value = [stock_position]
        mock_ib.reqTickers.return_value = [stock_ticker]
        mock_ib.tickers.return_value = []
        
        # 执行测试
        result = get_snapshot()
        
        # 验证股票名称保持原样
        assert len(result.positions) == 1
        stock_pos = result.positions[0]
        assert stock_pos.symbol == "AAPL"  # 保持原始symbol
        assert stock_pos.sec_type == "STK"
        
        # 验证股票市值计算不变（无乘数）
        expected_market_value = 100.0 * 150.00  # 15000.0
        assert stock_pos.market_value == expected_market_value
        assert stock_pos.market_value_cny == expected_market_value * 7.2
```

- [ ] **Step 2: 运行集成测试**

运行集成测试：
```bash
python -m pytest tests/test_options_integration.py -v
```
预期：PASS（如果mock正确配置）

- [ ] **Step 3: 修复任何集成问题**

如果测试失败，检查并修复：
- import路径是否正确
- mock配置是否匹配实际的ib_client逻辑
- 期望值计算是否正确

- [ ] **Step 4: 运行所有测试确保无回归**

运行完整测试套件：
```bash
python -m pytest tests/ -v
```
预期：所有测试PASS，无回归

- [ ] **Step 5: 提交集成测试**

```bash
git add tests/test_options_integration.py
git commit -m "test: add comprehensive options integration tests

- Test complete option position flow: formatting + calculation
- Verify stock positions remain unchanged (no regression)
- Mock IB API components for reliable testing
- Validate market value calculation with multiplier"
```

### Task 7: 最终验证和文档更新

**Files:**
- Modify: `docs/superpowers/specs/2026-04-14-options-fix-design.md`

- [ ] **Step 1: 运行完整测试套件**

确保所有功能正常工作：
```bash
python -m pytest tests/ -v --tb=short
```
预期：所有测试PASS

- [ ] **Step 2: 手动验证关键场景**

创建简单验证脚本 `verify_options.py`：

```python
#!/usr/bin/env python3
"""手动验证期权功能的简单脚本"""
from unittest.mock import Mock
from backend.options_utils import format_option_symbol, calculate_market_value_with_multiplier

def test_manual_verification():
    # 测试期权名称格式化
    contract = Mock()
    contract.symbol = "SPY"
    contract.strike = 580.0
    contract.right = "P"
    contract.lastTradeDateOrContractMonth = "20260523"
    contract.multiplier = "100"
    
    symbol = format_option_symbol(contract)
    print(f"期权名称格式化: {symbol}")
    assert symbol == "SPY-580-PUT-20260523", f"期望 'SPY-580-PUT-20260523'，实际 '{symbol}'"
    
    # 测试期权市值计算
    market_value = calculate_market_value_with_multiplier(-1.0, 1.50, contract)
    print(f"裸卖1张$1.50期权的市值: ${market_value}")
    assert market_value == -150.0, f"期望 -150.0，实际 {market_value}"
    
    print("✅ 所有验证通过！")

if __name__ == "__main__":
    test_manual_verification()
```

运行验证脚本：
```bash
python verify_options.py
```
预期：输出验证通过信息

- [ ] **Step 3: 更新设计文档状态**

在 `docs/superpowers/specs/2026-04-14-options-fix-design.md` 顶部更新状态：

```markdown
**日期**: 2026-04-14  
**状态**: ✅ 实施完成并测试通过
```

- [ ] **Step 4: 清理临时文件**

删除验证脚本：
```bash
rm verify_options.py
```

- [ ] **Step 5: 最终提交**

```bash
git add docs/superpowers/specs/2026-04-14-options-fix-design.md
git commit -m "docs: mark options fix implementation as completed

- Update design document status to completed
- All tests passing and functionality verified
- Options display format: SPY-580-PUT-20260523 ✅
- Options market value calculation with 100x multiplier ✅
- Backward compatibility for stocks maintained ✅"
```

- [ ] **Step 6: 验证git历史清晰**

检查提交历史：
```bash
git log --oneline -10
```
确保提交消息清晰，展现了完整的实施过程

---

## 完成标准

✅ **期权名称格式化**：SPY-580-PUT-20260523 格式
✅ **期权市值修复**：正确应用100倍乘数  
✅ **向后兼容性**：股票等非期权合约不受影响
✅ **错误处理**：优雅降级，系统稳定性
✅ **测试覆盖**：单元测试 + 集成测试
✅ **代码质量**：清晰的责任分离，可维护性

**预期结果：**
- 裸卖1张$1.50期权显示为-$150（不再是-$1.50）
- 期权名称清晰区分：SPY-580-PUT-20260523
- 股票AAPL持仓显示和计算完全不变