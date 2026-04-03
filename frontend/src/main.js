import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')

// Expose VITE_API_BASE globally for App.vue
window.API_BASE = import.meta.env.VITE_API_BASE || window.location.origin
