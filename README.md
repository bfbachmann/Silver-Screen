# Silver Screen
## Twitter sentiment mining and analysis application

CPEN 321 Project Sept 2016 - Nov 2016

Please see Dev branch for most up-to-date code.
See docs directory for documentation.

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

4. Create a Vagrant virtual machine in the local directory:
    ```shell
    $ vagrant up
    ```
    Now ssh into the VM:
    ```shell
    $ vagrant ssh
    ```

5. Your shell should now say
    ```shell
    vagrant@precise64:~$
    ```
    Execute the following commands:
    ```shell
    $ cd /vagrant
    $ bash vagrant_setup.sh
    ```
    You will have to answer ```Y``` to a few ```Do you want to continue?``` prompts while utils are installed.

6. Once you have completed Step 5 you will need to add pyenv to your path. Open your bash profile in vim:
    ```shell
    $ vim ~/.profile
    ```
    Copy the following to the bottom of ~/.profile after pressing ```i``` to switch to insert mode. If this code is already in your profile you don't need to change anything.
    ```shell
    export PATH="/home/vagrant/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    ```
    Save and exit with ```esc``` then ``` : ``` then ```wq``` then ```enter```

7. Run the second setup script and answer ```Y``` when prompted.
    ```shell
    $ bash setup.sh
    ```
    This will take a while, it's installing a lot.

8. Now let set up Postgres.... WHEEOOOO!

    Switch to user postgres and create the SilverScreen database:
    ```shell
    $ sudo su - postgres
    $ createdb silverscreen
    ```
    Now create a user for our application
    ```shell
    $ createuser -P
    ```
    Make the username ```vagrant```, and when it asks for the password just hit ```enter```.
    Enter ```y``` when it asks if the user should have superuser privileges.

    Now open the postgres console:
    ```shell
    $ psql
    ```

    Grant all privileges to the new user on our database and exit the console:
    ```shell
    GRANT ALL PRIVILEGES ON DATABASE silverscreen TO vagrant;
    \q
    ```

    Now you need to switch back to user vagrant:
    ```shell
    $ exit
    ```

    Navigate to ```/etc/postgresql/9.1/main``` and own the config file as user vagrant:
    ```shell
    $ cd /etc/postgresql/9.1/main
    $ sudo chown vagrant pg_hba.conf
    ```

    Now we need to edit it. Open the config file in vim:
    ```shell
    $ vim pg_hba.conf
    ```

    Scroll to the bottom and edit the file so it looks like this:
    ```
    # Database administrative login by Unix domain socket
    local   all             postgres                                trust
    local   all             vagrant                                 trust
    # TYPE  DATABASE        USER            ADDRESS                 METHOD

    # "local" is for Unix domain socket connections only
    local   all             all                                     trust
    # IPv4 local connections:
    host    all             all             127.0.0.1/32            trust
    # IPv6 local connections:
    host    all             all             ::1/128                 trust
    ```

    Now restart postgres:
    ```shell
    $ sudo service postgresql restart
    ```

    WE'RE DONE!! You should now be able to run the server with
    ```shell
    $ cd /vagrant
    $ sudo pip install -r requirements.txt # if you don't already have the requirements installed
    $ python manage.py runserver
    ```

    ......wasn't that easy?
