# Probo Example: Python

A Flask demo that displays the environment variables a Probo CI build injects
into a container. It renders two tables:

- **Build variables** — the documented Probo catalog (`PROBO_ENVIRONMENT`,
  `BUILD_ID`, `BRANCH_NAME`, …) with live values where present.
- **Secrets & other injected variables** — everything else made visible to the
  process (organization/project secrets and any custom variables), discovered
  dynamically.

## Project layout

|-----|-----------|
|.probo.yaml | Proposed Probo config (type: python + PythonApp plugin) |
|PROBO_PYTHON.md | Design proposal for Probo's Python support |
|src/app.py | Flask app; exposes the WSGI callable `app` |
|src/probo_env.py | Env-var filtering + build/secret partitioning |
|src/templates/index.html | The page |
|src/requirements.txt | Flask + gunicorn |

## Run locally

```bash
cd src
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Dev server:
.venv/bin/python app.py                          # http://0.0.0.0:8000

# Or the way Probo's proposed PythonApp plugin runs it:
.venv/bin/gunicorn --bind 127.0.0.1:8000 app:app
```

Simulate a Probo build environment:

```bash
cd src
PROBO_ENVIRONMENT=TRUE BUILD_ID=abc123 BRANCH_NAME=main \
  MY_API_TOKEN=example .venv/bin/gunicorn --bind 127.0.0.1:8000 app:app
```

## How it runs in a Probo Python container

1. **Installs dependencies at build time** — creates a venv and runs
   `pip install -r requirements.txt` in `$SRC_DIR/src`.
2. **Writes `/src/startup.sh`** — `cd /src/src; <env vars> gunicorn --bind
   127.0.0.1:8000 app:app` (one `KEY="value"` per `environment:` entry).
3. The container's `app-start.js` runs that file; nginx reverse-proxies
   `*.probo.build` to the app on `127.0.0.1:8000`.

Variables listed under `environment:` are forwarded to the app and appear on the
page (standard build vars in the first table, custom ones like `DEMO_CUSTOM_VAR`
in the second).
