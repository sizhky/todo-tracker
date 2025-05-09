.PHONY: tests

ui:
	python -m src.textual_ui
	
dummy-ui:
	python -m src.learning_textual

mcp:
	mcp dev src/td/mcp.py

format:
	ruff format
	
test: format
	pytest -v --tb=short --disable-warnings --maxfail=1 tests