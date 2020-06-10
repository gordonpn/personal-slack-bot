#!/bin/sh
echo "$DOCKER_TOKEN"| docker login -u gordonpn --password-stdin
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
docker buildx rm builder || true
docker buildx create --name builder --driver docker-container --use
docker buildx inspect --bootstrap
cd /drone/src/slack_bot || exit 1
docker buildx build -t gordonpn/slack-bot:latest --platform linux/amd64,linux/arm64 --push .
cd /drone/src/reddit_scraper || exit 1
docker buildx build -t gordonpn/reddit-scraper:latest --platform linux/amd64,linux/arm64 --push .
