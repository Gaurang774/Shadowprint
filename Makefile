# Shadowprint — Developer Makefile
# Owner: Jasjyot Singh [J] & Gaurang Udgirkar [G]

.PHONY: help install preflight test clean

PYTHON ?= python

help:
	@echo "Shadowprint Development Commands:"
	@echo "  make install    - Install pinned dependencies"
	@echo "  make preflight  - Run environment sanity checks (Docker, Ollama, Python)"
	@echo "  make test       - Run test suite"
	@echo "  make clean      - Clean cache and temporary files"

install:
	$(PYTHON) -m pip install -r requirements.txt

preflight:
	$(PYTHON) scripts/preflight_check.py

test:
	$(PYTHON) -m pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache/
