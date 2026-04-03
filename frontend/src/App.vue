<template>
  <div class="app">
    <!-- Header -->
    <header class="header">
      <div class="header-inner">
        <div class="logo">
          <span class="logo-icon">🔍</span>
          <div>
            <h1>Sherlock GUI</h1>
            <p>用户名社工查询 · 400+ 平台</p>
          </div>
        </div>
        <div class="header-actions">
          <a href="https://github.com/sherlock-project/sherlock" target="_blank" class="btn-ghost">GitHub</a>
          <a href="https://sherlockproject.xyz" target="_blank" class="btn-ghost">官网</a>
        </div>
      </div>
    </header>

    <main class="main">
      <!-- Left Panel: Search Config -->
      <aside class="sidebar">
        <!-- Usernames -->
        <section class="panel">
          <h2 class="panel-title">
            <span>👤</span> 用户名
          </h2>
          <div class="chip-input">
            <div class="chips">
              <span v-for="(name, i) in usernames" :key="i" class="chip">
                {{ name }}
                <button @click="removeUsername(i)">×</button>
              </span>
            </div>
            <input
              v-model="inputUsername"
              placeholder="输入用户名后按回车"
              @keydown.enter.prevent="addUsername"
              @keydown.comma.prevent="addUsername"
            />
          </div>
          <p class="hint">支持同时搜索多个用户名，用逗号或回车分隔</p>
        </section>

        <!-- Presets -->
        <section class="panel">
          <h2 class="panel-title"><span>⚡</span> 预设模式</h2>
          <div class="presets">
            <button
              v-for="preset in presets"
              :key="preset.id"
              class="preset-btn"
              :class="{ active: selectedPreset === preset.id }"
              @click="applyPreset(preset)"
            >
              <span class="preset-icon">{{ preset.name[0] }}</span>
              <div>
                <div class="preset-name">{{ preset.name }}</div>
                <div class="preset-desc">{{ preset.description }}</div>
              </div>
            </button>
          </div>
        </section>

        <!-- Config Sections -->
        <section class="panel">
          <h2 class="panel-title">
            <span>⚙️</span> 搜索配置
            <button class="toggle-all" @click="showAll = !showAll">
              {{ showAll ? '收起' : '展开全部' }}
            </button>
          </h2>

          <!-- Network -->
          <details class="config-section" :open="showAll || !collapsedSections.has('network')">
            <summary @click.prevent="toggleSection('network')">
              🌐 网络与代理
              <span class="arrow">{{ collapsedSections.has('network') ? '▶' : '▼' }}</span>
            </summary>
            <div class="config-body">
              <label class="toggle-row">
                <span>使用 Tor 匿名网络</span>
                <input type="checkbox" v-model="config.tor" />
                <span class="toggle-slider"></span>
              </label>
              <label class="toggle-row">
                <span>每个请求换新 Tor 线路</span>
                <input type="checkbox" v-model="config.unique_tor" :disabled="!config.tor" />
                <span class="toggle-slider"></span>
              </label>
              <div class="field">
                <label>代理地址</label>
                <input type="text" v-model="config.proxy" placeholder="socks5://127.0.0.1:1080" />
              </div>
              <div class="field">
                <label>超时时间（秒）</label>
                <input type="number" v-model.number="config.timeout" min="1" max="300" />
              </div>
            </div>
          </details>

          <!-- Output -->
          <details class="config-section" :open="showAll || !collapsedSections.has('output')">
            <summary @click.prevent="toggleSection('output')">
              📄 输出格式
              <span class="arrow">{{ collapsedSections.has('output') ? '▶' : '▼' }}</span>
            </summary>
            <div class="config-body">
              <label class="toggle-row">
                <span>生成 CSV 文件</span>
                <input type="checkbox" v-model="config.csv" />
                <span class="toggle-slider"></span>
              </label>
              <label class="toggle-row">
                <span>生成 Excel 文件</span>
                <input type="checkbox" v-model="config.xlsx" />
                <span class="toggle-slider"></span>
              </label>
              <div class="field">
                <label>输出文件夹</label>
                <input type="text" v-model="config.folder_output" placeholder="留空则保存到默认目录" />
              </div>
            </div>
          </details>

          <!-- Display -->
          <details class="config-section" :open="showAll || !collapsedSections.has('display')">
            <summary @click.prevent="toggleSection('display')">
              🖥️ 显示选项
              <span class="arrow">{{ collapsedSections.has('display') ? '▶' : '▼' }}</span>
            </summary>
            <div class="config-body">
              <label class="toggle-row">
                <span>仅显示找到的平台</span>
                <input type="checkbox" v-model="config.print_found" />
                <span class="toggle-slider"></span>
              </label>
              <label class="toggle-row">
                <span>显示所有平台（含未找到）</span>
                <input type="checkbox" v-model="config.print_all" />
                <span class="toggle-slider"></span>
              </label>
              <label class="toggle-row">
                <span>在浏览器打开结果链接</span>
                <input type="checkbox" v-model="config.browse" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </details>

          <!-- Filtering -->
          <details class="config-section" :open="showAll || !collapsedSections.has('filter')">
            <summary @click.prevent="toggleSection('filter')">
              🔎 平台过滤
              <span class="arrow">{{ collapsedSections.has('filter') ? '▶' : '▼' }}</span>
            </summary>
            <div class="config-body">
              <label class="toggle-row">
                <span>包含 NSFW 平台</span>
                <input type="checkbox" v-model="config.nsfw" />
                <span class="toggle-slider"></span>
              </label>
              <label class="toggle-row">
                <span>使用本地数据文件</span>
                <input type="checkbox" v-model="config.local" />
                <span class="toggle-slider"></span>
              </label>
              <div class="field">
                <label>指定平台（逗号分隔）</label>
                <input type="text" v-model="sitesInput" placeholder="如: github, twitter, weibo" />
              </div>
              <div v-if="sitesInput" class="site-preview">
                已选: {{ parsedSites.join(', ') }}
              </div>
              <button class="btn-outline btn-sm" @click="showSitePicker = true">
                🗂️ 从列表选择平台 ({{ selectedSites.length }})
              </button>
            </div>
          </details>

          <!-- Advanced -->
          <details class="config-section" :open="showAll || !collapsedSections.has('advanced')">
            <summary @click.prevent="toggleSection('advanced')">
              🚀 高级选项
              <span class="arrow">{{ collapsedSections.has('advanced') ? '▶' : '▼' }}</span>
            </summary>
            <div class="config-body">
              <label class="toggle-row">
                <span>详细输出模式</span>
                <input type="checkbox" v-model="config.verbose" />
                <span class="toggle-slider"></span>
              </label>
              <div class="field">
                <label>从 JSON 文件加载用户名</label>
                <input type="text" v-model="config.json_file" placeholder="https://example.com/users.json" />
              </div>
            </div>
          </details>
        </section>

        <!-- Search Button -->
        <button class="btn-search" @click="startSearch" :disabled="!usernames.length || isSearching">
          <span v-if="!isSearching">🔍 开始查询</span>
          <span v-else>⏳ 查询中 ({{ currentJob?.usernames.join(', ') }})...</span>
        </button>
      </aside>

      <!-- Right Panel: Results -->
      <div class="content">
        <!-- Jobs List -->
        <div v-if="allJobs.length" class="jobs-bar">
          <div
            v-for="job in allJobs"
            :key="job.job_id"
            class="job-chip"
            :class="job.status"
            @click="selectJob(job.job_id)"
          >
            <span class="job-dot"></span>
            {{ job.usernames[0] }}{{ job.usernames.length > 1 ? `+${job.usernames.length-1}` : '' }}
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!currentJob && !isSearching" class="empty-state">
          <div class="empty-icon">🔍</div>
          <h3>准备就绪</h3>
          <p>在左侧输入用户名，选择配置，点击「开始查询」</p>
          <div class="feature-grid">
            <div class="feature-card">
              <span>🔐</span>
              <div>
                <h4>隐私保护</h4>
                <p>支持 Tor 匿名网络</p>
              </div>
            </div>
            <div class="feature-card">
              <span>📊</span>
              <div>
                <h4>多格式导出</h4>
                <p>CSV / Excel / JSON</p>
              </div>
            </div>
            <div class="feature-card">
              <span>🌐</span>
              <div>
                <h4>400+ 平台</h4>
                <p>覆盖全球主流社交平台</p>
              </div>
            </div>
            <div class="feature-card">
              <span>🐳</span>
              <div>
                <h4>Docker 部署</h4>
                <p>一行命令启动服务</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Running State -->
        <div v-if="isSearching" class="running-state">
          <div class="pulse-ring">
            <div class="pulse-ring-inner">
              <div class="searching-icon">🔍</div>
            </div>
          </div>
          <h3>正在搜索 {{ currentJob?.usernames.join(', ') }}</h3>
          <p>正在遍历 400+ 平台，请稍候...</p>
          <p class="status-note">状态: {{ currentJob?.status }}</p>
          <p class="status-note" v-if="currentJob?.started_at">
            开始时间: {{ new Date(currentJob.started_at).toLocaleString('zh-CN') }}
          </p>
        </div>

        <!-- Completed/Failed Results -->
        <div v-if="currentJob && !isSearching" class="results">
          <div class="results-header">
            <div>
              <h3>查询结果</h3>
              <p class="result-meta">
                用户名: <strong>{{ currentJob.usernames.join(', ') }}</strong> ·
                状态: <span :class="'status-' + currentJob.status">{{ currentJob.status }}</span>
              </p>
              <p class="result-meta" v-if="currentJob.completed_at">
                完成: {{ new Date(currentJob.completed_at).toLocaleString('zh-CN') }}
              </p>
            </div>
            <div class="result-actions">
              <button
                v-if="currentJob.files"
                v-for="(url, username) in currentJob.files"
                :key="username"
                class="btn-download"
                @click="downloadFile(url)"
              >
                📥 下载 {{ username }}.{{ getExt(url) }}
              </button>
              <button class="btn-outline btn-sm" @click="clearJob">清除</button>
            </div>
          </div>

          <!-- Error -->
          <div v-if="currentJob.error" class="error-box">
            <strong>❌ 错误信息</strong>
            <pre>{{ currentJob.error }}</pre>
          </div>

          <!-- Raw Output -->
          <div v-if="currentJob.raw_output" class="output-box">
            <div class="output-header">
              <span>📋 原始输出</span>
              <button class="btn-ghost btn-sm" @click="copyOutput">复制</button>
            </div>
            <pre class="raw-output">{{ currentJob.raw_output }}</pre>
          </div>
        </div>
      </div>
    </main>

    <!-- Site Picker Modal -->
    <div v-if="showSitePicker" class="modal-overlay" @click.self="showSitePicker = false">
      <div class="modal">
        <div class="modal-header">
          <h3>选择要查询的平台</h3>
          <div class="modal-actions">
            <button class="btn-outline btn-sm" @click="selectedSites = [...allSites]">全选</button>
            <button class="btn-outline btn-sm" @click="selectedSites = []">清空</button>
            <button class="btn-primary btn-sm" @click="confirmSites">确认 ({{ selectedSites.length }})</button>
          </div>
        </div>
        <div class="modal-search">
          <input type="text" v-model="siteSearch" placeholder="搜索平台名称..." />
        </div>
        <div class="site-grid">
          <label
            v-for="site in filteredSites"
            :key="site"
            class="site-item"
            :class="{ selected: selectedSites.includes(site) }"
          >
            <input type="checkbox" :value="site" v-model="selectedSites" />
            {{ site }}
          </label>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'

