#!/bin/bash

# type "bash setup.sh" to execute this script
echo "CREATING DATABASE (will not work without a Postgres installation)"
eval "createdb -h localhost -p 5432 silverscreen"

echo "STARTING DATABASE SERVER (will not work without Postgres installation)"
eval "pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start"

echo "INSTALLING REQUIREMENTS (will not work without pip3 installation)"
eval "pip3 install -r requirements.txt"

echo "INSTALLING Python 3.4.0"
eval "pyenv install 3.4.0"

echo "SETTING LOCAL PYTHON VERSION TO 3.4.0 (will not work without Python 3.4.0 installed)"
eval "pyenv local 3.4.0"
