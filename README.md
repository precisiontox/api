# PSQL2GRAPHQL

A python graphQL API that reads its data dynamically from a PostgreSQL <= 9.2 database.

## USAGE

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt
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