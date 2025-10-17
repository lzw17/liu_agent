<template>
  <div class="page-wrap">
    <el-card shadow="hover" class="card">
      <div class="header">
        <h3>营养食谱</h3>
        <div>
          <el-button type="primary" @click="fetchRecipes" :loading="loading">刷新</el-button>
          <el-button type="success" plain @click="generateRecipes" :loading="generating" style="margin-left:8px;">一键生成今日食谱</el-button>
        </div>
      </div>

      <el-form :inline="true" :model="form" class="form">
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="餐别">
          <el-select v-model="form.meal_type" placeholder="选择餐别">
            <el-option label="早餐" value="早餐" />
            <el-option label="午餐" value="午餐" />
            <el-option label="晚餐" value="晚餐" />
            <el-option label="加餐" value="加餐" />
          </el-select>
        </el-form-item>
        <el-form-item label="菜品">
          <el-input v-model="form.name" placeholder="如：清蒸鱼/西蓝花炒鸡胸" />
        </el-form-item>
        <el-form-item label="热量(kcal)">
          <el-input v-model.number="form.calories" type="number" placeholder="可选" />
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="addRecipe" :loading="adding">添加</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="recipes" stripe class="table">
        <el-table-column prop="date" label="日期" width="140" />
        <el-table-column prop="meal_type" label="餐别" width="120" />
        <el-table-column prop="name" label="菜品" />
        <el-table-column prop="calories" label="热量(kcal)" width="140" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'NutritionRecipes',
  data() {
    return {
      loading: false,
      generating: false,
      adding: false,
      recipes: [],
      form: {
        date: new Date().toISOString().slice(0,10),
        meal_type: '早餐',
        name: '',
        calories: null
      }
    }
  },
  methods: {
    async fetchRecipes() {
      this.loading = true
      try {
        const { data } = await axios.get('/api/health-assistant/recipes')
        this.recipes = data
      } catch (e) {
        this.$message.error('获取食谱失败')
      } finally {
        this.loading = false
      }
    },
    async generateRecipes() {
      this.generating = true
      try {
        await axios.post('/api/health-assistant/generate/recipes')
        this.$message.success('已生成今日食谱')
        this.fetchRecipes()
      } catch (e) {
        this.$message.error('生成失败')
      } finally {
        this.generating = false
      }
    },
    async addRecipe() {
      if (!this.form.name) {
        this.$message.warning('请输入菜品名称')
        return
      }
      this.adding = true
      try {
        await axios.post('/api/health-assistant/recipes', this.form)
        this.$message.success('添加成功')
        this.form.name = ''
        this.form.calories = null
        this.fetchRecipes()
      } catch (e) {
        this.$message.error('添加失败')
      } finally {
        this.adding = false
      }
    }
  },
  mounted() {
    this.fetchRecipes()
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
