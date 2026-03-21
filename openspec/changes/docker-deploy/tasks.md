# Docker 部署配置

## 概述

为移动开发平台创建 Docker 容器化部署配置。

## 后端任务

### 1. Dockerfile 配置
- [ ] 1. 创建后端 Dockerfile
- [ ] 2. 配置 Python 虚拟环境
- [ ] 3. 安装依赖并优化镜像大小

### 2. 前端 Dockerfile
- [ ] 4. 创建前端 Dockerfile (多阶段构建)
- [ ] 5. 配置 Nginx

### 3. Docker Compose
- [ ] 6. 创建 docker-compose.yml
- [ ] 7. 配置 Redis 服务
- [ ] 8. 配置 Celery Worker
- [ ] 9. 配置 Nginx 反向代理
- [ ] 10. 添加环境变量配置

## 前端任务

### 4. 环境配置
- [ ] 11. 创建 .env.example
- [ ] 12. 配置 API 地址

## 验收标准

- [ ] 后端镜像可以构建
- [ ] 前端镜像可以构建
- [ ] Docker Compose 可以启动所有服务
- [ ] 服务间可以正常通信
