#!/bin/bash
set -e # everything must succeed.

# if virtual environment called 'venv' doesn't exist, create it
if [ ! -d venv ]; then
    virtualenv --python=`which python2` venv
fi

# activate it
source venv/bin/activate

# install any requirements
pip install -r requirements.txt

source .configure.sh
