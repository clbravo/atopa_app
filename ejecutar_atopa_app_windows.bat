@ECHO OFF

echo Actualizando la aplicación...
git pull
docker-compose restart
set /p=Hit Pulse ENTER para abrir la aplicación...

