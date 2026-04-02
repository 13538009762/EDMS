[简体中文](./README.zh-CN.md) | English

# EDMS Docker 部署指南

## 目录结构

```
match/
├── bin/                    # 启动脚本和运行时文件目录
│   ├── Windows/           # Windows 系统脚本
│   │   ├── start.bat      # Windows 启动脚本
│   │   └── stop.bat       # Windows 停止脚本
│   ├── Linux/             # Linux/macOS 系统脚本
│   │   ├── start.sh       # Linux/macOS 启动脚本
│   │   └── stop.sh        # Linux/macOS 停止脚本
│   ├── .env               # 环境变量配置（自动生成）
│   ├── data/              # 数据持久化目录（自动生成）
│   └── images/            # Docker 镜像导出文件（自动生成）
│       ├── edms-backend.tar
│       └── edms-frontend.tar
├── docker/                 # Docker 配置目录
│   ├── backend/
│   │   └── Dockerfile     # 后端 Dockerfile
│   ├── frontend/
│   │   ├── Dockerfile     # 前端 Dockerfile
│   │   └── nginx.conf     # Nginx 配置
│   ├── docker-compose.yml # Docker Compose 配置
│   ├── .env.example       # 环境变量模板
│   ├── build.bat          # Windows 构建脚本
│   └── build.sh           # Linux/macOS 构建脚本
├── backend/                # 后端代码
└── frontend/               # 前端代码
```

## 快速开始

### 首次设置

#### Windows 用户

1. **构建**
   ```cmd
   docker\build.bat
   ```

2. **启动服务**
   ```cmd
   bin\Windows\start.bat
   ```

3. **访问应用**
   - 前端：http://localhost
   - 后端 API：http://localhost/api

4. **停止服务**
   ```cmd
   bin\Windows\stop.bat
   ```

#### Linux/macOS 用户

1. **添加执行权限**
   ```bash
   chmod +x bin/Linux/*.sh docker/*.sh
   ```

2. **构建**
   ```bash
   ./docker/build.sh
   ```

3. **启动服务**
   ```bash
   ./bin/Linux/start.sh
   ```

4. **访问应用**
   - 前端：http://localhost
   - 后端 API：http://localhost/api

5. **停止服务**
   ```bash
   ./bin/Linux/stop.sh
   ```

## 配置说明

### 环境变量 (.env 文件)

`.env` 文件在构建过程中自动创建。重要配置项：

- `WEB_PORT`: Web 服务端口（默认 80）
- `JWT_SECRET_KEY`: JWT 密钥（**为空时自动生成**，生产环境务必修改）
- `CORS_ORIGINS`: 允许的 CORS 来源
- `DATABASE_URL`: 数据库连接字符串

### 数据持久化

所有数据保存在 `docker/data/` 目录：
- `docker/data/backend/` - 后端应用数据
- `docker/data/database/` - 数据库文件

**数据不会因容器删除而丢失**

## 高级用法

### 查看日志

```bash
# Windows
docker-compose -f bin\docker-compose.yml logs -f

# Linux/macOS
docker compose -f bin/docker-compose.yml logs -f
```

### 重启服务

```bash
# Windows
docker-compose -f bin\docker-compose.yml restart

# Linux/macOS
docker compose -f bin/docker-compose.yml restart
```

### 重新构建

```bash
# Windows
docker\build.bat

# Linux/macOS
./docker/build.sh
```

### 完全清理

```bash
# Windows
docker-compose -f bin\docker-compose.yml down -v

# Linux/macOS
docker compose -f bin/docker-compose.yml down -v
```

## 镜像导出与分发

### 导出镜像

**Windows:**
```cmd
bin\export-images.bat
```

**Linux/macOS:**
```bash
./bin/export-images.sh
```

生成文件：
- `edms-backend.tar` - 后端镜像
- `edms-frontend.tar` - 前端镜像

### 导入镜像

在目标机器上：

```bash
docker load -i edms-backend.tar
docker load -i edms-frontend.tar
```

然后运行构建脚本和启动脚本。

## 故障排查

### 端口被占用

**错误信息**: `Port 80 is already in use`

**解决方案**:
1. 编辑 `docker/.env` 文件
2. 修改 `WEB_PORT=8080`（或其他未被占用的端口）
3. 重新构建：`docker\build.bat` 或 `./docker/build.sh`
4. 重新启动服务

### Docker 无法启动

**Windows**:
- 确保 Docker Desktop 已安装并运行
- 检查 Hyper-V 是否启用

**Linux**:
```bash
# 检查 Docker 状态
sudo systemctl status docker

# 启动 Docker
sudo systemctl start docker
```

### .env 文件未找到

**错误**: `ERROR: .env file not found! Please run docker/build.bat first`

**解决方案**: 先运行构建脚本：
- Windows: `docker\build.bat`
- Linux/macOS: `./docker/build.sh`

### 数据库错误

如果是首次运行或迁移数据：
```bash
# 查看后端日志
docker-compose -f docker/docker-compose.yml logs backend
```

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+ (或 Docker Desktop)
- 2GB+ 可用内存
- 5GB+ 可用磁盘空间

## 技术栈

**后端**:
- Python 3.11
- Flask 3.0
- SQLAlchemy 2.0
- SQLite (默认)

**前端**:
- Node.js 20
- Vue 3
- Vite 6
- Element Plus

**服务器**:
- Nginx (Alpine)

## 支持与反馈

如有问题，请查看日志或联系技术支持。
