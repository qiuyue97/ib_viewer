# 期权显示和计算修复设计

**日期**: 2026-04-14  
**状态**: 设计完成，待实施

## 问题描述

当前 IB Viewer 在期权处理上存在两个重大问题：

1. **市值计算错误**：期权市值计算缺少合约乘数，导致市值被低估100倍
   - 当前：裸卖1张$1.50期权显示为 -$1.50
   - 应该：裸卖1张$1.50期权显示为 -$150

2. **名称显示不清晰**：期权只显示底层资产符号，无法区分不同合约
   - 当前：多个苹果期权都显示为 "AAPL"
   - 期望：显示为 "SPY-580-PUT-20260523" 格式

## 设计方案

### 架构概览

**文件结构变更：**
```
backend/
├── ib_client.py        # 修改：调用期权工具函数
├── options_utils.py    # 新增：期权专用工具函数
├── models.py          # 保持不变
└── ...
```

**数据流：**
```
IB API → ib_client.py → [期权判断] → options_utils.py → 格式化/计算 → Position对象
```

### 核心组件

#### 1. 期权工具模块 (`backend/options_utils.py`)

```python
def format_option_symbol(contract: Contract) -> str:
    """
    格式化期权名称为用户期望格式：SPY-580-PUT-20260523
    采用最大努力原则：有什么字段放什么，缺失的跳过
    
    示例输出：
    - 完整信息：SPY-580-PUT-20260523
    - 缺少日期：SPY-580-PUT  
    - 缺少行权价：SPY-PUT-20260523
    - 只有基本信息：SPY-PUT
    """

def get_option_multiplier(contract: Contract) -> float:
    """
    获取期权合约乘数
    优先使用 contract.multiplier，缺失时期权默认 100
    """

def calculate_market_value_with_multiplier(position: float, price: float, contract: Contract) -> float:
    """
    计算期权市值，应用合约乘数
    """
```

#### 2. 主逻辑修改 (`ib_client.py`)

在 `get_snapshot()` 函数的持仓处理循环中添加期权判断：

```python
# 符号格式化
if contract.secType == "OPT":
    symbol = format_option_symbol(contract)
else:
    symbol = contract.symbol  # 股票等保持原样

# 市值计算
if contract.secType == "OPT":
    market_value = calculate_market_value_with_multiplier(
        pos.position, market_price, contract
    )
else:
    market_value = pos.position * market_price  # 股票等保持原有计算
```

### 关键特性

#### 期权名称格式化逻辑

1. **底层资产符号**：必需，来自 `contract.symbol`
2. **行权价**：可选，来自 `contract.strike`，格式化为整数或浮点数
3. **期权类型**：可选，来自 `contract.right`，转换为 "CALL"/"PUT"
4. **到期日期**：可选，来自 `contract.lastTradeDateOrContractMonth`，格式化为 YYYYMMDD

#### 乘数处理逻辑

1. **动态获取**：优先使用 `contract.multiplier` 字段
2. **默认回退**：期权缺失时默认为 100，非期权默认为 1
3. **类型安全**：确保乘数为有效数值

#### 错误处理策略

1. **渐进降级**：期权字段缺失时跳过该字段，不影响其他字段
2. **异常隔离**：任何异常都不中断整个持仓获取流程
3. **向后兼容**：确保现有 API 接口和数据结构不变

### 影响范围

#### 修改的文件
- `backend/ib_client.py`：添加期权判断和函数调用
- `backend/options_utils.py`：新增工具函数文件

#### 保持不变的文件
- `backend/models.py`：数据模型不变
- `frontend/src/types.ts`：类型定义不变
- `frontend/src/components/Positions.tsx`：显示组件不变

#### 行为变更
- **期权合约**：名称和市值计算改进
- **股票合约**：完全保持原有行为
- **期货合约**：完全保持原有行为

### 测试策略

#### 单元测试
- `format_option_symbol()` 的各种输入场景
- `get_option_multiplier()` 的边界条件
- `calculate_market_value_with_multiplier()` 的计算准确性

#### 集成测试
- 模拟 IB 合约对象的完整流程测试
- 期权与非期权的混合持仓场景

#### 验证点
- 期权名称格式：`SPY-580-PUT-20260523`
- 期权市值计算：-1 × $1.50 × 100 = -$150
- 股票不受影响：AAPL 持仓计算保持原有逻辑

### 实施风险

#### 低风险
- 新增独立工具模块，不影响现有逻辑
- 明确的条件分支，期权和非期权处理隔离
- 向后兼容的 API 设计

#### 缓解措施
- 充分的异常处理确保系统稳定性
- 保持原有代码路径作为回退方案
- 渐进部署：可先部署名称修复，再部署市值修复

## 成功标准

1. **功能正确性**
   - 期权名称显示为期望格式
   - 期权市值计算包含正确乘数
   - 非期权合约行为完全不变

2. **系统稳定性** 
   - 任何异常都不中断持仓获取
   - 性能无明显下降

3. **可维护性**
   - 清晰的代码组织和职责分离
   - 完整的错误处理和测试覆盖

## 后续考虑

- 如果未来需要处理期货，可扩展工具函数支持
- 可考虑添加期权到期日预警等增强功能
- 前端可增加期权专用的显示组件