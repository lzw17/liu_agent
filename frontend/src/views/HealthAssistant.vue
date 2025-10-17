<template>
  <div class="assistant-wrap">
    <el-row :gutter="20" class="greeting-row">
      <el-col :span="16">
        <el-card shadow="hover" class="greeting-card">
          <div class="greeting">
            <img src="/yuanqi.jpg" class="avatar" alt="元启康健" />
            <div>
              <h2>您好，{{ timeGreeting }}！我是您的 AI 个人健康助理 <span class="name">小元</span></h2>
              <p>智能体名称：<strong>元启康健AI智能健康小助手</strong></p>
              <p>有什么想了解的健康小知识都可以问我，请问有什么可以帮您？~</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="today-plan-card">
          <div class="tp-header">
            <span>今日计划</span>
            <el-button type="primary" size="small" @click="fetchTodayPlan" :loading="loadingToday">刷新</el-button>
          </div>
          <el-empty v-if="todayPlan.length === 0" description="今日暂无计划" />
          <el-timeline v-else class="plan-timeline">
            <el-timeline-item v-for="p in todayPlan" :key="p.id" :type="p.done ? 'success' : 'primary'" :hollow="!p.done">
              <div class="plan-item">
                <el-tag size="small" type="info">{{ p.category }}</el-tag>
                <span class="plan-title" :class="{done: p.done}">{{ p.title }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
        <el-card shadow="hover" class="score-card" style="margin-top: 12px;">
          <div class="tp-header">
            <span>今日健康评分</span>
            <el-button type="primary" size="small" @click="fetchScore" :loading="loadingScore">刷新</el-button>
          </div>
          <div v-if="!score" style="color:#909399;">暂无评分数据</div>
          <div v-else class="score-wrap">
            <div class="score-total">{{ score.total }}</div>
            <div class="score-subs">
              <el-tag type="success" size="small">BMI {{ score.subs?.bmi ?? '-' }}</el-tag>
              <el-tag type="warning" size="small">心血管 {{ score.subs?.cardio ?? '-' }}</el-tag>
              <el-tag type="info" size="small">睡眠 {{ score.subs?.sleep ?? '-' }}</el-tag>
              <el-tag type="primary" size="small">活动 {{ score.subs?.activity ?? '-' }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="quick-row">
      <el-col :span="4">
        <el-card class="quick-card" shadow="hover" @click="$router.push('/assistant/plan')">
          <div class="qc">
            <el-icon class="icon"><Calendar /></el-icon>
            <div>我的计划</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="quick-card" shadow="hover" @click="$router.push('/assistant/checkin')">
          <div class="qc">
            <el-icon class="icon"><Finished /></el-icon>
            <div>健康打卡</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="quick-card" shadow="hover" @click="$router.push('/assistant/recipes')">
          <div class="qc">
            <el-icon class="icon"><Food /></el-icon>
            <div>营养食谱</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="quick-card" shadow="hover" @click="$router.push('/assistant/therapy')">
          <div class="qc">
            <el-icon class="icon"><MagicStick /></el-icon>
            <div>养身理疗</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="quick-card" shadow="hover" @click="$router.push('/assistant/profile')">
          <div class="qc">
            <el-icon class="icon"><User /></el-icon>
            <div>后台信息</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="quick-card" shadow="hover" @click="$router.push('/assistant/metrics')">
          <div class="qc">
            <el-icon class="icon"><Histogram /></el-icon>
            <div>健康指标</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="quick-card" shadow="hover" @click="$router.push('/assistant/analytics')">
          <div class="qc">
            <el-icon class="icon"><DataAnalysis /></el-icon>
            <div>数据分析</div>
          </div>
        </el-card>
      </el-col>
      
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HealthAssistant',
  data() {
    return {
      todayPlan: [],
      loadingToday: false,
      loadingScore: false,
      score: null
    }
  },
  computed: {
    timeGreeting() {
      const h = new Date().getHours()
      if (h < 12) return '上午好'
      if (h < 18) return '下午好'
      return '晚上好'
    }
  },
  methods: {
    async fetchTodayPlan() {
      this.loadingToday = true
      try {
        const { data } = await axios.get('/api/health-assistant/today-plan')
        this.todayPlan = data
      } catch (e) {
        this.$message.error('获取今日计划失败')
      } finally {
        this.loadingToday = false
      }
    },
    async fetchScore() {
      this.loadingScore = true
      try {
        const { data } = await axios.get('/api/health-assistant/score')
        this.score = data
      } catch (e) {
        this.$message.error('获取评分失败')
      } finally {
        this.loadingScore = false
      }
    }
  },
  mounted() {
    this.fetchTodayPlan()
    this.fetchScore()
  }
}
</script>

<style scoped>
.assistant-wrap {
  padding: 20px;
}
.greeting-card {
  background: linear-gradient(135deg, #eef5ff 0%, #ffffff 100%);
}
.greeting {
  display: flex;
  gap: 16px;
  align-items: center;
}
.avatar {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.name { color: #1e80ff; }
.today-plan-card .tp-header{
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}
.score-wrap{ display:flex; align-items:center; gap:12px; }
.score-total{ font-size: 28px; font-weight: 800; color:#1e80ff; }
.plan-timeline { margin-top: 10px; }
.plan-item { display: flex; align-items: center; gap: 8px; }
.plan-title { font-weight: 500; }
.plan-title.done { text-decoration: line-through; color: #909399; }
.quick-row{ margin-top: 20px; }
.quick-card{ cursor:pointer; text-align:center; background: #ffffff; }
.qc{ display:flex; flex-direction:column; align-items:center; gap:8px; padding: 24px 0; color:#1e80ff }
.icon{ font-size: 28px; }
</style>
