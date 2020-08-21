#!/bin/sh
# Activate python environment
export PYENV_VERSION=rouk
# conda activate rouk
export FLASK_APP=$ROUK_HOME/rouk
fuser -k 9999/tcp
flask player &
flask run -h 0.0.0.0 -p 14281