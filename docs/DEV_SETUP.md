# Development Setup — ms_chat + ia_common (dev compose)

Purpose: make it safe to run `docker compose -f docker-compose.dev.yml up --build` with bind-mounts and editable installs for `ia_common`.

1) Create the local package scaffold BEFORE `docker compose up`

```bash
# from repo root
mkdir -p ia_common
touch ia_common/__init__.py
chown -R $(id -u):$(id -g) ia_common
```

This prevents Docker from creating root-owned folders when mounting.

2) Ensure your dev virtualenv has `uv` (Astral) installed (optional, used in container command):

```bash
.venv/bin/pip install uv
```

3) Start development services (build + bind-mounts):

```bash
cd $(git rev-parse --show-toplevel)
docker compose -f docker-compose.dev.yml up --build ms_chat qdrant
```

Notes on hot-reload
- The compose service starts Uvicorn with `--reload` and `--reload-dir` for both `/app/src` and `/app/ia_common`. This causes Uvicorn to watch file changes in both locations.
- Ensure `uvicorn[standard]` or `watchfiles` is available in the container image for reliable reload behavior.

Troubleshooting
- If editable install of `ia_common` fails due to permissions, exec into the container and inspect:

```bash
docker compose -f docker-compose.dev.yml exec ms_chat /bin/sh
# inside container
ls -la /app
pip install -e /app/ia_common
```

- If the container created `ia_common` as root on the host, fix and re-run:

```bash
sudo chown -R $(id -u):$(id -g) ia_common
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up --build
```

Cleanup
- To remove bind-mount artifacts and cache dirs used by tests, run:

```bash
docker compose -f docker-compose.dev.yml down
rm -rf .venv ia_service_core/cag_cache ia_common/__pycache__
```

Tips
- Use `--reload-dir` flags to watch additional folders. Example already configured in `docker-compose.dev.yml`.
- On OSX/Linux, prefer `CHOKIDAR_USEPOLLING=true` for frontend watchers when using bind mounts over Docker Desktop.
- Keep `ia_common` minimal and add public APIs under `ia_common/<module>.py` and update `__all__` for discoverability.
