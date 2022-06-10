#!/bin/bash
python ./app/create_initial_test_db.py
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload