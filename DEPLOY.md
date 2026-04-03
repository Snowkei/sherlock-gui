# Sherlock GUI - 部署指南

## 架构

```
┌─────────────────────┐      ┌─────────────────────────────┐
│  Cloudflare Pages   │      │       Fly.io / Railway       │
│   Vue 3 前端 (静态)  │ ─── │  Python FastAPI 后端 (Docker) │
│  自动构建部署         │ API  │     ghcr.io 自动拉取         │
└─────────────────────┘      └─────────────────────────────┘
```

- **前端**: Cloudflare Pages（静态托管）
- **后端**: Fly.io 或 Railway（Docker 容器）
- **CI/CD**: GitHub Actions（自动构建 + 推送）
- **镜像**: GitHub Container Registry (ghcr.io)

---

## 方式一：GitHub Actions 自动部署（推荐）

### 第一步：配置 GitHub Secrets

在 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions** 中添加：

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare 账户 ID | [Cloudflare Dashboard](https://dash.cloudflare.com) 右侧复制 |
| `CLOUDFLARE_PAGES_API_TOKEN` | Pages 部署 Token | Cloudflare → Profile → API Tokens → Create Custom Token |
| `FLY_API_TOKEN` | Fly.io 部署 Token | [Fly.io dashboard](https://fly.io) → Account → API Tokens |
| `VITE_API_BASE_URL` | 后端 API 地址 | Fly.io 部署后获得的 URL |

> ⚠️ `VITE_API_BASE_URL` 可以等 Fly.io 部署完成后再填入，填入后前端会自动带上后端地址。

### 第二步：部署后端到 Fly.io

**方式 A - 手动初始化（一次性）：**

```bash
# 安装 Fly CLI
brew install flyctl

# 登录
flyctl auth login

# 在项目根目录初始化（fly.toml 已配置好）
flyctl launch --no-deploy --name sherlock-gui-backend
# 选择: 已有项目，不创建新仓库，不设置 Upstash

# 首次部署
flyctl deploy --image ghcr.io/snowkei/sherlock-gui-backend:latest
```

**方式 B - 完全自动化（通过 GitHub Actions）：**

在 GitHub Secrets 中添加 `FLY_API_TOKEN` 后，每次推送 `backend/` 分支，GitHub Actions 会自动：
1. 构建 Docker 镜像
2. 推送到 ghcr.io
3. 调用 Fly.io API 部署

### 第三步：部署前端到 Cloudflare Pages

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com) → **Pages**
2. **Create a project** → **Connect to Git** → 选择 `snowkei/sherlock-gui`
3. 配置构建：
   - **Build command**: `cd frontend && npm ci && npm run build`
   - **Build output directory**: `frontend/dist`
4. **Environment variables** 添加：
   - `VITE_API_BASE_URL` = 你的 Fly.io 后端 URL（如 `https://sherlock-gui-backend.fly.dev`）
5. 点击 **Save and Deploy**

### 以后每次提交

```
git push
  → frontend/ 改动 → GitHub Actions → Cloudflare Pages 自动部署
  → backend/  改动 → GitHub Actions → 构建镜像 + Fly.io 自动部署
```

---

## 方式二：Docker 本地部署

```bash
# 克隆
git clone https://github.com/Snowkei/sherlock-gui.git
cd sherlock-gui

# 启动（前后端一体）
docker compose -f deploy/docker-compose.yml up -d
# 打开 http://localhost:8080

# 带 Tor 匿名模式
docker compose -f deploy/docker-compose.yml --profile tor up -d
```

---

## 方式三：纯 Fly.io CLI 部署

```bash
flyctl launch --image ghcr.io/snowkei/sherlock-gui-backend:latest --name sherlock-gui-backend
flyctl secrets set API_KEY=your-secret-key
flyctl梧桐 deploy
```

---

## 方式四：Railway 部署

Railway 支持直接从 GitHub 部署 Dockerfile：

1. 打开 https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. 选择 `snowkei/sherlock-gui`
4. Railway 自动检测到 `backend/Dockerfile`，开始构建
5. 复制 Railway 分配的 URL，填入前端 `VITE_API_BASE_URL`

---

## 环境变量

### 前端构建时注入（Vite）

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `VITE_API_BASE` | 后端 API 地址 | `https://sherlock-gui-backend.fly.dev` |

### 后端运行时

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | HTTP 监听端口 | `8080` |
| `PYTHONUNBUFFERED` | 实时输出日志 | `1` |

---

## 文件结构

```
sherlock-gui/
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── main.js         # 入口，注入 API_BASE
│   │   └── App.vue         # 主界面组件
│   ├── package.json
│   └── vite.config.js      # Vite 构建配置
├── backend/                # FastAPI 后端
│   ├── main.py             # API 服务（408行）
│   ├── requirements.txt    # Python 依赖
│   ├── Dockerfile          # Docker 镜像
│   └── railway.toml        # Railway 配置
├── .github/workflows/
│   ├── deploy-frontend.yml # → Cloudflare Pages
│   └── deploy-backend.yml   # → Fly.io + GHCR
├── Dockerfile              # 根级 Dockerfile（Railway 用）
├── fly.toml                # Fly.io 配置
└── deploy/
    ├── docker-compose.yml  # 本地 Docker 部署
    └── docker-compose.prod.yml
```
