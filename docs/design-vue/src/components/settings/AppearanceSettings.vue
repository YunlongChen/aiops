<!--
  外观主题设置组件
  提供主题切换和颜色配置功能
  @author AI Assistant
  @date 2024-01-24
-->
<template>
  <div class="appearance-settings">
    <!-- 主题设置 -->
    <div class="settings-section">
      <div class="section-header">
        <h2>主题设置</h2>
        <p>自定义系统外观和主题</p>
      </div>
      
      <div class="theme-selector">
        <div 
          class="theme-option" 
          :class="{ active: selectedTheme === 'light' }"
          @click="selectTheme('light')"
        >
          <div class="theme-preview light-theme">
            <div class="preview-header"></div>
            <div class="preview-sidebar"></div>
            <div class="preview-content"></div>
          </div>
          <span>浅色主题</span>
        </div>
        
        <div 
          class="theme-option" 
          :class="{ active: selectedTheme === 'dark' }"
          @click="selectTheme('dark')"
        >
          <div class="theme-preview dark-theme">
            <div class="preview-header"></div>
            <div class="preview-sidebar"></div>
            <div class="preview-content"></div>
          </div>
          <span>深色主题</span>
        </div>
        
        <div 
          class="theme-option" 
          :class="{ active: selectedTheme === 'auto' }"
          @click="selectTheme('auto')"
        >
          <div class="theme-preview auto-theme">
            <div class="preview-header"></div>
            <div class="preview-sidebar"></div>
            <div class="preview-content"></div>
          </div>
          <span>跟随系统</span>
        </div>
      </div>
    </div>

    <!-- 颜色配置 -->
    <div class="settings-section">
      <div class="section-header">
        <h2>颜色配置</h2>
        <p>自定义系统主色调</p>
      </div>
      
      <div class="color-palette">
        <div 
          v-for="color in colorOptions" 
          :key="color"
          class="color-option" 
          :class="{ active: selectedColor === color }"
          :style="{ backgroundColor: color }"
          @click="selectColor(color)"
        ></div>
      </div>
      
      <div class="color-preview">
        <h3>预览效果</h3>
        <div class="preview-elements">
          <button class="btn btn-primary" :style="{ backgroundColor: selectedColor }">
            主要按钮
          </button>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ backgroundColor: selectedColor, width: '60%' }"
            ></div>
          </div>
          <div class="badge" :style="{ backgroundColor: selectedColor }">
            标签
          </div>
        </div>
      </div>
    </div>

    <!-- 布局设置 -->
    <div class="settings-section">
      <div class="section-header">
        <h2>布局设置</h2>
        <p>调整界面布局和显示选项</p>
      </div>
      
      <div class="layout-options">
        <div class="setting-item">
          <label class="switch-label">
            <span>紧凑模式</span>
            <div class="switch">
              <input type="checkbox" v-model="compactMode">
              <span class="slider"></span>
            </div>
          </label>
          <small>减少界面元素间距，显示更多内容</small>
        </div>
        
        <div class="setting-item">
          <label class="switch-label">
            <span>显示侧边栏</span>
            <div class="switch">
              <input type="checkbox" v-model="showSidebar">
              <span class="slider"></span>
            </div>
          </label>
          <small>控制左侧导航栏的显示和隐藏</small>
        </div>
        
        <div class="setting-item">
          <label class="switch-label">
            <span>固定头部</span>
            <div class="switch">
              <input type="checkbox" v-model="fixedHeader">
              <span class="slider"></span>
            </div>
          </label>
          <small>页面滚动时保持头部导航固定</small>
        </div>
        
        <div class="setting-item">
          <label for="fontSize">字体大小</label>
          <select id="fontSize" v-model="fontSize" class="form-select">
            <option value="small">小</option>
            <option value="medium">中</option>
            <option value="large">大</option>
          </select>
          <small>调整界面文字大小</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppearanceSettings',
  data() {
    return {
      selectedTheme: 'light',
      selectedColor: '#4F46E5',
      colorOptions: [
        '#4F46E5', // 蓝色
        '#059669', // 绿色
        '#DC2626', // 红色
        '#7C3AED', // 紫色
        '#EA580C', // 橙色
        '#0891B2'  // 青色
      ],
      compactMode: false,
      showSidebar: true,
      fixedHeader: true,
      fontSize: 'medium'
    }
  },
  methods: {
    /**
     * 选择主题
     */
    selectTheme(theme) {
      this.selectedTheme = theme
      this.applyTheme(theme)
    },

    /**
     * 选择颜色
     */
    selectColor(color) {
      this.selectedColor = color
      this.applyColor(color)
    },

    /**
     * 应用主题
     */
    applyTheme(theme) {
      // TODO: 实际应用主题逻辑
      console.log('应用主题:', theme)
    },

    /**
     * 应用颜色
     */
    applyColor(color) {
      // TODO: 实际应用颜色逻辑
      console.log('应用颜色:', color)
    },

    /**
     * 获取设置数据
     */
    getSettings() {
      return {
        theme: this.selectedTheme,
        primaryColor: this.selectedColor,
        compactMode: this.compactMode,
        showSidebar: this.showSidebar,
        fixedHeader: this.fixedHeader,
        fontSize: this.fontSize
      }
    },

    /**
     * 重置设置到默认值
     */
    resetSettings() {
      this.selectedTheme = 'light'
      this.selectedColor = '#4F46E5'
      this.compactMode = false
      this.showSidebar = true
      this.fixedHeader = true
      this.fontSize = 'medium'
    }
  }
}
</script>

