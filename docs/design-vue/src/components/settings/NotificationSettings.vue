<!--
  通知设置组件
  提供系统通知和告警配置功能
  @author AI Assistant
  @date 2024-01-24
-->
<template>
  <div class="notification-settings">
    <!-- 通知配置 -->
    <div class="settings-section">
      <div class="section-header">
        <h2>通知配置</h2>
        <p>管理系统通知和告警设置</p>
      </div>
      
      <div class="notification-settings-grid">
        <!-- 系统通知 -->
        <div class="notification-group">
          <h3>系统通知</h3>
          <div class="notification-item">
            <span>系统启动/停止</span>
            <div class="switch">
              <input type="checkbox" id="systemStartStop" v-model="notifications.systemStartStop">
              <span class="slider"></span>
            </div>
          </div>
          <div class="notification-item">
            <span>系统更新</span>
            <div class="switch">
              <input type="checkbox" id="systemUpdate" v-model="notifications.systemUpdate">
              <span class="slider"></span>
            </div>
          </div>
          <div class="notification-item">
            <span>配置变更</span>
            <div class="switch">
              <input type="checkbox" id="configChange" v-model="notifications.configChange">
              <span class="slider"></span>
            </div>
          </div>
          <div class="notification-item">
            <span>备份完成</span>
            <div class="switch">
              <input type="checkbox" id="backupComplete" v-model="notifications.backupComplete">
              <span class="slider"></span>
            </div>
          </div>
        </div>
        
        <!-- 监控告警 -->
        <div class="notification-group">
          <h3>监控告警</h3>
          <div class="notification-item">
            <span>高优先级告警</span>
            <div class="switch">
              <input type="checkbox" id="highPriorityAlert" v-model="notifications.highPriorityAlert">
              <span class="slider"></span>
            </div>
          </div>
          <div class="notification-item">
            <span>中优先级告警</span>
            <div class="switch">
              <input type="checkbox" id="mediumPriorityAlert" v-model="notifications.mediumPriorityAlert">
              <span class="slider"></span>
            </div>
          </div>
          <div class="notification-item">
            <span>低优先级告警</span>
            <div class="switch">
              <input type="checkbox" id="lowPriorityAlert" v-model="notifications.lowPriorityAlert">
              <span class="slider"></span>
            </div>
          </div>
          <div class="notification-item">
            <span>告警恢复</span>
            <div class="switch">
              <input type="checkbox" id="alertRecovery" v-model="notifications.alertRecovery">
              <span class="slider"></span>
            </div>
          </div>
        </div>

        <!-- 自愈系统 -->
        <div class="notification-group">
          <h3>自愈系统</h3>
          <div class="notification-item">
            <span>自愈任务开始</span>
            <div class="switch">
              <input type="checkbox" id="healingStart" v-model="notifications.healingStart">
              <span class="slider"></span>
            </div>
          </div>
          <div class="notification-item">
            <span>自愈任务完成</span>
            <div class="switch">
              <input type="checkbox" id="healingComplete" v-model="notifications.healingComplete">
              <span class="slider"></span>
            </div>
          </div>
          <div class="notification-item">
            <span>自愈任务失败</span>
            <div class="switch">
              <input type="checkbox" id="healingFailed" v-model="notifications.healingFailed">
              <span class="slider"></span>
            </div>
          </div>
        </div>

        <!-- AI分析 -->
        <div class="notification-group">
          <h3>AI分析</h3>
          <div class="notification-item">
            <span>异常检测</span>
            <div class="switch">
              <input type="checkbox" id="anomalyDetection" v-model="notifications.anomalyDetection">
              <span class="slider"></span>
            </div>
          </div>
          <div class="notification-item">
            <span>预测告警</span>
            <div class="switch">
              <input type="checkbox" id="predictiveAlert" v-model="notifications.predictiveAlert">
              <span class="slider"></span>
            </div>
          </div>
          <div class="notification-item">
            <span>分析报告</span>
            <div class="switch">
              <input type="checkbox" id="analysisReport" v-model="notifications.analysisReport">
              <span class="slider"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知渠道 -->
    <div class="settings-section">
      <div class="section-header">
        <h2>通知渠道</h2>
        <p>配置通知发送方式和渠道</p>
      </div>
      
      <div class="channel-settings">
        <div class="channel-item">
          <div class="channel-header">
            <div class="channel-info">
              <i class="fas fa-envelope"></i>
              <span>邮件通知</span>
            </div>
            <div class="switch">
              <input type="checkbox" id="emailEnabled" v-model="channels.email.enabled">
              <span class="slider"></span>
            </div>
          </div>
          <div v-if="channels.email.enabled" class="channel-config">
            <div class="config-item">
              <label for="emailAddress">邮箱地址</label>
              <input 
                type="email" 
                id="emailAddress" 
                v-model="channels.email.address" 
                class="form-input"
                placeholder="admin@example.com"
              >
            </div>
            <div class="config-item">
              <label for="emailFrequency">发送频率</label>
              <select id="emailFrequency" v-model="channels.email.frequency" class="form-select">
                <option value="immediate">立即发送</option>
                <option value="hourly">每小时汇总</option>
                <option value="daily">每日汇总</option>
              </select>
            </div>
          </div>
        </div>

        <div class="channel-item">
          <div class="channel-header">
            <div class="channel-info">
              <i class="fas fa-comment"></i>
              <span>短信通知</span>
            </div>
            <div class="switch">
              <input type="checkbox" id="smsEnabled" v-model="channels.sms.enabled">
              <span class="slider"></span>
            </div>
          </div>
          <div v-if="channels.sms.enabled" class="channel-config">
            <div class="config-item">
              <label for="phoneNumber">手机号码</label>
              <input 
                type="tel" 
                id="phoneNumber" 
                v-model="channels.sms.phone" 
                class="form-input"
                placeholder="+86 138 0000 0000"
              >
            </div>
            <div class="config-item">
              <label class="switch-label">
                <span>仅紧急告警</span>
                <div class="switch">
                  <input type="checkbox" v-model="channels.sms.emergencyOnly">
                  <span class="slider"></span>
                </div>
              </label>
            </div>
          </div>
        </div>

        <div class="channel-item">
          <div class="channel-header">
            <div class="channel-info">
              <i class="fab fa-weixin"></i>
              <span>微信通知</span>
            </div>
            <div class="switch">
              <input type="checkbox" id="wechatEnabled" v-model="channels.wechat.enabled">
              <span class="slider"></span>
            </div>
          </div>
          <div v-if="channels.wechat.enabled" class="channel-config">
            <div class="config-item">
              <label for="wechatWebhook">Webhook URL</label>
              <input 
                type="url" 
                id="wechatWebhook" 
                v-model="channels.wechat.webhook" 
                class="form-input"
                placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
              >
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知时间 -->
    <div class="settings-section">
      <div class="section-header">
        <h2>通知时间</h2>
        <p>设置通知发送的时间范围</p>
      </div>
      
      <div class="time-settings">
        <div class="time-item">
          <label class="switch-label">
            <span>启用免打扰时间</span>
            <div class="switch">
              <input type="checkbox" v-model="timeSettings.quietHours.enabled">
              <span class="slider"></span>
            </div>
          </label>
        </div>
        
        <div v-if="timeSettings.quietHours.enabled" class="time-range">
          <div class="time-input">
            <label for="quietStart">开始时间</label>
            <input 
              type="time" 
              id="quietStart" 
              v-model="timeSettings.quietHours.start" 
              class="form-input"
            >
          </div>
          <div class="time-input">
            <label for="quietEnd">结束时间</label>
            <input 
              type="time" 
              id="quietEnd" 
              v-model="timeSettings.quietHours.end" 
              class="form-input"
            >
          </div>
        </div>
        
        <div class="time-item">
          <label class="switch-label">
            <span>周末暂停通知</span>
            <div class="switch">
              <input type="checkbox" v-model="timeSettings.weekendPause">
              <span class="slider"></span>
            </div>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotificationSettings',
  data() {
    return {
      notifications: {
        // 系统通知
        systemStartStop: true,
        systemUpdate: true,
        configChange: false,
        backupComplete: true,
        // 监控告警
        highPriorityAlert: true,
        mediumPriorityAlert: true,
        lowPriorityAlert: false,
        alertRecovery: true,
        // 自愈系统
        healingStart: true,
        healingComplete: true,
        healingFailed: true,
        // AI分析
        anomalyDetection: true,
        predictiveAlert: true,
        analysisReport: false
      },
      channels: {
        email: {
          enabled: true,
          address: '',
          frequency: 'immediate'
        },
        sms: {
          enabled: false,
          phone: '',
          emergencyOnly: true
        },
        wechat: {
          enabled: false,
          webhook: ''
        }
      },
      timeSettings: {
        quietHours: {
          enabled: false,
          start: '22:00',
          end: '08:00'
        },
        weekendPause: false
      }
    }
  },
  methods: {
    /**
     * 获取设置数据
     */
    getSettings() {
      return {
        notifications: this.notifications,
        channels: this.channels,
        timeSettings: this.timeSettings
      }
    },

    /**
     * 重置设置到默认值
     */
    resetSettings() {
      this.notifications = {
        systemStartStop: true,
        systemUpdate: true,
        configChange: false,
        backupComplete: true,
        highPriorityAlert: true,
        mediumPriorityAlert: true,
        lowPriorityAlert: false,
        alertRecovery: true,
        healingStart: true,
        healingComplete: true,
        healingFailed: true,
        anomalyDetection: true,
        predictiveAlert: true,
        analysisReport: false
      }
      
      this.channels = {
        email: {
          enabled: true,
          address: '',
          frequency: 'immediate'
        },
        sms: {
          enabled: false,
          phone: '',
          emergencyOnly: true
        },
        wechat: {
          enabled: false,
          webhook: ''
        }
      }
      
      this.timeSettings = {
        quietHours: {
          enabled: false,
          start: '22:00',
          end: '08:00'
        },
        weekendPause: false
      }
    }
  }
}
</script>

<style scoped>
.notification-settings {
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

/* 通知设置网格 */
.notification-settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.notification-group {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}

.notification-group h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item span {
  font-size: 0.875rem;
  color: #374151;
}

/* 通知渠道 */
.channel-settings {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.channel-item {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}

.channel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.channel-info i {
  width: 1.25rem;
  text-align: center;
}

.channel-config {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.config-item label {
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

/* 时间设置 */
.time-settings {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.time-item {
  display: flex;
  align-items: center;
}

.time-range {
  display: flex;
  gap: 1rem;
  margin-left: 2rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.375rem;
}

.time-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.time-input label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

/* 开关样式 */
.switch-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  width: 100%;
}

.switch {
  position: relative;
  width: 44px;
  height: 24px;
  flex-shrink: 0;
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
  .notification-settings-grid {
    grid-template-columns: 1fr;
  }
  
  .channel-config {
    grid-template-columns: 1fr;
  }
  
  .time-range {
    flex-direction: column;
    margin-left: 0;
  }
  
  .notification-settings {
    padding: 1rem;
  }
  
  .settings-section {
    padding: 1rem;
  }
}
</style>