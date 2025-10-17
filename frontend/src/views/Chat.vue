<template>
  <div class="chat-container">
    <!-- Chat Header -->
    <div class="chat-header">
      <div class="header-left">
        <h2>🤖 元启康健AI智能健康小助手</h2>
        <span class="model-info">武昌工学院 AI 项目</span>
      </div>
      <div class="header-right">
        <el-space>
          <el-select v-model="activeProvider" placeholder="选择模型" size="large" style="min-width: 180px" @change="saveProvider">
            <el-option v-for="p in providers" :key="p" :label="p" :value="p" />
          </el-select>
          <el-switch
            v-model="useKnowledgeBase"
            active-text="知识库增强"
            inactive-text="纯对话模式"
            size="large"
          />
          <el-button type="primary" @click="showToolsDialog = true" size="small">
            <el-icon><Tools /></el-icon>
            工具箱
          </el-button>
        </el-space>
      </div>
    </div>

    <!-- Messages Area -->
    <div class="messages-area" ref="messagesContainer">
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-content">
          <el-icon class="welcome-icon"><ChatDotRound /></el-icon>
          <h3>你好！我是武昌工学院的元启康健AI智能健康小助手小元-，很高兴为你服务。请问有什么可以帮你的吗？</h3>
          <p></p>
          <div class="capabilities-grid">
            <div class="capability-card" @click="quickMessage('请介绍你的功能和工具')">
              <el-icon><Tools /></el-icon>
              <span>工具能力</span>
            </div>
            <div class="capability-card" @click="quickMessage('帮我制定一个学习计划')">
              <el-icon><Calendar /></el-icon>
              <span>任务规划</span>
            </div>
            <div class="capability-card" @click="quickMessage('搜索人工智能最新发展')">
              <el-icon><Search /></el-icon>
              <span>信息搜索</span>
            </div>
            <div class="capability-card" @click="quickMessage('写一个Python程序计算斐波那契数列')">
              <el-icon><Document /></el-icon>
              <span>代码编程</span>
            </div>
          </div>
        </div>
      </div>

      <div
        v-for="(message, index) in messages"
        :key="index"
        class="message"
        :class="{ 'user-message': message.role === 'user', 'assistant-message': message.role === 'assistant' }"
      >
        <div class="message-avatar">
          <el-avatar v-if="message.role === 'user'" :size="36">
            <el-icon><User /></el-icon>
          </el-avatar>
          <el-avatar v-else :size="36" style="background: linear-gradient(45deg, #667eea, #764ba2)">
            <el-icon><Robot /></el-icon>
          </el-avatar>
        </div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(message.content)"></div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <div v-if="loading" class="loading-message">
        <div class="message-avatar">
          <el-avatar :size="36" style="background: linear-gradient(45deg, #667eea, #764ba2)">
            <el-icon class="is-loading"><Loading /></el-icon>
          </el-avatar>
        </div>
        <div class="loading-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <p>AI正在思考中...</p>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <div class="input-container">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="💬 输入您的问题... (Ctrl+Enter 发送)"
          @keydown.ctrl.enter="sendMessage"
          :disabled="loading"
          class="message-input"
          resize="none"
        />
        <div class="input-actions">
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

    <!-- Tools Dialog -->
    <el-dialog
      v-model="showToolsDialog"
      title="🔧 工具箱"
      width="80%"
      :before-close="handleToolsDialogClose"
    >
      <div class="tools-grid">
        <div class="tool-category">
          <h4>💻 开发工具</h4>
          <div class="tool-items">
            <div class="tool-item" @click="insertToolCommand('python_execute', '执行Python代码')">
              <el-icon><Document /></el-icon>
              <span>Python执行器</span>
            </div>
            <div class="tool-item" @click="insertToolCommand('file_editor', '文件操作')">
              <el-icon><Folder /></el-icon>
              <span>文件编辑器</span>
            </div>
            <div class="tool-item" @click="insertToolCommand('bash', '执行系统命令')">
              <el-icon><Monitor /></el-icon>
              <span>命令行工具</span>
            </div>
          </div>
        </div>
        <div class="tool-category">
          <h4>🔍 信息工具</h4>
          <div class="tool-items">
            <div class="tool-item" @click="insertToolCommand('web_search', '网络搜索')">
              <el-icon><Search /></el-icon>
              <span>网络搜索</span>
            </div>
            <div class="tool-item" @click="insertToolCommand('knowledge_base_search', '知识库查询')">
              <el-icon><Reading /></el-icon>
              <span>知识库</span>
            </div>
          </div>
        </div>
        <div class="tool-category">
          <h4>📋 管理工具</h4>
          <div class="tool-items">
            <div class="tool-item" @click="insertToolCommand('planning', '任务规划')">
              <el-icon><Calendar /></el-icon>
              <span>任务规划</span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

