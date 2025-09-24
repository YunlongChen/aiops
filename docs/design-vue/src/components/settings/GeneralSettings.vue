<!--
  常规设置组件
  提供系统基本信息、性能配置和安全设置
  @author AI Assistant
  @date 2024-01-24
-->
<template>
  <div class="general-settings">
    <!-- 基本信息 -->
    <div class="settings-section">
      <div class="section-header">
        <h2>基本信息</h2>
        <p>配置系统的基本信息和运行参数</p>
      </div>
      
      <div class="settings-grid">
        <div class="setting-item">
          <label for="systemName">系统名称</label>
          <input 
            type="text" 
            id="systemName" 
            v-model="settings.systemName" 
            class="form-input"
          >
          <small>显示在页面标题和导航栏中的系统名称</small>
        </div>
        
        <div class="setting-item">
          <label for="systemVersion">系统版本</label>
          <input 
            type="text" 
            id="systemVersion" 
            v-model="settings.systemVersion" 
            class="form-input" 
            readonly
          >
          <small>当前系统版本号</small>
        </div>
        
        <div class="setting-item">
          <label for="timezone">时区设置</label>
          <select id="timezone" v-model="settings.timezone" class="form-select">
            <option value="Asia/Shanghai">Asia/Shanghai (UTC+8)</option>
            <option value="UTC">UTC (UTC+0)</option>
            <option value="America/New_York">America/New_York (UTC-5)</option>
            <option value="Europe/London">Europe/London (UTC+0)</option>
          </select>
          <small>系统默认时区</small>
        </div>
        
        <div class="setting-item">
          <label for="language">界面语言</label>
          <select id="language" v-model="settings.language" class="form-select">
            <option value="zh-CN">简体中文</option>
            <option value="en-US">English</option>
            <option value="ja-JP">日本語</option>
          </select>
          <small>系统界面显示语言</small>
        </div>
      </div>
    </div>

    <!-- 性能配置 -->
    <div class="settings-section">
      <div class="section-header">
        <h2>性能配置</h2>
        <p>调整系统性能相关参数</p>
      </div>
      
      <div class="settings-grid">
        <div class="setting-item">
          <label for="refreshInterval">数据刷新间隔</label>
          <select id="refreshInterval" v-model="settings.refreshInterval" class="form-select">
            <option value="5">5秒</option>
            <option value="10">10秒</option>
            <option value="30">30秒</option>
            <option value="60">1分钟</option>
          </select>
          <small>监控数据自动刷新间隔</small>
        </div>
        
        <div class="setting-item">
          <label for="dataRetention">数据保留期</label>
          <select id="dataRetention" v-model="settings.dataRetention" class="form-select">
            <option value="7">7天</option>
            <option value="30">30天</option>
            <option value="90">90天</option>
            <option value="365">1年</option>
          </select>
          <small>历史数据保留时间</small>
        </div>
        
        <div class="setting-item">
          <label for="maxConcurrent">最大并发连接</label>
          <input 
            type="number" 
            id="maxConcurrent" 
            v-model="settings.maxConcurrent" 
            min="100" 
            max="10000" 
            class="form-input"
          >
          <small>系统支持的最大并发连接数</small>
        </div>
        
        <div class="setting-item">
          <label class="switch-label">
            <span>启用缓存</span>
            <div class="switch">
              <input type="checkbox" id="enableCache" v-model="settings.enableCache">
              <span class="slider"></span>
            </div>
          </label>
          <small>启用数据缓存以提高性能</small>
        </div>
      </div>
    </div>

    <!-- 安全设置 -->
    <div class="settings-section">
      <div class="section-header">
        <h2>安全设置</h2>
        <p>配置系统安全相关选项</p>
      </div>
      
      <div class="settings-grid">
        <div class="setting-item">
          <label for="sessionTimeout">会话超时</label>
          <select id="sessionTimeout" v-model="settings.sessionTimeout" class="form-select">
            <option value="30">30分钟</option>
            <option value="60">1小时</option>
            <option value="240">4小时</option>
            <option value="480">8小时</option>
          </select>
          <small>用户会话自动过期时间</small>
        </div>
        
        <div class="setting-item">
          <label for="passwordPolicy">密码策略</label>
          <select id="passwordPolicy" v-model="settings.passwordPolicy" class="form-select">
            <option value="simple">简单</option>
            <option value="medium">中等</option>
            <option value="strong">强</option>
          </select>
          <small>用户密码复杂度要求</small>
        </div>
        
        <div class="setting-item">
          <label class="switch-label">
            <span>启用双因子认证</span>
            <div class="switch">
              <input type="checkbox" id="enable2FA" v-model="settings.enable2FA">
              <span class="slider"></span>
            </div>
          </label>
          <small>为用户账户启用双因子认证</small>
        </div>
        
        <div class="setting-item">
          <label class="switch-label">
            <span>记录审计日志</span>
            <div class="switch">
              <input type="checkbox" id="enableAudit" v-model="settings.enableAudit">
              <span class="slider"></span>
            </div>
          </label>
          <small>记录用户操作和系统事件</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GeneralSettings',
  data() {
    return {
      settings: {
        systemName: 'AIOps 智能运维平台',
        systemVersion: 'v2.1.0',
        timezone: 'Asia/Shanghai',
        language: 'zh-CN',
        refreshInterval: '10',
        dataRetention: '30',
        maxConcurrent: 1000,
        enableCache: true,
        sessionTimeout: '60',
        passwordPolicy: 'medium',
        enable2FA: false,
        enableAudit: true
      }
    }
  },
  methods: {
    /**
     * 获取设置数据
     */
    getSettings() {
      return this.settings
    },

    /**
     * 重置设置到默认值
     */
    resetSettings() {
      this.settings = {
        systemName: 'AIOps 智能运维平台',
        systemVersion: 'v2.1.0',
        timezone: 'Asia/Shanghai',
        language: 'zh-CN',
        refreshInterval: '10',
        dataRetention: '30',
        maxConcurrent: 1000,
        enableCache: true,
        sessionTimeout: '60',
        passwordPolicy: 'medium',
        enable2FA: false,
        enableAudit: true
      }
    }
  }
}
</script>

<style scoped>
.general-settings {
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

.section-header p {
  color: #6b7280;
  margin: 0;
  font-size: 0.875rem;
}

.settings-grid {
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

.form-input,
.form-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-input[readonly] {
  background: #f9fafb;
  color: #6b7280;
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
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .general-settings {
    padding: 1rem;
  }
  
  .settings-section {
    padding: 1rem;
  }
}
</style>