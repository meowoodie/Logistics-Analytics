Recommendation System for SF clients relationship
===

### § Introduction

A recommendation system demo for SF clients (companies) based on potential business connection. This project is a web based service built on a Python microframework (Flask)[http://flask.pocoo.org/], which connects to our core recommendation algorithm.

### § Architecture

Below is an illustration for the project architecture.

![service folder structure]()

Basically, the entire project includes three key components:

- **Algorithm Module**: A Python package for providing computation results according to the algorithm.

- **Database Service**: A conventional database service that access to the data of SF logistic transactions and customer profiling information.
- **Web Service** (Backend API Provider): A `Flask` project providing a simple web container which is able to retrieve data from database service, get results from algorithm module and rendering visualization results to the frontend.
- **Frontend**: Webpage, Mobile Application (IOS/Android/...) and so on.

For now, the database service is a simple MySQL database with a (Loopback)[https://loopback.io/] database wrapper that provides high-level data model API. And frontend is a simple html template that provides interactive Map visualization (Google Map), statistical graphs and so on. Both of these two services are highly replaceable.

### § Deployment

##### ¶ Install Python denpendencies

To install required Python dependencies (including algorithm module), run following commands:
```
python -r requirements.txt
```

> TODO: modularization of our algorithm module (Python package)

##### ¶ Start MySQL database service

1. Start database
```
sudo /usr/local/mysql/support-files/mysql.server start
```
2. To run the database wrapper service, run the following commands:
```
cd loopback-database-wrapper/
node .
```
The wrapper is for providing user-friendly data access layer. In our application, there are three key data model, which are `company info`, `feature vector`, and `recommendation results` respectively.

Prior to running the wrapper, associated configurations are required, specifically including: `server/datasources.json`, `server/model-config.json` (for connecting indicated database) and `common\/models/*.js`, `common\/models/*.json` (for defining data models).

In order to connect a `MySQL` database, an example json file is going to be configured as follow:
```json
"sfexpress_ds": {
    "host": "localhost",
    "port": 3306,
    "url": "mysql://root:pwd@localhost/sfexpress",
    "database": "sfexpress",
    "password": "pwd",
    "name": "sfexpress_ds",
    "user": "root",
    "connector": "mysql"
}
```
And an example of data model configuration for `company info` is shown as below:
```json
{
  "name": "company_info",
  "base": "PersistedModel",
  "idInjection": true,
  "options": {
    "validateUpsert": true
  },
  "properties": {
    "company_id": {
      "type": "string",
      "id": true,
      "required": true
    },
    "lat": {
      "type": "float"
    },
    "lng": {
      "type": "float"
    },
    "main_business" : {
      "type": "string"
    },
    "is_oversea" : {
      "type": "string"
    },
    "industry_lv1": {"type": "string"},
    "industry_lv2": {"type": "string"},
    "industry_lv3": {"type": "string"},
    "area_code": {"type": "string"},
    "area_desc": {"type": "string"},
    "city": {"type": "string"},
    "coop_month" : {"type": "int"}
  },
  "validations": [],
  "relations": {},
  "acls": [],
  "methods": {}
}
```

##### ¶ System boot
To boot the system, run the following commands in order to start `Flask` service:

```
FLASK_APP=view.py
python -m flask run
```

In the end, open the url (here is http://your_ip_address:5000/) in the browser to visit the webpage.

#### Frontend

In our application, the frontend is presented in the form of a webpage, which requires some of third-party denpendencies, including (Google Map API)[https://cloud.google.com/maps-platform/] service, (Material Design CSS)[https://materializecss.com/], (Blue Bird)[http://bluebirdjs.com/docs/getting-started.html] (for asynchronous promise) (Chart JS)[http://www.chartjs.org/docs/latest/], (UnderscoreJS)[http://underscorejs.org/] (for basic data operation) and so on.
