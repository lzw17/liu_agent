<template>
  <div style="padding: 20px; height: calc(100vh - 60px); display: flex; flex-direction: column;">
    <h1>简单聊天测试</h1>
    
    <!-- 消息显示区域 -->
    <div style="flex: 1; border: 1px solid #ccc; padding: 10px; margin: 10px 0; overflow-y: auto;">
      <div v-for="(msg, index) in messages" :key="index" style="margin-bottom: 10px;">
        <strong>{{ msg.role }}:</strong> {{ msg.content }}
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
      <input 
        v-model="inputText" 
        @keyup.enter="sendMessage"
        placeholder="输入消息..."
        style="flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px;"
      />
      <button @click="sendMessage" style="padding: 10px 20px; background: #409eff; color: white; border: none; border-radius: 4px; cursor: pointer;">发送</button>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'

export default {
  name: 'SimpleChat',
  setup() {
    const messages = reactive([
      { role: 'assistant', content: '你好！我是LiuAgent，请输入消息测试。' }
    ])
    const inputText = ref('')
    
    const sendMessage = async () => {
      if (!inputText.value.trim()) return
      
      // 添加用户消息
      messages.push({ role: 'user', content: inputText.value })
      const userMessage = inputText.value
      inputText.value = ''
      
      try {
        // 调用API
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: userMessage,
            use_knowledge_base: false
          })
        })
        
        const data = await response.json()
        messages.push({ role: 'assistant', content: data.response })
      } catch (error) {
        messages.push({ role: 'assistant', content: '错误: ' + error.message })
      }
    }
    
    return {
      messages,
      inputText,
      sendMessage
    }
  }
}
</script>
