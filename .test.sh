#!/bin/bash

set -e # everything must pass

# remove any old compiled python files
# these can trip up pylint/pyflakes
find src/ -name '*.pyc' -delete

# quick pass with pyflakes to make sure no dumb errors snuck through
# disabled until all those bugs are fixed (HEM HEM)
#pyflakes src/

# pass any arguments to the test runner
args="$@"
module="src"
print_coverage=1
if [ ! -z "$args" ]; then
    module="$args"
    print_coverage=0
fi

# keep the command simple as the settings.py is already complex
./src/manage.py test --nomigrations

#coverage run --source='src/' --omit='*/tests/*,*/migrations/*' src/manage.py test "$module" --nomigrations
echo "* passed tests"
