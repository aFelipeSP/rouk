#!/bin/sh
export FLASK_APP=~/src/rouk
fuser -k 9999/tcp
flask player &
flask run -h 0.0.0.0 -p 14281