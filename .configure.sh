#!/bin/bash

set -e # everything must past

### configuration that can be done every time install.sh is run

# ensure you're on the most recent migration
./src/manage.py migrate




### initial once-off configuration

if [ ! -f .configured.flag ]; then
    # loading fixtures will nuke existing 
    # data. we don't want to do that all the time
    fixture="./src/core/fixtures/"
    ./src/manage.py loaddata $fixture/settinggroups.json
    #./src/manage.py loaddata $fixture/settings.json # doesn't exist?
    ./src/manage.py loaddata $fixture/cc-licenses.json
    ./src/manage.py loaddata $fixture/role.json

    echo 
    echo 'To create an admin user with a (necessary) profile, run:'
    echo '    $ ./manage.sh create_admin'
    echo 
fi

### done with configuration, set flag

touch .configured.flag
