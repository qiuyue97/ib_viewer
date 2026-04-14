# IB Viewer

一个实时监控 Interactive Brokers (IB) 账户资产的 Web 应用，支持多币种资产展示和收益率计算。

## 功能特性

- 📊 **实时资产监控**：自动获取 IB 账户余额和持仓信息
- 💱 **多币种支持**：支持 USD、CNH 现金余额分别显示
- 📈 **收益率计算**：基于资金注入记录计算投资收益率
- 🔄 **自动刷新**：后台定时刷新数据，减少 API 调用
- 🌐 **Web 界面**：简洁的 Web UI，支持实时数据推送

## 技术栈

**后端**
- FastAPI - 现代 Python Web 框架
- ib_insync - Interactive Brokers API 客户端
- SQLAlchemy - 数据库 ORM
- WebSocket - 实时数据推送

**前端**
- React 19 - UI 框架
- TypeScript - 类型安全
- Vite - 构建工具
- Tailwind CSS - 样式框架

**部署**
- Docker & Docker Compose
- IB Gateway - 官方交易网关

## 快速开始

### 环境要求

- Docker & Docker Compose
- Interactive Brokers 账户
- Node.js 18+ (仅开发时需要)

### 部署步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd ib_viewer
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   ```
   
   编辑 `.env` 文件，填入您的 IB 账户信息：
   ```env
   IB_ACCOUNT_ID=your_account_id     # 子账户号（可选）
   IB_USERNAME=your_ib_username      # IB 用户名
   IB_PASSWORD=your_ib_password      # IB 密码
   VNC_PASSWORD=your_vnc_password    # VNC 访问密码
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **访问应用**
   - Web 界面：http://localhost:8100
   - VNC (手动登录)：vnc://localhost:5900

### 前端开发构建

如需单独构建前端：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 构建产物在 dist/ 目录
```

## 服务说明

### 容器服务

- **ib-gateway**: IB 官方网关容器，处理 TWS 连接
- **ib-viewer**: 主应用容器（后端 + 前端）
- **watchdog**: 监控容器，在 ib-gateway 重启时自动重启应用

### 端口映射

- `8100`: Web 应用主端口
- `4001`: IB Gateway API 端口
- `5900`: VNC 端口（用于手动登录）

## API 接口

### 资金注入管理

基础地址：`http://localhost:8100/api`

**查询记录**
```bash
curl http://localhost:8100/api/capital
```

**新增记录**
```bash
curl -X POST http://localhost:8100/api/capital \
  -H "Content-Type: application/json" \
  -d '{
    "amount_cny": 100000.00,
    "injected_on": "2024-01-15", 
    "note": "初始入金"
  }'
```

**删除记录**
```bash
curl -X DELETE http://localhost:8100/api/capital/{id}
```

## 数据说明

- **现金余额**：分别显示 USD 和 CNH (离岸人民币) 持有量
- **汇率**：自动获取 USDCNH 实时汇率，支持历史数据回退
- **持仓**：显示所有证券持仓，自动转换为人民币估值
- **收益率**：基于历次资金注入计算总收益率

## 注意事项

1. **账户权限**：确保 IB 账户已开通 API 访问权限
2. **网络连接**：容器需要访问 IB 服务器，确保网络连通
3. **数据安全**：`.env` 文件包含敏感信息，已在 `.gitignore` 中排除
4. **交易模式**：默认连接实盘账户，如需纸上交易请修改 `TRADING_MODE`

## 故障排除

**连接问题**
- 检查 IB 账户状态和 API 权限
- 通过 VNC 端口 5900 访问 TWS 界面进行手动登录

**数据异常**
- 查看容器日志：`docker-compose logs ib-viewer`
- 重启服务：`docker-compose restart`

**构建失败**
- 确保网络连接正常（使用阿里云 PyPI 镜像）
- 清理并重新构建：`docker-compose build --no-cache`

## 许可证

MIT License