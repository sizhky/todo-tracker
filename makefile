.PHONY: tests

ui:
	python -m src.textual_ui
	
dummy-ui:
	python -m src.learning_textual

html:
	python src/web_ui/main.py

mcp:
	mcp dev src/td/mcp.py

api:
	python src/td/api.py

format:
	ruff format
	
test:
	pytest -v --tb=short --disable-warnings --maxfail=1 tests

deploy-docs:
	mkdocs gh-deploy