@echo off
echo Rebuilding server_producer service
docker compose build --no-cache

echo Restarting server_producer service
docker compose up -d --no-deps server

echo Restarting consumer service
docker compose up -d --no-deps consumer
