<template>
  <div class="search-container">
    <el-card class="search-card">
      <template #header>
        <div class="card-header">
          <el-icon><Search /></el-icon>
          <span>网络搜索</span>
        </div>
      </template>

      <!-- Search Input -->
      <div class="search-input-section">
        <el-input
          v-model="searchQuery"
          size="large"
          placeholder="输入搜索关键词..."
          @keyup.enter="performSearch"
          class="search-input"
        >
          <template #prepend>
            <el-select v-model="selectedEngine" placeholder="搜索引擎" style="width: 120px">
              <el-option label="自动选择" value="" />
              <el-option label="DuckDuckGo" value="duckduckgo" />
              <el-option label="Google" value="google" />
              <el-option label="Bing" value="bing" />
            </el-select>
          </template>
          <template #append>
            <el-button @click="performSearch" :loading="isSearching" type="primary">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- Search Results -->
      <div v-if="isSearching" class="loading-section">
        <el-skeleton :rows="5" animated />
        <div class="loading-text">正在搜索中，请稍候...</div>
      </div>

      <div v-else-if="searchResults.length > 0" class="results-section">
        <div class="results-header">
          <h3>搜索结果</h3>
          <el-tag type="info">共找到 {{ searchResults.length }} 条结果</el-tag>
        </div>

        <div class="results-list">
          <div
            v-for="(result, index) in searchResults"
            :key="index"
            class="result-item"
          >
            <div class="result-header">
              <h4 class="result-title">
                <a :href="result.url" target="_blank" rel="noopener noreferrer">
                  {{ result.title }}
                </a>
              </h4>
              <el-tag size="small" :type="getEngineTagType(result.source)">
                {{ getEngineDisplayName(result.source) }}
              </el-tag>
            </div>
            
            <div class="result-url">{{ result.url }}</div>
            
            <div class="result-snippet">{{ result.snippet }}</div>
            
            <div class="result-actions">
              <el-button size="small" @click="copyResult(result)">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
              <el-button size="small" @click="askAboutResult(result)">
                <el-icon><ChatDotRound /></el-icon>
                询问AI
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="hasSearched && searchResults.length === 0" class="empty-results">
        <el-empty description="未找到相关结果">
          <el-button type="primary" @click="searchQuery = ''; hasSearched = false">
            重新搜索
          </el-button>
        </el-empty>
      </div>

      <div v-else class="search-tips">
        <h3>搜索提示</h3>
        <ul>
          <li>🔍 输入关键词进行网络搜索</li>
          <li>🌐 支持多个搜索引擎，自动选择最佳结果</li>
          <li>📋 可以复制搜索结果或直接询问AI</li>
          <li>🎯 搜索结果会自动整合到聊天对话中</li>
        </ul>
        
        <div class="example-searches">
          <h4>示例搜索：</h4>
          <el-tag
            v-for="example in exampleSearches"
            :key="example"
            @click="searchQuery = example; performSearch()"
            class="example-tag"
          >
            {{ example }}
          </el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '../utils/api'

export default {
  name: 'Search',
  setup() {
    const router = useRouter()
    const searchQuery = ref('')
    const selectedEngine = ref('')
    const searchResults = reactive([])
    const isSearching = ref(false)
    const hasSearched = ref(false)
    
    const exampleSearches = [
      '人工智能最新发展',
      'Vue.js 3.0 新特性',
      '2024年科技趋势',
      'Python机器学习教程',
      '武昌工学院'
    ]

    const performSearch = async () => {
      if (!searchQuery.value.trim()) {
        ElMessage.warning('请输入搜索关键词')
        return
      }

      isSearching.value = true
      hasSearched.value = true
      
      try {
        const response = await api.post('/search', {
          query: searchQuery.value,
          max_results: 10,
          engine: selectedEngine.value || undefined
        })

        searchResults.length = 0
        searchResults.push(...response.data.results)

        if (searchResults.length === 0) {
          ElMessage.info('未找到相关结果，请尝试其他关键词')
        } else {
          ElMessage.success(`找到 ${searchResults.length} 条搜索结果`)
        }
      } catch (error) {
        console.error('Search error:', error)
        ElMessage.error('搜索失败，请重试')
      } finally {
        isSearching.value = false
      }
    }

    const getEngineTagType = (source) => {
      const types = {
        'duckduckgo': 'primary',
        'google': 'success',
        'bing': 'warning'
      }
      return types[source] || 'info'
    }

    const getEngineDisplayName = (source) => {
      const names = {
        'duckduckgo': 'DuckDuckGo',
        'google': 'Google',
        'bing': 'Bing'
      }
      return names[source] || source
    }

    const copyResult = async (result) => {
      try {
        const text = `${result.title}\n${result.url}\n${result.snippet}`
        await navigator.clipboard.writeText(text)
        ElMessage.success('搜索结果已复制到剪贴板')
      } catch (error) {
        console.error('Copy error:', error)
        ElMessage.error('复制失败')
      }
    }

    const askAboutResult = (result) => {
      // Navigate to chat with pre-filled question about the result
      const question = `请帮我分析这个搜索结果：\n\n标题：${result.title}\n链接：${result.url}\n摘要：${result.snippet}`
      
      router.push({
        path: '/chat',
        query: { message: question }
      })
    }

    return {
      searchQuery,
      selectedEngine,
      searchResults,
      isSearching,
      hasSearched,
      exampleSearches,
      performSearch,
      getEngineTagType,
      getEngineDisplayName,
      copyResult,
      askAboutResult
    }
  }
}
</script>

<style scoped>
.search-container {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  font-size: 16px;
}

.search-input-section {
  margin-bottom: 24px;
}

.search-input {
  width: 100%;
}

.loading-section {
  text-align: center;
  padding: 40px 20px;
}

.loading-text {
  margin-top: 16px;
  color: #909399;
  font-size: 14px;
}

.results-section {
  margin-top: 24px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.results-header h3 {
  margin: 0;
  color: #303133;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-item {
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.result-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.result-title {
  margin: 0;
  flex: 1;
  margin-right: 12px;
}

.result-title a {
  color: #409eff;
  text-decoration: none;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}

.result-title a:hover {
  text-decoration: underline;
}

.result-url {
  color: #67c23a;
  font-size: 14px;
  margin-bottom: 8px;
  word-break: break-all;
}

.result-snippet {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12px;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.empty-results {
  text-align: center;
  padding: 60px 20px;
}

.search-tips {
  text-align: center;
  padding: 40px 20px;
  color: #606266;
}

.search-tips h3 {
  color: #303133;
  margin-bottom: 20px;
}

.search-tips ul {
  text-align: left;
  display: inline-block;
  margin: 20px 0;
}

.search-tips li {
  margin-bottom: 8px;
  font-size: 14px;
}

.example-searches {
  margin-top: 30px;
}

.example-searches h4 {
  color: #303133;
  margin-bottom: 12px;
}

.example-tag {
  margin: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.example-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
