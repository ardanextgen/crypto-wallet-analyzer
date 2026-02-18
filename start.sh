#!/bin/sh
# Railway Start Script - Expandiert $PORT korrekt
exec uvicorn src.api.server:app --host 0.0.0.0 --port $PORT
