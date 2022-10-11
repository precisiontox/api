# PSQL2GRAPHQL

A python graphQL API that reads its data dynamically from a PostgreSQL <= 9.2 database.

## USAGE

Create an environment using venv or conda
```shell
python3 -m venv venv
source venv/bin/activate
sudo apt-get install libpq-dev python-dev
sudo apt install build-essential
pip install -r requirement.txt
mv .env.example .env
```

```shell
conda env create -f environment.yml
mv .env.example .env
```

Then open .env and fill in the values with your credentials and connection.

```
USER=username
USER_PWD=password
HOST=https://example.com
DATABASE_NAME=database_name
```
Finally:

```shell  
flask run
```

The app is served on port 5000.

## Running in Passenger

Install and validate Passenger using commands below (works on Ubuntu 18.04 and 20.04)

```shell
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 561F9B9CAC40B2F7
sudo apt-get install -y apt-transport-https ca-certificates

sudo sh -c 'echo deb https://oss-binaries.phusionpassenger.com/apt/passenger bionic main > /etc/apt/sources.list.d/passenger.list'
sudo apt-get update
sudo apt-get install -y passenger
passenger-config validate-install
``` 

Run the API using `sudo passenger start`

If you want you can stop the API using `sudo passenger stop`

The app is served on port 5000.
