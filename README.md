# Silver Screen [![Build Status](https://travis-ci.org/bfbachmann/Silver-Screen.svg?branch=master)](https://travis-ci.org/bfbachmann/Silver-Screen)
## Twitter sentiment mining and analysis application

CPEN 321 Project Sept 2016 - Dec 2016

The live version of Silver Screen can be found [here](https://silverscrn.herokuapp.com/).

_Note:_ The live version of the site represents the current state of the code in ```master```, not ```dev```.

See ```docs``` directory and check out our Github Wiki for design documentation.

See ```dev``` branch for latest code.

## Documentation Links
Design Document: [here](https://docs.google.com/document/d/1dcyPxOl4ow4xKoFgt6TrqmlBqRJRLbmeUN1lyH9fY58/edit#)

Project Plan/Backlog: [here](https://docs.google.com/spreadsheets/d/1o6x0yL5FPlVRYyGUr6k0v0zUYX_COgLFxeTlp4fbnfA/edit#gid=0)

Requirements: [here](https://docs.google.com/document/d/1CNddmEScitOrEP2MNHRjLysgsNNTds0RgeEN0csd7kU/edit)

Testing & Validation Document: [here](https://docs.google.com/document/d/1KTpPY8q_gpljrQ3FbQaI5MdFmHCtp00v8KOeBLbci-Q/edit?usp=sharing)

[Python-twitter documentation](https://github.com/bear/python-twitter)

[OMDb documentation](https://github.com/dgilland/omdb.py)

[Chart.js documentation](http://www.chartjs.org/docs/#bubble-chart-introduction)

## Repository Structure

### Master vs Dev Distinction

It is important to note that the code present on the ```master``` branch has been configured to be deployed on Heroku, not on a local development platform (there are distinct differences between database initialization which must be reflected in the settings files). The installation instructions provided below are for a local installation, and should be performed on the code from the ```dev``` branch.

### Sentiment Analysis

All source code responsible for tweet sentiment analysis can be found in the `sentimentanalysis` directory. The class `TweetSenitment` in `analyzer.py` is the wrapper for all sentiment analysis functionality. See `sentimentanalysis/lexicon_done.txt` for the full seniment analysis lexicon.

### SilverScreen Configuration

Configuration files like `settings.py` can be found in the `SilverScreen` directory. Note that the application's routing is managed by `urls.py` in the `SilverScreen` directory. This routing makes use of the lower-level routing specified in `app/urls.py`.

### Models

All data and API wrappers can be found in `app/models`.

### Views and Templates

The application's major control flows (responses to requests) are handled in `app/views/views.py`. HTML templates rendered in responses are stored in `app/templates`.

### Tests

Tests can be found in `app/tests`.

Once you have you environment set up you can run tests manually with
```python
$ python manage.py test app.tests
```
from the project directory in Vagrant.

## Repository Structure

### Sentiment Analysis

All source code responsible for tweet sentiment analysis can be found in the `sentimentanalysis` directory. The class `TweetSenitment` in `analyzer.py` is the wrapper for all sentiment analysis functionality. See `sentimentanalysis/lexicon_done.txt` for the full seniment analysis lexicon.

### SilverScreen Configuration

Configuration files like `settings.py` can be found in the `SilverScreen` directory. Note that the application's routing is managed by `urls.py` in the `SilverScreen` directory. This routing makes use of the lower-level routing specified in `app/urls.py`.

### Models

All data and API wrappers can be found in `app/models.py`.

### Views and Templates

The application's major control flows (responses to requests) are handled in `app/views.py`. HTML templates rendered in responses are stored in `app/templates`.

### Tests

Tests can be found in `app/tests.py`.

Once you have you environment set up you can run tests manually with
```python
$ python manage.py test
```
from the project directory in Vagrant.

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

8. Now lets setup Postgres

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

9. Silver Screen requires API access from Twitter to operate. Twitter API keys are free and can be acquired [here](https://apps.twitter.com/).

    Once you have acquired your keys, create a file named ```api_keys.yml``` in the ```scripts/twitter_api/``` folder. Format the file as follows:

    ```
    consumer_key: <<YOUR CONSUMER_KEY>>
    consumer_secret: <<YOUR CONSUMER_SECRET>>

    access_token_key: <<YOUR ACCESS_TOKEN_KEY>>
    access_token_secret: <<YOUR ACCESS_TOKEN_SECRET>>
    ```

    replacing the values in angle brackets with the keys you acquired from Twitter.

10. WE'RE DONE!! You should now be able to run the server with
    ```shell
    $ cd /vagrant
    $ sudo pip install -r requirements.txt # if you don't already have the requirements installed
    $ python manage.py migrate
    $ python manage.py runserver
    ```

    ......wasn't that easy?

### Note about Heroku Deployments

As previously mentioned, the above installation instructions are designed for local installations only. To install Silver Screen on Heroku, follow the directions on the [Heroku dashboard](https://dashboard.heroku.com/apps). Rather than supplying API keys through the ```api_keys.yml``` file, set the keys under the ```Config Variables``` heading in the ```Settings``` tab.
