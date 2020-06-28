@ECHO OFF

SET ATOPA_APP_PASS=%1
SET ATOPA_SERVER_IP=%2
SET ATOPA_SERVER_PORT=%3
SET LOCAL_IP=%4
SET ATOPA_APP_PATH=.\atopa_app
SET ATOPA_APP_URL=https://github.com/AndreaCarballo/atopa_app.git

IF "%4"=="" (echo Uso: .\instalador_atopa_app_windows.bat contraseña ip_servidor puerto_servidor ip_ordenador)
IF "%4"=="" (set /P ATOPA_APP_PASS=Introduzca la contraseña que quiere darle a la base de datos de la aplicación:)
IF "%4"=="" (set /P ATOPA_SERVER_IP=Introduzca la ip del servidor:)
IF "%4"=="" (set /P ATOPA_SERVER_PORT=Introduzca el puerto del servidor:)
IF "%4"=="" (set /P LOCAL_IP=Introduzca la ip de su ordenador:)
echo Iniciando la instalación...

IF NOT EXIST %ATOPA_APP_PATH% GOTO NOWINDIR
  CD %ATOPA_APP_PATH%
  git pull
  GOTO FIN
:NOWINDIR
git clone --branch master %ATOPA_APP_URL%
CD %ATOPA_APP_PATH%

:FIN
echo Creando las variables de entorno ....

echo ENV_PASSWORD=%ATOPA_APP_PASS% > .env
echo ENV_SERVER_IP=%ATOPA_SERVER_IP% >>.env
echo ENV_SERVER_PORT=%ATOPA_SERVER_PORT% >>.env
echo ENV_LOCAL_IP=%LOCAL_IP% >>.env

echo ENV_MYSQL_ROOT_PASSWORD=%ATOPA_APP_PASS% >>.env


"C:\Program Files (x86)\GnuWin32\bin\openssl.exe" req -x509 -newkey rsa:4096 -keyout atopa_key.pem -out atopa.pem -days 365 -nodes -config req.conf -sha256

echo START https://%LOCAL_IP%:8020 >> ejecutar_atopa_app_windows.bat

SET LF=^


REM important to have two blank lines after the SET command
<NUL set /p=/wait^%LF%%LF%> entrypoint
<NUL set /p=cd atopa ^&^& ^\^%LF%%LF%>> entrypoint
<NUL set /p=python3 manage.py makemigrations ^&^& ^\^%LF%%LF%>> entrypoint
<NUL set /p=python3 manage.py migrate^%LF%%LF%>> entrypoint
<NUL set /p=mysql -u root -h db -p%ATOPA_APP_PASS% --default-character-set=utf8 atopa_app ^< /atopa/mysqldumps/startDB.sql ^&^&^%LF%%LF%>> entrypoint
<NUL set /p=gunicorn --workers 3 --user www-data --bind 0.0.0.0:8010 mysite.wsgi:application ^&^%LF%%LF%>> entrypoint
<NUL set /p=/usr/sbin/nginx -g ^"daemon off;^"^%LF%%LF%>> entrypoint

echo @ECHO OFF > comandos.bat
echo IF ^"%%1^"==^"^" (echo Uso: .\comandos.bat build ^^^| up ^^^| down ^^^| restart ^^^| status ^^^| django-shell ^^^| createsuperuser ^^^| makemigrations ^^^| migrate ^^^| compilemessages ^^^| web-shell ^^^| db-shell ^^^| clean-migrations) >> comandos.bat
echo IF ^"%%1^"==^"^" (exit) >> comandos.bat
echo IF ^"%%1^"==^"build^" (docker-compose build) >> comandos.bat
echo IF ^"%%1^"==^"up^" (docker-compose up -d) >> comandos.bat
echo IF ^"%%1^"==^"down^" (docker-compose down) >> comandos.bat
echo IF ^"%%1^"==^"restart^" (docker-compose restart) >> comandos.bat
echo IF ^"%%1^"==^"status^" (docker ps) >> comandos.bat
echo IF ^"%%1^"==^"django-shell^" (docker-compose exec web python3 /atopa/atopa/manage.py shell) >> comandos.bat
echo IF ^"%%1^"==^"createsuperuser^" (docker-compose exec web python3 /atopa/atopa/manage.py createsuperuser) >> comandos.bat
echo IF ^"%%1^"==^"makemigrations^" (docker-compose exec web python3 /atopa/atopa/manage.py makemigrations) >> comandos.bat
echo IF ^"%%1^"==^"migrate^" (docker-compose exec web python3 /atopa/atopa/manage.py migrate) >> comandos.bat
echo IF ^"%%1^"==^"compilemessages^" (docker-compose exec web python3 /atopa/atopa/manage.py compilemessages) >> comandos.bat
echo IF ^"%%1^"==^"web-shell^" (docker exec -it atopa /bin/bash) >> comandos.bat
echo IF ^"%%1^"==^"clean-migrations^" (find . -path ^'*/migrations/*.pyc^'  -delete ^&^& find . -path ^'*/migrations/*.py^' -not -name ^'__init__.py^' -delete ^&^& echo ^'DONE!^') >> comandos.bat
echo IF ^"%%1^"==^"db-shell^" (docker exec -it atopa_db mysql -h db -u root -p%ATOPA_APP_PASS%) >> comandos.bat

docker-compose build
docker-compose up -d
set /p=Hit Instalación finalizada correctamente. Pulse ENTER para salir...
