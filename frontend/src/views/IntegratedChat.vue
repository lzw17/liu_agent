<template>
  <div class="integrated-container">
    <!-- 仅保留聊天区域，工具能力在对话内部按任务区分 -->
    <div class="chat-section">
      <Chat />
    </div>
  </div>
  
</template>

<script>
import Chat from './Chat.vue'

export default {
  name: 'IntegratedChat',
  components: {
    Chat
  }
}
</script>

<style scoped>
.integrated-container {
  height: 100%;
  overflow: hidden;
}

.chat-section {
  height: 100%;
}
</style>
