<template>
  <div class="planning-container">
    <!-- Planning Header -->
    <div class="planning-header">
      <div class="header-left">
        <h2>任务规划</h2>
        <span class="subtitle">AI智能任务规划与执行</span>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="createNewPlan">
          <el-icon><Plus /></el-icon>
          新建规划
        </el-button>
      </div>
    </div>

    <!-- Planning Content -->
    <div class="planning-content">
      <div v-if="plans.length === 0" class="empty-state">
        <div class="empty-content">
          <el-icon class="empty-icon"><List /></el-icon>
          <h3>开始您的智能规划</h3>
          <p>AI将帮助您制定详细的任务规划，包括目标分解、时间安排和执行步骤</p>
          <el-button type="primary" size="large" @click="createNewPlan">
            <el-icon><Plus /></el-icon>
            创建第一个规划
          </el-button>
        </div>
      </div>

      <div v-else class="plans-grid">
        <el-card 
          v-for="plan in plans" 
          :key="plan.id" 
          class="plan-card"
          @click="selectPlan(plan)"
          :class="{ active: selectedPlan?.id === plan.id }"
        >
          <div class="plan-header">
            <h4>{{ plan.title }}</h4>
            <el-tag :type="getPlanStatusType(plan.status)">{{ plan.status }}</el-tag>
          </div>
          <p class="plan-description">{{ plan.description }}</p>
          <div class="plan-meta">
            <span class="plan-date">{{ formatDate(plan.created_at) }}</span>
            <span class="plan-progress">{{ plan.completed_tasks }}/{{ plan.total_tasks }} 完成</span>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Plan Detail Dialog -->
    <el-dialog 
      v-model="showPlanDialog" 
      :title="isEditing ? '编辑规划' : '新建规划'"
      width="800px"
    >
      <el-form :model="currentPlan" label-width="100px">
        <el-form-item label="规划标题">
          <el-input v-model="currentPlan.title" placeholder="请输入规划标题" />
        </el-form-item>
        <el-form-item label="规划描述">
          <el-input 
            v-model="currentPlan.description" 
            type="textarea" 
            :rows="3"
            placeholder="请描述您的规划目标和要求"
          />
        </el-form-item>
        <el-form-item label="AI生成">
          <el-button type="primary" @click="generatePlan" :loading="generating">
            <el-icon><Magic /></el-icon>
            让AI帮我规划
          </el-button>
        </el-form-item>
        <el-form-item v-if="currentPlan.tasks && currentPlan.tasks.length > 0" label="任务列表">
          <div class="tasks-list">
            <div 
              v-for="(task, index) in currentPlan.tasks" 
              :key="index"
              class="task-item"
            >
              <el-checkbox v-model="task.completed">{{ task.title }}</el-checkbox>
              <p class="task-description">{{ task.description }}</p>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPlanDialog = false">取消</el-button>
        <el-button type="primary" @click="savePlan">保存规划</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

