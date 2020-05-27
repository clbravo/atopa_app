@ECHO OFF

SET ATOPA_APP_PASS=%1
SET ATOPA_SERVER_IP=%2
SET ATOPA_SERVER_PORT=%3
SET LOCAL_IP=%4
SET ATOPA_SERVER_PATH=.\atopa_app
SET ATOPA_SERVER_URL=https://github.com/clbravo/atopa_app.git

IF "%4"=="" (echo Uso: ./instalador_atopa_app_windows.bat contraseña ip_servidor puerto_servidor ip_ordenador)
IF "%4"=="" (exit)

IF NOT EXIST %ATOPA_SERVER_PATH% GOTO NOWINDIR
  CD %ATOPA_SERVER_PATH%
  rem git pull
  GOTO FIN
:NOWINDIR
git clone --branch master %ATOPA_SERVER_URL%
CD %ATOPA_SERVER_PATH%

:FIN
echo Creando las variables de entorno ....

echo ENV_PASSWORD=%ATOPA_APP_PASS% > .env
echo ENV_SERVER_IP=%ATOPA_SERVER_IP% >>.env
echo ENV_SERVER_PORT=%ATOPA_SERVER_PORT% >>.env


echo ENV_MYSQL_ROOT_PASSWORD=%ATOPA_APP_PASS% >>.env

echo ENV_EMAIL_HOST=smtp.gmail.com >> .env
echo ENV_EMAIL_HOST_USER= >> .env  	 
echo ENV_EMAIL_HOST_PASSWORD= >> .env 
echo ENV_EMAIL_PORT=587 >> .env

"C:\Program Files (x86)\GnuWin32\bin\openssl.exe" req -x509 -newkey rsa:4096 -keyout atopa_key.pem -out atopa.pem -days 365 -nodes -config req.conf -sha256

echo /wait > entrypoint

echo cd atopaserver ^&^& ^\ >> entrypoint
echo python3 manage.py makemigrations ^&^& ^\ >> entrypoint
echo python3 manage.py migrate >> entrypoint
echo mysql -u root -h db -p%ATOPA_APP_PASS% --default-character-set=utf8 atopa_app ^< /atopa/mysqldumps/startDB.sql >> entrypoint
echo gunicorn --workers 3 --bind 0.0.0.0:8010 atopaserver.wsgi:application ^& >> entrypoint
echo /usr/sbin/nginx -g ^"daemon off;^" >> entrypoint

echo @ECHO OFF > comandos.bat
echo IF ^"%%1^"==^"^" (echo Uso: ./comandos.bat build ^| up ^| down ^| restart ^| status ^| django-shell ^| createsuperuser ^| makemigrations ^| migrate ^| compilemessages ^| web-shell ^| db-shell ^| clean-migrations) >> comandos.bat
echo IF ^"%%1^"==^"^" (exit) >> comandos.bat
echo IF ^"%%1^"==^"build^" (docker-compose build) >> comandos.bat
echo IF ^"%%1^"==^"up^" (docker-compose up -d) >> comandos.bat
echo IF ^"%%1^"==^"down^" (docker-compose down) >> comandos.bat
echo IF ^"%%1^"==^"restart^" (docker-compose restart) >> comandos.bat
echo IF ^"%%1^"==^"status^" (docker ps) >> comandos.bat
echo IF ^"%%1^"==^"django-shell^" (docker-compose exec web python /atopa/atopaserver/manage.py shell) >> comandos.bat
echo IF ^"%%1^"==^"createsuperuser^" (docker-compose exec web python /atopa/atopaserver/manage.py createsuperuser) >> comandos.bat
echo IF ^"%%1^"==^"makemigrations^" (docker-compose exec web python /atopa/atopaserver/manage.py makemigrations) >> comandos.bat
echo IF ^"%%1^"==^"migrate^" (docker-compose exec web python /atopa/atopaserver/manage.py migrate) >> comandos.bat
echo IF ^"%%1^"==^"compilemessages^" (docker-compose exec web python /atopa/atopaserver/manage.py compilemessages) >> comandos.bat
echo IF ^"%%1^"==^"web-shell^" (docker exec -it atopaserver /bin/bash) >> comandos.bat
echo IF ^"%%1^"==^"clean-migrations^" (find . -path ^'*/migrations/*.pyc^'  -delete ^&^& find . -path ^'*/migrations/*.py^' -not -name ^'__init__.py^' -delete ^&^& echo ^'DONE!^') >> comandos.bat
echo IF ^"%%1^"==^"db-shell^" (docker exec -it atopaserver_db mysql -h db -u root -p%ATOPA_APP_PASS%) >> comandos.bat

docker-compose build