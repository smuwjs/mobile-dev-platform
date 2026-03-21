# Phase 3: OpenSpec 集成与 Claude Code 执行

## 概述

实现移动端开发管理平台的核心功能：OpenSpec 需求拆解、Claude Code 任务执行、成本量化评估。

## 后端任务

### 1. OpenSpec 集成

- [x] 1. 创建 OpenSpec 服务层 (`app/services/openspec.py`)
- [x] 2. 实现 `generate_proposal()` - 生成需求提案
- [x] 3. 实现 `generate_design()` - 生成技术架构设计
- [x] 4. 实现 `generate_specs()` - 生成功能规范拆解
- [x] 5. 实现 `generate_tasks()` - 生成实现任务清单
- [x] 6. 创建 OpenSpec API 端点 (`/api/v1/openspec/*`)
- [x] 7. 添加 OpenAPI 文档集成

### 2. Claude Code 执行器

- [x] 8. 创建 Claude Code 服务层 (`app/services/claude_executor.py`)
- [x] 9. 实现 tmux 会话管理（创建、暂停、恢复、终止）
- [x] 10. 实现任务步骤执行逻辑
- [x] 11. 实现输出捕获与解析
- [x] 12. 创建任务执行 API 端点 (`/api/v1/exec/*`)
- [x] 13. 实现执行状态管理

### 3. 异常检测与告警

- [x] 14. 实现无输出超时检测（5分钟）
- [x] 15. 实现编译失败检测
- [x] 16. 实现 API 限流自动处理
- [x] 17. 创建告警服务 (`app/services/alert.py`)
- [x] 18. 添加告警记录 API

### 4. 成本量化模型

- [x] 19. 创建成本计算服务 (`app/services/cost_calculator.py`)
- [x] 20. 实现时间预估算法
- [x] 21. 实现 Token 预估算法
- [x] 22. 实现成本计算逻辑
- [x] 23. 创建成本记录模型与 API

### 5. 数据模型扩展

- [x] 24. 扩展 Projects 表（添加 platform, tech_stack, architecture 等字段）
- [x] 25. 扩展 Tasks 表（添加 proposal, design, specs, tasks 等 JSON 字段）
- [x] 26. 创建 TaskLogs 表（任务执行日志）
- [x] 27. 创建 Metrics 表（量化数据记录）

## 前端任务

### 6. OpenSpec 拆解页面

- [x] 28. 创建需求输入表单组件 (`RequirementInputForm.tsx`)
- [x] 29. 实现拆解结果展示页面 (`DecompositionResultView.tsx`)
- [x] 30. 实现任务清单编辑功能 (`TaskListEditor.tsx`)
- [x] 31. 实现成本预估展示组件 (`CostEstimation.tsx`)

### 7. 任务执行页面

- [x] 32. 创建任务执行控制面板（开始/暂停/恢复/终止）(`ExecutionControlPanel.tsx`)
- [x] 33. 实现实时日志输出窗口 (`RealtimeLogViewer.tsx`)
- [x] 34. 实现进度条组件 (`TaskProgress.tsx`)
- [x] 35. 实现异常告警显示 (`AlertDisplay.tsx`)

### 8. 成本统计页面

- [x] 36. 创建成本统计仪表盘 (`pages/costs/index.tsx`)
- [x] 37. 实现历史数据分析图表 (`pages/estimation/index.tsx`)
- [x] 38. 实现预估模型配置页面 (`pages/estimation/index.tsx`)

## 部署任务

### 9. 环境配置

- [x] 39. 创建 OpenClaw Skill 配置文件
- [x] 40. 配置 Claude Code 运行环境
- [x] 41. 添加 API 密钥管理

## 验收标准

- [ ] 可以通过 UI 输入需求并生成完整的 OpenSpec 文档
- [ ] 可以启动 Claude Code 执行开发任务
- [ ] 可以实时监控任务执行进度和日志
- [ ] 可以检测异常并发送告警
- [ ] 可以计算和展示成本预估与实际消耗
- [ ] 服务层测试覆盖率 >70%
