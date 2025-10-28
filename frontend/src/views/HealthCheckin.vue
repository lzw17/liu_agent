<template>
  <div class="page-wrap">
    <el-card shadow="hover" class="card">
      <div class="header">
        <h3>健康打卡</h3>
        <div>
          <el-button type="primary" @click="fetchCheckins" :loading="loading">刷新</el-button>
        </div>
      </div>

      <el-form :inline="true" :model="form" class="form">
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" placeholder="选择类型">
            <el-option label="体重" value="体重" />
            <el-option label="步数" value="步数" />
            <el-option label="血压" value="血压" />
            <el-option label="睡眠" value="睡眠" />
          </el-select>
        </el-form-item>
        <el-form-item label="值">
          <el-input v-model="form.value" placeholder="如：68.5kg / 8000步 / 120-80 / 7.5小时" />
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="addCheckin" :loading="adding">打卡</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="checkins" stripe class="table" max-height="60vh">
        <el-table-column prop="date" label="日期" width="140" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="value" label="值" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-popconfirm title="确定删除该记录吗？" @confirm="deleteCheckin(row)">
              <template #reference>
                <el-button type="danger" text size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HealthCheckin',
  data() {
    return {
      loading: false,
      adding: false,
      checkins: [],
      form: {
        date: new Date().toISOString().slice(0,10),
        type: '体重',
        value: ''
      }
    }
  },
  methods: {
    async fetchCheckins() {
      this.loading = true
      try {
        const { data } = await axios.get('/api/health-assistant/checkins')
        this.checkins = data
      } catch (e) {
        this.$message.error('获取打卡记录失败')
      } finally {
        this.loading = false
      }
    },
    async addCheckin() {
      if (!this.form.value) {
        this.$message.warning('请输入打卡值')
        return
      }
      this.adding = true
      try {
        await axios.post('/api/health-assistant/checkins', this.form)
        this.$message.success('打卡成功')
        this.form.value = ''
        this.fetchCheckins()
      } catch (e) {
        this.$message.error('打卡失败')
      } finally {
        this.adding = false
      }
    },
    async deleteCheckin(row) {
      try {
        await axios.delete(`/api/health-assistant/checkins/${row.id}`)
        this.$message.success('已删除')
        this.fetchCheckins()
      } catch (e) {
        this.$message.error('删除失败')
      }
    }
  },
  mounted() {
    this.fetchCheckins()
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
