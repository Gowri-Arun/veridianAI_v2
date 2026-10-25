PYTHON ?= python

setup:
	$(PYTHON) -m pip install -r requirements.txt

api:
	$(PYTHON) -m uvicorn app.main:app --reload

ui:
	$(PYTHON) -m streamlit run frontend/streamlit_app.py

test:
	$(PYTHON) -m pytest

validate-benchmark:
	$(PYTHON) -m scripts.validate_jsonl

check-env:
	$(PYTHON) -m scripts.check_environment

validate-data:
	$(PYTHON) -m scripts.validate_week2_data

eval-retrieval:
	$(PYTHON) -m scripts.run_retrieval_eval

validate-sql-benchmark:
	$(PYTHON) -m scripts.validate_sql_benchmark

eval-sql:
	$(PYTHON) -m scripts.run_sql_eval

format:
	$(PYTHON) -m compileall app frontend scripts tests
