<template>
  <!-- 测试用例列表组件 -->
  <div class="test-case-list">
    <!-- 列表头部 -->
    <div class="list-header">
      <div class="header-left">
        <h2>测试用例管理</h2>
        <span class="case-count">共 {{ filteredTestCases.length }} 个测试用例</span>
      </div>
      <div class="header-right">
        <button 
          class="btn btn-primary"
          @click="$emit('create')"
        >
          <svg viewBox="0 0 24 24">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor"/>
          </svg>
          创建测试用例
        </button>
      </div>
    </div>

    <!-- 搜索和过滤 -->
    <div class="list-filters">
      <div class="search-box">
        <svg class="search-icon" viewBox="0 0 24 24">
          <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" fill="currentColor"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索测试用例..."
          class="search-input"
        >
      </div>
      
      <div class="filter-controls">
        <select v-model="filterPriority" class="filter-select">
          <option value="">所有优先级</option>
          <option value="low">低</option>
          <option value="medium">中</option>
          <option value="high">高</option>
          <option value="critical">紧急</option>
        </select>
        
        <select v-model="filterLanguage" class="filter-select">
          <option value="">所有语言</option>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="bash">Bash</option>
          <option value="powershell">PowerShell</option>
          <option value="go">Go</option>
          <option value="rust">Rust</option>
        </select>
        
        <button 
          class="btn btn-outline"
          @click="clearFilters"
          v-if="hasActiveFilters"
        >
          清除筛选
        </button>
      </div>
    </div>

    <!-- 测试用例列表 -->
    <div class="list-content">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="filteredTestCases.length === 0" class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="currentColor"/>
        </svg>
        <h3>{{ searchQuery || filterPriority || filterLanguage ? '未找到匹配的测试用例' : '暂无测试用例' }}</h3>
        <p>{{ searchQuery || filterPriority || filterLanguage ? '请尝试调整搜索条件' : '点击上方按钮创建您的第一个测试用例' }}</p>
        <button 
          v-if="!searchQuery && !filterPriority && !filterLanguage"
          class="btn btn-primary"
          @click="$emit('create')"
        >
          创建测试用例
        </button>
      </div>
      
      <div v-else class="test-cases-grid">
        <div 
          v-for="testCase in paginatedTestCases" 
          :key="testCase.id"
          class="test-case-card"
          @click="$emit('view', testCase)"
        >
          <!-- 卡片头部 -->
          <div class="card-header">
            <div class="card-title">
              <h3>{{ testCase.name }}</h3>
              <span class="test-case-id">#{{ testCase.id }}</span>
            </div>
            <div class="card-actions" @click.stop>
              <button 
                class="action-btn"
                @click="$emit('run', testCase)"
                title="运行测试"
              >
                <svg viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z" fill="currentColor"/>
                </svg>
              </button>
              <button 
                class="action-btn"
                @click="$emit('edit', testCase)"
                title="编辑"
              >
                <svg viewBox="0 0 24 24">
                  <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="currentColor"/>
                </svg>
              </button>
              <button 
                class="action-btn delete-btn"
                @click="confirmDelete(testCase)"
                title="删除"
              >
                <svg viewBox="0 0 24 24">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" fill="currentColor"/>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 卡片内容 -->
          <div class="card-content">
            <p class="card-description">{{ testCase.description || '暂无描述' }}</p>
            
            <div class="card-meta">
              <div class="meta-item">
                <span class="meta-label">语言:</span>
                <span class="language-badge" :class="`language-${testCase.script_language}`">
                  {{ getLanguageDisplayName(testCase.script_language) }}
                </span>
              </div>
              
              <div class="meta-item">
                <span class="meta-label">优先级:</span>
                <span class="priority-badge" :class="`priority-${testCase.priority}`">
                  {{ getPriorityDisplayName(testCase.priority) }}
                </span>
              </div>
              
              <div class="meta-item" v-if="testCase.tags && testCase.tags.length > 0">
                <span class="meta-label">标签:</span>
                <div class="tags">
                  <span 
                    v-for="tag in testCase.tags.slice(0, 3)" 
                    :key="tag" 
                    class="tag"
                  >
                    {{ tag }}
                  </span>
                  <span v-if="testCase.tags.length > 3" class="tag-more">
                    +{{ testCase.tags.length - 3 }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="card-stats">
              <div class="stat-item">
                <svg viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                </svg>
                <span>{{ testCase.run_count || 0 }} 次运行</span>
              </div>
              
              <div class="stat-item">
                <svg viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="currentColor"/>
                </svg>
                <span>{{ getSuccessRate(testCase) }}% 成功率</span>
              </div>
              
              <div class="stat-item">
                <svg viewBox="0 0 24 24">
                  <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zM12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z" fill="currentColor"/>
                </svg>
                <span>{{ formatDate(testCase.updated_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          class="pagination-btn"
          @click="currentPage = 1"
          :disabled="currentPage === 1"
        >
          首页
        </button>
        <button 
          class="pagination-btn"
          @click="currentPage--"
          :disabled="currentPage === 1"
        >
          上一页
        </button>
        
        <div class="pagination-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页
        </div>
        
        <button 
          class="pagination-btn"
          @click="currentPage++"
          :disabled="currentPage === totalPages"
        >
          下一页
        </button>
        <button 
          class="pagination-btn"
          @click="currentPage = totalPages"
          :disabled="currentPage === totalPages"
        >
          末页
        </button>
      </div>
    </div>
    
    <!-- 删除确认对话框 -->
    <div v-if="showDeleteDialog" class="dialog-overlay" @click="cancelDelete">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>确认删除</h3>
        </div>
        <div class="dialog-content">
          <p>确定要删除测试用例 "{{ deleteTarget?.name }}" 吗？</p>
          <p class="warning-text">此操作不可撤销，相关的运行记录也将被删除。</p>
        </div>
        <div class="dialog-actions">
          <button class="btn btn-secondary" @click="cancelDelete">取消</button>
          <button class="btn btn-danger" @click="deleteTestCase">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import errorHandler from '@/services/errorHandler'

export default {
  name: 'TestCaseList',
  
  props: {
    testCases: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['create', 'edit', 'view', 'run', 'delete'],
  
  setup(props, { emit }) {
    const searchQuery = ref('')
    const filterPriority = ref('')
    const filterLanguage = ref('')
    const currentPage = ref(1)
    const pageSize = ref(12)
    const showDeleteDialog = ref(false)
    const deleteTarget = ref(null)
    
    /**
     * 是否有活跃的筛选条件
     */
    const hasActiveFilters = computed(() => {
      return searchQuery.value || filterPriority.value || filterLanguage.value
    })
    
    /**
     * 过滤后的测试用例
     */
    const filteredTestCases = computed(() => {
      let filtered = [...props.testCases]
      
      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(testCase => 
          testCase.name.toLowerCase().includes(query) ||
          (testCase.description && testCase.description.toLowerCase().includes(query)) ||
          (testCase.tags && testCase.tags.some(tag => tag.toLowerCase().includes(query)))
        )
      }
      
      // 优先级过滤
      if (filterPriority.value) {
        filtered = filtered.filter(testCase => testCase.priority === filterPriority.value)
      }
      
      // 语言过滤
      if (filterLanguage.value) {
        filtered = filtered.filter(testCase => testCase.script_language === filterLanguage.value)
      }
      
      return filtered
    })
    
    /**
     * 总页数
     */
    const totalPages = computed(() => {
      return Math.ceil(filteredTestCases.value.length / pageSize.value)
    })
    
    /**
     * 分页后的测试用例
     */
    const paginatedTestCases = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredTestCases.value.slice(start, end)
    })
    
    /**
     * 获取语言显示名称
     */
    const getLanguageDisplayName = (language) => {
      const names = {
        python: 'Python',
        javascript: 'JavaScript',
        bash: 'Bash',
        powershell: 'PowerShell',
        go: 'Go',
        rust: 'Rust'
      }
      return names[language] || language
    }
    
    /**
     * 获取优先级显示名称
     */
    const getPriorityDisplayName = (priority) => {
      const names = {
        low: '低',
        medium: '中',
        high: '高',
        critical: '紧急'
      }
      return names[priority] || priority
    }
    
    /**
     * 获取成功率
     */
    const getSuccessRate = (testCase) => {
      if (!testCase.run_count || testCase.run_count === 0) {
        return 0
      }
      const successCount = testCase.success_count || 0
      return Math.round((successCount / testCase.run_count) * 100)
    }
    
    /**
     * 格式化日期
     */
    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now - date
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return '今天'
      } else if (diffDays === 1) {
        return '昨天'
      } else if (diffDays < 7) {
        return `${diffDays}天前`
      } else {
        return date.toLocaleDateString('zh-CN')
      }
    }
    
    /**
     * 清除筛选条件
     */
    const clearFilters = () => {
      searchQuery.value = ''
      filterPriority.value = ''
      filterLanguage.value = ''
      currentPage.value = 1
    }
    
    /**
     * 确认删除
     */
    const confirmDelete = (testCase) => {
      deleteTarget.value = testCase
      showDeleteDialog.value = true
    }
    
    /**
     * 取消删除
     */
    const cancelDelete = () => {
      showDeleteDialog.value = false
      deleteTarget.value = null
    }
    
    /**
     * 删除测试用例
     */
    const deleteTestCase = async () => {
      try {
        emit('delete', deleteTarget.value)
        showDeleteDialog.value = false
        deleteTarget.value = null
        errorHandler.showSuccess('测试用例删除成功')
      } catch (error) {
        errorHandler.handleApiError(error)
      }
    }
    
    // 监听筛选条件变化，重置页码
    watch([searchQuery, filterPriority, filterLanguage], () => {
      currentPage.value = 1
    })
    
    return {
      searchQuery,
      filterPriority,
      filterLanguage,
      currentPage,
      pageSize,
      showDeleteDialog,
      deleteTarget,
      hasActiveFilters,
      filteredTestCases,
      totalPages,
      paginatedTestCases,
      getLanguageDisplayName,
      getPriorityDisplayName,
      getSuccessRate,
      formatDate,
      clearFilters,
      confirmDelete,
      cancelDelete,
      deleteTestCase
    }
  }
}
</script>

