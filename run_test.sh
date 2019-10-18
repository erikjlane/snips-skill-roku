#!/bin/sh

mosquitto -p 1234 &
. venv/bin/activate
pytest tests/test_*.py
killall mosquitto
