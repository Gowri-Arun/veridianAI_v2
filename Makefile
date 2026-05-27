setup:
	pip install -r requirements.txt

api:
	uvicorn app.main:app --reload

ui:
	streamlit run frontend/streamlit_app.py

test:
	pytest

validate-benchmark:
	python scripts/validate_jsonl.py

format:
	python -m compileall app
