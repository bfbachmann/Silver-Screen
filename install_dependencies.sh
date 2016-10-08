#!/bin/bash

# run this script using > bash install_dependencies.sh
# this script will use pip to install all Python dependencies for the project

declare -a dependencies=("Django" "nltk" "numpy" "psycopg2" "python-twitter" "PyYAML")
response="$(pip list)"
install=""

for i in "${dependencies[@]}"
do
    if [[ "${response}" == *"$i"* ]]
    then
        echo "$i already installed";
    else
        install+="$i "
    fi
done

if [ "$install" != "" ]
then
    echo "Installing dependencies: $install"
    eval "pip install $install"
fi
