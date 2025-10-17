<template>
  <div class="page-wrap">
    <el-card shadow="hover" class="card">
      <div class="header">
        <h3>健康数据分析</h3>
        <div class="actions">
          <el-select v-model="types" multiple placeholder="选择指标" style="min-width: 300px">
            <el-option v-for="opt in typeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-date-picker v-model="range" type="daterange" value-format="YYYY-MM-DD" start-placeholder="开始日期" end-placeholder="结束日期" />
          <el-button @click="refresh">查询</el-button>
          <el-button @click="lastNDays(7)" type="primary" plain>最近7天</el-button>
          <el-button @click="lastNDays(30)" type="primary" plain>最近30天</el-button>
        </div>
      </div>

      <div class="charts">
        <el-card shadow="never" class="chart-card">
          <div class="chart-title">指标曲线</div>
          <div ref="metricsRef" class="chart"></div>
        </el-card>
        <el-card shadow="never" class="chart-card">
          <div class="chart-title">健康评分趋势</div>
          <div ref="scoreRef" class="chart"></div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  name: 'Analytics',
  data() {
    const end = new Date()
    const start = new Date()
    start.setDate(end.getDate() - 30)
    return {
      metricsChart: null,
      scoreChart: null,
      range: [start.toISOString().slice(0,10), end.toISOString().slice(0,10)],
      types: ['weight','bmi','heart_rate','bp_systolic','bp_diastolic','steps','sleep_hours'],
      typeOptions: [
        { label: '体重', value: 'weight' },
        { label: 'BMI', value: 'bmi' },
        { label: '心率', value: 'heart_rate' },
        { label: '收缩压', value: 'bp_systolic' },
        { label: '舒张压', value: 'bp_diastolic' },
        { label: '步数', value: 'steps' },
        { label: '睡眠时长', value: 'sleep_hours' },
        { label: '血糖', value: 'blood_glucose' },
        { label: '甘油三酯', value: 'triglyceride' },
        { label: 'HDL', value: 'hdl' },
        { label: 'LDL', value: 'ldl' },
        { label: '体脂率%', value: 'body_fat' }
      ]
    }
  },
  methods: {
    async refresh() {
      await Promise.all([this.loadSeries(), this.loadScoreHistory()])
    },
    lastNDays(n){
      const end = new Date()
      const start = new Date()
      start.setDate(end.getDate() - n)
      this.range = [start.toISOString().slice(0,10), end.toISOString().slice(0,10)]
      this.refresh()
    },
    async loadSeries() {
      if (!this.metricsChart) {
        this.metricsChart = echarts.init(this.$refs.metricsRef)
      }
      const params = {
        types: this.types.join(','),
        start: this.range?.[0],
        end: this.range?.[1]
      }
      const { data } = await axios.get('/api/health-assistant/metrics/series', { params })
      const datesSet = new Set()
      this.types.forEach(t => {
        (data[t]||[]).forEach(pt => datesSet.add(pt.date))
      })
      const dates = Array.from(datesSet).sort()
      const series = this.types.map(t => ({
        name: t,
        type: 'line',
        showSymbol: false,
        data: dates.map(d => {
          const found = (data[t]||[]).find(x => x.date === d)
          return found ? found.value : null
        })
      }))
      this.metricsChart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: this.types },
        xAxis: { type: 'category', data: dates },
        yAxis: { type: 'value', scale: true },
        grid: { left: 40, right: 20, bottom: 40, top: 40 },
        series
      })
    },
    async loadScoreHistory() {
      if (!this.scoreChart) {
        this.scoreChart = echarts.init(this.$refs.scoreRef)
      }
      const days = 90
      const { data } = await axios.get('/api/health-assistant/score/history', { params: { days } })
      const dates = data.map(x => x.date)
      const total = data.map(x => x.total)
      this.scoreChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: dates },
        yAxis: { type: 'value', min: 0, max: 100 },
        grid: { left: 40, right: 20, bottom: 40, top: 40 },
        series: [{ name: '总分', type: 'line', areaStyle: {}, data: total, smooth: true }]
      })
    }
  },
  mounted() {
    this.refresh()
    window.addEventListener('resize', () => {
      this.metricsChart && this.metricsChart.resize()
      this.scoreChart && this.scoreChart.resize()
    })
  }
}
</script>

<style scoped>
.page-wrap { padding: 20px; }
.header { display:flex; align-items:center; justify-content:space-between; margin-bottom: 12px; gap: 12px; }
.actions { display:flex; gap: 10px; align-items: center; }
.charts { display: grid; grid-template-columns: 1fr; gap: 16px; }
.chart-card { background: #fff; }
.chart { height: 360px; width: 100%; }
.chart-title { margin-bottom: 8px; color: #666; font-weight: 600; }
.card { background: #fff; }
</style>
