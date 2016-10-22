# Silver Screen
## Twitter sentiment mining and analysis application

CPEN 321 Project Sept 2016 - Nov 2016

## Documentation Links
[Python-twitter documentation](https://github.com/bear/python-twitter)

[OMDb documentation](https://github.com/dgilland/omdb.py)

[Chart.js documentation](http://www.chartjs.org/docs/#bubble-chart-introduction)

Design Document: [here](https://docs.google.com/document/d/1dcyPxOl4ow4xKoFgt6TrqmlBqRJRLbmeUN1lyH9fY58/edit#)

Project Plan/Backlog: [here](https://docs.google.com/spreadsheets/d/1o6x0yL5FPlVRYyGUr6k0v0zUYX_COgLFxeTlp4fbnfA/edit#gid=0)

Requirements: [here](https://docs.google.com/document/d/1CNddmEScitOrEP2MNHRjLysgsNNTds0RgeEN0csd7kU/edit)

## Setup
Make sure you have Postgres installed (bash)
```shell
$ which postgres
```
Make sure you have pip and pip3 installed (bash)
```shell
$ which pip3
$ which pip
```
Run setup script
```shell
$ bash setup.sh
```
Get Twitter API keys and place them in scripts/twitter_api/api_keys.yml

## Running the Server
You can run the server locally by doing:
```shell
$ python manage.py startserver
```
or
```shell
$ bash run.sh
```
Note: If you get the following error:
```shell
    Is the server running on host "localhost" (127.0.0.1) and accepting
	   TCP/IP connections on port 5432?
```
you need to restart your Postgres server with the following (bash) command:
```shell
$ pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
```
