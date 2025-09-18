# Makefile for decompose-vector

.PHONY: all install clean help

all: help

install: requirements.txt ## Install dependencies into the direnv virtual environment
	pip install -r requirements.txt

clean: ## Remove virtual environments
	rm -rf .direnv

help: ## Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
