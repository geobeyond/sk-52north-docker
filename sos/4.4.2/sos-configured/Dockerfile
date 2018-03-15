FROM geobeyond/sos:4.4.2
MAINTAINER Francesco Bartoli <francesco.bartoli@geobeyond.it>

# Project: https://github.com/52North/sos

RUN apt-get -y install netcat \
    && apt-get clean

COPY sos-config/configuration.db $CATALINA_HOME/webapps/observations/
COPY sos-config/datasource.properties $CATALINA_HOME/webapps/observations/WEB-INF
COPY tomcat-bin/setenv.sh $CATALINA_HOME/bin
COPY tomcat-bin/index.html $CATALINA_HOME/webapps/ROOT
#COPY tomcat-bin/observations.xml $CATALINA_HOME/conf/Catalina/localhost

# install python and pip
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y python python-pip python-dev \
    && apt-get install -y postgresql-client

COPY sos-config/requirements.txt /tmp
COPY sos-config/entrypoint.sh /tmp
COPY sos-config/tasks.py /tmp

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && chmod +x $CATALINA_HOME/bin/*.sh \
    && chmod +x /tmp/entrypoint.sh \
    && chmod +x /tmp/tasks.py

CMD ["/tmp/entrypoint.sh"]
