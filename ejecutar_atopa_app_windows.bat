@ECHO OFF

echo Actualizando la aplicación...
git pull
docker-compose restart
set /p=Pulse ENTER para abrir la aplicación...

