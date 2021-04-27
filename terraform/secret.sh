#!/bin/bash
secret=$(docker-compose run app manage generate_secret_key)
echo -n "{\"secret\":\"${secret}\"}"
