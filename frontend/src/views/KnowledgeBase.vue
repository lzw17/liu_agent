<template>
  <div class="knowledge-base-container">
    <el-row :gutter="20">
      <!-- Upload Section -->
      <el-col :span="8">
        <el-card class="upload-card">
          <template #header>
            <div class="card-header">
              <el-icon><Upload /></el-icon>
              <span>文档上传</span>
            </div>
          </template>
          
          <el-upload
            ref="uploadDragger"
            class="upload-dragger"
            drag
            :action="uploadUrl"
            :before-upload="beforeUpload"
            :on-success="onUploadSuccess"
            :on-error="onUploadError"
            :show-file-list="false"
            accept=".pdf,.docx,.txt"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、DOCX、TXT 格式，文件大小不超过 10MB
              </div>
            </template>
          </el-upload>

          <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
            <el-progress :percentage="uploadProgress" :status="uploadStatus" />
          </div>
        </el-card>

        <!-- Search Section -->
        <el-card class="search-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <el-icon><Search /></el-icon>
              <span>知识库搜索</span>
            </div>
          </template>
          
          <el-input
            v-model="searchQuery"
            placeholder="搜索知识库内容..."
            @keyup.enter="searchKnowledgeBase"
          >
            <template #append>
              <el-button @click="searchKnowledgeBase" :loading="isSearching">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>

          <div v-if="documents.length === 0 && !isLoading" class="empty-search-state">
            <el-empty description="请先上传文档到知识库，然后再进行搜索">
              <el-button type="primary" @click="triggerUpload">
                上传文档
              </el-button>
            </el-empty>
          </div>
          <div v-else-if="searchResults.length > 0" class="search-results">
            <h4>搜索结果 ({{ searchResults.length }})</h4>
            <div
              v-for="(result, index) in searchResults"
              :key="index"
              class="search-result-item"
            >
              <div class="result-source">{{ result.source }}</div>
              <div class="result-content">{{ result.content }}</div>
              <div class="result-score">相似度: {{ (result.similarity_score * 100).toFixed(1) }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Documents List -->
      <el-col :span="16">
        <el-card class="documents-card">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>知识库文档 ({{ documents.length }})</span>
              <el-button @click="loadDocuments" :loading="isLoading" size="small" style="margin-left: auto;">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <div v-if="isLoading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="documents.length === 0" class="empty-state">
            <el-empty description="暂无文档，请上传文档到知识库">
              <el-button type="primary" @click="triggerUpload">
                上传文档
              </el-button>
            </el-empty>
          </div>

          <el-table v-else :data="documents" style="width: 100%">
            <el-table-column prop="filename" label="文件名" min-width="200">
              <template #default="scope">
                <div class="filename">
                  <el-icon><Document /></el-icon>
                  <span>{{ scope.row.filename }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="pages" label="页数" width="80" align="center" />
            
            <el-table-column prop="chunks" label="分块数" width="100" align="center" />
            
            <el-table-column prop="upload_date" label="上传时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.upload_date) }}
              </template>
            </el-table-column>
            
            <el-table-column prop="file_size" label="文件大小" width="120">
              <template #default="scope">
                {{ formatFileSize(scope.row.file_size) }}
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="120" align="center">
              <template #default="scope">
                <el-button
                  type="danger"
                  size="small"
                  @click="deleteDocument(scope.row)"
                  :loading="scope.row.deleting"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'

export default {
  name: 'KnowledgeBase',
  setup() {
    const documents = reactive([])
    const isLoading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const searchQuery = ref('')
    const searchResults = reactive([])
    const isSearching = ref(false)
    
    const uploadUrl = '/api/upload-pdf'

    const loadDocuments = async () => {
      isLoading.value = true
      try {
        const response = await api.get('/api/knowledge-base')
        console.log('Knowledge base response:', response.data)
        documents.length = 0
        if (response.data && response.data.documents) {
          documents.push(...response.data.documents)
        }
      } catch (error) {
        console.error('Load documents error:', error)
        ElMessage.error('加载文档列表失败')
      } finally {
        isLoading.value = false
      }
    }

    const beforeUpload = (file) => {
      const isValidType = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'].includes(file.type)
      const isValidSize = file.size / 1024 / 1024 < 10

      if (!isValidType) {
        ElMessage.error('只支持 PDF、DOCX、TXT 格式的文件')
        return false
      }
      if (!isValidSize) {
        ElMessage.error('文件大小不能超过 10MB')
        return false
      }

      uploadProgress.value = 0
      uploadStatus.value = 'active'
      return true
    }

    const onUploadSuccess = (response) => {
      uploadProgress.value = 100
      uploadStatus.value = 'success'
      ElMessage.success(`文档上传成功！处理了 ${response.chunks} 个文本块`)
      loadDocuments()
      
      setTimeout(() => {
        uploadProgress.value = 0
      }, 2000)
    }

    const onUploadError = (error) => {
      uploadProgress.value = 100
      uploadStatus.value = 'exception'
      console.error('Upload error:', error)
      ElMessage.error('文档上传失败，请重试')
      
      setTimeout(() => {
        uploadProgress.value = 0
      }, 2000)
    }

    const deleteDocument = async (document) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除文档 "${document.filename}" 吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )

        document.deleting = true
        await api.delete(`/api/knowledge-base/${document.id}`)
        
        const index = documents.findIndex(d => d.id === document.id)
        if (index > -1) {
          documents.splice(index, 1)
        }
        
        ElMessage.success('文档删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Delete error:', error)
          ElMessage.error('删除文档失败')
        }
      } finally {
        document.deleting = false
      }
    }

    const searchKnowledgeBase = async () => {
      if (!searchQuery.value.trim()) {
        ElMessage.warning('请输入搜索关键词')
        return
      }

      isSearching.value = true
      try {
        const response = await api.post('/api/knowledge-base/search', {
          query: searchQuery.value,
          max_results: 10
        })
        
        searchResults.length = 0
        searchResults.push(...response.data.results)
        
        if (searchResults.length === 0) {
          ElMessage.info('未找到相关内容')
        }
      } catch (error) {
        console.error('Search error:', error)
        ElMessage.error('搜索失败，请重试')
      } finally {
        isSearching.value = false
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('zh-CN')
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    const scrollToUpload = () => {
      // 滚动到上传区域
      const uploadCard = document.querySelector('.upload-card')
      if (uploadCard) {
        uploadCard.scrollIntoView({ behavior: 'smooth' })
      }
    }
    
    const triggerUpload = () => {
      // 滚动到上传区域
      scrollToUpload()
      
      // 等待滚动完成后触发上传按钮点击
      setTimeout(() => {
        if (uploadDragger.value) {
          const uploadButton = uploadDragger.value.$el.querySelector('input[type="file"]')
          if (uploadButton) {
            uploadButton.click()
          }
        }
      }, 500)
    }

    onMounted(() => {
      loadDocuments()
    })

    return {
      documents,
      isLoading,
      uploadProgress,
      uploadStatus,
      uploadUrl,
      searchQuery,
      searchResults,
      isSearching,
      loadDocuments,
      beforeUpload,
      onUploadSuccess,
      onUploadError,
      deleteDocument,
      searchKnowledgeBase,
      formatDate,
      formatFileSize,
      scrollToUpload,
      triggerUpload
    }
  }
}
</script>

<style scoped>
.knowledge-base-container {
  padding: 20px 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.upload-dragger {
  width: 100%;
}

.upload-progress {
  margin-top: 16px;
}

.search-results {
  margin-top: 16px;
}

.search-result-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #fafafa;
}

.result-source {
  font-size: 12px;
  color: #409eff;
  font-weight: bold;
  margin-bottom: 4px;
}

.result-content {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-score {
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.loading-container {
  padding: 20px;
}

.empty-state, .empty-search-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-search-state {
  margin-top: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 30px 20px;
}

.filename {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filename span {
  word-break: break-all;
}
</style>
