#!/bin/bash
# does a complete lint+test+scrub of the code
# this is best done before a commit.

# try just using './.test.sh' for fasting testing 

source install.sh # activate the venv
#source .lint.sh  # run the linter. picks up any basic errors or code smells
source .test.sh   # run the unit tests. not run if lint fails
source .scrub.sh  # run the autopep8 tool to fix minor lint issues. not run if tests fail.