export default {
  name: 'Chat',
  setup() {
    const messages = reactive([])
    const inputMessage = ref('')
    const loading = ref(false)
    const useKnowledgeBase = ref(true)
    const conversationId = ref(null)
    const messagesContainer = ref(null)
    const showToolsDialog = ref(false)
    const providers = ref([])
    const activeProvider = ref('primary')

    // Configure marked for better rendering
    marked.setOptions({
      breaks: true,
      gfm: true
    })

    const formatMessage = (content) => {
      return marked(content)
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('zh-CN')
    }

    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
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

      await scrollToBottom()

      try {
        // 统一使用流式输出（SSE）
        const originBase = (typeof window !== 'undefined' && window.location) ? window.location.origin : ''
        const apiBase = (api && api.defaults && api.defaults.baseURL) ? api.defaults.baseURL : ''
        const base = originBase || apiBase || ''
        const url = new URL('/api/chat/stream', base.endsWith('/') ? base : base + '/').toString()

        const payload = {
          message: currentMessage,
          use_knowledge_base: !!useKnowledgeBase.value,
          conversation_id: conversationId.value,
          provider: activeProvider.value
        }

        const resp = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
          body: JSON.stringify(payload)
        })

        if (!resp.ok) throw new Error(`流式接口HTTP错误: ${resp.status}`)

        // 先创建一条空的 assistant 消息用于增量渲染
        const assistantMessage = { role: 'assistant', content: '', timestamp: new Date() }
        messages.push(assistantMessage)
        await scrollToBottom()

        if (resp.body && resp.body.getReader) {
          // 原生流式读取
          const reader = resp.body.getReader()
          const decoder = new TextDecoder('utf-8')
          let buffer = ''
          while (true) {
            const { done, value } = await reader.read()
            if (done) break
            buffer += decoder.decode(value, { stream: true })
            const parts = buffer.split('\n\n')
            buffer = parts.pop() || ''
            for (const chunk of parts) {
              const line = chunk.trim()
              if (!line || !line.startsWith('data:')) continue
              const dataStr = line.replace(/^data:\s*/, '')
              if (dataStr === '[DONE]') { buffer = ''; break }
              try {
                const obj = JSON.parse(dataStr)
                const piece = obj.delta || obj.response || obj.content || ''
                if (piece) {
                  assistantMessage.content += piece
                  messages[messages.length - 1] = { ...assistantMessage }
                  await scrollToBottom()
                }
                if (obj.conversation_id && !conversationId.value) {
                  conversationId.value = obj.conversation_id
                }
              } catch (e) {
                console.warn('解析流数据失败:', e, line)
              }
            }
          }
        } else {
          // 某些环境不支持流式；退化为一次性文本解析
          const text = await resp.text()
          const blocks = text.split('\n\n')
          for (const blk of blocks) {
            const line = blk.trim()
            if (!line || !line.startsWith('data:')) continue
            const dataStr = line.replace(/^data:\s*/, '')
            if (dataStr === '[DONE]') break
            try {
              const obj = JSON.parse(dataStr)
              const piece = obj.delta || obj.response || obj.content || ''
              if (piece) {
                assistantMessage.content += piece
                messages[messages.length - 1] = { ...assistantMessage }
              }
              if (obj.conversation_id && !conversationId.value) {
                conversationId.value = obj.conversation_id
              }
            } catch (e) {
              console.warn('解析文本块失败:', e, line)
            }
          }
          await scrollToBottom()
        }
      } catch (error) {
        console.error('Chat error:', error)
        // 流式失败统一回退到非流式接口
        try {
          console.warn('流式失败，回退到非流式 /api/chat ...')
          const response = await api.post('/api/chat', {
            message: currentMessage,
            use_knowledge_base: !!useKnowledgeBase.value,
            conversation_id: conversationId.value,
            provider: activeProvider.value
          })
          const content = response?.data?.response || ''
          const last = messages[messages.length - 1]
          if (last && last.role === 'assistant') {
            last.content = (last.content || '') + content
            messages[messages.length - 1] = { ...last }
          } else {
            messages.push({ role: 'assistant', content, timestamp: new Date() })
          }
          if (response?.data?.conversation_id && !conversationId.value) {
            conversationId.value = response.data.conversation_id
          }
          await scrollToBottom()
        } catch (fallbackErr) {
          console.error('Fallback /api/chat 也失败:', fallbackErr)
          const msg = (error && error.message) ? error.message : '发送消息失败，请重试'
          ElMessage.error(msg)
        }
      } finally {
        loading.value = false
        scrollToBottom()
      }
    }

    const clearMessages = () => {
      messages.length = 0
      conversationId.value = null
      ElMessage.success('对话已清空')
    }

    const quickMessage = (message) => {
      inputMessage.value = message
      sendMessage()
    }

    // Missing helpers for Tools dialog and command insertion
    const handleToolsDialogClose = () => {
      showToolsDialog.value = false
    }

    const insertToolCommand = (toolName, displayName) => {
      // 在输入框中预填一条带有任务类型的提示，用户可直接发送
      const hint = `【${displayName || '工具'}】请描述你的需求：`
      inputMessage.value = hint
      showToolsDialog.value = false
    }

    const saveProvider = () => {
      try { localStorage.setItem('liuagent_provider', activeProvider.value || 'primary') } catch (e) {}
    }

    onMounted(async () => {
      try {
        const cached = localStorage.getItem('liuagent_provider')
        if (cached) activeProvider.value = cached
      } catch (e) {}
      try {
        const { data } = await api.get('/api/config')
        if (data && Array.isArray(data.llm_providers)) {
          providers.value = data.llm_providers
          if (!providers.value.includes(activeProvider.value)) {
            activeProvider.value = providers.value[0] || 'primary'
          }
        }
      } catch (e) {
        // ignore
      }
    })

    return {
      messages,
      inputMessage,
      loading,
      useKnowledgeBase,
      showToolsDialog,
      formatMessage,
      formatTime,
      quickMessage,
      sendMessage,
      clearMessages,
      handleToolsDialogClose,
      insertToolCommand,
      messagesContainer,
      providers,
      activeProvider,
      saveProvider
    }
  }
}
</script>

