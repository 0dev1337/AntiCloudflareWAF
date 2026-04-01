# AntiCloudflareWAF

FastAPI service that solves Cloudflare UAM/WAF challenges and returns `cf_clearance` + user-agent.

## Project Structure

- `api`: API app factory, middleware, request schemas, and routes
- `services`: Cloudflare solving service logic
- `core`: shared infrastructure utilities (logging)
- `main.py`: local development entrypoint

## Run

```bash
py main.py
```
