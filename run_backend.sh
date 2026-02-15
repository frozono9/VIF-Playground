#!/bin/bash
# Run from project root
export PYTHONPATH=$PYTHONPATH:$(pwd)
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
