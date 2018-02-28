FROM geobeyond/sos:4.4.0
MAINTAINER Francesco Bartoli <francesco.bartoli@geobeyond.it>

# Project: https://github.com/52North/sos

RUN apt-get -y install netcat \
    && apt-get clean

COPY sos-config/configuration.db $CATALINA_HOME/webapps/observations/
COPY sos-config/datasource.properties $CATALINA_HOME/webapps/observations/WEB-INF
COPY tomcat-bin/* $CATALINA_HOME/bin

# install python and pip
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y python python-pip python-dev \

COPY sos-config/requirements.txt /tmp
COPY entrypoint.sh /tmp
COPY tasks.py /tmp

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && chmod +x $CATALINA_HOME/bin/*.sh \
    && chmod +x /tmp/entrypoint.sh \
    && chmod +x /tmp/tasks.py

CMD ["/tmp/entrypoint.sh"]
