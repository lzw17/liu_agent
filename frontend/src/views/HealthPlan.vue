<template>
  <div class="page-wrap">
    <el-card shadow="hover" class="card">
      <div class="header">
        <h3>我的计划</h3>
        <div>
          <el-button type="primary" @click="fetchPlans" :loading="loading">刷新</el-button>
          <el-button type="success" plain @click="generatePlan" :loading="generating" style="margin-left:8px;">一键生成今日计划</el-button>
          <el-button type="warning" plain @click="adjustPlans" :loading="adjusting" style="margin-left:8px;">智能调整</el-button>
        </div>
      </div>
      <el-form :inline="true" :model="form" class="form">
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="类别">
          <el-select v-model="form.category" placeholder="请选择">
            <el-option label="运动" value="运动" />
            <el-option label="饮食" value="饮食" />
            <el-option label="休息" value="休息" />
            <el-option label="检查" value="检查" />
            <el-option label="理疗" value="理疗" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.title" placeholder="如：晚饭后慢跑30分钟" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.done">已完成</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="addPlan" :loading="adding">添加</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="plans" stripe class="table">
        <el-table-column prop="date" label="日期" width="140" />
        <el-table-column prop="category" label="类别" width="120" />
        <el-table-column prop="title" label="计划内容" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.done ? 'success' : 'info'">{{ row.done ? '已完成' : '未完成' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HealthPlan',
  data() {
    return {
      loading: false,
      generating: false,
      adjusting: false,
      adding: false,
      plans: [],
      form: {
        date: new Date().toISOString().slice(0,10),
        category: '运动',
        title: '',
        done: false
      }
    }
  },
  methods: {
    async fetchPlans() {
      this.loading = true
      try {
        const { data } = await axios.get('/api/health-assistant/plans')
        this.plans = data
      } catch (e) {
        this.$message.error('获取计划失败')
      } finally {
        this.loading = false
      }
    },
    async generatePlan() {
      this.generating = true
      try {
        await axios.post('/api/health-assistant/generate/plan')
        this.$message.success('已生成今日计划')
        this.fetchPlans()
      } catch (e) {
        this.$message.error('生成失败')
      } finally {
        this.generating = false
      }
    },
    async adjustPlans() {
      this.adjusting = true
      try {
        await axios.post('/api/health-assistant/adjust')
        this.$message.success('已根据评分智能调整计划')
        this.fetchPlans()
      } catch (e) {
        this.$message.error('调整失败')
      } finally {
        this.adjusting = false
      }
    },
    async addPlan() {
      if (!this.form.title) {
        this.$message.warning('请输入计划内容')
        return
      }
      this.adding = true
      try {
        await axios.post('/api/health-assistant/plans', this.form)
        this.$message.success('添加成功')
        this.form.title = ''
        this.fetchPlans()
      } catch (e) {
        this.$message.error('添加失败')
      } finally {
        this.adding = false
      }
    }
  },
  mounted() {
    this.fetchPlans()
  }
}
</script>

<style scoped>
.page-wrap { padding: 20px; }
.header { display:flex; align-items:center; justify-content:space-between; margin-bottom: 12px; }
.form { margin-bottom: 12px; }
.table { margin-top: 8px; }
.card { background: #fff; }
</style>
