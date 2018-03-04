# Crime-Pattern-Detection Flask Project
![system_overview](https://github.com/meowoodie/Crime-Pattern-Detection-for-APD/blob/Suyi/service/static/readme_img/System_overview.jpeg)

*<p align="center">Interface of the project.</p>*

* [Introduction](#introduction)
* [Setup](#setup)
* [Usage](#launch)
* [Components](#components)
* [To Do](#to-do)
* [Contributing](#contributing)


## Introduction
The service folder in the Crime-Pattern-Detection project is a Flask project. It contains several files that build a system to fetch data from database and demonstrate the results of crime incident correlation detection. It contains database wrapper, date visualization, full text search and many other features to demonstrate the results of incident correlation detection. Below is an illustration for the structure of the service folder. 

![service folder structure](https://github.com/meowoodie/Crime-Pattern-Detection-for-APD/blob/Suyi/service/static/readme_img/service_folder_structure.png)

*<p align="center">An illustration for the structure of service folder.</p>*

The folder mainly contains three components:

- Database wrapper: it provides restful API to connect the MySQL database and parse the retrieved data to JSON format.
- Flask project: it provides functions to process the retrieved data from the database according to the user input.
- Front end webpage: it provides functions to render a web page, on which we can show the detection results. Also, we can receive user input from the webpage.

Currently, we provide two main search functions in our system:
- Search correlated crime by incident ID: User input an incident ID and a number N to get top N similar incidents
- Search correlated crime by keyword: User input a keyword and a number N to get N incidents whose reports contain the keyword.

## Setup

#### Preliminary
Make sure there are 4 files or folders in the Service folder, including:  ```dao.py```,```view.py```,```static```,```templates```.<br />  
> ```dao.py``` : This is a python file which works as a database wrappper. 

> ```view.py```: This is a python file which works as a view componnent. 

> ```static``` : This is a folder which contains Javascript programs and CSS files.

> ```templates```: This is a folder which contains the HTML file.

#### Install Python package
To install our Python package, you need to run the following commands(assuming that you are in root directory of the project now):
```
cd holmes
python setup.py install
```

#### Connect MySQL database
Make sure you have your MySQL Server Instance run. 
On Mac, you may need to run the following command:<br />
``` sudo /usr/local/mysql/support-files/mysql.server start```

## Launch

#### Run the database wrapper
To run the database wrapper, you need to run the following commands(assuming that you are in root directory of the project now):
```
cd loopback-database-wrapper/
node .
```

#### Run the system
To run the system, you need to run the following commands (assuming that you are in root directory of the project now):<br />
```FLASK_APP=service/view.py```<br />
```python -m flask run```<br />
Then please wait for the model to be loaded for a few minutes:
```
[2017-09-15T19:09:14.529101-04:00] Loading Crime Codes Dictionary & Labels ...
[2017-09-15T19:09:14.777038-04:00] Loading existed dictionary ...
[2017-09-15T19:09:14.819520-04:00] Dictionary: Dictionary(74945 unique tokens: [u'darryle', u'fawn', u'tajudeen', u'schlegel', u'nunnery']...)
[2017-09-15T19:09:14.819673-04:00] Loading existed corpus ...
[2017-09-15T19:09:14.856084-04:00] Corpus: MmCorpus(219402 documents, 74945 features, 17014638 non-zero entries)
[2017-09-15T19:09:14.856212-04:00] Init Tfidf model.
[2017-09-15T19:10:41.919867-04:00] Calculating similarities ...
```
Finally, you can see:
``` 
Serving Flask app "view"
Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
Copy the url(here is http://127.0.0.1:5000/ ) into browser address bar and open the system.

## Components

#### Database Wrapper

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
