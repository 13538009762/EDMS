[简体中文](./README.zh-CN.md) | English

# EDMS Docker Deployment Guide

## Directory Structure

```
match/
├── bin/                    # Runtime files and startup scripts directory
│   ├── Windows/           # Windows scripts
│   │   ├── start.bat      # Windows startup script
│   │   └── stop.bat       # Windows stop script
│   ├── Linux/             # Linux/macOS scripts
│   │   ├── start.sh       # Linux/macOS startup script
│   │   └── stop.sh        # Linux/macOS stop script
│   ├── .env               # Environment configuration (auto-generated)
│   ├── data/              # Data persistence directory (auto-generated)
│   └── images/            # Docker image export files (auto-generated)
│       ├── edms-backend.tar
│       └── edms-frontend.tar
├── docker/                 # Docker configuration directory
│   ├── backend/
│   │   └── Dockerfile     # Backend Dockerfile
│   ├── frontend/
│   │   ├── Dockerfile     # Frontend Dockerfile
│   │   └── nginx.conf     # Nginx configuration
│   ├── docker-compose.yml # Docker Compose configuration
│   ├── .env.example       # Environment variable template
│   ├── build.bat          # Windows build script
│   └── build.sh           # Linux/macOS build script
├── backend/                # Backend code
└── frontend/               # Frontend code
```

## Quick Start

### First-Time Setup

#### Windows Users

1. **Build**
   ```cmd
   docker\build.bat
   ```

2. **Start Services**
   ```cmd
   bin\Windows\start.bat
   ```

3. **Access Application**
   - Frontend: http://localhost
   - Backend API: http://localhost/api

4. **Stop Services**
   ```cmd
   bin\Windows\stop.bat
   ```

#### Linux/macOS Users

1. **Add Execute Permissions**
   ```bash
   chmod +x bin/Linux/*.sh docker/*.sh
   ```

2. **Build**
   ```bash
   ./docker/build.sh
   ```

3. **Start Services**
   ```bash
   ./bin/Linux/start.sh
   ```

4. **Access Application**
   - Frontend: http://localhost
   - Backend API: http://localhost/api

5. **Stop Services**
   ```bash
   ./bin/Linux/stop.sh
   ```

## Configuration

### Environment Variables (.env File)

The `.env` file is automatically created during the build process. Important configuration items:

- `WEB_PORT`: Web service port (default 80)
- `JWT_SECRET_KEY`: JWT secret key (**auto-generated if empty**, must be changed in production)
- `CORS_ORIGINS`: Allowed CORS origins
- `DATABASE_URL`: Database connection string

### Data Persistence

All data is saved in the `docker/data/` directory:
- `docker/data/backend/` - Backend application data
- `docker/data/database/` - Database files

**Data will not be lost due to container deletion**

## Advanced Usage

### View Logs

```bash
# Windows
docker-compose -f docker/docker-compose.yml logs -f

# Linux/macOS
docker compose -f docker/docker-compose.yml logs -f
```

### Restart Services

```bash
# Windows
docker-compose -f docker/docker-compose.yml restart

# Linux/macOS
docker compose -f docker/docker-compose.yml restart
```

### Rebuild

```bash
# Windows
docker\build.bat

# Linux/macOS
./docker/build.sh
```

### Complete Cleanup

```bash
# Windows
docker-compose -f docker/docker-compose.yml down -v

# Linux/macOS
docker compose -f docker/docker-compose.yml down -v
```

## Image Export and Distribution

### Export Images

**Windows:**
```cmd
bin\export-images.bat
```

**Linux/macOS:**
```bash
./bin/export-images.sh
```

Generated files:
- `edms-backend.tar` - Backend image
- `edms-frontend.tar` - Frontend image

### Import Images

On the target machine:

```bash
docker load -i edms-backend.tar
docker load -i edms-frontend.tar
```

Then run the build script and startup script.

## Troubleshooting

### Port in Use

**Error Message**: `Port 80 is already in use`

**Solution**:
1. Edit the `docker/.env` file
2. Change `WEB_PORT=8080` (or another unused port)
3. Rebuild: `docker\build.bat` or `./docker/build.sh`
4. Restart services

### Docker Cannot Start

**Windows**:
- Ensure Docker Desktop is installed and running
- Check if Hyper-V is enabled

**Linux**:
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker
sudo systemctl start docker
```

### .env File Not Found

**Error**: `ERROR: .env file not found! Please run docker/build.bat first`

**Solution**: Run the build script first:
- Windows: `docker\build.bat`
- Linux/macOS: `./docker/build.sh`

### Database Errors

If running for the first time or migrating data:
```bash
# View backend logs
docker-compose -f docker/docker-compose.yml logs backend
```

## Security Recommendations

1. **Change JWT Secret**: Auto-generated key is for development only. Must change `JWT_SECRET_KEY` in production
2. **Use HTTPS**: Configure SSL certificates in production
3. **Restrict CORS**: Configure `CORS_ORIGINS` according to actual needs
4. **Regular Backups**: Regularly backup the `docker/data/` directory

## System Requirements

- Docker 20.10+
- Docker Compose 2.0+ (or Docker Desktop)
- 2GB+ available memory
- 5GB+ available disk space

## Technology Stack

**Backend**:
- Python 3.11
- Flask 3.0
- SQLAlchemy 2.0
- SQLite (default)

**Frontend**:
- Node.js 20
- Vue 3
- Vite 6
- Element Plus

**Server**:
- Nginx (Alpine)

## Support and Feedback

If you have any issues, please check the logs or contact technical support.
