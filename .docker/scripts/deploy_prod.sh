#!/bin/sh
set -euo pipefail
docker container stop slack-bot_mongo-db-dev
docker container stop reddit-scraper-dev
docker container stop slack-bot-dev
docker-compose -f /drone/src/docker-compose.yml -f /drone/src/docker-compose.prod.yml up --detach --build
