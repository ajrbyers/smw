#!/bin/bash
set -e # everything must succeed.
print 'install'

# if virtual environment called 'venv' doesn't exist, create it
if [ ! -d venv ]; then
    virtualenv --python=`which python2` venv
fi

# activate it
source venv/bin/activate

print 'activated'

if [ ! -z src/core/settings.py ]; then
    cd src/core/
    ln -sf dev_settings.py settings.py
    cd -
fi
print 'settings done'

# install any requirements
pip install -r requirements.txt

source .configure.sh
