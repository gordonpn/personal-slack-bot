#!/usr/bin/env bash
set -euo pipefail
docker container stop slack-bot_mongo-db-dev || true
docker container stop reddit-scraper-dev || true
docker container stop slack-bot-dev || true
docker-compose -f /drone/src/docker-compose.yml -f /drone/src/docker-compose.prod.yml up --detach --build
