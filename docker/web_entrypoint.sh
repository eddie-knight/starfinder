#!/bin/sh
dockerize -timeout 60s -wait tcp://database:3306 flask run -h 0.0.0.0 -p5000 --reload
