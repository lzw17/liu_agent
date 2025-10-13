<template>
  <div style="padding: 20px; background: white; height: 100vh;">
    <h1>测试页面</h1>
    <p>如果你能看到这个页面，说明路由正常工作</p>
    
    <!-- 简单的输入框测试 -->
    <div style="margin-top: 30px; border: 2px solid red; padding: 20px;">
      <h3>输入框测试</h3>
      <el-input 
        v-model="testMessage" 
        placeholder="这是一个测试输入框"
        style="margin-bottom: 10px;"
      />
      <el-button type="primary" @click="showAlert">测试按钮</el-button>
      <p>输入内容: {{ testMessage }}</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'SimpleTest',
  setup() {
    const testMessage = ref('')
    
    const showAlert = () => {
      ElMessage.success('按钮点击成功！输入内容: ' + testMessage.value)
    }
    
    return {
      testMessage,
      showAlert
    }
  }
}
</script>
