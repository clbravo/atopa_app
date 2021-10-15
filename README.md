# Atopa_App

Atopa App in django

## Estructura de carpetas

Esta es la estructura de carpetas que sigue la aplicación dentro del directorio donde se haya clonado.

- atopa_app/
	|-> atopa/
	     |-> alumnos/
	     |-> cuestionarios/
	     |-> locale/
	     |-> logs/
	     | manage.py
	     |-> mysite/
	     |-> resultados/
	     |-> static/
	     |-> teacher/
	     |-> templates/
	| atopaapp
	| docker-compose.yml
	| Dockerfile
	| ejecutar_atopa_app.sh
	| entrypoint
	| instalador_atopa_app.sh
	| LICENSE
	|-> logs 
	| Makefile
	| mysqldumps
	| README.md
	| requirements.txt
	
El directorio atopa_app incluye todo el entorno que utiliza la aplicación, incluyendo los logs y la propia aplicación.

En la carpeta de logs se irán mostrando todos los mensajes de la aplicación, solo se generan mensajes para debug de la app.

Y la carpeta atopa_app/ es la raíz de nuestra aplicación.
Dentro de ella podemos encontrar en cada carpeta cada una de las apps que forman la app principal. Se ha dividido en 4 apps: teacher, alumnos, cuestionarios y resultados. La app mysite es donde se encuentran configuraciones generales de la app.

## Pasos de instalación

## Instalación en Linux o MAC OS
1. Es necesario instarlar docker y docker-compose
2. Es necesario instalar openssl
3. Descargar y ejecutar el archivo instalador_atopa_app.sh. 
```	
	./instalador_atopa_app.sh <clave_base_datos> <ip_servidor> <puerto_servidor> <ip_local>
```

Versiones usadas: 
```
Django==3.1.12
requests==2.23.0
MySQL-python==1.2.5
django-bootstrap4==1.1.1
django-mysql==3.5.0
django-octicons==1.0.2
django-crispy-forms==1.9.1
django_bootstrap_breadcrumbs==0.9.2
reportlab==3.5.42
django-widget-tweaks==1.4.8
gunicorn==20.0.4
```

## Instalación en Windows

1. Es necesario instalar Docker Desktop
2. Es necesario instalar openssl
3. Descargar y ejecutar el archivo instalador_atopa_app_windows.bat
4. Si es necesario, edita la línea en la que se hace la llamada a openssl.exe, para que la ruta sea la correcta en tu equipo
```
	./instalador_atopa_app.sh <clave_base_datos> <ip_servidor> <puerto_servidor> <ip_local>
```

Versiones usadas: 
```
Django==3.1.12
requests==2.23.0
MySQL-python==1.2.5
django-bootstrap4==1.1.1
django-mysql==3.5.0
django-octicons==1.0.2
django-crispy-forms==1.9.1
django_bootstrap_breadcrumbs==0.9.2
reportlab==3.5.42
django-widget-tweaks==1.4.8
gunicorn==20.0.4
```

## Ejecución de la aplicación en Linux o Mac OS:
```
cd atopa_app
./ejecutar_atopa_app.sh <ip_local> 
```

## Ejecución de la aplicación en Windows:
```
Descargar y ejecutar el archivo ejecutar_atopa_app_windows.bat. 
```

## Desarrolladores

Jose Portela Magdaleno

Andrea Carballo Torres

Cristina López Bravo

Francisco de Arriba Pérez
