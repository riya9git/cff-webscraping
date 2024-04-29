#!/bin/bash

set -e

rm -rf export/
mkdir export
touch export/.gitkeep
source activate cff
python src/main.py
