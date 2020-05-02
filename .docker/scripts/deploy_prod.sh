#!/bin/sh
docker container stop slack-bot_mongo-db-dev
docker container stop reddit-scraper-dev
docker container stop slack-bot-dev
docker-compose -f /drone/src/docker-compose.yml up -f /drone/src/docker-compose.prod.yml up --detach --build
