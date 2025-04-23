#!/bin/bash

set -e

rm -rf export/
mkdir export
touch export/.gitkeep
source activate webscraping
python src/main.py
