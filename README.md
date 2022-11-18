# Flask Google Schedule Project

A web app that facilitates the creation of appointment between an administrator and their clients.

## Install:

1. `poetry install`

## Running the app:

2. `python .\main.py`

## About the project

This is a flask project that allows for an administrator to connect their google calendar to the application to facilitate appointments with clients or patients. It uses the google calendar API in order to retrieve freebusy times from the admin's calendar and create events in their calendar.

Clients can allow the app to see their freebusy times. The app will retrieve both the admin's and the client's freebusy times. With this information, the client can create a consultation at a time that is free for both parties by creating an event in the admin's calendar. To do so, they must provide their own email, the date and time of the consultation, and the duration of the consultation. Only logged in clients are able to retrieve the freebusy times and to create an appointment.

This app follows the OAuth 2.0 protocol to get authorization from Google API to access the admin's and the clients' relevant information.

## Generate authorize app url

### Request

`curl -X GET "/google/authorization" -H "accept: application/json" -H "admin: key"`

### Response

```
HTTP/1.1 200
Status: 200
access-control-allow-origin: placeholder
connection: close
content-length: 424
content-type: application/json
date: Fri, 18 Nov 2022 18:27:05 GMT
server: Werkzeug/2.2.2 Python/3.10.6
vary: Cookie

{
  "message": "Generated authorization URL",
  "url": "https://accounts.google.com/o/oauth2/auth?response_type=url_to_authorize"
}
```

## Get freebusy times

### Request

`curl -X GET "/google/consultation?date=18-11-2022" -H "accept: application/json"`
_Note_: Do not fill "date" in order to get all freebusy times for the next 30 days.

### Response

```
HTTP/1.1 200
Status: 200
access-control-allow-origin: placeholder
connection: close
content-length: 288
content-type: application/json
date: Fri, 18 Nov 2022 18:39:29 GMT
server: Werkzeug/2.2.2 Python/3.10.6
vary: Cookie

{
  "owner": {
    "busyTimes": [],
    "message": "Success",
    "weekday": "Sexta"
  },
  "user": {
    "busyTimes": [
      {
        "end": "2022-11-18T10:00:00-03:00",
        "start": "2022-11-18T09:00:00-03:00"
      }
    ],
    "message": "Success",
    "weekday": "Sexta"
  }
}
```

## Create a consultation

### Request

`curl -X POST "/google/consultation?date=18-11-2022&time=20%3A00&length=01%3A30&email=email%40gmail.com" -H "accept: application/json"`

### Response

```
HTTP/1.1 200
Status: 200
connection: close
content-length: 68
content-type: application/json
date: Fri, 18 Nov 2022 18:44:29 GMT
server: Werkzeug/2.2.2 Python/3.10.6
vary: Cookie

{
  "busyTimes": [],
  "message": "Success",
  "weekday": "Sexta"
}
```
