#!/usr/bin/env bash
set -euo pipefail
docker container stop slack-bot_mongo-db
docker container stop reddit-scraper
docker container stop slack-bot
docker-compose -f /drone/src/docker-compose.yml -f /drone/src/docker-compose.dev.yml up --detach --build
