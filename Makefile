.PHONY: backend frontend install install-frontend docker-up docker-down clean

# ── Local dev ──────────────────────────────────────────────
backend:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm start

install:
	pip install -r backend/requirements.txt

install-frontend:
	cd frontend && npm install

# ── Docker ─────────────────────────────────────────────────
docker-up:
	docker compose up --build

docker-down:
	docker compose down

# ── Utilities ──────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

lint:
	ruff check backend/

test-api:
	curl -s -X POST http://localhost:8000/predict \
	  -H "Content-Type: application/json" \
	  -d '{"tenure":3,"monthly_charges":85,"contract":"Month-to-month","internet_service":"Fiber optic"}' \
	  | python -m json.tool
