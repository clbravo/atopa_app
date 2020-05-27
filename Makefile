build:
	bash -c "docker-compose build"
up:
	bash -c "docker-compose up -d"
down:
	bash -c "docker-compose down"
restart:
	bash -c "docker-compose restart"
status:
	bash -c "docker ps"
django-shell:
	bash -c "docker-compose exec web python /atopa/atopa/manage.py shell"
createsuperuser:
	bash -c "docker-compose exec web python /atopa/atopa/manage.py createsuperuser"
makemigrations:
	bash -c "docker-compose exec web python /atopa/atopa/manage.py makemigrations"
migrate:
	bash -c "docker-compose exec web python /atopa/atopa/manage.py migrate"
compilemessages:
	bash -c "docker-compose exec web python /atopa/atopa/manage.py compilemessages"
web-shell:
	bash -c "docker exec -it atopa /bin/bash"
db-shell:
	bash -c 'docker exec -it atopa_db mysql -h db -u root -p'
clean-migrations:
	bash -c "find . -path '*/migrations/*.pyc'  -delete && find . -path '*/migrations/*.py' -not -name '__init__.py' -delete && echo 'DONE!'"
