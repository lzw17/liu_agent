<template>
  <div class="page-wrap">
    <el-card shadow="hover" class="card">
      <div class="header">
        <h3>后台信息（个人档案）</h3>
        <div>
          <el-button type="primary" @click="loadProfile" :loading="loading">刷新</el-button>
          <el-button type="success" @click="saveProfile" :loading="saving">保存</el-button>
        </div>
      </div>

      <el-form :model="form" label-width="120px" class="form">
        <el-form-item label="用户ID">
          <el-input v-model="form.id" placeholder="如：user-1" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender" placeholder="选择性别">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input v-model.number="form.age" type="number" />
        </el-form-item>
        <el-form-item label="身高(cm)">
          <el-input v-model.number="form.height_cm" type="number" />
        </el-form-item>
        <el-form-item label="体重(kg)">
          <el-input v-model.number="form.weight_kg" type="number" />
        </el-form-item>
        <el-form-item label="慢性病史">
          <el-select v-model="form.conditions" multiple filterable allow-create default-first-option placeholder="输入并回车添加">
            <el-option v-for="item in form.conditions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="过敏史">
          <el-select v-model="form.allergies" multiple filterable allow-create default-first-option placeholder="输入并回车添加">
            <el-option v-for="item in form.allergies" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="偏好/目标">
          <el-select v-model="form.preferences" multiple filterable allow-create default-first-option placeholder="输入并回车添加">
            <el-option v-for="item in form.preferences" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserProfile',
  data() {
    return {
      loading: false,
      saving: false,
      form: {
        id: 'user-1',
        name: '',
        gender: '',
        age: null,
        height_cm: null,
        weight_kg: null,
        conditions: [],
        allergies: [],
        preferences: []
      }
    }
  },
  methods: {
    async loadProfile() {
      this.loading = true
      try {
        const { data } = await axios.get('/api/health-assistant/profile')
        if (data) this.form = data
      } catch (e) {
        this.$message.warning('尚未设置个人档案')
      } finally {
        this.loading = false
      }
    },
    async saveProfile() {
      if (!this.form.id || !this.form.name) {
        this.$message.warning('请至少填写 用户ID 和 姓名')
        return
      }
      this.saving = true
      try {
        await axios.post('/api/health-assistant/profile', this.form)
        this.$message.success('保存成功')
      } catch (e) {
        this.$message.error('保存失败')
      } finally {
        this.saving = false
      }
    }
  },
  mounted() {
    this.loadProfile()
  }
}
</script>

<style scoped>
.page-wrap { padding: 20px; }
.header { display:flex; align-items:center; justify-content:space-between; margin-bottom: 12px; }
.form { background: #fff; padding: 8px; border-radius: 4px; }
.card { background: #fff; }
</style>
