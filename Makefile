.PHONY: install test lint typecheck index replay eval serve security web clean help

PYTHON ?= python

install:
	$(PYTHON) -m pip install -e .[dev]

test:
	$(PYTHON) -m pytest -v --cov=kairos --cov-report=term-missing tests/

lint:
	$(PYTHON) -m ruff check kairos/ tests/

typecheck:
	$(PYTHON) -m mypy --strict kairos/

index:
	$(PYTHON) -m kairos.cli index --corpus data/corpus

replay:
	$(PYTHON) -m kairos.cli replay --split $(or $(SPLIT),dev)

eval:
	$(PYTHON) -m eval.run_suite

serve:
	$(PYTHON) -m uvicorn kairos.api.app:app --host 0.0.0.0 --port 8000 --reload

security:
	$(PYTHON) -m bandit -r kairos/ -c .bandit.yml || true

web:
	@echo "Building frontend placeholder in web/..."
	@mkdir -p web/dist kairos/api/static
	@echo "<h1>Kairos UI Placeholder</h1>" > kairos/api/static/index.html

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov runs/ index/
