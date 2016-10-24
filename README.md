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

1. [Download](https://www.vagrantup.com/downloads.html) Vagrant
2. [Install](https://www.vagrantup.com/docs/getting-started/) Vagrant
3. Make sure you are in the SilverScreen directory
4. Exectue the following commands:
```shell
$ vagrant up
$ vagrant ssh
```
5. Your shell should now say
```shell
vagrant@precise64:/vagrant$
```
Execute the following command:
```shell
$ bash vagrant_setup.sh
```
Chill out and wait for the script to do its thing.
6. Now:
```shell
$ cd /etc/postgresql/9.1/main/
$ vim pg_hba.conf
```
Copy the following to the bottom of pg_hba.conf
```shell
export PATH="/home/vagrant/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
Save and exit with ```esc``` then ``` : ``` then ```wq``` then ```enter```
7. Run the second setup script
```shell
$ bash setup.sh
```
8. Then execute the following commands:
```shell
$ sudo su postgres
$ createuser vagrant
# answer "y" when it asks "Shall the new role be a superuser? (y/n)"
$ createdb -h localhost -p 5432 silverscreen
$ exit
$ python manage.py startserver 0.0.0:8080
```
