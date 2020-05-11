[![Build Status](https://travis-ci.com/danila19991/OpenFoam-web-ui.svg?branch=master)](https://travis-ci.com/danila19991/OpenFoam-web-ui)
[![codecov](https://codecov.io/gh/danila19991/OpenFoam-web-ui/branch/master/graph/badge.svg)](https://codecov.io/gh/danila19991/OpenFoam-web-ui)
# Remote experimenter
Project for Grid & Cloud course on the Faculty of Applied Mathematics and Control Processes of Saint Petersburg University 2020

# How to deploy
For install python dependencies `pip install -r requirements.txt`  
Server need to be prepared with installed [docker](https://docs.docker.com/get-docker/) and [OpenFoam](https://openfoam.org/download/)

To start system:
 - `python prestart.py`
 - `python start_main.py`(interactive terminal)
 - `python start_worker.py`(interactive terminal)
 
To stop system:
 - stop interactive terminals
 - `python clean_main.py`