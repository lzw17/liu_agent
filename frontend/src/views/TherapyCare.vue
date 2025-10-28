<template>
  <div class="page-wrap">
    <el-card shadow="hover" class="card">
      <div class="header">
        <h3>养身理疗</h3>
        <div>
          <el-button type="primary" @click="fetchTherapies" :loading="loading">刷新</el-button>
          <el-button type="success" plain @click="generateTherapies" :loading="generating" style="margin-left:8px;">一键生成今日理疗</el-button>
        </div>
      </div>

      <el-form :inline="true" :model="form" class="form">
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="项目">
          <el-input v-model="form.name" placeholder="如：艾灸/推拿/热敷/泡脚" />
        </el-form-item>
        <el-form-item label="时长(分钟)">
          <el-input v-model.number="form.duration_min" type="number" placeholder="可选" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" placeholder="可选" />
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="addTherapy" :loading="adding">添加</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="therapies" stripe class="table" max-height="60vh">
        <el-table-column prop="date" label="日期" width="140" />
        <el-table-column prop="name" label="项目" width="200" />
        <el-table-column prop="duration_min" label="时长(分钟)" width="140" />
        <el-table-column prop="notes" label="备注" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-popconfirm title="确定删除该理疗吗？" @confirm="deleteTherapy(row)">
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
  name: 'TherapyCare',
  data() {
    return {
      loading: false,
      generating: false,
      adding: false,
      therapies: [],
      form: {
        date: new Date().toISOString().slice(0,10),
        name: '',
        duration_min: null,
        notes: ''
      }
    }
  },
  methods: {
    async fetchTherapies() {
      this.loading = true
      try {
        const { data } = await axios.get('/api/health-assistant/therapies')
        this.therapies = data
      } catch (e) {
        this.$message.error('获取理疗记录失败')
      } finally {
        this.loading = false
      }
    },
    async generateTherapies() {
      this.generating = true
      try {
        await axios.post('/api/health-assistant/generate/therapies')
        this.$message.success('已生成今日理疗建议')
        this.fetchTherapies()
      } catch (e) {
        this.$message.error('生成失败')
      } finally {
        this.generating = false
      }
    },
    async addTherapy() {
      if (!this.form.name) {
        this.$message.warning('请输入理疗项目')
        return
      }
      this.adding = true
      try {
        await axios.post('/api/health-assistant/therapies', this.form)
        this.$message.success('添加成功')
        this.form.name = ''
        this.form.duration_min = null
        this.form.notes = ''
        this.fetchTherapies()
      } catch (e) {
        this.$message.error('添加失败')
      } finally {
        this.adding = false
      }
    },
    async deleteTherapy(row) {
      try {
        await axios.delete(`/api/health-assistant/therapies/${row.id}`)
        this.$message.success('已删除')
        this.fetchTherapies()
      } catch (e) {
        this.$message.error('删除失败')
      }
    }
  },
  mounted() {
    this.fetchTherapies()
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
