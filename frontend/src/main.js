import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import KnowledgeBase from './views/KnowledgeBase.vue'
import ChatSimple from './views/ChatSimple.vue'
import IntegratedChat from './views/IntegratedChat.vue'
import HealthAssistant from './views/HealthAssistant.vue'
import HealthPlan from './views/HealthPlan.vue'
import HealthCheckin from './views/HealthCheckin.vue'
import NutritionRecipes from './views/NutritionRecipes.vue'
import TherapyCare from './views/TherapyCare.vue'
import UserProfile from './views/UserProfile.vue'
import Metrics from './views/Metrics.vue'
import Analytics from './views/Analytics.vue'

const routes = [
  { path: '/', redirect: '/assistant' },
  { path: '/chat', component: IntegratedChat },
  { path: '/knowledge', component: KnowledgeBase },
  { path: '/chat-simple', component: ChatSimple },
  { path: '/assistant', component: HealthAssistant },
  { path: '/assistant/plan', component: HealthPlan },
  { path: '/assistant/checkin', component: HealthCheckin },
  { path: '/assistant/recipes', component: NutritionRecipes },
  { path: '/assistant/therapy', component: TherapyCare },
  { path: '/assistant/profile', component: UserProfile },
  { path: '/assistant/metrics', component: Metrics },
  { path: '/assistant/analytics', component: Analytics }
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
