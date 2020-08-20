#!/bin/sh
export FLASK_APP=~/src/rouk
fuser -k 9999/tcp
flask player &
flask run