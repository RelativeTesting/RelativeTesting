#!/bin/bash

# Homebrew default locations (both for python and z3)
export PYTHONMODS="/usr/local/lib/python3.11/site-packages:" 
export Z3HOME="/usr/local/Cellar/z3/4.12.1/lib/python3.11/site-packages/"
export Z3BIN="/usr/local/Cellar/z3/4.12.1/bin"


# Python setup
export PYTHONPATH=$PYTHONMODS:$Z3HOME

# Path setup
export PATH=$PATH:$Z3BIN


