#!/bin/bash
set -e

/usr/local/bin/invoke update >> /usr/src/app/invoke.log

source $HOME/.bashrc
source $HOME/.override_env

/usr/local/bin/invoke updatedb >> /usr/src/app/invoke.log

echo "updatedb task done"

# start tomcat
exec catalina.sh run
