#! /bin/bash

ATOPA_HOME=~/atopa
ATOPA_APP_PATH=$ATOPA_HOME/atopa_app
ATOPA_APP_URL=https://github.com/clbravo/atopa_app.git
ATOPA_APP_PASS=$1
ATOPA_SERVER_IP=$2
ATOPA_SERVER_PORT=$3
LOCAL_IP=$4

get_ATOPA_APP()
{
        if [ -d $ATOPA_HOME ] ;
        then
                echo "Actualizando el directorio" $ATOPA_HOME
                cd $ATOPA_HOME

                if [ -d $ATOPA_APP_PATH ];
                then
                        echo "Cambiado al directorio" $ATOPA_APP_PATH
                        cd $ATOPA_APP_PATH
                        git pull
                else
                        echo "Clonando la aplicacion" $ATOPA_HOME
                        git clone --branch master $ATOPA_APP_URL
                fi
        else
                echo "Creando directorio" $ATOPA_HOME
                mkdir ~/atopa
                cd ~/atopa
                echo "Clonando la aplicacion " $ATOPA_APP_PATH
                git clone --branch master $ATOPA_APP_URL
        fi
}

crearVariablesEntorno()
{
	echo "Creando las variables de entorno ...."

	cd $ATOPA_APP_PATH
	# Settings
	echo "ENV_PASSWORD=$ATOPA_APP_PASS" > .env
	echo "ENV_SERVER_IP=$ATOPA_SERVER_IP" >>.env
	echo "ENV_SERVER_PORT=$ATOPA_SERVER_PORT" >>.env
	echo "ENV_LOCAL_IP=$LOCAL_IP" >>.env

	# Docker
	echo "ENV_MYSQL_ROOT_PASSWORD=$ATOPA_APP_PASS" >>.env

}

actualizarAccesoBaseDatos()
{
        echo "Dando acceso al nuevo usuario ...."

        SHELL_1="bash -c 'docker exec -it atopa_db mysql -h db -u root -p'"
        SHELL_2="bash -c 'docker exec -it atopa_db mysql -h db -u root -p$ATOPA_APP_PASS'"
        ENTRYPOINT_1="mysql -u root -h db -p --default-character-set=utf8 atopa_app < \/atopa\/mysqldumps\/startDB.sql"
        ENTRYPOINT_2="mysql -u root -h db -p$ATOPA_APP_PASS --default-character-set=utf8 atopa_app < \/atopa\/mysqldumps\/startDB.sql"

        cd $ATOPA_HOME/atopa_app
        sed "s/$SHELL_1/$SHELL_2/" ./Makefile >./salida
        mv ./salida ./Makefile
        sed "s/$ENTRYPOINT_1/$ENTRYPOINT_2/" ./entrypoint >./salida
        mv ./salida ./entrypoint
	chmod 750 ./entrypoint
}

generarCertificados()
{
	cd $ATOPA_APP_PATH
	echo 'Generar un certificado [s/N]:'
	read respuesta

	if [[ $respuesta == *s*  ||  $respuesta == *S* ]]
	then
		req -x509 -newkey rsa:4096 -keyout atopa_key.pem -out atopa.pem -days 365 -nodes -config req.conf -sha256
	else
        	echo "No se ha generado un certificado"
	fi
}


#Comprobar que se han introducido los valores de user, pass y host
if [ $# -ne 4 ];
then 
	echo "Uso: ./instalador_atopa_app.sh contraseña ip_servidor puerto_servidor ip_ordenador"
    	exit
fi

#Instala GIT si es necesario
sudo apt install git
sudo apt-get install build-essential
#Clona o actualiza la aplicacion atopa
get_ATOPA_APP
crearVariablesEntorno
generarCertificados
actualizarAccesoBaseDatos

chmod 750 ejecutar_atopa_app.sh

cd $ATOPA_APP_PATH
mkdir ./logs
mkdir ./atopa/logs
sudo make build
