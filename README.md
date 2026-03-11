## 功能特性

### 核心监控功能
- ✅ **系统监控**: CPU、内存、磁盘、网络使用情况
- ✅ **会话统计**: 活跃会话数、历史会话、会话时长
- ✅ **工具使用**: 各工具调用频率、成功率统计
- ✅ **模型使用**: API 调用次数、token 消耗、响应时间

### 高级监控功能
- 🔄 **任务状态追踪**: todo, on-going, done, stuck 状态及资源占用
- 🤖 **代理状态监控**: busy, idle, stuck 状态及资源占用
- 📚 **技能清单管理**: 按代理查看技能，按技能查看代理分布
- 🔔 **实时告警**: 系统异常、性能下降、错误告警

### 技术特性
- ⚡ **实时更新**: WebSocket 实时数据推送
- 📱 **响应式设计**: 支持桌面和移动端
- 🎨 **现代化UI**: Ant Design + Recharts 可视化
- 🐳 **容器化部署**: Docker 一键部署

## 技术架构

### 前端技术栈
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI 库**: Ant Design 5
- **图表库**: Recharts 2
- **状态管理**: React Context
- **实时通信**: Socket.io Client

### 后端技术栈
- **运行时**: Node.js 18+
- **框架**: Express 4
- **数据库**: SQLite 3
- **实时通信**: Socket.io 4
- **任务调度**: node-cron

### 部署架构
```
前端 (React) → Nginx → 用户浏览器
    ↑               ↑
后端 (Node.js) ← WebSocket
    ↓
数据库 (SQLite)
```
