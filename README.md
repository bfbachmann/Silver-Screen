# Silver Screen
## Twitter sentiment mining and analysis application

CPEN 321 Project Sept 2016 - Nov 2016

See https://github.com/bear/python-twitter for python-twitter documentation.

## Documentation Links
Design Document: [here](https://docs.google.com/document/d/1dcyPxOl4ow4xKoFgt6TrqmlBqRJRLbmeUN1lyH9fY58/edit#)

Project Plan/Backlog: [here](https://docs.google.com/spreadsheets/d/1o6x0yL5FPlVRYyGUr6k0v0zUYX_COgLFxeTlp4fbnfA/edit#gid=0)

Requirements: [here](https://docs.google.com/document/d/1CNddmEScitOrEP2MNHRjLysgsNNTds0RgeEN0csd7kU/edit)

### Setting up the database
Make sure you have Postgres installed
```shell
which postgres
```
Create the database
```shell
bash createdb.sh
```

### Installing Python dependencies
```shell
pip3 install requirements.txt
```

### Running the server
```shell
python manage.py runserver
```
