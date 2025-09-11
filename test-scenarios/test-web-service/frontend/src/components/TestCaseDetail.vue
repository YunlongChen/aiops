<template>
  <!-- 测试用例详情组件 -->
  <div class="test-case-detail">
    <!-- 详情头部 -->
    <div class="detail-header">
      <div class="header-left">
        <button class="btn btn-outline back-btn" @click="$emit('back')">
          <svg viewBox="0 0 24 24">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" fill="currentColor"/>
          </svg>
          返回
        </button>
        <div class="header-info">
          <h1>{{ testCase.name }}</h1>
          <div class="header-meta">
            <span class="test-case-id">#{{ testCase.id }}</span>
            <span class="priority-badge" :class="`priority-${testCase.priority}`">
              {{ getPriorityDisplayName(testCase.priority) }}
            </span>
            <span class="language-badge" :class="`language-${testCase.script_language}`">
              {{ getLanguageDisplayName(testCase.script_language) }}
            </span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-success" @click="$emit('run', testCase)">
          <svg viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" fill="currentColor"/>
          </svg>
          运行测试
        </button>
        <button class="btn btn-primary" @click="$emit('edit', testCase)">
          <svg viewBox="0 0 24 24">
            <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="currentColor"/>
          </svg>
          编辑
        </button>
      </div>
    </div>

    <!-- 详情内容 -->
    <div class="detail-content">
      <!-- 基本信息 -->
      <div class="detail-section">
        <h2 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="currentColor"/>
          </svg>
          基本信息
        </h2>
        <div class="info-grid">
          <div class="info-item">
            <label>描述</label>
            <p>{{ testCase.description || '暂无描述' }}</p>
          </div>
          <div class="info-item">
            <label>标签</label>
            <div class="tags" v-if="testCase.tags && testCase.tags.length > 0">
              <span v-for="tag in testCase.tags" :key="tag" class="tag">
                {{ tag }}
              </span>
            </div>
            <p v-else class="no-data">暂无标签</p>
          </div>
          <div class="info-item">
            <label>创建时间</label>
            <p>{{ formatDateTime(testCase.created_at) }}</p>
          </div>
          <div class="info-item">
            <label>更新时间</label>
            <p>{{ formatDateTime(testCase.updated_at) }}</p>
          </div>
        </div>
      </div>

      <!-- 运行时配置 -->
      <div class="detail-section">
        <h2 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
          </svg>
          运行时配置
        </h2>
        <div class="config-grid">
          <div class="config-item">
            <label>Docker镜像</label>
            <code>{{ testCase.docker_image || '默认镜像' }}</code>
          </div>
          <div class="config-item">
            <label>超时时间</label>
            <span>{{ testCase.timeout || 300 }} 秒</span>
          </div>
          <div class="config-item">
            <label>内存限制</label>
            <span>{{ testCase.memory_limit || 512 }} MB</span>
          </div>
          <div class="config-item">
            <label>CPU限制</label>
            <span>{{ testCase.cpu_limit || 1.0 }} 核</span>
          </div>
        </div>
      </div>

      <!-- 环境变量 -->
      <div class="detail-section">
        <h2 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="currentColor"/>
          </svg>
          环境变量
        </h2>
        <div class="env-variables" v-if="testCase.environment_variables && testCase.environment_variables.length > 0">
          <div v-for="env in testCase.environment_variables" :key="env.key" class="env-item">
            <code class="env-key">{{ env.key }}</code>
            <span class="env-separator">=</span>
            <code class="env-value">{{ env.value }}</code>
          </div>
        </div>
        <p v-else class="no-data">暂无环境变量</p>
      </div>

      <!-- 测试脚本 -->
      <div class="detail-section">
        <h2 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0L19.2 12l-4.6-4.6L16 6l6 6-6 6-1.4-1.4z" fill="currentColor"/>
          </svg>
          测试脚本
          <button class="copy-btn" @click="copyScript" title="复制脚本">
            <svg viewBox="0 0 24 24">
              <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z" fill="currentColor"/>
            </svg>
          </button>
        </h2>
        <div class="script-container">
          <pre class="script-content"><code :class="`language-${testCase.script_language}`">{{ testCase.test_script }}</code></pre>
        </div>
      </div>

      <!-- 预期结果 -->
      <div class="detail-section">
        <h2 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/>
          </svg>
          预期结果
        </h2>
        <div class="expected-results">
          <div class="result-item">
            <label>预期退出码</label>
            <code>{{ testCase.expected_exit_code || 0 }}</code>
          </div>
          <div class="result-item" v-if="testCase.expected_output">
            <label>预期输出 (正则表达式)</label>
            <code class="regex-pattern">{{ testCase.expected_output }}</code>
          </div>
        </div>
      </div>

      <!-- 运行统计 -->
      <div class="detail-section">
        <h2 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" fill="currentColor"/>
          </svg>
          运行统计
        </h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ testCase.run_count || 0 }}</div>
            <div class="stat-label">总运行次数</div>
          </div>
          <div class="stat-card success">
            <div class="stat-value">{{ testCase.success_count || 0 }}</div>
            <div class="stat-label">成功次数</div>
          </div>
          <div class="stat-card error">
            <div class="stat-value">{{ (testCase.run_count || 0) - (testCase.success_count || 0) }}</div>
            <div class="stat-label">失败次数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ getSuccessRate(testCase) }}%</div>
            <div class="stat-label">成功率</div>
          </div>
        </div>
      </div>

      <!-- 运行历史 -->
      <div class="detail-section">
        <h2 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z" fill="currentColor"/>
          </svg>
          运行历史
          <button class="refresh-btn" @click="$emit('refresh-history')" title="刷新历史">
            <svg viewBox="0 0 24 24">
              <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor"/>
            </svg>
          </button>
        </h2>
        
        <div v-if="loadingHistory" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载运行历史...</p>
        </div>
        
        <div v-else-if="runHistory.length === 0" class="empty-state">
          <svg class="empty-icon" viewBox="0 0 24 24">
            <path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z" fill="currentColor"/>
          </svg>
          <h3>暂无运行历史</h3>
          <p>点击上方"运行测试"按钮开始第一次测试</p>
        </div>
        
        <div v-else class="history-list">
          <div 
            v-for="run in runHistory" 
            :key="run.id"
            class="history-item"
            :class="{ 'expanded': expandedRuns.includes(run.id) }"
          >
            <div class="history-header" @click="toggleRunExpansion(run.id)">
              <div class="history-info">
                <div class="status-indicator" :class="run.status">
                  <svg v-if="run.status === 'success'" viewBox="0 0 24 24">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/>
                  </svg>
                  <svg v-else-if="run.status === 'failed'" viewBox="0 0 24 24">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" fill="currentColor"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                  </svg>
                </div>
                <div class="history-details">
                  <div class="history-title">
                    运行 #{{ run.id }}
                    <span class="status-text" :class="run.status">
                      {{ getStatusDisplayName(run.status) }}
                    </span>
                  </div>
                  <div class="history-meta">
                    <span>{{ formatDateTime(run.started_at) }}</span>
                    <span v-if="run.duration">耗时: {{ formatDuration(run.duration) }}</span>
                    <span v-if="run.exit_code !== undefined">退出码: {{ run.exit_code }}</span>
                  </div>
                </div>
              </div>
              <div class="expand-icon">
                <svg viewBox="0 0 24 24">
                  <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z" fill="currentColor"/>
                </svg>
              </div>
            </div>
            
            <div class="history-content" v-if="expandedRuns.includes(run.id)">
              <div class="output-section" v-if="run.output">
                <h4>输出内容</h4>
                <pre class="output-content">{{ run.output }}</pre>
              </div>
              
              <div class="error-section" v-if="run.error">
                <h4>错误信息</h4>
                <pre class="error-content">{{ run.error }}</pre>
              </div>
              
              <div class="run-details">
                <div class="detail-row">
                  <span class="detail-label">运行环境:</span>
                  <span>{{ run.runtime_manager || '默认' }}</span>
                </div>
                <div class="detail-row" v-if="run.docker_image">
                  <span class="detail-label">Docker镜像:</span>
                  <code>{{ run.docker_image }}</code>
                </div>
                <div class="detail-row">
                  <span class="detail-label">开始时间:</span>
                  <span>{{ formatDateTime(run.started_at) }}</span>
                </div>
                <div class="detail-row" v-if="run.finished_at">
                  <span class="detail-label">结束时间:</span>
                  <span>{{ formatDateTime(run.finished_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import errorHandler from '@/services/errorHandler'

export default {
  name: 'TestCaseDetail',
  
  props: {
    testCase: {
      type: Object,
      required: true
    },
    runHistory: {
      type: Array,
      default: () => []
    },
    loadingHistory: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['back', 'edit', 'run', 'refresh-history'],
  
  setup(props, { emit }) {
    const expandedRuns = ref([])
    
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
     * 获取状态显示名称
     */
    const getStatusDisplayName = (status) => {
      const names = {
        success: '成功',
        failed: '失败',
        running: '运行中',
        pending: '等待中',
        cancelled: '已取消'
      }
      return names[status] || status
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
     * 格式化日期时间
     */
    const formatDateTime = (dateString) => {
      if (!dateString) return '未知'
      
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
    
    /**
     * 格式化持续时间
     */
    const formatDuration = (seconds) => {
      if (seconds < 60) {
        return `${seconds}秒`
      } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60)
        const remainingSeconds = seconds % 60
        return `${minutes}分${remainingSeconds}秒`
      } else {
        const hours = Math.floor(seconds / 3600)
        const minutes = Math.floor((seconds % 3600) / 60)
        return `${hours}小时${minutes}分钟`
      }
    }
    
    /**
     * 复制脚本
     */
    const copyScript = async () => {
      try {
        await navigator.clipboard.writeText(props.testCase.test_script)
        errorHandler.showSuccess('脚本已复制到剪贴板')
      } catch (error) {
        errorHandler.showError('复制失败，请手动选择复制')
      }
    }
    
    /**
     * 切换运行记录展开状态
     */
    const toggleRunExpansion = (runId) => {
      const index = expandedRuns.value.indexOf(runId)
      if (index > -1) {
        expandedRuns.value.splice(index, 1)
      } else {
        expandedRuns.value.push(runId)
      }
    }
    
    return {
      expandedRuns,
      getLanguageDisplayName,
      getPriorityDisplayName,
      getStatusDisplayName,
      getSuccessRate,
      formatDateTime,
      formatDuration,
      copyScript,
      toggleRunExpansion
    }
  }
}
</script>

<style scoped>
.test-case-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* 详情头部 */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.back-btn {
  margin-top: 4px;
}

.header-info h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #111827;
  line-height: 1.2;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.test-case-id {
  font-size: 14px;
  color: #6b7280;
  font-family: monospace;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 详情内容 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.detail-section {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #374151;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: #6b7280;
}

.copy-btn,
.refresh-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  margin-left: auto;
  transition: all 0.2s ease;
}

.copy-btn:hover,
.refresh-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.copy-btn svg,
.refresh-btn svg {
  width: 16px;
  height: 16px;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item label {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.info-item p {
  margin: 0;
  color: #6b7280;
  line-height: 1.5;
}

.no-data {
  color: #9ca3af !important;
  font-style: italic;
}

/* 配置网格 */
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.config-item label {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.config-item code {
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  font-family: monospace;
}

/* 标签 */
.tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  background: #f3f4f6;
  color: #374151;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

/* 徽章样式 */
.language-badge,
.priority-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
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

/* 环境变量 */
.env-variables {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.env-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
  font-family: monospace;
  font-size: 13px;
}

.env-key {
  color: #059669;
  font-weight: 500;
}

.env-separator {
  color: #6b7280;
}

.env-value {
  color: #dc2626;
}

/* 脚本容器 */
.script-container {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.script-content {
  margin: 0;
  padding: 16px;
  background: #f9fafb;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 预期结果 */
.expected-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-item label {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.regex-pattern {
  background: #fef3c7;
  color: #92400e;
  padding: 8px 12px;
  border-radius: 6px;
  font-family: monospace;
  font-size: 13px;
  word-break: break-all;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.stat-card.success {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.stat-card.error {
  background: #fef2f2;
  border-color: #fecaca;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
}

.stat-card.success .stat-value {
  color: #059669;
}

.stat-card.error .stat-value {
  color: #dc2626;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

/* 加载和空状态 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: #d1d5db;
  margin-bottom: 12px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #374151;
}

.empty-state p {
  margin: 0;
  color: #6b7280;
}

/* 运行历史 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.history-item.expanded {
  border-color: #3b82f6;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  background: #f9fafb;
  transition: background-color 0.2s ease;
}

.history-header:hover {
  background: #f3f4f6;
}

.history-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.status-indicator.success {
  background: #dcfce7;
  color: #059669;
}

.status-indicator.failed {
  background: #fef2f2;
  color: #dc2626;
}

.status-indicator.running {
  background: #dbeafe;
  color: #2563eb;
}

.status-indicator svg {
  width: 16px;
  height: 16px;
}

.history-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-title {
  font-weight: 500;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-text {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.status-text.success {
  background: #dcfce7;
  color: #059669;
}

.status-text.failed {
  background: #fef2f2;
  color: #dc2626;
}

.status-text.running {
  background: #dbeafe;
  color: #2563eb;
}

.history-meta {
  font-size: 12px;
  color: #6b7280;
  display: flex;
  gap: 12px;
}

.expand-icon {
  color: #6b7280;
  transition: transform 0.2s ease;
}

.history-item.expanded .expand-icon {
  transform: rotate(180deg);
}

.expand-icon svg {
  width: 20px;
  height: 20px;
}

.history-content {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  background: white;
}

.output-section,
.error-section {
  margin-bottom: 20px;
}

.output-section h4,
.error-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.output-content,
.error-content {
  margin: 0;
  padding: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-family: monospace;
  font-size: 12px;
  line-height: 1.4;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

.error-content {
  background: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

.run-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.detail-label {
  font-weight: 500;
  color: #374151;
  min-width: 80px;
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

.btn-success {
  background: #059669;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #047857;
}

.btn-outline {
  background: none;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-outline:hover {
  background: #f9fafb;
}

.btn svg {
  width: 16px;
  height: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .test-case-detail {
    padding: 16px;
  }
  
  .detail-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-left {
    flex-direction: column;
    gap: 12px;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .info-grid,
  .config-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .history-meta {
    flex-direction: column;
    gap: 4px;
  }
  
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .detail-label {
    min-width: auto;
  }
}
</style>