<template>
  <div style="height: 100%; display: flex; flex-direction: column; background: white;">
    <!-- Header -->
    <div style="padding: 20px; border-bottom: 1px solid #eee; background: white;">
      <h2 style="margin: 0; color: #333;">🤖 元启康健AI智能健康小助手</h2>
      <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">武昌工学院 AI 竞赛项目 | DeepSeek-V3 驱动</p>
    </div>

    <!-- Messages Area -->
    <div style="flex: 1; padding: 20px; background: #f5f5f5; overflow-y: auto;">
      <div v-if="messages.length === 0" style="text-align: center; padding: 50px;">
        <h3 style="color: #666;">你好！我是武昌工学院的元启康健AI智能健康小助手小元-，很高兴为你服务。请问有什么可以帮你的吗？</h3>
        <p style="color: #999;"></p>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; max-width: 400px; margin: 30px auto;">
          <div @click="quickStart('请介绍你的功能')" style="padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 10px; cursor: pointer; text-align: center;">
            <div style="font-size: 24px; margin-bottom: 8px;">🛠️</div>
            <div>工具能力</div>
          </div>
          <div @click="quickStart('帮我制定学习计划')" style="padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 10px; cursor: pointer; text-align: center;">
            <div style="font-size: 24px; margin-bottom: 8px;">📅</div>
            <div>任务规划</div>
          </div>
          <div @click="quickStart('搜索人工智能最新发展')" style="padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 10px; cursor: pointer; text-align: center;">
            <div style="font-size: 24px; margin-bottom: 8px;">🔍</div>
            <div>信息搜索</div>
          </div>
          <div @click="quickStart('写一个Python程序')" style="padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 10px; cursor: pointer; text-align: center;">
            <div style="font-size: 24px; margin-bottom: 8px;">💻</div>
            <div>代码编程</div>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div v-for="(message, index) in messages" :key="index" style="margin-bottom: 20px;">
        <div style="display: flex; gap: 10px;" :style="message.role === 'user' ? 'justify-content: flex-end;' : ''">
          <div v-if="message.role === 'assistant'" style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(45deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; color: white; font-size: 18px;">
            🤖
          </div>
          <div style="max-width: 70%; padding: 12px 16px; border-radius: 12px;" :style="message.role === 'user' ? 'background: #667eea; color: white;' : 'background: white; border: 1px solid #eee;'">
            <div v-html="formatMessage(message.content)"></div>
            <div style="font-size: 12px; opacity: 0.7; margin-top: 5px;">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>
          <div v-if="message.role === 'user'" style="width: 36px; height: 36px; border-radius: 50%; background: #ccc; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px;">
            👤
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" style="display: flex; gap: 10px; margin-bottom: 20px;">
        <div style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(45deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; color: white; font-size: 18px;">
          🤖
        </div>
        <div style="background: white; border: 1px solid #eee; padding: 12px 16px; border-radius: 12px;">
          <div style="display: flex; gap: 4px;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #667eea; animation: bounce 1.4s infinite ease-in-out both;"></div>
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #667eea; animation: bounce 1.4s infinite ease-in-out both; animation-delay: -0.32s;"></div>
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #667eea; animation: bounce 1.4s infinite ease-in-out both; animation-delay: -0.16s;"></div>
          </div>
          <div style="margin-top: 5px; color: #666;">AI正在思考中...</div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div style="padding: 20px; background: white; border-top: 1px solid #eee;">
      <div style="display: flex; gap: 10px; align-items: flex-end;">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="💬 输入您的问题... (Ctrl+Enter 发送)"
          @keydown.ctrl.enter="sendMessage"
          :disabled="loading"
          style="flex: 1;"
          resize="none"
        />
        <div style="display: flex; flex-direction: column; gap: 8px;">
          <el-button type="primary" @click="sendMessage" :loading="loading" size="large">
            <el-icon><Send /></el-icon>
            发送
          </el-button>
          <el-button @click="clearMessages" size="large">
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

export default {
  name: 'ChatSimple',
  setup() {
    const messages = reactive([])
    const inputMessage = ref('')
    const loading = ref(false)

    const formatMessage = (content) => {
      return content.replace(/\n/g, '<br>')
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('zh-CN')
    }

    const sendMessage = async () => {
      if (!inputMessage.value.trim() || loading.value) return

      const userMessage = {
        role: 'user',
        content: inputMessage.value.trim(),
        timestamp: new Date()
      }

      messages.push(userMessage)
      const currentMessage = inputMessage.value.trim()
      inputMessage.value = ''
      loading.value = true

      try {
        const response = await api.post('/api/chat', {
          message: currentMessage,
          use_knowledge_base: true
        })

        const assistantMessage = {
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date()
        }

        messages.push(assistantMessage)
      } catch (error) {
        console.error('Chat error:', error)
        ElMessage.error('发送消息失败，请重试')
        
        const errorMessage = {
          role: 'assistant',
          content: '抱歉，我现在无法回复。请检查网络连接或稍后重试。',
          timestamp: new Date()
        }
        messages.push(errorMessage)
      } finally {
        loading.value = false
      }
    }

    const clearMessages = () => {
      messages.length = 0
      ElMessage.success('对话已清空')
    }

    const quickStart = (message) => {
      inputMessage.value = message
      sendMessage()
    }

    return {
      messages,
      inputMessage,
      loading,
      formatMessage,
      formatTime,
      sendMessage,
      clearMessages,
      quickStart
    }
  }
}
</script>

<style scoped>
@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
</style>
