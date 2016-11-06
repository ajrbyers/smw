#!/bin/bash

set -e # everything must pass

pyflakes src/  # fast check of code for basic issues
#pylint src/   # slower check of code
