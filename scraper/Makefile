.DEFAULT_GOAL := help
.PHONY: help install

help: ## Show this help
		@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install requirements
	pip install -r requirements.txt

