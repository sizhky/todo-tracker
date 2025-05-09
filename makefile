.PHONY: tests

ui:
	python -m src.textual_ui
	
dummy-ui:
	python -m src.learning_textual

dev-mcp:
	mcp dev src/todo_tracker/mcp/server.py

format:
	ruff format
	
test: format
	pytest -v --tb=short --disable-warnings --maxfail=1 tests