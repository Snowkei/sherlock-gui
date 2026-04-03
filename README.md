# Sherlock GUI

A beautiful web interface for [Sherlock](https://github.com/sherlock-project/sherlock) — find usernames across 400+ social platforms.

## Features

- 🎨 Modern dark-themed UI
- ⚡ Preset modes: Quick Scan, Full Scan, Tor Stealth, Chinese Platforms, NSFW
- 🌐 Full config: Tor, Proxy, Timeout, Output format (CSV/Excel)
- 🔎 Select platforms from a 400+ list
- 📥 Download results per username
- 🐳 Docker-ready with one-command deployment
- ☁️ Cloudflare Tunnel / Pages deployment supported

## Quick Start

### Docker

```bash
docker compose -f deploy/docker-compose.yml up -d
# Open http://localhost:8000
```

### Build Frontend + Run

```bash
cd frontend && npm install && npm run build
cd ../backend && pip install -r requirements.txt && python main.py
# Open http://localhost:8000
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Frontend UI |
| GET | `/health` | Health check |
| POST | `/api/search` | Start search job |
| GET | `/api/jobs/{id}` | Get job status/results |
| GET | `/api/jobs` | List all jobs |
| DELETE | `/api/jobs/{id}` | Delete job |
| GET | `/api/presets` | Get config presets |
| GET | `/api/sites` | Get supported platforms |

## License

MIT
