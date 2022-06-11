# "To the point" documentation

### Usage:

After cloning use docker-compose up, it will create a postgres backend, and a volume as well as
the fastapi application itself.

It will run on 0.0.0.0:8000, so you should be able to reach it from your host computer.

The necessary tables should be created automatically on first run, but if there is a problem,
you can run create_initial_database.py manually.

See OpenAPI at the default /docs route.

For the sake of the demo most of the functionality doesn't need any authentication.
If you'd like to try JWT authentication though you can create a user first, and then authenticate with OpenAPI's
Authorize button in the top right corner and log in.


### Demo site:

There is a demo available on heroku:
https://thundervarg.herokuapp.com/

(Don't judge, it has to be called something...)

Feel free to play around with it.

### 