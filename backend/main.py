"""
Sherlock GUI Backend - FastAPI Server
Serves the Vue frontend and proxies Sherlock searches
"""

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

# ──────────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────────

app = FastAPI(
    title="Sherlock GUI API",
    description="Web UI for Sherlock - Find Usernames Across Social Networks",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# In-memory job store (use Redis in production)
jobs: dict = {}

# ──────────────────────────────────────────────
# Pydantic Models
# ──────────────────────────────────────────────

class SearchRequest(BaseModel):
    usernames: list[str] = Field(..., min_length=1, description="Usernames to search")
    # Output options
    folder_output: Optional[str] = Field(None, description="Output folder for results")
    output: Optional[str] = Field(None, description="Single output file (for one username)")
    # Proxy & Network
    tor: bool = Field(False, description="Route through Tor")
    unique_tor: bool = Field(False, description="Use unique Tor circuit per request")
    proxy: Optional[str] = Field(None, description="Proxy URL (e.g. socks5://127.0.0.1:1080)")
    # Output format
    csv: bool = Field(False, description="Generate CSV output")
    xlsx: bool = Field(False, description="Generate Excel XLSX output")
    # Filtering
    site: Optional[list[str]] = Field(None, description="Limit to specific sites")
    exclude_site: Optional[list[str]] = Field(None, description="Exclude specific sites")
    nsfw: bool = Field(False, description="Include NSFW sites")
    # Display options
    print_all: bool = Field(False, description="Show sites where username was NOT found")
    print_found: bool = Field(False, description="Only show sites where username was found")
    no_color: bool = Field(True, description="Disable color output")
    # Behavior
    timeout: int = Field(60, ge=1, le=300, description="Request timeout in seconds")
    browse: bool = Field(False, description="Open results in browser")
    local: bool = Field(False, description="Use local data.json file")
    verbose: bool = Field(False, description="Verbose/debug output")
    # JSON input
    json_file: Optional[str] = Field(None, description="Load usernames from JSON file URL")


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobResult(BaseModel):
    job_id: str
    status: str  # pending | running | completed | failed
    usernames: list[str]
    results: Optional[dict] = None
    files: Optional[dict] = None  # {username: file_url}
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# ──────────────────────────────────────────────
# Sherlock Execution
# ──────────────────────────────────────────────

async def run_sherlock(search_req: SearchRequest, job_id: str):
    """Run Sherlock search in background asyncio subprocess"""
    job = jobs[job_id]
    job["status"] = "running"
    job["started_at"] = datetime.utcnow().isoformat() + "Z"

    # Build sherlock arguments
    args = ["python", "-m", "sherlock"]

    # Core arguments
    for username in search_req.usernames:
        args.append(username)

    # Output options
    if search_req.folder_output:
        args += ["--folderoutput", search_req.folder_output]
    if search_req.output and len(search_req.usernames) == 1:
        args += ["--output", search_req.output]
    if search_req.csv:
        args.append("--csv")
    if search_req.xlsx:
        args.append("--xlsx")
    if search_req.print_all:
        args.append("--print-all")
    if search_req.print_found:
        args.append("--print-found")
    if search_req.no_color:
        args.append("--no-color")
    if search_req.browse:
        args.append("--browse")
    if search_req.local:
        args.append("--local")
    if search_req.nsfw:
        args.append("--nsfw")
    if search_req.verbose:
        args.append("--verbose")

    # Network
    if search_req.tor:
        args.append("--tor")
    if search_req.unique_tor:
        args.append("--unique-tor")
    if search_req.proxy:
        args += ["--proxy", search_req.proxy]

    # Site filtering
    if search_req.site:
        for site in search_req.site:
            args += ["--site", site]

    # Timeout
    args += ["--timeout", str(search_req.timeout)]

    # JSON file
    if search_req.json_file:
        args += ["--json", search_req.json_file]

    try:
        # Run sherlock
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(BASE_DIR),
        )

        stdout, _ = await process.communicate()
        output = stdout.decode("utf-8", errors="replace") if stdout else ""

        if process.returncode == 0:
            job["status"] = "completed"
            job["completed_at"] = datetime.utcnow().isoformat() + "Z"

            # Collect result files
            result_files = {}
            for username in search_req.usernames:
                # Sherlock saves as username.txt by default
                safe_name = username.replace("/", "_").replace("\\", "_")
                for ext in ["txt", "csv", "xlsx", "json"]:
                    fpath = RESULTS_DIR / f"{safe_name}.{ext}"
                    if fpath.exists():
                        result_files[username] = f"/api/results/{job_id}/{safe_name}.{ext}"
                        break
                else:
                    # Try to find by glob
                    import glob
                    matches = list(RESULTS_DIR.glob(f"{safe_name}.*"))
                    if matches:
                        result_files[username] = f"/api/results/{job_id}/{matches[0].name}"

            job["files"] = result_files
            job["raw_output"] = output[-5000:]  # Last 5000 chars
        else:
            job["status"] = "failed"
            job["error"] = output[-3000:]
            job["completed_at"] = datetime.utcnow().isoformat() + "Z"

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        job["completed_at"] = datetime.utcnow().isoformat() + "Z"


