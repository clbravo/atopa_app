#! /bin/bash

ATOPA_APP_PATH=~/atopa/atopa_app
LOCAL_IP=$1

get_ATOPA_APP()
{
	echo "Cambiando al directorio de ATOPA_APP"

	if [ -d $ATOPA_APP_PATH ];
	then
		echo "Cambiado al directorio"  $ATOPA_APP_PATH
		cd $ATOPA_APP_PATH
		git pull
	else
		echo "Primero debe instalar la aplicacion (instalador_atopa_app.sh)"
		exit
	fi
}

#Comprobar que se han introducido los valores de user, pass y host
if [ $# -ne 1 ];
then
	echo "Uso: ./ejecutar_atopa_app.sh ip_ordenador"
    	exit
fi

#Actualiza la aplicacion atopa
get_ATOPA_APP

cd $ATOPA_APP_PATH

STATE=$(sudo  docker container inspect atopa -f '{{.State.Status}}')

echo $STATE

if [[ $STATE == *running* ]] 
then
	sudo make restart
else
 	 sudo make up
fi

sleep 1
if which xdg-open > /dev/null
then
  xdg-open https://$LOCAL_IP:8020
elif which gnome-open > /dev/null
then
  gnome-open https://$LOCAL_IP:8020
fi