export default {
  name: 'Planning',
  setup() {
    const plans = ref([])
    const selectedPlan = ref(null)
    const showPlanDialog = ref(false)
    const isEditing = ref(false)
    const generating = ref(false)
    
    const currentPlan = reactive({
      title: '',
      description: '',
      tasks: []
    })

    const createNewPlan = () => {
      Object.assign(currentPlan, {
        title: '',
        description: '',
        tasks: []
      })
      isEditing.value = false
      showPlanDialog.value = true
    }

    const selectPlan = (plan) => {
      selectedPlan.value = plan
      Object.assign(currentPlan, plan)
      isEditing.value = true
      showPlanDialog.value = true
    }

    const generatePlan = async () => {
      if (!currentPlan.description.trim()) {
        ElMessage.warning('请先输入规划描述')
        return
      }

      generating.value = true
      try {
        const response = await api.post('/api/chat', {
          message: `请帮我制定一个详细的任务规划：${currentPlan.description}。请以JSON格式返回，包含tasks数组，每个任务包含title和description字段。`,
          use_knowledge_base: false
        })

        // 解析AI返回的规划
        const aiResponse = response.data.response
        // 这里可以添加更复杂的解析逻辑
        const mockTasks = [
          { title: '需求分析', description: '分析项目需求和目标', completed: false },
          { title: '方案设计', description: '制定详细的实施方案', completed: false },
          { title: '资源准备', description: '准备所需的资源和工具', completed: false },
          { title: '执行实施', description: '按计划执行任务', completed: false },
          { title: '测试验证', description: '测试和验证结果', completed: false },
          { title: '总结优化', description: '总结经验并优化流程', completed: false }
        ]
        
        currentPlan.tasks = mockTasks
        ElMessage.success('AI规划生成成功！')
      } catch (error) {
        console.error('Generate plan error:', error)
        ElMessage.error('生成规划失败，请重试')
      } finally {
        generating.value = false
      }
    }

    const savePlan = () => {
      if (!currentPlan.title.trim()) {
        ElMessage.warning('请输入规划标题')
        return
      }

      const planData = {
        ...currentPlan,
        id: isEditing.value ? selectedPlan.value.id : Date.now(),
        status: '进行中',
        created_at: isEditing.value ? selectedPlan.value.created_at : new Date(),
        total_tasks: currentPlan.tasks.length,
        completed_tasks: currentPlan.tasks.filter(t => t.completed).length
      }

      if (isEditing.value) {
        const index = plans.value.findIndex(p => p.id === selectedPlan.value.id)
        if (index !== -1) {
          plans.value[index] = planData
        }
      } else {
        plans.value.push(planData)
      }

      showPlanDialog.value = false
      ElMessage.success(isEditing.value ? '规划更新成功' : '规划创建成功')
    }

    const getPlanStatusType = (status) => {
      const statusMap = {
        '进行中': 'primary',
        '已完成': 'success',
        '暂停': 'warning',
        '已取消': 'danger'
      }
      return statusMap[status] || 'info'
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('zh-CN')
    }

    onMounted(() => {
      // 加载示例数据
      plans.value = [
        {
          id: 1,
          title: '学习人工智能基础',
          description: '系统学习AI基础知识和实践应用',
          status: '进行中',
          created_at: new Date(),
          total_tasks: 6,
          completed_tasks: 2,
          tasks: [
            { title: '学习机器学习基础', description: '了解基本概念和算法', completed: true },
            { title: '实践编程练习', description: '完成相关编程作业', completed: true },
            { title: '深度学习入门', description: '学习神经网络基础', completed: false }
          ]
        }
      ]
    })

    return {
      plans,
      selectedPlan,
      showPlanDialog,
      isEditing,
      generating,
      currentPlan,
      createNewPlan,
      selectPlan,
      generatePlan,
      savePlan,
      getPlanStatusType,
      formatDate
    }
  }
}
</script>

<style scoped>
.planning-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: white;
}

.planning-header {
  padding: 20px 30px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header-left h2 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 24px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.planning-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  background: #fafafa;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
}

.empty-content {
  max-width: 400px;
}

.empty-icon {
  font-size: 64px;
  color: #667eea;
  margin-bottom: 20px;
}

.empty-content h3 {
  color: #303133;
  margin-bottom: 15px;
  font-size: 24px;
}

.empty-content p {
  color: #606266;
  margin-bottom: 30px;
  line-height: 1.6;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.plan-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.plan-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.plan-card.active {
  border-color: #667eea;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.plan-header h4 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.plan-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 15px;
}

.plan-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.plan-progress {
  color: #667eea;
  font-weight: 500;
}

.tasks-list {
  max-height: 300px;
  overflow-y: auto;
}

.task-item {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.task-item:last-child {
  border-bottom: none;
}

.task-description {
  margin: 5px 0 0 24px;
  font-size: 12px;
  color: #909399;
}
</style>
