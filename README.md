# AntiCloudflareWAF

Async FastAPI service for solving Cloudflare UAM/WAF challenges and returning a usable `cf_clearance` cookie with matching browser `user_agent`.

## Features

- Async Cloudflare challenge solving via Camoufox
- Simple REST API (`/health`, `/waf`)
- Request timing and completion middleware logs
- Minimal pretty console logger for readable output
- Configurable runtime options (proxy, locale, headless, WebRTC/WebGL flags)

## Project Layout

```text
.
|- api/
|  |- app.py              # FastAPI app factory
|  |- middleware.py       # Request logging middleware
|  |- schemas.py          # Pydantic request models
|  \- routes/waf.py       # API endpoints
|- core/
|  \- logging.py          # Shared logger utility
|- services/
|  \- cloudflare_solver.py# WAF solve workflow
|- main.py                # Local run entrypoint
\- README.md
```

## Requirements

- Python 3.11+ (recommended)
- Installed dependencies for:
  - `fastapi`
  - `uvicorn`
  - `pydantic`
  - `camoufox`

## Quick Start

Install dependencies (example):

```bash
py -m pip install fastapi uvicorn pydantic camoufox
```

Run the server:

```bash
py main.py
```

Server will listen on `http://0.0.0.0:8000`.

## API Documentation

When running, interactive docs are available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Reference

### `GET /health`

Health check endpoint.

#### Response `200`

```json
{
  "status": "ok"
}
```

---

### `POST /waf`

Solve Cloudflare WAF for a target domain.

#### Request Body

```json
{
  "domain": "https://cfcybernews.eu",
  "headless": true,
  "proxy": null,
  "disable_coop": true,
  "locale": ["en-US"],
  "block_webrtc": false,
  "block_webgl": false,
  "humanize": true,
  "geoip": true,
  "os": "macos",
  "i_know_what_im_doing": true
}
```

#### Field Notes

- `domain` (string, required): target URL.
- `proxy` (string, optional): currently expected as `http://username:password@host:port`.
- Remaining fields are optional and mapped directly to Camoufox launch options.

#### Success Response `200`

```json
{
  "ok": true,
  "domain": "https://cfcybernews.eu",
  "cf_clearance": "cf_clearance=...",
  "user_agent": "Mozilla/5.0 (...)",
  "proxy": null
}
```

#### Failure Response `502`

```json
{
  "ok": false,
  "message": "Unable to get cf_clearance cookie",
  "domain": "https://cfcybernews.eu"
}
```

## Example Requests

Without proxy:

```bash
curl -X POST "http://localhost:8000/waf" \
  -H "Content-Type: application/json" \
  -d "{\"domain\":\"https://cfcybernews.eu\"}"
```

With proxy:

```bash
curl -X POST "http://localhost:8000/waf" \
  -H "Content-Type: application/json" \
  -d "{\"domain\":\"https://example.com\",\"proxy\":\"http://user:pass@host:8080\"}"
```

## Notes

- WAF bypassing behavior depends on target challenge complexity and network conditions.
- Use responsibly and only on systems/domains you are authorized to test.
