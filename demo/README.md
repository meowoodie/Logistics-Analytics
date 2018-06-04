Recommendation System for SF clients relationship
===

### Introduction

A recommendation system demo for SF clients (companies) based on potential business connection. This project is a web based service built on a Python microframework `Flask`, which connects to our core recommendation algorithm.

### Architecture

Below is an illustration for the project architecture.

![service folder structure]()

Basically, the entire project includes three key components:

- **Algorithm Module**: A Python package for providing computation results according to the algorithm.

- **Database Service**: A conventional database service that access to the data of SF logistic transactions and customer profiling information.
- **Web Service** (Backend API Provider): A `Flask` project providing a simple web container which is able to retrieve data from database service, get results from algorithm module and rendering visualization results to the frontend.
- **Frontend**: Webpage, Mobile Application (IOS/Android/...) and so on.

For now, the database service is a simple MySQL database with a `Loopback` database wrapper that provides high-level data model API. And frontend is a simple html template that provides interactive Map visualization (Google Map), statistical graphs and so on. Both of these two services are highly replaceable.

### Deployment

##### Install Python denpendencies

To install required Python dependencies, run following commands:
```
python -r requirements.txt
```

##### Start MySQL database service

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

##### System boot
To boot the system, run the following commands in order to start `Flask` service:

```
FLASK_APP=view.py
python -m flask run
```

Finally, open the url (here is http://your_ip_address:5000/ ) in the browser to visit the webpage.

### Components

##### Database Wrapper

Database wrapper was an abstract interface for connecting various kinds of database via standard restful API and the data models that web service needs. Generally speaking, the data models that you implement in web service inherit from interface 'DBConnecter' for getting access to the database.

We have three classes in this Python script, and their relations are shown as below:

![DAO_UML](https://github.com/meowoodie/Crime-Pattern-Detection-for-APD/blob/Suyi/service/static/readme_img/DAO_UML.png)

*<p align="center">UML of dao.py</p>*

The data streams that we received from database wrapper have uniform data structures for easier data information extraction.
Usually items of the data stream from database wrapper can be defined as follows:
```
{
  "id":       incident_num,
  "avg_lat":  avg_lat,
  "avg_long": avg_long,
  "city":     city,
  "date":   date,
  "priority": priority,
  "category": category,
  "incident_date_timestamp": incident_date_timestamp
}
```
```
{
  "id":          incident_num,
  "update_date": update_date,
  "remarks":     remarks\
}
```

#### Flask project

View.py is the main script for a Flask project, which defines various of interfaces for getting access to backend services or data. The view component would extract the information of the payload. Then the extracted data might be processed by the data model. Finally, the result which consists of "statue" and "res" will be sent to front end HTML page. Below is the illustration:
```
{
  "status": 0,
  "res": [{
    "id": filter_ids[ind],
    "similarity": float(sims[ind]),
    "label": categories[ind],
    "position": { "lat": positions[ind][0], "lng": -1 * positions[ind][1] },
    "city": cities[ind],
    "priority": priorities[ind],
    "update_dates": update_dates[ind],
    "date": dates[ind],
    "text": remarks[ind] }]
}
```
#### Front End

The front end web page provides several visualization functions to demonstrate the results of incident correlation detection.

##### Demonstrate incidents on the map
<br>Each dot represents a crime incident with real location.</br>
<div align=center><img src="https://github.com/meowoodie/Crime-Pattern-Detection-for-APD/blob/Suyi/service/static/readme_img/dots_on_map.gif"/></div>

*<p align="center">Demonstrate incidents on the map.</p>*

#### Represent similarities using dot size
Larger dots mean incidents with higher similarities.
<div align=center><img src="https://github.com/meowoodie/Crime-Pattern-Detection-for-APD/blob/Suyi/service/static/readme_img/biggerdots.jpg"/></div>

*<p align="center">Represent similarities using dot size.</p>*

#### Represent similarities using lines
Darker lines mean higher similarties between incidents.
<div align=center><img src="https://github.com/meowoodie/Crime-Pattern-Detection-for-APD/blob/Suyi/service/static/readme_img/lines.gif"/></div>

*<p align="center">Represent similarities using lines.</p>*
