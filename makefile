.PHONY: tests

textual-ui:
	python -m src.textual_ui
	
dummy-ui:
	python -m src.learning_textual

ngrok-set:
	nohup ngrok http 1234 > ngrok.log 2>&1 &

ngrok-kill:
	@echo "Killing ngrok..."
	@pkill -f ngrok

web:
	make ngrok-set
	until curl --silent http://localhost:4040/api/tunnels; do sleep 1; done
	python src/web_ui/main.py
	make ngrok-kill

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