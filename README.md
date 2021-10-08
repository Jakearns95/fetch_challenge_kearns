# Jake Kearns Fetch Coding Challnege
## Overview


## Installation
Once you have cloned this repo, navigate inside the folder and start the virutal enviroment with the following command:
```bash
source venv/bin/active
```
This virtual enviroment already has all the packages install to run the web server. Once the virtual enviroment is running, we will need to install/migrate the changes make inside django. To do this, navivigate inside the folder labeld `fetch-challenge-kearns` and run the following command:

```bash
python manage.py makemigrations
python manage.py migrate
```

These commands will make sure you have everything install and loaded in correctly before we start the server with the following command:

```bash
python manage.py runserver
```

This command will bootup Django and run a local server that allows API requests. If everything is working correctly, you should see something like this:
```bash
(venv) jkearns@jakes-air fetch_coding_challenge % python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
October 08, 2021 - 17:08:49
Django version 3.2.8, using settings 'fetch_coding_challenge.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
[08/Oct/2021 17:08:59] "POST /transactions/use HTTP/1.1" 200 62
```
Take note of the location of the server since this will be the base for your future requests. Above it shows my server to be running here: `http://127.0.0.1:8000/`. If your server is not the same, adjust your request to reflect your local server.

## Endpoints
Now that your local server is up and running, you have access to the following endpoints:

```python
from django.urls import path

from . import views

urlpatterns = [
    path('view_all', views.view_all, name='view_all'),
    path('add', views.add, name='add'),
    path('use', views.use, name='use'),
    path('delete', views.delete, name='delete'),
]
```
`view_all`: is a GET request that will display all transactions in the sql database (if there is any)

`add`: takes a single line POST request, verifys the data and enters it into the database. If the request is negative, it is treated as an adjustment and will be applied to the older payer transaction. If there is not a payer with enough points, it will throw an error.

`use`: takes a single line POST request to redeem points. It will redeem points starting with the oldest transaction. The endpoint will return the number of points used from each payer.

`delete`: is an endpoint that will delete/clear all endpoints in the database.

## Testing/Examples

To get started, lets make sure the database in empty by making the following request:
```bash
curl http://127.0.0.1:8000/transactions/delete
```
As mentioned above, this will wipe all transactions in the database. Run the following commands to re-populate the database with transactions using the `add` enpoint:
```bash
curl -X POST http://127.0.0.1:8000/transactions/add -H 'Content-Type: application/json' -d '{"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" }'
curl -X POST http://127.0.0.1:8000/transactions/add -H 'Content-Type: application/json' -d '{"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" }'
curl -X POST http://127.0.0.1:8000/transactions/add -H 'Content-Type: application/json' -d '{"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z"}'
curl -X POST http://127.0.0.1:8000/transactions/add -H 'Content-Type: application/json' -d '{"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }'
curl -X POST http://127.0.0.1:8000/transactions/add -H 'Content-Type: application/json' -d '{"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" }'
```

By running hitting the `view_all` endpoint, you can see that all transactions have been entered. Any negitive transactions has been applied to the oldest transaction for that payer:
```bash
curl http://127.0.0.1:8000/transactions/view_all
```
```bash
jkearns@jakes-air ~ % curl http://127.0.0.1:8000/transactions/view_all
"{\"DANNON\":1100,\"MILLER COORS\":10000,\"UNILEVER\":200}"%
jkearns@jakes-air ~ %
```
The final endpoint we can run is the `use` endpoint. This will redeem the number of points specified by the request (if there is enough points) and return a usage report broken down by payer:
```bash
curl -X POST http://127.0.0.1:8000/transactions/use -H 'Content-Type: application/json' -d '{"points": 5000}'
```


## Shortcomings/Needs improvement
- serializer error handling
- serializer updates
- negative post request
- tracking

## Conclusions
