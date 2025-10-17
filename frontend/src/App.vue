<template>
  <div id="app">
    <el-container class="app-container">
      <!-- Left Sidebar -->
      <el-aside class="app-sidebar" width="280px">
        <div class="sidebar-header">
          <img src="/yuanqi.jpg" alt="元启康健AI" class="logo" />
          <div class="title-section">
            <h2 class="title">元启康健AI智能健康小助手</h2>
            <span class="subtitle">AI个人健康助理 · 小元</span>
          </div>
        </div>
        
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu"
          router
          :collapse="false"
        >
          <el-menu-item index="/chat">
            <el-icon><ChatDotRound /></el-icon>
            <span>智能对话</span>
          </el-menu-item>
          <el-menu-item index="/knowledge">
            <el-icon><Document /></el-icon>
            <span>知识库管理</span>
          </el-menu-item>
          <el-menu-item index="/assistant">
            <el-icon><User /></el-icon>
            <span>医疗小助手</span>
          </el-menu-item>
          <el-menu-item index="/assistant/plan">
            <el-icon><Calendar /></el-icon>
            <span>我的计划</span>
          </el-menu-item>
          <el-menu-item index="/assistant/checkin">
            <el-icon><Finished /></el-icon>
            <span>健康打卡</span>
          </el-menu-item>
          <el-menu-item index="/assistant/recipes">
            <el-icon><Food /></el-icon>
            <span>营养食谱</span>
          </el-menu-item>
          <el-menu-item index="/assistant/therapy">
            <el-icon><MagicStick /></el-icon>
            <span>养身理疗</span>
          </el-menu-item>
          <el-menu-item index="/assistant/profile">
            <el-icon><Setting /></el-icon>
            <span>后台信息</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-footer">
          <el-divider />
          <div class="feature-list">
            <div class="feature-item">
              <el-icon><Document /></el-icon>
              <span>PDF知识库</span>
            </div>
            <div class="feature-item">
              <el-icon><ChatDotRound /></el-icon>
              <span>智能问答</span>
            </div>
            <div class="feature-item">
              <el-icon><Search /></el-icon>
              <span>网络搜索</span>
            </div>
            <div class="feature-item">
              <el-icon><Setting /></el-icon>
              <span>多模型支持</span>
            </div>
          </div>
        </div>
      </el-aside>

      <!-- Main Content Area -->
      <el-container class="main-container">
        <el-main class="app-main">
          <router-view />
        </el-main>
        
        <el-footer class="app-footer">
          <p>&copy; 2024 武昌工学院 LiuAgent AI 竞赛项目 | Powered by DeepSeek</p>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style scoped>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  height: 100vh;
  overflow: hidden;
}

.app-container {
  height: 100vh;
}

.app-sidebar {
  background: linear-gradient(180deg, #1e80ff 0%, #3ba0ff 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  width: 45px;
  height: 45px;
  border-radius: 8px;
  object-fit: cover;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.title-section {
  flex: 1;
}

.title {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: white;
}

.subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  display: block;
  margin-top: 4px;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  padding: 20px 0;
}

.sidebar-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.8);
  border: none;
  margin: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  padding: 8px 0;
}

.main-container {
  background: linear-gradient(135deg, #f6fbff 0%, #e8f3ff 100%);
  display: flex;
  flex-direction: column;
}

.app-main {
  padding: 0;
  flex: 1;
  overflow: hidden;
  height: calc(100vh - 60px);
}

.app-footer {
  background: rgba(255, 255, 255, 0.9);
  text-align: center;
  color: #666;
  font-size: 12px;
}

/* Global styles */
:global(body) {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

:global(*) {
  box-sizing: border-box;
}
</style>
