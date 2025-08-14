#!/bin/bash
set -e

python ./main.py db drop

python ./main.py db init

python ./main.py db add

exec python ./main.py serve
