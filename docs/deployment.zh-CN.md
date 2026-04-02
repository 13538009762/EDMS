[简体中文](./deployment.zh-CN.md) | [English](./deployment.en.md)

# 部署

1. 安装后端依赖，并为生产环境设置 `JWT_SECRET_KEY` / `SECRET_KEY`。
2. 使用生产级 WSGI 服务器运行 Flask（例如 gunicorn + eventlet 用于 Socket.IO），或仅用于演示时使用 `socketio.run`。
3. 构建前端（`cnpm run build`），通过 nginx 或类似工具提供 `frontend/dist` 服务，并将 `/api` 和 `/socket.io` 代理到后端源。
