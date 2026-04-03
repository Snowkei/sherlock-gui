# Sherlock GUI

> 🔍 A beautiful web interface for [Sherlock](https://github.com/sherlock-project/sherlock) — find usernames across 400+ social platforms.

**Live Demo**: https://sherlock-gui.pages.dev

## Features

- 🎨 Modern dark-themed UI
- ⚡ Preset modes: Quick Scan · Full Scan · Tor Stealth · Chinese Platforms · NSFW
- 🌐 Configurable: Tor, Proxy, Timeout, Output formats (CSV/Excel)
- 🔎 Select platforms from a 400+ site list
- 📥 Download results per username
- 🐳 Docker-ready
- ☁️ Auto-deploy via GitHub Actions → Cloudflare Pages + Railway

## Quick Start

### Docker

```bash
docker compose -f deploy/docker-compose.yml up -d
# Open http://localhost:8000
```

### Local Development

```bash
# Backend
cd backend && pip install -r requirements.txt && python main.py

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Deploy to Production

See [DEPLOY.md](./DEPLOY.md) for step-by-step deployment instructions.

## API Endpoints

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
