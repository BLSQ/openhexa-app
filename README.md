Habari
======

Habari is a Data Science Platform developed by BlueSquare.

The platform is based on the following technologies:

- Jupyter (https://jupyter.org/)
- JupyterHub (https://jupyter.org/hub)

Local setup
-----------

Habari provides a docker-based environment, useful for a local development environment.

To launch it, just build the image and up:

```bash
docker-compose build
docker-compose up
```

The platform will be available at http://localhost:8000/.

You will then need to:

1. Create a user account using the `habari` username and a password of your choice (
   the signup is available at http://localhost:8000/hub/signup)
2. Log in with this account (http://localhost:8000/hub/login)

This account will be the first admin account, that you can use in turn to create other users.