#!/bin/bash
# Build frontend
npm install
npm run build

# Start backend
gunicorn app:app --bind 0.0.0.0:$PORT