<style scoped>
.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
}

.chat-header {
  padding: 20px 30px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.header-left h2 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 24px;
}

.model-info {
  color: #909399;
  font-size: 14px;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 30px;
  background: #fafafa;
  min-height: 400px;
}

.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
}

.welcome-content {
  max-width: 500px;
}

.welcome-icon {
  font-size: 64px;
  color: #667eea;
  margin-bottom: 20px;
}

.welcome-content h3 {
  color: #303133;
  margin-bottom: 15px;
  font-size: 24px;
}

.welcome-content p {
  color: #606266;
  margin-bottom: 30px;
  line-height: 1.6;
}

.capabilities-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-top: 20px;
  max-width: 400px;
}

.capability-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
}

.capability-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.capability-card .el-icon {
  font-size: 24px;
}

.capability-card span {
  font-size: 14px;
  font-weight: 500;
}

/* Tools Dialog Styles */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.tool-category h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.tool-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.tool-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 15px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.tool-item:hover {
  border-color: #667eea;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
  transform: translateY(-2px);
}

.tool-item .el-icon {
  font-size: 20px;
  color: #667eea;
}

.tool-item span {
  font-size: 12px;
  color: #606266;
  text-align: center;
}

.quick-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-tag {
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.action-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.message {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
  gap: 15px;
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-content {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border-radius: 18px 18px 6px 18px;
}

.assistant-message .message-content {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 18px 18px 18px 6px;
}

.message-content {
  max-width: 70%;
  padding: 15px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 8px;
}

.loading-message {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 20px;
}

.loading-content {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 18px 18px 18px 6px;
  padding: 15px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.typing-indicator {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.input-area {
  padding: 20px 30px;
  background: white;
  border-top: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.input-container {
  display: flex;
  gap: 15px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
}

.input-actions {
  display: flex;
  gap: 10px;
}
</style>
