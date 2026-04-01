# Deployment

1. Install backend dependencies and set `JWT_SECRET_KEY` / `SECRET_KEY` for production.
2. Run Flask with a production WSGI server (e.g. gunicorn + eventlet for Socket.IO), or use `socketio.run` for demos only.
3. Build the frontend (`cnpm run build`), serve `frontend/dist` via nginx or similar, and proxy `/api` and `/socket.io` to the backend origin.
