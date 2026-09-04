.PHONY: bootstrap config check test up pull restart logs status down

bootstrap:
	python3 scripts/bootstrap.py

config:
	python3 scripts/generate_config.py

check: config
	python3 scripts/preflight.py

test:
	python3 -m unittest discover -s tests -v

pull:
	docker compose pull

up: check
	docker compose up -d

restart: check
	docker compose up -d --force-recreate

logs:
	docker compose logs -f --tail=200

status:
	docker compose ps
	@ls -lh output/all.yaml output/last-good.yaml 2>/dev/null || true

down:
	docker compose down
