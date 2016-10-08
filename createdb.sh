#!/bin/bash

# type "bash createdb.sh" to execute this script
# it create a Posgres database to connect the application to
eval "createdb -h localhost -p 5432 silverscreen"
