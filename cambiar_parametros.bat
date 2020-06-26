@ECHO OFF

echo ¿Qué parámetro desea cambiar?
echo 1. Contraseña
echo 2. Ip del servidor
echo 3. Puerto del servidor
echo 4. Ip del ordenador
set /P option=Introduzca el número correspondiente con su opción elegida (1-4):

IF "%option%"=="1" (goto pass)
IF "%option%"=="2" (goto ipserver)
IF "%option%"=="3" (goto port)
IF "%option%"=="4" (goto iplocal)
goto :eof


:pass
set /P pass=Introduzca su contraseña:
echo ENV_PASSWORD=%pass% > .env2
echo ENV_MYSQL_ROOT_PASSWORD=%pass% >>.env2
for /f "usebackq tokens=1-2 delims==" %%a in (.env) do (
    if /i "%%a"=="ENV_SERVER_IP" (
        echo ENV_SERVER_IP=%%b >> .env2
    ) else if /i "%%a"=="ENV_SERVER_PORT" (
        echo ENV_SERVER_PORT=%%b >> .env2
    ) else if /i "%%a"=="ENV_LOCAL_IP" (
        echo ENV_LOCAL_IP=%%b >> .env2
    )
)
del .env
ren ".env2" ".env"
goto :fin

:ipserver
set /P ipserver=Introduzca la ip del servidor:
for /f "usebackq tokens=1-2 delims==" %%a in (.env) do (
    if /i "%%a"=="ENV_SERVER_PORT" (
        echo ENV_SERVER_PORT=%%b >> .env2
    ) else if /i "%%a"=="ENV_PASSWORD" (
        echo ENV_PASSWORD=%%b > .env2
        echo ENV_MYSQL_ROOT_PASSWORD=%%b >> .env2
        echo ENV_SERVER_IP=%ipserver% >> .env2
    ) else if /i "%%a"=="ENV_LOCAL_IP" (
        echo ENV_LOCAL_IP=%%b >> .env2
    )
)
del .env
ren ".env2" ".env"
goto :fin

:port
set /P port=Introduzca el puerto del servidor:
for /f "usebackq tokens=1-2 delims==" %%a in (.env) do (
    if /i "%%a"=="ENV_SERVER_IP" (
        echo ENV_SERVER_IP=%%b >> .env2
        echo ENV_SERVER_PORT=%port% >> .env2
    ) else if /i "%%a"=="ENV_PASSWORD" (
        echo ENV_PASSWORD=%%b > .env2
        echo ENV_MYSQL_ROOT_PASSWORD=%%b >> .env2
    ) else if /i "%%a"=="ENV_LOCAL_IP" (
        echo ENV_LOCAL_IP=%%b >> .env2
    )
)
del .env
ren ".env2" ".env"
goto :fin

:iplocal

echo ¿Cómo se conecta a Internet?
echo 1. Wi-Fi
echo 2. Cable Ethernet
set /P wifi=Introduzca el número correspondiente con su opción elegida (1-2):
setlocal enabledelayedexpansion
IF "%wifi%"=="1" (goto wifi)
IF "%wifi%"=="2" (goto ether)
goto :iplocal
:wifi
set adapter=Wi-Fi
goto next
:ether
set "adapter=Ethernet Ethernet"
:next
set adapterfound=false
set iplocal=""
for /f "usebackq tokens=1-2 delims=:" %%f in (`ipconfig`) do (
    set "item=%%f"
    if /i not "x!item:%adapter%=!"=="x!item!" (
        set adapterfound=true
    ) else if not "!item!"=="!item:IPv4=!" if "!adapterfound!"=="true" (
        echo Tu dirección IP es: %%g
        set iplocal=%%g
        set adapterfound=false
    )
)
for /f "usebackq tokens=1-2 delims==" %%a in (.env) do (
    if /i "%%a"=="ENV_SERVER_IP" (
        echo ENV_SERVER_IP=%%b >> .env2
    ) else if /i "%%a"=="ENV_PASSWORD" (
        echo ENV_PASSWORD=%%b > .env2
        echo ENV_MYSQL_ROOT_PASSWORD=%%b >> .env2
    ) else if /i "%%a"=="ENV_SERVER_PORT" (
        echo ENV_SERVER_PORT=%%b >> .env2
    )
)
if %iplocal%=="" (
    setlocal disabledelayedexpansion
    echo No se pudo encontrar la ip
    set /P ipnew=Introduzca su ip:
    goto inputip
    
) else (
    echo ENV_LOCAL_IP=%iplocal:~1% >> .env2
    goto nextip
)
:inputip
echo ENV_LOCAL_IP=%ipnew% >> .env2
:nextip
del .env
ren ".env2" ".env"
goto :fin

:fin
docker-compose down
docker-compose up -d
set /p=Cambios realizados correctamente. Pulse ENTER para cerrar...