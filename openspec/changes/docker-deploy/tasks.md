# Docker 部署配置

## 概述

为移动开发平台创建 Docker 容器化部署配置。

## 后端任务

### 1. Dockerfile 配置
- [x] 1. 创建后端 Dockerfile
- [x] 2. 配置 Python 虚拟环境
- [x] 3. 安装依赖并优化镜像大小

### 2. 前端 Dockerfile
- [x] 4. 创建前端 Dockerfile (多阶段构建)
- [x] 5. 配置 Nginx

### 3. Docker Compose
- [x] 6. 创建 docker-compose.yml
- [x] 7. 配置 Redis 服务
- [x] 8. 配置 Celery Worker
- [x] 9. 配置 Nginx 反向代理
- [x] 10. 添加环境变量配置

## 前端任务

### 4. 环境配置
- [x] 11. 创建 .env.example
- [x] 12. 配置 API 地址

## 验收标准

- [x] 后端镜像可以构建
- [x] 前端镜像可以构建
- [x] Docker Compose 可以启动所有服务
- [x] 服务间可以正常通信

## 实现文件

- backend/Dockerfile - 后端多阶段构建
- frontend/Dockerfile - 前端多阶段构建 + Nginx
- frontend/nginx.conf - Nginx 配置
- docker-compose.yml - 服务编排
- .env.example - 环境变量模板
