<template>
  <div style="padding: 20px;">
    <h1>测试页面</h1>
    <p>如果您能看到这个页面，说明路由工作正常。</p>
    <el-button type="primary" @click="testClick">测试按钮</el-button>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'

export default {
  name: 'Test',
  setup() {
    const testClick = () => {
      ElMessage.success('测试成功！')
    }
    
    return {
      testClick
    }
  }
}
</script>
