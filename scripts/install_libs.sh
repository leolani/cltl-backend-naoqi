#!/bin/bash

pip install --user virtualenv

python -m virtualenv venv
source venv/bin/activate

ls -tr libs | grep -v virtualenv | {
  while read i;
  do pip install "libs/$i";
  done
}