<style scoped>
.appearance-settings {
  padding: 1.5rem;
}

.settings-section {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.section-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1rem 0;
}

.section-header p {
  color: #6b7280;
  margin: 0;
  font-size: 0.875rem;
}

/* 主题选择器 */
.theme-selector {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.theme-option:hover {
  border-color: #d1d5db;
}

.theme-option.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.theme-preview {
  width: 120px;
  height: 80px;
  border-radius: 0.375rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.light-theme {
  background: #ffffff;
}

.dark-theme {
  background: #1f2937;
}

.auto-theme {
  background: linear-gradient(45deg, #ffffff 50%, #1f2937 50%);
}

.preview-header {
  height: 20px;
  background: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
}

.dark-theme .preview-header {
  background: #374151;
  border-color: #4b5563;
}

.preview-sidebar {
  position: absolute;
  left: 0;
  top: 20px;
  width: 30px;
  height: 60px;
  background: #e5e7eb;
}

.dark-theme .preview-sidebar {
  background: #4b5563;
}

.preview-content {
  position: absolute;
  right: 0;
  top: 20px;
  width: 90px;
  height: 60px;
  background: #f9fafb;
}

.dark-theme .preview-content {
  background: #111827;
}

.theme-option span {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

/* 颜色选择器 */
.color-palette {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.color-option {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid transparent;
  transition: all 0.2s;
}

.color-option:hover {
  transform: scale(1.1);
}

.color-option.active {
  border-color: #ffffff;
  box-shadow: 0 0 0 2px #2563eb;
}

/* 颜色预览 */
.color-preview {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
}

.preview-elements {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  color: white;
  font-weight: 500;
  cursor: pointer;
}

.progress-bar {
  width: 120px;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: all 0.3s;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  color: white;
  font-size: 0.75rem;
  font-weight: 500;
}

/* 布局选项 */
.layout-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.setting-item label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.form-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-select:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.setting-item small {
  color: #6b7280;
  font-size: 0.75rem;
}

/* 开关样式 */
.switch-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.switch {
  position: relative;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #d1d5db;
  transition: 0.3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #2563eb;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .theme-selector {
    grid-template-columns: 1fr;
  }
  
  .color-palette {
    justify-content: center;
  }
  
  .layout-options {
    grid-template-columns: 1fr;
  }
  
  .appearance-settings {
    padding: 1rem;
  }
  
  .settings-section {
    padding: 1rem;
  }
  
  .preview-elements {
    justify-content: center;
  }
}
</style>