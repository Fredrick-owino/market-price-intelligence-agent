.PHONY: demo check

demo:
	bash infra/bootstrap-local-demo.sh

check:
	.venv/bin/ruff check backend
	.venv/bin/ruff format --check backend
	.venv/bin/python -m pytest -q backend/tests
	npm run typecheck --prefix frontend
	npm run build --prefix frontend
