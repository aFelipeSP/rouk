# rouk
Control the music in your raspberry pi, from any browser in the intranet.

## What you need
1. A raspberry pi with omxplayer installed.

## Installation
1. Install [Neo4j](https://neo4j.com/docs/operations-manual/current/installation/linux/debian/) and make sure it is running everytime you run the program.
1. Download or clone this project. From now on the path where you placed the project will be $ROUK_HOME.
1. `cd rouk`
1. (Optional) Create a python environment for this app: `python -m venv venv` and activate it: `source ./venv/bin/activate`, or use conda/pyenv.
1. Install python requirements:
    ```
    pip install -r requirements.txt
    ```
1. `mkdir instance`
1. `cd instance`
1. `touch config.py`
1. Edit this file, adding the following config variables.

    * NEO4J_USER (user of the Neo4j database)
    * NEO4J_PASSWORD (password of the Neo4j database)
    * MUSIC_ROOT (path of the folder containing your music)

    An example of this file would be:
    ```
    NEO4J_USER = 'neo4j'
    NEO4J_PASSWORD = 'password'
    MUSIC_ROOT = '/home/pi/Music'
    ```
1. `cd ..`
1. Set flask current app: `export FLASK_APP=rouk`
1. Create the music database for the app.
    ```
    flask update-library
    ```
    Run this command everytime you want to update your music library.
1. (Optional) Create systemd service to run *rouk* as a service:
    1. `sudo cp rouk.service /etc/systemd/system/rouk.service`
    1. Edit **ExecStart** at `/etc/systemd/system/rouk.service` to use python version you want and to point to rouk.py file inside $ROUK_HOME.
    1. `sudo chmod 644 /etc/systemd/system/rouk.service`
    1. `sudo systemctl enable myservice`
    1. Reebot.
1. If you didn't make the last step, you can manually start the process:
    ```
    python ./rouk.py
    ```
1. Open a browser in any computer connected to the same browser as your raspberry pi and go to the following address:
    ```
    http://HOST_OF_YOUR_RASPBERRY_PI:14281
    ```
    * If you need the hostname of yous raspberry pi, open a terminal and run `hostname -I`.
1. Enjoy.
