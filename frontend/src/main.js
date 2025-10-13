import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import KnowledgeBase from './views/KnowledgeBase.vue'
import ChatSimple from './views/ChatSimple.vue'
import IntegratedChat from './views/IntegratedChat.vue'

const routes = [
  { path: '/', redirect: '/chat' },
  { path: '/chat', component: IntegratedChat },
  { path: '/knowledge', component: KnowledgeBase },
  { path: '/chat-simple', component: ChatSimple }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app')
