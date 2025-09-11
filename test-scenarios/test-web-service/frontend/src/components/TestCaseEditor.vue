<template>
  <!-- 测试用例详细编辑器 -->
  <div class="test-case-editor">
    <!-- 编辑器头部 -->
    <div class="editor-header">
      <div class="editor-title">
        <h2 v-if="isEditing">编辑测试用例</h2>
        <h2 v-else>创建测试用例</h2>
        <span v-if="testCase.id" class="test-case-id">ID: {{ testCase.id }}</span>
      </div>
      <div class="editor-actions">
        <button 
          class="btn btn-secondary" 
          @click="$emit('cancel')"
          :disabled="saving"
        >
          取消
        </button>
        <button 
          class="btn btn-primary" 
          @click="saveTestCase"
          :disabled="saving || !isValid"
        >
          <span v-if="saving">保存中...</span>
          <span v-else>{{ isEditing ? '更新' : '创建' }}</span>
        </button>
      </div>
    </div>

    <!-- 编辑器内容 -->
    <div class="editor-content">
      <!-- 基本信息 -->
      <div class="editor-section">
        <h3 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="currentColor"/>
          </svg>
          基本信息
        </h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="name">测试用例名称 *</label>
            <input
              id="name"
              v-model="testCase.name"
              type="text"
              class="form-control"
              placeholder="请输入测试用例名称"
              :class="{ 'is-invalid': errors.name }"
            >
            <div v-if="errors.name" class="invalid-feedback">{{ errors.name }}</div>
          </div>
          
          <div class="form-group">
            <label for="description">描述</label>
            <textarea
              id="description"
              v-model="testCase.description"
              class="form-control"
              rows="3"
              placeholder="请输入测试用例描述"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="tags">标签</label>
            <div class="tags-input">
              <div class="tags-list">
                <span 
                  v-for="(tag, index) in testCase.tags" 
                  :key="index" 
                  class="tag"
                >
                  {{ tag }}
                  <button 
                    type="button" 
                    class="tag-remove"
                    @click="removeTag(index)"
                  >
                    ×
                  </button>
                </span>
              </div>
              <input
                v-model="newTag"
                type="text"
                class="tag-input"
                placeholder="添加标签"
                @keydown.enter.prevent="addTag"
                @keydown.comma.prevent="addTag"
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="priority">优先级</label>
            <select id="priority" v-model="testCase.priority" class="form-control">
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
              <option value="critical">紧急</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 脚本配置 -->
      <div class="editor-section">
        <h3 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0L19.2 12l-4.6-4.6L16 6l6 6-6 6-1.4-1.4z" fill="currentColor"/>
          </svg>
          脚本配置
        </h3>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="script_language">脚本语言 *</label>
            <select 
              id="script_language" 
              v-model="testCase.script_language" 
              class="form-control"
              :class="{ 'is-invalid': errors.script_language }"
            >
              <option value="">请选择脚本语言</option>
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="bash">Bash</option>
              <option value="powershell">PowerShell</option>
              <option value="go">Go</option>
              <option value="rust">Rust</option>
            </select>
            <div v-if="errors.script_language" class="invalid-feedback">{{ errors.script_language }}</div>
          </div>
          
          <div class="form-group full-width">
            <label for="test_script">测试脚本 *</label>
            <div class="script-editor">
              <div class="script-toolbar">
                <button 
                  type="button" 
                  class="toolbar-btn"
                  @click="formatScript"
                  title="格式化代码"
                >
                  <svg viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="currentColor"/>
                  </svg>
                  格式化
                </button>
                <button 
                  type="button" 
                  class="toolbar-btn"
                  @click="validateScript"
                  title="验证脚本"
                >
                  <svg viewBox="0 0 24 24">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/>
                  </svg>
                  验证
                </button>
                <button 
                  type="button" 
                  class="toolbar-btn"
                  @click="insertTemplate"
                  title="插入模板"
                >
                  <svg viewBox="0 0 24 24">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" fill="currentColor"/>
                  </svg>
                  模板
                </button>
              </div>
              <textarea
                id="test_script"
                v-model="testCase.test_script"
                class="script-textarea"
                :placeholder="getScriptPlaceholder()"
                :class="{ 'is-invalid': errors.test_script }"
                rows="15"
                spellcheck="false"
              ></textarea>
              <div v-if="errors.test_script" class="invalid-feedback">{{ errors.test_script }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 运行时配置 -->
      <div class="editor-section">
        <h3 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
          </svg>
          运行时配置
        </h3>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="docker_image">Docker镜像</label>
            <input
              id="docker_image"
              v-model="testCase.docker_image"
              type="text"
              class="form-control"
              placeholder="例如: python:3.9-slim"
            >
            <small class="form-text">留空将使用默认镜像</small>
          </div>
          
          <div class="form-group">
            <label for="timeout">超时时间 (秒)</label>
            <input
              id="timeout"
              v-model.number="testCase.timeout"
              type="number"
              class="form-control"
              min="1"
              max="3600"
              placeholder="300"
            >
          </div>
          
          <div class="form-group">
            <label for="memory_limit">内存限制 (MB)</label>
            <input
              id="memory_limit"
              v-model.number="testCase.memory_limit"
              type="number"
              class="form-control"
              min="64"
              max="8192"
              placeholder="512"
            >
          </div>
          
          <div class="form-group">
            <label for="cpu_limit">CPU限制 (核数)</label>
            <input
              id="cpu_limit"
              v-model.number="testCase.cpu_limit"
              type="number"
              class="form-control"
              min="0.1"
              max="8"
              step="0.1"
              placeholder="1.0"
            >
          </div>
        </div>
      </div>

      <!-- 环境变量 -->
      <div class="editor-section">
        <h3 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="currentColor"/>
          </svg>
          环境变量
          <button 
            type="button" 
            class="btn-add-env"
            @click="addEnvironmentVariable"
            title="添加环境变量"
          >
            <svg viewBox="0 0 24 24">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor"/>
            </svg>
          </button>
        </h3>
        
        <div class="env-variables">
          <div 
            v-for="(env, index) in testCase.environment_variables" 
            :key="index" 
            class="env-variable"
          >
            <input
              v-model="env.key"
              type="text"
              class="env-key"
              placeholder="变量名"
            >
            <input
              v-model="env.value"
              type="text"
              class="env-value"
              placeholder="变量值"
            >
            <button 
              type="button" 
              class="btn-remove-env"
              @click="removeEnvironmentVariable(index)"
              title="删除环境变量"
            >
              <svg viewBox="0 0 24 24">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" fill="currentColor"/>
              </svg>
            </button>
          </div>
          
          <div v-if="testCase.environment_variables.length === 0" class="no-env-variables">
            <p>暂无环境变量</p>
            <button 
              type="button" 
              class="btn btn-outline"
              @click="addEnvironmentVariable"
            >
              添加环境变量
            </button>
          </div>
        </div>
      </div>

      <!-- 预期结果 -->
      <div class="editor-section">
        <h3 class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/>
          </svg>
          预期结果
        </h3>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="expected_exit_code">预期退出码</label>
            <input
              id="expected_exit_code"
              v-model.number="testCase.expected_exit_code"
              type="number"
              class="form-control"
              min="0"
              max="255"
              placeholder="0"
            >
          </div>
          
          <div class="form-group full-width">
            <label for="expected_output">预期输出 (正则表达式)</label>
            <textarea
              id="expected_output"
              v-model="testCase.expected_output"
              class="form-control"
              rows="3"
              placeholder="例如: ^Success.*completed$"
            ></textarea>
            <small class="form-text">支持正则表达式匹配输出内容</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import errorHandler from '@/services/errorHandler'

export default {
  name: 'TestCaseEditor',
  
  props: {
    testCase: {
      type: Object,
      default: () => ({
        id: null,
        name: '',
        description: '',
        tags: [],
        priority: 'medium',
        script_language: '',
        test_script: '',
        docker_image: '',
        timeout: 300,
        memory_limit: 512,
        cpu_limit: 1.0,
        environment_variables: [],
        expected_exit_code: 0,
        expected_output: ''
      })
    }
  },
  
  emits: ['save', 'cancel'],
  
  setup(props, { emit }) {
    const saving = ref(false)
    const newTag = ref('')
    const errors = ref({})
    
    /**
     * 是否为编辑模式
     */
    const isEditing = computed(() => {
      return props.testCase.id !== null && props.testCase.id !== undefined
    })
    
    /**
     * 表单验证
     */
    const isValid = computed(() => {
      return props.testCase.name && 
             props.testCase.script_language && 
             props.testCase.test_script &&
             Object.keys(errors.value).length === 0
    })
    
    /**
     * 验证表单
     */
    const validateForm = () => {
      const newErrors = {}
      
      if (!props.testCase.name) {
        newErrors.name = '测试用例名称不能为空'
      }
      
      if (!props.testCase.script_language) {
        newErrors.script_language = '请选择脚本语言'
      }
      
      if (!props.testCase.test_script) {
        newErrors.test_script = '测试脚本不能为空'
      }
      
      errors.value = newErrors
      return Object.keys(newErrors).length === 0
    }
    
    /**
     * 获取脚本占位符
     */
    const getScriptPlaceholder = () => {
      const placeholders = {
        python: `# Python 测试脚本示例\n# 请编写您的测试逻辑\n\nprint("Hello, World!")\nassert 1 + 1 == 2, "数学计算错误"\nprint("测试通过")
`,
        javascript: `// JavaScript 测试脚本示例\n// 请编写您的测试逻辑\n\nconsole.log("Hello, World!");\nif (1 + 1 !== 2) {\n  throw new Error("数学计算错误");\n}\nconsole.log("测试通过");
`,
        bash: `#!/bin/bash\n# Bash 测试脚本示例\n# 请编写您的测试逻辑\n\necho "Hello, World!"\nif [ $((1 + 1)) -ne 2 ]; then\n  echo "数学计算错误" >&2\n  exit 1\nfi\necho "测试通过"
`,
        powershell: `# PowerShell 测试脚本示例\n# 请编写您的测试逻辑\n\nWrite-Host "Hello, World!"\nif ((1 + 1) -ne 2) {\n  Write-Error "数学计算错误"\n  exit 1\n}\nWrite-Host "测试通过"
`,
        go: `package main\n\nimport "fmt"\n\n// Go 测试脚本示例\n// 请编写您的测试逻辑\n\nfunc main() {\n\tfmt.Println("Hello, World!")\n\tif 1+1 != 2 {\n\t\tpanic("数学计算错误")\n\t}\n\tfmt.Println("测试通过")\n}
`,
        rust: `// Rust 测试脚本示例\n// 请编写您的测试逻辑\n\nfn main() {\n    println!("Hello, World!");\n    assert_eq!(1 + 1, 2, "数学计算错误");\n    println!("测试通过");\n}
`
      }
      
      return placeholders[props.testCase.script_language] || '请编写您的测试脚本...'
    }
    
    /**
     * 添加标签
     */
    const addTag = () => {
      const tag = newTag.value.trim()
      if (tag && !props.testCase.tags.includes(tag)) {
        props.testCase.tags.push(tag)
        newTag.value = ''
      }
    }
    
    /**
     * 移除标签
     */
    const removeTag = (index) => {
      props.testCase.tags.splice(index, 1)
    }
    
    /**
     * 添加环境变量
     */
    const addEnvironmentVariable = () => {
      props.testCase.environment_variables.push({
        key: '',
        value: ''
      })
    }
    
    /**
     * 移除环境变量
     */
    const removeEnvironmentVariable = (index) => {
      props.testCase.environment_variables.splice(index, 1)
    }
    
    /**
     * 格式化脚本
     */
    const formatScript = () => {
      // 简单的格式化逻辑
      try {
        let script = props.testCase.test_script
        // 移除多余的空行
        script = script.replace(/\n\s*\n\s*\n/g, '\n\n')
        // 移除行尾空格
        script = script.replace(/[ \t]+$/gm, '')
        props.testCase.test_script = script
        
        errorHandler.showSuccess('脚本格式化完成')
      } catch (error) {
        errorHandler.handleValidationError('脚本格式化失败: ' + error.message)
      }
    }
    
    /**
     * 验证脚本
     */
    const validateScript = async () => {
      try {
        // 这里可以调用后端API进行脚本验证
        errorHandler.showInfo('脚本验证功能开发中...')
      } catch (error) {
        errorHandler.handleValidationError('脚本验证失败: ' + error.message)
      }
    }
    
    /**
     * 插入模板
     */
    const insertTemplate = () => {
      if (props.testCase.script_language) {
        props.testCase.test_script = getScriptPlaceholder()
        errorHandler.showSuccess('模板插入成功')
      } else {
        errorHandler.showWarning('请先选择脚本语言')
      }
    }
    
    /**
     * 保存测试用例
     */
    const saveTestCase = async () => {
      if (!validateForm()) {
        errorHandler.showWarning('请检查表单输入')
        return
      }
      
      saving.value = true
      
      try {
        // 清理环境变量（移除空的键值对）
        const cleanedEnvVars = props.testCase.environment_variables.filter(
          env => env.key.trim() && env.value.trim()
        )
        
        const testCaseData = {
          ...props.testCase,
          environment_variables: cleanedEnvVars
        }
        
        emit('save', testCaseData)
        
      } catch (error) {
        errorHandler.handleValidationError('保存失败: ' + error.message)
      } finally {
        saving.value = false
      }
    }
    
    // 监听脚本语言变化，自动更新占位符
    watch(
      () => props.testCase.script_language,
      (newLang) => {
        if (newLang && !props.testCase.test_script) {
          // 如果脚本为空，自动插入模板
          setTimeout(() => {
            if (!props.testCase.test_script) {
              insertTemplate()
            }
          }, 100)
        }
      }
    )
    
    return {
      saving,
      newTag,
      errors,
      isEditing,
      isValid,
      getScriptPlaceholder,
      addTag,
      removeTag,
      addEnvironmentVariable,
      removeEnvironmentVariable,
      formatScript,
      validateScript,
      insertTemplate,
      saveTestCase
    }
  }
}
</script>

<style scoped>
.test-case-editor {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.editor-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.test-case-id {
  font-size: 14px;
  color: #6b7280;
  margin-left: 12px;
}

.editor-actions {
  display: flex;
  gap: 12px;
}

.editor-content {
  padding: 24px;
}

.editor-section {
  margin-bottom: 32px;
}

.editor-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: #6b7280;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
  font-size: 14px;
}

.form-control {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control.is-invalid {
  border-color: #ef4444;
}

.invalid-feedback {
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
}

.form-text {
  color: #6b7280;
  font-size: 12px;
  margin-top: 4px;
}

/* 标签输入 */
.tags-input {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 8px;
  min-height: 40px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  background: #3b82f6;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag-remove {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
}

.tag-remove:hover {
  background: rgba(255, 255, 255, 0.2);
}

.tag-input {
  border: none;
  outline: none;
  flex: 1;
  min-width: 100px;
  font-size: 14px;
}

/* 脚本编辑器 */
.script-editor {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  overflow: hidden;
}

.script-toolbar {
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  padding: 8px 12px;
  display: flex;
  gap: 8px;
}

.toolbar-btn {
  background: none;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: #6b7280;
  transition: all 0.2s ease;
}

.toolbar-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.toolbar-btn svg {
  width: 14px;
  height: 14px;
}

.script-textarea {
  width: 100%;
  border: none;
  outline: none;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  resize: vertical;
  min-height: 300px;
}

/* 环境变量 */
.env-variables {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.env-variable {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 8px;
  align-items: center;
}

.env-key,
.env-value {
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
}

.btn-add-env,
.btn-remove-env {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.btn-add-env {
  color: #3b82f6;
  margin-left: auto;
}

.btn-add-env:hover {
  background: #eff6ff;
}

.btn-remove-env {
  color: #ef4444;
}

.btn-remove-env:hover {
  background: #fef2f2;
}

.btn-add-env svg,
.btn-remove-env svg {
  width: 16px;
  height: 16px;
}

.no-env-variables {
  text-align: center;
  padding: 24px;
  color: #6b7280;
}

.no-env-variables p {
  margin: 0 0 12px 0;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .editor-actions {
    justify-content: stretch;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .env-variable {
    grid-template-columns: 1fr;
    gap: 4px;
  }
  
  .script-toolbar {
    flex-wrap: wrap;
  }
}
</style>