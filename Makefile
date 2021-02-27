.PHONY: daf test format clean download generate figure help

daf: ## download, arrange, and figure
	@make clean
	@make download
	@make arrange
	@make figure
	@make clean

test: ## test
	@make clean
	poetry run pytest
	@make clean

format: ## fix code format
	poetry run black .
	poetry run autoflake -r --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables .
	poetry run isort . --profile black
	poetry run mypy .

clean: ## clean data directory
	-@rm -f data/raw/*.zip
	-@rm -f data/raw/*.xls
	-@rm -f data/raw/*.xlsx
	-@rm -f data/interim/*.csv

download: ## download from BoJ
	poetry run python src/downloader.py

arrange: ## convert & aggregate xls or xlsx files
	poetry run python src/converter.py
	poetry run python src/aggregator.py

figure:  ## visualize the data
	poetry run python src/visualizer.py

help: ## this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
