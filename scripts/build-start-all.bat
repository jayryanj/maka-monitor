@echo off
echo Building Docker images with no cache...
docker compose build --no-cache

echo Starting Docker containers in detached mode...
docker compose up --detach
pause