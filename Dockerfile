from ubuntu:18.04

RUN mkdir /logs
RUN mkdir /atopa
WORKDIR /atopa
RUN mkdir logs

RUN touch /logs/debug.log

ADD . /atopa
EXPOSE 80
EXPOSE 443
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y &&\
    apt-get install -y python3-dev &&\
    apt-get install -y python3-pip &&\
    apt-get install -y libmysqlclient-dev libpq-dev nginx &&\
    apt-get install -y mysql-client --no-install-recommends &&\
    apt-get install -y libssl-dev  &&\
    apt-get install -y gettext &&\
    apt-get clean
RUN pip3 install --upgrade setuptools &&\
    pip3 install mysqlclient
RUN pip3 install -r requirements.txt
RUN chown -R www-data:www-data /atopa/atopa
RUN cp atopa.pem /etc/ssl/
RUN cp atopa_key.pem /etc/ssl/
RUN cp atopaapp /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/atopaapp /etc/nginx/sites-enabled
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.4.0/wait /wait
RUN chmod +x /wait
RUN chmod 750 ./entrypoint

ENTRYPOINT ./entrypoint