<style scoped>
.test-case-list {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

/* 列表头部 */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #111827;
}

.case-count {
  color: #6b7280;
  font-size: 14px;
}

/* 搜索和过滤 */
.list-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #6b7280;
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

/* 列表内容 */
.list-content {
  min-height: 400px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #d1d5db;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #374151;
}

.empty-state p {
  margin: 0 0 20px 0;
  color: #6b7280;
}

/* 测试用例网格 */
.test-cases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.test-case-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.test-case-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.card-title h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  line-height: 1.3;
}

.test-case-id {
  font-size: 12px;
  color: #6b7280;
}

.card-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  background: none;
  border: none;
  padding: 6px;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.action-btn.delete-btn:hover {
  background: #fef2f2;
  color: #ef4444;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-description {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.meta-label {
  color: #6b7280;
  min-width: 40px;
}

.language-badge,
.priority-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.language-python { background: #fef3c7; color: #92400e; }
.language-javascript { background: #fef3c7; color: #92400e; }
.language-bash { background: #f3f4f6; color: #374151; }
.language-powershell { background: #dbeafe; color: #1e40af; }
.language-go { background: #ecfdf5; color: #065f46; }
.language-rust { background: #fef2f2; color: #991b1b; }

.priority-low { background: #f0f9ff; color: #0369a1; }
.priority-medium { background: #fef3c7; color: #92400e; }
.priority-high { background: #fef2f2; color: #dc2626; }
.priority-critical { background: #fdf2f8; color: #be185d; }

.tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tag {
  background: #f3f4f6;
  color: #374151;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.tag-more {
  background: #e5e7eb;
  color: #6b7280;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.card-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6b7280;
}

.stat-item svg {
  width: 14px;
  height: 14px;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 32px;
}

.pagination-btn {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  padding: 8px 16px;
  font-size: 14px;
  color: #6b7280;
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow: hidden;
}

.dialog-header {
  padding: 20px 24px 0 24px;
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.dialog-content {
  padding: 16px 24px;
}

.dialog-content p {
  margin: 0 0 12px 0;
  color: #374151;
  line-height: 1.5;
}

.warning-text {
  color: #dc2626;
  font-size: 14px;
}

.dialog-actions {
  padding: 16px 24px 24px 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
}

.btn-outline {
  background: none;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-outline:hover {
  background: #f9fafb;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn svg {
  width: 16px;
  height: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .test-case-list {
    padding: 16px;
  }
  
  .list-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .list-filters {
    flex-direction: column;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .filter-controls {
    flex-wrap: wrap;
  }
  
  .test-cases-grid {
    grid-template-columns: 1fr;
  }
  
  .card-stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .pagination {
    flex-wrap: wrap;
  }
}
</style>