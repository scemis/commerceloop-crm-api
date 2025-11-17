## First time run
 
1. Set environment variables values
- open or create .env file and make connection to your DB, by default there should be           
DATABASE_URL=mysql+pymysql://{username}:{password}@{servername}/{dbname}
- set onother values
SECRET_KEY={value}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

2. go to DB (MySql) and make Query            
>> DROP DATABASE `crm-db`
>> CREATE DATABASE `crm-db` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;

3. back into VCode in terminal write such commands after that install all what update 
all what you need with 			
>> pip install -r requirements.txt

4. Migrate latest data
set connection string in alembic.ini file

```
[alembic]
script_location = alembic
sqlalchemy.url = mysql+pymysql://{username}:{password}@{servername}/{dbname}
ex: mysql+pymysql://admin:password@mysql-server-crm.mysql.database.azure.com/demo-db
```
migrate to the latest version
>> alembic upgrade head  

## create localhost ssl certificate
>> openssl req -x509 -newkey rsa:4096 -keyout localhost-cert-key.pem -out localhost-cert.pem -sha256 -days 365 -nodes -subj "/CN=localhost" 

## run on localhost
>> uvicorn main:app --reload --port 8000 --ssl-keyfile localhost-cert-key.pem --ssl-certfile localhost-cert.pem

## quick test
https://127.0.0.1:8000/api/echo

### swagger:
https://127.0.0.1:8000/docs

# tracer
## import pdb; pdb.set_trace()

# freeze requirements
>> pip freeze > requirements.txt