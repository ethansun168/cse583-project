#!/bin/bash

set -e  # Stop on any error

echo "Running static analysis..."
cd analysis/Static/
bash run_all.sh

echo "Running dynamic analysis..."
cd ../dynamic/
bash run_all.sh

echo "Running memory access analysis..."
cd ../memory_access/
bash run_all.sh
python3 unique.py

echo "All analysis steps completed successfully."
