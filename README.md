# Jake Kearns Fetch Coding Challnege
## Overview
This application was built with [Django](https://www.djangoproject.com/) a python web framework and is designed for a coding challenge to create, update, and redeem points for one user. The app is ran locally and takes HTTP requests to create, update or redeem points. All data will be stored on a locally hosted SQL server tied to Django.

Django was used for its ease of use and ability to rapidly develop a prototype locally. I was originally going to use AWS API gateway with a lambda function, but I wanted a user to be able to run this locally without setting up any infrastructure on AWS. 

Some challenge I faced, outlined in the `Shortcomings` section, was around the serializers I used to verify/update the data and throw errors. In future iterations of this project, I would work to resolve those shortcomings. 

## Installation
Once you have cloned this repo, navigate inside the folder and start the virtual environment with the following command:
```bash
source venv/bin/active
```
This virtual environment already has all the packages install to run the web server. Once the virtual environment is running, we will need to install/migrate the changes made inside Django. To do this, navigate inside the folder labeled `fetch-challenge-kearns` and run the following command:

```bash
python manage.py makemigrations
python manage.py migrate
```

These commands will make sure you have everything installed and loaded in correctly before we start the server with the following command:

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
Take note of the location of the server since this will be the base for your future requests. Above it shows my server to be running here: `http://127.0.0.1:8000/`. If your server is not the same, adjust your test requests to reflect your local server.

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

`add`: takes a single line POST request, verifies the data and enters it into the database. If the request is negative, it is treated as an adjustment and will be applied to previous payer transactions (starting with the oldest first). If there is not a payer with enough points, it will throw an error.

`use`: takes a single line POST request to redeem points. It will redeem points starting with the oldest transaction. The endpoint will return the number of points used from each payer.

`delete`: is an endpoint that will delete/clear all endpoints in the database.

## Testing/Examples

To get started, let's make sure the database is empty. Open your console and make a request using the `delete` endpoint:
```bash
curl http://127.0.0.1:8000/transactions/delete
```
As mentioned above, this will wipe all transactions in the database. Run the following commands to re-populate the database with transactions using the `add` endpoint:
```bash
curl -X POST http://127.0.0.1:8000/transactions/add -H 'Content-Type: application/json' -d '{"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" }'
curl -X POST http://127.0.0.1:8000/transactions/add -H 'Content-Type: application/json' -d '{"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" }'
curl -X POST http://127.0.0.1:8000/transactions/add -H 'Content-Type: application/json' -d '{"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z"}'
curl -X POST http://127.0.0.1:8000/transactions/add -H 'Content-Type: application/json' -d '{"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }'
curl -X POST http://127.0.0.1:8000/transactions/add -H 'Content-Type: application/json' -d '{"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" }'
```

By calling the `view_all` endpoint, you can see that all transactions have been entered. Any negative transactions will have been applied to the oldest transactions for that payer:
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
The output of that command will look something like this:
```bash
jkearns@jakes-air ~ % curl -X POST http://127.0.0.1:8000/transactions/use -H 'Content-Type: application/json' -d '{"points": 5000}'
"[{\"DANNON\":-100,\"MILLER COORS\":-4700,\"UNILEVER\":-200}]"%
```

## Shortcomings/Needs improvement
- Error Handling
    - The app has error handling but not to the extent that I would like it. The serializer classes have built in errors that, for the purpose of this challenge, I was unable to get to work correctly. In future iterations I would build in more error handling in custom serializer objects.

- Model updates
    - On a similar path as error handling, I ran into some issues with updating the model through the serializer class when redeeming points. I decided to circumvent the serializers and edit the models directly which could cause issues down the line since I am not verifying the data.

- Handling negative point requests
    - In the challenge, it was outlined that the server must be able to take in negative point POST requests to the `add` endpoint. I struggled with this because it seemed more like an adjustment than a transaction. When my app receives a negative point transaction, it will deduct it from the oldest payer with points and not record the transaction - causing a misrepresentation of past transactions.


## Credits
Below is a list of sites I used to help me with this challenge. Check them out, they were useful during this challenge:
- https://www.django-rest-framework.org/api-guide/serializers/
- https://www.django-rest-framework.org/

## License
[MIT](https://choosealicense.com/licenses/mit/)
