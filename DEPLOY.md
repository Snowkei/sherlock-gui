# Sherlock GUI - 部署指南

## 架构

- **前端**: Cloudflare Pages（自动部署）
- **后端**: Railway.app（自动部署）
- **CI/CD**: GitHub Actions

---

## 一键部署

### 1. 部署后端到 Railway

点击下方按钮一键部署：

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/Snowkei/sherlock-gui)

部署后会得到一个 URL，如：`https://sherlock-gui-backend.railway.app`

### 2. 配置 Cloudflare Pages

1. Fork 本仓库
2. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
3. 进入 **Pages** → **Create a project** → **Connect to Git**
4. 选择你 fork 的仓库
5. 配置：
   - **Framework preset**: None
   - **Build command**: `cd frontend && npm ci && npm run build`
   - **Build output directory**: `frontend/dist`
6. **添加环境变量**：
   - `VITE_API_BASE_URL`: 你的 Railway 后端地址（如 `https://sherlock-gui-backend.railway.app`）
7. 点击 **Save and Deploy**

### 3. 配置 GitHub Secrets（自动部署）

在你的 GitHub 仓库 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare 账户 ID | Cloudflare Dashboard 右侧 |
| `CLOUDFLARE_PAGES_API_TOKEN` | Cloudflare API Token | 创建 API Token：Edit Cloudflare Workers |
| `VITE_API_BASE_URL` | 后端 API 地址 | Railway 部署后的 URL |

---

## 本地开发

### 后端

```bash
cd backend
pip install -r requirements.txt
python main.py
# 打开 http://localhost:8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
# 打开 http://localhost:5173
```

---

## 项目结构

```
sherlock-gui/
├── frontend/          # Vue 3 前端
│   ├── src/
│   │   ├── main.js
│   │   └── App.vue    # 主组件
│   ├── package.json
│   └── vite.config.js
├── backend/           # FastAPI 后端
│   ├── main.py        # API 服务
│   ├── requirements.txt
│   └── Dockerfile
├── .github/workflows/ # GitHub Actions CI/CD
│   ├── deploy-frontend.yml
│   └── deploy-backend.yml
├── Dockerfile         # Railway 用根级 Dockerfile
└── README.md
```

---

## 注意事项

1. **Sherlock 依赖**: 后端需要 `sherlock-project` 包，已包含在 `requirements.txt` 中
2. **跨域**: 后端已配置 CORS 允许前端域名访问
3. **健康检查**: `/health` 端点用于 Railway 健康检查
4. **结果文件**: 搜索结果保存在容器内 `/app/results/` 目录，重启后清空（生产环境建议挂载持久存储）

---

## License

MIT
