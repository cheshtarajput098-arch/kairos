.PHONY: install test lint typecheck index replay eval serve security web clean help

PYTHON ?= python

install:
	$(PYTHON) -m pip install -e .[dev]

test:
	COVERAGE_FILE=/tmp/.coverage $(PYTHON) -m pytest -o cache_dir=/tmp/.pytest_cache -v --cov=kairos --cov-report=term-missing tests/

lint:
	$(PYTHON) -m ruff check --cache-dir /tmp/.ruff_cache kairos/ tests/

typecheck:
	$(PYTHON) -m mypy --cache-dir /tmp/.mypy_cache --strict kairos/

index:
	$(PYTHON) -m kairos.cli index --corpus data/corpus

replay:
	$(PYTHON) -m kairos.cli replay --split $(or $(SPLIT),dev)

eval:
	$(PYTHON) -m eval.run_suite --split $(or $(SPLIT),dev) --out $(or $(OUT),runs/eval)

serve:
	$(PYTHON) -m uvicorn kairos.api.app:app --host 0.0.0.0 --port 8000 --reload

security:
	$(PYTHON) -m bandit -r kairos/ -c .bandit.yml
	$(PYTHON) -m pip_audit || true
	$(PYTHON) -m pytest tests/security/

redteam:
	$(PYTHON) -m eval.redteam

web:
	@echo "Syncing frontend dist to kairos/api/static..."
	@mkdir -p kairos/api/static
	@cp -r web/dist/* kairos/api/static/ 2>/dev/null || true

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov runs/ index/
