<template>
  <div class="page-wrap">
    <el-card shadow="hover" class="card">
      <div class="header">
        <h3>健康指标录入</h3>
        <div>
          <el-button type="primary" @click="fetchMetrics" :loading="loading">刷新</el-button>
        </div>
      </div>

      <el-form :inline="true" :model="form" class="form">
        <el-form-item label="时间">
          <el-date-picker v-model="form.datetime" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" placeholder="选择类型" @change="applyDefaultUnit">
            <el-option label="体重" value="weight" />
            <el-option label="BMI" value="bmi" />
            <el-option label="心率" value="heart_rate" />
            <el-option label="收缩压" value="bp_systolic" />
            <el-option label="舒张压" value="bp_diastolic" />
            <el-option label="步数" value="steps" />
            <el-option label="睡眠时长" value="sleep_hours" />
            <el-option label="血糖" value="blood_glucose" />
            <el-option label="甘油三酯" value="triglyceride" />
            <el-option label="HDL" value="hdl" />
            <el-option label="LDL" value="ldl" />
            <el-option label="体脂率%" value="body_fat" />
          </el-select>
        </el-form-item>
        <el-form-item label="数值">
          <el-input v-model.number="form.value" type="number" placeholder="输入数值" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="form.unit" placeholder="可选" />
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="addMetric" :loading="adding">添加</el-button>
        </el-form-item>
      </el-form>

      <div class="filter">
        <el-form :inline="true" :model="query">
          <el-form-item label="类型">
            <el-select v-model="query.type" placeholder="全部" clearable>
              <el-option label="体重" value="weight" />
              <el-option label="BMI" value="bmi" />
              <el-option label="心率" value="heart_rate" />
              <el-option label="收缩压" value="bp_systolic" />
              <el-option label="舒张压" value="bp_diastolic" />
              <el-option label="步数" value="steps" />
              <el-option label="睡眠时长" value="sleep_hours" />
              <el-option label="血糖" value="blood_glucose" />
              <el-option label="甘油三酯" value="triglyceride" />
              <el-option label="HDL" value="hdl" />
              <el-option label="LDL" value="ldl" />
              <el-option label="体脂率%" value="body_fat" />
            </el-select>
          </el-form-item>
          <el-form-item label="起止日期">
            <el-date-picker v-model="query.range" type="daterange" value-format="YYYY-MM-DD" start-placeholder="开始日期" end-placeholder="结束日期" />
          </el-form-item>
          <el-form-item>
            <el-button @click="fetchMetrics">查询</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="metrics" stripe class="table" max-height="480">
        <el-table-column prop="date" label="日期" width="140" />
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="type" label="类型" width="160" />
        <el-table-column prop="value" label="值" width="120" />
        <el-table-column prop="unit" label="单位" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Metrics',
  data() {
    return {
      loading: false,
      adding: false,
      metrics: [],
      form: {
        datetime: new Date().toISOString().slice(0,19),
        type: 'weight',
        value: null,
        unit: 'kg'
      },
      query: {
        type: '',
        range: []
      }
    }
  },
  methods: {
    applyDefaultUnit() {
      const map = {
        weight: 'kg',
        bmi: '',
        heart_rate: 'bpm',
        bp_systolic: 'mmHg',
        bp_diastolic: 'mmHg',
        steps: 'steps',
        sleep_hours: 'h',
        blood_glucose: 'mmol/L',
        triglyceride: 'mmol/L',
        hdl: 'mmol/L',
        ldl: 'mmol/L',
        body_fat: '%'
      }
      this.form.unit = map[this.form.type] ?? ''
    },
    async fetchMetrics() {
      this.loading = true
      try {
        const params = {}
        if (this.query.type) params.type = this.query.type
        if (this.query.range && this.query.range.length === 2) {
          params.start = this.query.range[0]
          params.end = this.query.range[1]
        }
        const { data } = await axios.get('/api/health-assistant/metrics', { params })
        this.metrics = data.slice(-200).reverse()
      } catch (e) {
        this.$message.error('获取指标失败')
      } finally {
        this.loading = false
      }
    },
    async addMetric() {
      if (!this.form.type || this.form.value === null) {
        this.$message.warning('请填写完整')
        return
      }
      this.adding = true
      try {
        const payload = {
          type: this.form.type,
          value: Number(this.form.value),
          unit: this.form.unit || null,
          timestamp: this.form.datetime
        }
        await axios.post('/api/health-assistant/metrics', payload)
        this.$message.success('添加成功')
        this.fetchMetrics()
      } catch (e) {
        this.$message.error('添加失败')
      } finally {
        this.adding = false
      }
    }
  },
  mounted() {
    this.fetchMetrics()
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