# ──────────────────────────────────────────────
# API Routes
# ──────────────────────────────────────────────

@app.get("/")
async def serve_frontend():
    """Serve the Vue frontend"""
    index_path = BASE_DIR / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return HTMLResponse("<h1>Sherlock GUI</h1><p>Build the frontend first: cd frontend && npm run build</p>")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "sherlock-gui", "version": "1.0.0"}


# ── Sites Catalog ──

@app.get("/api/sites")
async def get_sites():
    """Return all supported sites with metadata"""
    import importlib.util
    try:
        spec = importlib.util.find_spec("sherlock")
        site_list_path = Path(spec.submodule_search_locations[0]) / "sites.md"
        if site_list_path.exists():
            content = site_list_path.read_text()
            return {"source": "sites.md", "raw": content}
    except Exception:
        pass

    # Fallback: return known popular sites
    popular_sites = [
        "github", "twitter", "instagram", "facebook", "youtube",
        "tiktok", "reddit", "linkedin", "pinterest", "snapchat",
        "discord", "telegram", "whatsapp", "weibo", "douyin",
        "bilibili", "xiaohongshu", "zhihu", "douban", "taobao",
        "spotify", "steam", "twitch", "medium", "tumblr",
        "threads", "mastodon", "mastodon.social", "lemmy",
        "odysee", "archive.org", "pastebin", "deviantart",
        "dribbble", "behance", "500px", "flickr", "vsco",
        "etsy", "shopify", "wordpress", "blogger", "wix",
        "squarespace", "about.me", "disqus", "tripadvisor",
        "yelp", "goodreads", "letterboxd", "metacritic",
        "last.fm", "soundcloud", "bandcamp", "mixcloud",
        "reverbnation", "patreon", "ko-fi", "gumroad",
        "substack", "gitea", "codeberg", "gitlab", "bitbucket",
    ]
    return {"sites": popular_sites, "total": len(popular_sites)}


# ── Search Jobs ──

@app.post("/api/search", response_model=JobResponse)
async def create_search(request: SearchRequest, background_tasks: BackgroundTasks):
    """Start a new Sherlock search job"""
    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "usernames": request.usernames,
        "request": request.model_dump(),
        "results": None,
        "files": None,
        "error": None,
        "started_at": None,
        "completed_at": None,
    }

    background_tasks.add_task(run_sherlock, request, job_id)

    return JobResponse(
        job_id=job_id,
        status="pending",
        message=f"Search job created for {len(request.usernames)} username(s). Poll /api/jobs/{job_id} for results."
    )


@app.get("/api/jobs/{job_id}", response_model=JobResult)
async def get_job(job_id: str):
    """Get job status and results"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    return JobResult(
        job_id=job["job_id"],
        status=job["status"],
        usernames=job["usernames"],
        results=job.get("results"),
        files=job.get("files"),
        error=job.get("error"),
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
    )


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs"""
    return {
        "jobs": [
            {
                "job_id": j["job_id"],
                "status": j["status"],
                "usernames": j["usernames"],
                "started_at": j.get("started_at"),
                "completed_at": j.get("completed_at"),
            }
            for j in jobs.values()
        ]
    }


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its results"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    del jobs[job_id]
    return {"message": "Job deleted"}


# ── Config Presets ──

@app.get("/api/presets")
async def get_presets():
    """Return predefined configuration presets"""
    return {
        "presets": [
            {
                "id": "quick",
                "name": "⚡ Quick Scan",
                "description": "Search top 30 popular platforms",
                "config": {"print_found": True, "timeout": 30},
            },
            {
                "id": "full",
                "name": "🔍 Full Scan",
                "description": "Search all 400+ supported platforms",
                "config": {"print_found": True, "timeout": 120},
            },
            {
                "id": "nsfw",
                "name": "🔞 Full + NSFW",
                "description": "All platforms including adult sites",
                "config": {"nsfw": True, "print_found": True, "timeout": 120},
            },
            {
                "id": "stealth",
                "name": "🕵️ Stealth (Tor)",
                "description": "Route through Tor for anonymity",
                "config": {"tor": True, "timeout": 120},
            },
            {
                "id": "chinese",
                "name": "🇨🇳 Chinese Platforms",
                "description": "Search Chinese social platforms",
                "config": {
                    "site": ["weibo", "douyin", "bilibili", "xiaohongshu", "zhihu", "douban", "taobao"],
                    "timeout": 60,
                },
            },
            {
                "id": "custom",
                "name": "⚙️ Custom",
                "description": "Configure every option manually",
                "config": {},
            },
        ]
    }


# ── Results Files ──

@app.get("/api/results/{job_id}/{filename}")
async def get_result_file(job_id: str, filename: str):
    """Download a result file"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    file_path = RESULTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Detect content type
    import mimetypes
    content_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(
        str(file_path),
        media_type=content_type or "application/octet-stream",
        filename=filename,
    )


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