const API_BASE = window.location.origin

export default {
  name: 'App',
  setup() {
    // ── State ──────────────────────────────────
    const usernames = ref([])
    const inputUsername = ref('')
    const selectedPreset = ref('quick')

    const config = reactive({
      tor: false,
      unique_tor: false,
      proxy: '',
      csv: false,
      xlsx: false,
      folder_output: '',
      print_found: true,
      print_all: false,
      browse: false,
      nsfw: false,
      local: false,
      verbose: false,
      json_file: '',
      timeout: 60,
    })

    const sitesInput = ref('')
    const selectedSites = ref([])
    const allSites = ref([])

    const presets = ref([])
    const allJobs = ref([])
    const currentJobId = ref(null)
    const isSearching = computed(() => currentJob.value?.status === 'running' || currentJob.value?.status === 'pending')

    const showSitePicker = ref(false)
    const siteSearch = ref('')
    const showAll = ref(false)
    const collapsedSections = reactive(new Set())

    const toast = reactive({ show: false, message: '', type: 'info' })
    let pollInterval = null

    // ── Computed ───────────────────────────────
    const parsedSites = computed(() => {
      if (!sitesInput.value) return []
      return sitesInput.value.split(/[,，\s]+/).map(s => s.trim()).filter(Boolean)
    })

    const filteredSites = computed(() => {
      if (!siteSearch.value) return allSites.value
      const q = siteSearch.value.toLowerCase()
      return allSites.value.filter(s => s.toLowerCase().includes(q))
    })

    const currentJob = computed(() => allJobs.value.find(j => j.job_id === currentJobId.value) || null)

    // ── Methods ────────────────────────────────
    function addUsername() {
      const val = inputUsername.value.trim().replace(/,+$/, '')
      if (!val) return
      val.split(/[,，\s]+/).forEach(name => {
        const n = name.trim()
        if (n && !usernames.value.includes(n)) usernames.value.push(n)
      })
      inputUsername.value = ''
    }

    function removeUsername(i) { usernames.value.splice(i, 1) }

    function applyPreset(preset) {
      selectedPreset.value = preset.id
      Object.assign(config, preset.config)
      if (preset.config.site) {
        selectedSites.value = [...preset.config.site]
        sitesInput.value = preset.config.site.join(', ')
      } else if (preset.id === 'chinese') {
        selectedSites.value = ['weibo', 'douyin', 'bilibili', 'xiaohongshu', 'zhihu', 'douban', 'taobao']
        sitesInput.value = 'weibo, douyin, bilibili, xiaohongshu, zhihu, douban, taobao'
      }
      showToast(`已应用「${preset.name}」预设`, 'success')
    }

    function toggleSection(key) {
      if (collapsedSections.has(key)) collapsedSections.delete(key)
      else collapsedSections.add(key)
    }

    function confirmSites() {
      sitesInput.value = selectedSites.value.join(', ')
      showSitePicker.value = false
    }

    function selectJob(id) { currentJobId.value = id }
    function clearJob() { currentJobId.value = null }

    function getExt(url) { return url.split('.').pop() }

    async function downloadFile(url) {
      try {
        const a = document.createElement('a')
        a.href = API_BASE + url
        a.download = url.split('/').pop()
        a.click()
        showToast('开始下载...', 'success')
      } catch (e) { showToast('下载失败: ' + e.message, 'error') }
    }

    async function copyOutput() {
      if (!currentJob.value?.raw_output) return
      try {
        await navigator.clipboard.writeText(currentJob.value.raw_output)
        showToast('已复制到剪贴板', 'success')
      } catch { showToast('复制失败', 'error') }
    }

    function showToast(msg, type = 'info') {
      toast.message = msg; toast.type = type; toast.show = true
      setTimeout(() => toast.show = false, 3000)
    }

    async function startSearch() {
      if (!usernames.value.length) { showToast('请先输入用户名', 'error'); return }

      // Update selectedSites from sitesInput
      if (parsedSites.value.length) selectedSites.value = [...parsedSites.value]

      const payload = {
        usernames: usernames.value,
        ...config,
        site: selectedSites.value.length ? selectedSites.value : undefined,
      }

      try {
        const resp = await fetch(`${API_BASE}/api/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        const data = await resp.json()
        if (!resp.ok) throw new Error(data.detail || '请求失败')

        allJobs.value.unshift({ job_id: data.job_id, status: 'pending', usernames: usernames.value })
        currentJobId.value = data.job_id
        showToast('搜索任务已创建，正在查询...', 'success')
        startPolling()
      } catch (e) { showToast('启动失败: ' + e.message, 'error') }
    }

    function startPolling() {
      if (pollInterval) clearInterval(pollInterval)
      pollInterval = setInterval(pollJobs, 2000)
    }

    async function pollJobs() {
      if (!currentJobId.value) { stopPolling(); return }
      try {
        const resp = await fetch(`${API_BASE}/api/jobs/${currentJobId.value}`)
        if (!resp.ok) { stopPolling(); return }
        const data = await resp.json()
        const idx = allJobs.value.findIndex(j => j.job_id === data.job_id)
        if (idx !== -1) allJobs.value[idx] = { ...allJobs.value[idx], ...data }
        if (data.status === 'completed' || data.status === 'failed') {
          stopPolling()
          if (data.status === 'completed') showToast('✅ 查询完成！', 'success')
          else showToast('❌ 查询失败', 'error')
        }
      } catch { stopPolling() }
    }

    function stopPolling() {
      if (pollInterval) { clearInterval(pollInterval); pollInterval = null }
    }

    // ── Init ───────────────────────────────────
    async function init() {
      try {
        const [presetsRes, sitesRes, jobsRes] = await Promise.all([
          fetch(`${API_BASE}/api/presets`).then(r => r.json()).catch(() => ({ presets: [] })),
          fetch(`${API_BASE}/api/sites`).then(r => r.json()).catch(() => ({ sites: [] })),
          fetch(`${API_BASE}/api/jobs`).then(r => r.json()).catch(() => ({ jobs: [] })),
        ])
        presets.value = presetsRes.presets || []
        allSites.value = sitesRes.sites || sitesRes.raw ? extractSitesFromRaw(sitesRes.raw) : []
        allJobs.value = jobsRes.jobs || []

        if (allJobs.value.length) {
          const latest = allJobs.value.find(j => j.status === 'running' || j.status === 'pending')
          if (latest) { currentJobId.value = latest.job_id; startPolling() }
        }
      } catch (e) {
        console.error('Init failed:', e)
      }
    }

    function extractSitesFromRaw(raw) {
      if (typeof raw === 'string') {
        const matches = raw.match(/`?([a-z0-9_-]+)`?/gi)
        if (matches) return [...new Set(matches.map(m => m.replace(/`/gi, '').trim()).filter(s => s.length > 1 && !s.includes(' ')))]
      }
      return []
    }

    onMounted(init)
    onUnmounted(stopPolling)

    return {
      usernames, inputUsername, selectedPreset, config,
      sitesInput, selectedSites, allSites, presets, allJobs, currentJobId,
      isSearching, currentJob, showSitePicker, siteSearch, filteredSites,
      showAll, collapsedSections, toast,
      parsedSites, filteredSites,
      addUsername, removeUsername, applyPreset, toggleSection, confirmSites,
      selectJob, clearJob, getExt, downloadFile, copyOutput, startSearch,
    }
  }
}
</script>

<style>
/* ── Layout ───────────────────────────────── */
.app { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }

.header {
  background: rgba(10,10,15,0.95);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  backdrop-filter: blur(20px);
  position: sticky; top: 0; z-index: 100;
}
.header-inner {
  max-width: 1400px; margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex; align-items: center; justify-content: space-between;
}
.logo { display: flex; align-items: center; gap: 0.75rem; }
.logo-icon { font-size: 2rem; }
.logo h1 { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.5px; }
.logo p { font-size: 0.75rem; color: #64748b; margin-top: -2px; }
.header-actions { display: flex; gap: 0.5rem; }

.main { flex: 1; display: flex; overflow: hidden; max-width: 1400px; width: 100%; margin: 0 auto; }

/* ── Sidebar ───────────────────────────────── */
.sidebar {
  width: 380px; flex-shrink: 0;
  overflow-y: auto; padding: 1rem;
  border-right: 1px solid rgba(255,255,255,0.06);
  display: flex; flex-direction: column; gap: 0.75rem;
}
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

.content { flex: 1; overflow-y: auto; padding: 1.5rem; }

/* ── Panel ─────────────────────────────────── */
.panel {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px; padding: 1rem;
}
.panel-title {
  font-size: 0.875rem; font-weight: 600; margin-bottom: 0.75rem;
  display: flex; align-items: center; gap: 0.5rem;
  color: #94a3b8;
}
.toggle-all { margin-left: auto; font-size: 0.7rem; color: #64748b; cursor: pointer; background: none; border: none; }

/* ── Chip Input ─────────────────────────────── */
.chip-input {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px; padding: 0.5rem; min-height: 60px;
  display: flex; flex-wrap: wrap; gap: 0.35rem; align-items: flex-start;
}
.chip-input input {
  border: none; background: transparent; outline: none;
  color: #e2e8f0; font-size: 0.875rem; min-width: 120px; flex: 1;
}
.chips { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.chip {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white; border-radius: 6px; padding: 3px 10px;
  font-size: 0.8rem; display: flex; align-items: center; gap: 0.35rem;
}
.chip button { background: none; border: none; color: rgba(255,255,255,0.7); cursor: pointer; font-size: 1rem; line-height: 1; padding: 0; }
.chip button:hover { color: white; }
.hint { font-size: 0.72rem; color: #475569; margin-top: 0.4rem; }

/* ── Presets ───────────────────────────────── */
.presets { display: flex; flex-direction: column; gap: 0.4rem; }
.preset-btn {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.5rem 0.75rem; border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.06); background: transparent;
  color: #94a3b8; cursor: pointer; text-align: left; transition: all 0.2s;
}
.preset-btn:hover { background: rgba(255,255,255,0.04); color: #e2e8f0; }
.preset-btn.active { background: rgba(102,126,234,0.15); border-color: rgba(102,126,234,0.4); color: #a5b4fc; }
.preset-icon { font-size: 1.2rem; }
.preset-name { font-size: 0.8rem; font-weight: 600; }
.preset-desc { font-size: 0.7rem; color: #64748b; }

/* ── Config Sections ───────────────────────── */
.config-section {
  border-top: 1px solid rgba(255,255,255,0.04);
  margin-top: 0.5rem; padding-top: 0.5rem;
}
.config-section summary {
  list-style: none; display: flex; align-items: center;
  justify-content: space-between; cursor: pointer;
  font-size: 0.8rem; font-weight: 600; color: #94a3b8;
  padding: 0.25rem 0; user-select: none;
}
.config-section summary::-webkit-details-marker { display: none; }
.arrow { font-size: 0.65rem; }
.config-body { padding: 0.6rem 0 0.25rem; display: flex; flex-direction: column; gap: 0.6rem; }

.field { display: flex; flex-direction: column; gap: 0.25rem; }
.field label { font-size: 0.72rem; color: #64748b; }
.field input {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px; padding: 0.4rem 0.6rem; color: #e2e8f0;
  font-size: 0.8rem; width: 100%; outline: none; transition: border 0.2s;
}
.field input:focus { border-color: rgba(102,126,234,0.5); }
.field input:disabled { opacity: 0.4; cursor: not-allowed; }

.toggle-row {
  display: flex; align-items: center; justify-content: space-between;
  cursor: pointer; font-size: 0.78rem; color: #94a3b8; gap: 0.5rem;
}
.toggle-row input[type="checkbox"] { display: none; }
.toggle-slider {
  width: 36px; height: 20px; background: rgba(255,255,255,0.1);
  border-radius: 10px; position: relative; flex-shrink: 0;
  transition: background 0.2s; cursor: pointer;
}
.toggle-slider::after {
  content: ''; position: absolute; width: 14px; height: 14px;
  background: #94a3b8; border-radius: 50%; top: 3px; left: 3px;
  transition: all 0.2s;
}
.toggle-row input:checked + .toggle-slider { background: rgba(102,126,234,0.4); }
.toggle-row input:checked + .toggle-slider::after { background: #818cf8; transform: translateX(16px); }
.toggle-row input:disabled + .toggle-slider { opacity: 0.3; cursor: not-allowed; }

.site-preview { font-size: 0.72rem; color: #818cf8; word-break: break-all; }

/* ── Buttons ───────────────────────────────── */
.btn-ghost {
  padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.8rem;
  color: #64748b; background: transparent; border: 1px solid rgba(255,255,255,0.08);
  cursor: pointer; text-decoration: none; transition: all 0.2s;
}
.btn-ghost:hover { color: #e2e8f0; border-color: rgba(255,255,255,0.2); }
.btn-outline {
  padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.8rem;
  color: #94a3b8; background: transparent;
  border: 1px solid rgba(255,255,255,0.1); cursor: pointer; transition: all 0.2s;
}
.btn-outline:hover { background: rgba(255,255,255,0.04); color: #e2e8f0; }
.btn-primary { background: #667eea; color: white; border: none; cursor: pointer; }
.btn-primary:hover { background: #5a67d8; }
.btn-sm { font-size: 0.72rem; padding: 0.25rem 0.6rem; }

.btn-search {
  width: 100%; padding: 0.875rem; border-radius: 10px; font-size: 1rem;
  font-weight: 700; background: linear-gradient(135deg, #667eea, #764ba2);
  color: white; border: none; cursor: pointer; transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(102,126,234,0.3);
}
.btn-search:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(102,126,234,0.4); }
.btn-search:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.btn-download {
  padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.78rem;
  background: rgba(102,126,234,0.15); border: 1px solid rgba(102,126,234,0.3);
  color: #a5b4fc; cursor: pointer; transition: all 0.2s;
}
.btn-download:hover { background: rgba(102,126,234,0.25); }

/* ── Jobs Bar ──────────────────────────────── */
.jobs-bar { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
.job-chip {
  display: flex; align-items: center; gap: 0.35rem;
  padding: 0.3rem 0.75rem; border-radius: 20px; font-size: 0.78rem;
  cursor: pointer; background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08); transition: all 0.2s;
}
.job-chip:hover { background: rgba(255,255,255,0.08); }
.job-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.job-chip.pending .job-dot { background: #fbbf24; }
.job-chip.running .job-dot { background: #60a5fa; animation: pulse 1s infinite; }
.job-chip.completed .job-dot { background: #34d399; }
.job-chip.failed .job-dot { background: #f87171; }

@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

/* ── Empty State ───────────────────────────── */
.empty-state { text-align: center; padding: 3rem 1rem; color: #475569; }
.empty-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.empty-state h3 { font-size: 1.1rem; color: #64748b; margin-bottom: 0.35rem; }
.empty-state p { font-size: 0.85rem; }
.feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 2rem; text-align: left; }
.feature-card {
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px; padding: 1rem; display: flex; gap: 0.75rem; align-items: flex-start;
}
.feature-card span { font-size: 1.5rem; }
.feature-card h4 { font-size: 0.8rem; font-weight: 600; color: #e2e8f0; margin-bottom: 0.15rem; }
.feature-card p { font-size: 0.72rem; color: #475569; }

/* ── Running State ─────────────────────────── */
.running-state { text-align: center; padding: 4rem 1rem; }
.pulse-ring { width: 120px; height: 120px; margin: 0 auto 1.5rem; position: relative; }
.pulse-ring-inner {
  width: 80px; height: 80px; border-radius: 50%;
  background: rgba(102,126,234,0.15); border: 2px solid rgba(102,126,234,0.4);
  display: flex; align-items: center; justify-content: center;
  margin: auto; position: relative; z-index: 1;
}
.pulse-ring::before, .pulse-ring::after {
  content: ''; position: absolute; border-radius: 50%;
  border: 2px solid rgba(102,126,234,0.2); animation: ripple 2s ease-out infinite;
}
.pulse-ring::after { animation-delay: 1s; }
@keyframes ripple { 0% { width: 80px; height: 80px; top: 20px; left: 20px; opacity: 0.8; } 100% { width: 160px; height: 160px; top: -20px; left: -20px; opacity: 0; } }
.searching-icon { font-size: 2rem; animation: spin 2s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.running-state h3 { font-size: 1.2rem; color: #e2e8f0; margin-bottom: 0.5rem; }
.running-state p { color: #64748b; font-size: 0.85rem; }
.status-note { font-size: 0.75rem; color: #475569; margin-top: 0.25rem; }

/* ── Results ───────────────────────────────── */
.results-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 1.5rem; gap: 1rem;
}
.results-header h3 { font-size: 1.2rem; margin-bottom: 0.25rem; }
.result-meta { font-size: 0.78rem; color: #64748b; }
.result-meta strong { color: #a5b4fc; }
.result-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: flex-start; }
.status-pending { color: #fbbf24; }
.status-running { color: #60a5fa; }
.status-completed { color: #34d399; }
.status-failed { color: #f87171; }

.error-box {
  background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);
  border-radius: 10px; padding: 1rem; margin-bottom: 1rem;
}
.error-box strong { color: #f87171; font-size: 0.85rem; }
.error-box pre { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #fca5a5; margin-top: 0.5rem; white-space: pre-wrap; word-break: break-all; max-height: 300px; overflow-y: auto; }

.output-box {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px; overflow: hidden;
}
.output-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.6rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.04);
  font-size: 0.78rem; color: #64748b;
}
.raw-output {
  font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
  color: #94a3b8; padding: 1rem; white-space: pre-wrap;
  word-break: break-all; max-height: 500px; overflow-y: auto;
  line-height: 1.8;
}

/* ── Modal ─────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.7);
  backdrop-filter: blur(4px); z-index: 1000;
  display: flex; align-items: center; justify-content: center; padding: 1rem;
}
.modal {
  background: #111118; border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px; width: 100%; max-width: 700px; max-height: 80vh;
  display: flex; flex-direction: column; overflow: hidden;
}
.modal-header {
  padding: 1rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;
}
.modal-header h3 { font-size: 1rem; font-weight: 600; }
.modal-actions { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.modal-search { padding: 0.75rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.04); }
.modal-search input {
  width: 100%; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px; padding: 0.5rem 0.75rem; color: #e2e8f0; font-size: 0.85rem; outline: none;
}
.modal-search input:focus { border-color: rgba(102,126,234,0.5); }
.site-grid {
  overflow-y: auto; padding: 0.75rem 1.25rem;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 0.4rem;
}
.site-item {
  padding: 0.35rem 0.6rem; border-radius: 6px; font-size: 0.75rem;
  cursor: pointer; transition: all 0.15s; color: #64748b;
  border: 1px solid transparent; display: flex; align-items: center; gap: 0.35rem;
}
.site-item input { display: none; }
.site-item:hover { background: rgba(255,255,255,0.04); color: #94a3b8; }
.site-item.selected { background: rgba(102,126,234,0.12); border-color: rgba(102,126,234,0.3); color: #a5b4fc; }

/* ── Toast ─────────────────────────────────── */
.toast {
  position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%);
  padding: 0.6rem 1.25rem; border-radius: 8px; font-size: 0.82rem;
  z-index: 2000; animation: slideUp 0.3s ease;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.toast.info { background: rgba(100,116,139,0.9); color: white; }
.toast.success { background: rgba(52,211,153,0.9); color: white; }
.toast.error { background: rgba(248,113,113,0.9); color: white; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(10px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

/* ── Responsive ─────────────────────────────── */
@media (max-width: 768px) {
  .main { flex-direction: column; }
  .sidebar { width: 100%; border-right: none; border-bottom: 1px solid rgba(255,255,255,0.06); max-height: 50vh; }
  .feature-grid { grid-template-columns: 1fr; }
}
