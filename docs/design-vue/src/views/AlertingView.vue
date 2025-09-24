<!--
  告警管理主页面组件
  提供告警管理的完整功能，包括告警仪表板、规则配置、通知渠道、事件管理等
  集成多个子组件实现告警系统的全面管理
-->
<template>
  <div class="alerting-view">
    <!-- 内容头部 -->
    <div class="content-header">
      <div class="breadcrumb">
        <span class="breadcrumb-item">告警管理</span>
        <i class="fas fa-chevron-right"></i>
        <span class="breadcrumb-item active">{{ getCurrentTabName() }}</span>
      </div>
      
      <div class="header-actions">
        <button class="btn btn-secondary" @click="refreshData">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': isRefreshing }"></i>
          刷新
        </button>
        <button 
          class="btn btn-primary" 
          @click="createRule"
          v-if="activeTab === 'dashboard' || activeTab === 'rules'"
        >
          <i class="fas fa-plus"></i>
          {{ activeTab === 'rules' ? '创建规则' : '新建告警' }}
        </button>
        <button 
          class="btn btn-primary" 
          @click="createChannel"
          v-if="activeTab === 'channels'"
        >
          <i class="fas fa-plus"></i>
          创建渠道
        </button>
        <button 
          class="btn btn-primary" 
          @click="createTemplate"
          v-if="activeTab === 'templates'"
        >
          <i class="fas fa-plus"></i>
          创建模板
        </button>
      </div>
    </div>

    <!-- 子标签页导航 -->
    <div class="sub-tabs">
      <div class="tab-group">
        <div class="tab-section">
          <span class="tab-section-title">告警监控</span>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'dashboard' }"
            @click="setActiveTab('dashboard')"
          >
            <i class="fas fa-tachometer-alt"></i>
            告警仪表板
          </button>
        </div>
        
        <div class="tab-section">
          <span class="tab-section-title">告警配置</span>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'rules' }"
            @click="setActiveTab('rules')"
          >
            <i class="fas fa-list-ul"></i>
            告警规则
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'channels' }"
            @click="setActiveTab('channels')"
          >
            <i class="fas fa-paper-plane"></i>
            通知渠道
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'templates' }"
            @click="setActiveTab('templates')"
          >
            <i class="fas fa-file-alt"></i>
            消息模板
          </button>
        </div>
        
        <div class="tab-section">
          <span class="tab-section-title">事件管理</span>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'incidents' }"
            @click="setActiveTab('incidents')"
          >
            <i class="fas fa-fire"></i>
            事件处理
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'escalation' }"
            @click="setActiveTab('escalation')"
          >
            <i class="fas fa-arrow-up"></i>
            升级策略
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'oncall' }"
            @click="setActiveTab('oncall')"
          >
            <i class="fas fa-phone"></i>
            值班安排
          </button>
        </div>
        
        <div class="tab-section">
          <span class="tab-section-title">分析报告</span>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'history' }"
            @click="setActiveTab('history')"
          >
            <i class="fas fa-history"></i>
            告警历史
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'analytics' }"
            @click="setActiveTab('analytics')"
          >
            <i class="fas fa-chart-bar"></i>
            告警分析
          </button>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="tab-content">
      <!-- 告警仪表板 -->
      <AlertDashboard 
        v-if="activeTab === 'dashboard'"
        :key="refreshKey"
      />
      
      <!-- 告警规则 -->
      <div v-if="activeTab === 'rules'" class="alert-rules-content">
        <div class="rules-header">
          <div class="rules-stats">
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-list-ul"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ alertRules.length }}</div>
                <div class="stat-label">告警规则</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon active">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ alertRules.filter(r => r.enabled).length }}</div>
                <div class="stat-label">启用规则</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon warning">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ alertRules.filter(r => r.status === 'firing').length }}</div>
                <div class="stat-label">触发中</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="rules-table">
          <table class="table">
            <thead>
              <tr>
                <th>规则名称</th>
                <th>类型</th>
                <th>状态</th>
                <th>最后触发</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rule in alertRules" :key="rule.id">
                <td>
                  <div class="rule-info">
                    <div class="rule-name">{{ rule.name }}</div>
                    <div class="rule-description">{{ rule.description }}</div>
                  </div>
                </td>
                <td>
                  <span class="badge" :class="rule.type">{{ rule.typeText }}</span>
                </td>
                <td>
                  <span class="status-indicator" :class="rule.status">
                    <i :class="rule.statusIcon"></i>
                    {{ rule.statusText }}
                  </span>
                </td>
                <td>{{ rule.lastTriggered }}</td>
                <td>
                  <div class="action-buttons">
                    <button class="btn btn-sm btn-secondary">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- 通知渠道 -->
      <div v-if="activeTab === 'channels'" class="notification-channels-content">
        <div class="channels-grid">
          <div v-for="channel in notificationChannels" :key="channel.id" class="channel-card">
            <div class="channel-header">
              <div class="channel-icon" :class="channel.type">
                <i :class="channel.icon"></i>
              </div>
              <div class="channel-info">
                <div class="channel-name">{{ channel.name }}</div>
                <div class="channel-type">{{ channel.typeText }}</div>
              </div>
              <div class="channel-status">
                <span class="status-dot" :class="channel.status"></span>
              </div>
            </div>
            <div class="channel-body">
              <div class="channel-description">{{ channel.description }}</div>
              <div class="channel-config">
                <div v-for="config in channel.config" :key="config.key" class="config-item">
                  <span class="config-key">{{ config.key }}:</span>
                  <span class="config-value">{{ config.value }}</span>
                </div>
              </div>
            </div>
            <div class="channel-actions">
              <button class="btn btn-sm btn-secondary">测试</button>
              <button class="btn btn-sm btn-primary">编辑</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 消息模板 -->
      <div v-if="activeTab === 'templates'" class="message-templates-content">
        <div class="templates-list">
          <div v-for="template in messageTemplates" :key="template.id" class="template-card">
            <div class="template-header">
              <div class="template-info">
                <div class="template-name">{{ template.name }}</div>
                <div class="template-type">{{ template.type }}</div>
              </div>
              <div class="template-actions">
                <button class="btn btn-sm btn-secondary">预览</button>
                <button class="btn btn-sm btn-primary">编辑</button>
              </div>
            </div>
            <div class="template-content">
              <div class="template-subject">
                <strong>主题:</strong> {{ template.subject }}
              </div>
              <div class="template-body">
                <strong>内容:</strong>
                <div class="template-preview">{{ template.body }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 事件处理 -->
      <div v-if="activeTab === 'incidents'" class="incident-management-content">
        <div class="incidents-header">
          <div class="incidents-stats">
            <div class="stat-item">
              <div class="stat-value critical">{{ incidents.filter(i => i.severity === 'critical').length }}</div>
              <div class="stat-label">严重事件</div>
            </div>
            <div class="stat-item">
              <div class="stat-value warning">{{ incidents.filter(i => i.severity === 'warning').length }}</div>
              <div class="stat-label">警告事件</div>
            </div>
            <div class="stat-item">
              <div class="stat-value info">{{ incidents.filter(i => i.severity === 'info').length }}</div>
              <div class="stat-label">信息事件</div>
            </div>
          </div>
        </div>
        
        <div class="incidents-table">
          <table class="table">
            <thead>
              <tr>
                <th>事件ID</th>
                <th>标题</th>
                <th>严重程度</th>
                <th>状态</th>
                <th>负责人</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="incident in incidents" :key="incident.id">
                <td>{{ incident.id }}</td>
                <td>{{ incident.title }}</td>
                <td>
                  <span class="severity-badge" :class="incident.severity">
                    {{ incident.severityText }}
                  </span>
                </td>
                <td>
                  <span class="status-badge" :class="incident.status">
                    {{ incident.statusText }}
                  </span>
                </td>
                <td>{{ incident.assignee }}</td>
                <td>{{ incident.createdAt }}</td>
                <td>
                  <div class="action-buttons">
                    <button class="btn btn-sm btn-primary">查看</button>
                    <button class="btn btn-sm btn-secondary">分配</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- 升级策略 -->
      <div v-if="activeTab === 'escalation'" class="escalation-policies-content">
        <div class="policies-list">
          <div v-for="policy in escalationPolicies" :key="policy.id" class="policy-card">
            <div class="policy-header">
              <div class="policy-info">
                <div class="policy-name">{{ policy.name }}</div>
                <div class="policy-description">{{ policy.description }}</div>
              </div>
              <div class="policy-status">
                <span class="status-indicator" :class="policy.enabled ? 'active' : 'inactive'">
                  <i :class="policy.enabled ? 'fas fa-check-circle' : 'fas fa-pause-circle'"></i>
                  {{ policy.enabled ? '启用' : '禁用' }}
                </span>
              </div>
            </div>
            <div class="policy-steps">
              <div v-for="(step, index) in policy.steps" :key="index" class="escalation-step">
                <div class="step-number">{{ index + 1 }}</div>
                <div class="step-content">
                  <div class="step-action">{{ step.action }}</div>
                  <div class="step-delay">延迟: {{ step.delay }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 值班安排 -->
      <div v-if="activeTab === 'oncall'" class="oncall-schedule-content">
        <div class="schedule-header">
          <div class="current-oncall">
            <div class="oncall-info">
              <div class="oncall-label">当前值班</div>
              <div class="oncall-person">{{ currentOnCall.name }}</div>
              <div class="oncall-contact">{{ currentOnCall.contact }}</div>
            </div>
            <div class="oncall-avatar">
              <img :src="currentOnCall.avatar" :alt="currentOnCall.name">
            </div>
          </div>
        </div>
        
        <div class="schedule-calendar">
          <div class="calendar-header">
            <h3>值班日历</h3>
          </div>
          <div class="schedule-list">
            <div v-for="schedule in onCallSchedules" :key="schedule.id" class="schedule-item">
              <div class="schedule-time">
                <div class="schedule-date">{{ schedule.date }}</div>
                <div class="schedule-period">{{ schedule.period }}</div>
              </div>
              <div class="schedule-person">
                <div class="person-name">{{ schedule.person }}</div>
                <div class="person-role">{{ schedule.role }}</div>
              </div>
              <div class="schedule-contact">{{ schedule.contact }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 告警历史 -->
      <div v-if="activeTab === 'history'" class="alert-history-content">
        <div class="history-filters">
          <div class="filter-group">
            <label>时间范围:</label>
            <select class="form-control">
              <option>最近24小时</option>
              <option>最近7天</option>
              <option>最近30天</option>
            </select>
          </div>
          <div class="filter-group">
            <label>严重程度:</label>
            <select class="form-control">
              <option>全部</option>
              <option>严重</option>
              <option>警告</option>
              <option>信息</option>
            </select>
          </div>
        </div>
        
        <div class="history-table">
          <table class="table">
            <thead>
              <tr>
                <th>时间</th>
                <th>告警名称</th>
                <th>严重程度</th>
                <th>状态</th>
                <th>持续时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="alert in alertHistory" :key="alert.id">
                <td>{{ alert.timestamp }}</td>
                <td>{{ alert.name }}</td>
                <td>
                  <span class="severity-badge" :class="alert.severity">
                    {{ alert.severityText }}
                  </span>
                </td>
                <td>
                  <span class="status-badge" :class="alert.status">
                    {{ alert.statusText }}
                  </span>
                </td>
                <td>{{ alert.duration }}</td>
                <td>
                  <button class="btn btn-sm btn-secondary">详情</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- 告警分析 -->
      <div v-if="activeTab === 'analytics'" class="alert-analytics-content">
        <div class="analytics-overview">
          <div class="metric-card">
            <div class="metric-header">
              <h3>告警趋势</h3>
            </div>
            <div class="metric-chart">
              <div class="chart-placeholder">
                <i class="fas fa-chart-line"></i>
                <p>告警数量趋势图</p>
              </div>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-header">
              <h3>响应时间分析</h3>
            </div>
            <div class="response-metrics">
              <div class="response-item">
                <div class="response-label">平均响应时间</div>
                <div class="response-value">{{ analyticsData.avgResponseTime }}</div>
              </div>
              <div class="response-item">
                <div class="response-label">最快响应时间</div>
                <div class="response-value">{{ analyticsData.minResponseTime }}</div>
              </div>
              <div class="response-item">
                <div class="response-label">最慢响应时间</div>
                <div class="response-value">{{ analyticsData.maxResponseTime }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="analytics-details">
          <div class="top-alerts">
            <h3>频繁告警TOP10</h3>
            <div class="alert-ranking">
              <div v-for="(alert, index) in topAlerts" :key="alert.id" class="ranking-item">
                <div class="ranking-number">{{ index + 1 }}</div>
                <div class="ranking-info">
                  <div class="ranking-name">{{ alert.name }}</div>
                  <div class="ranking-count">{{ alert.count }}次</div>
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
import { ref, onMounted, onUnmounted } from 'vue'
import AlertDashboard from '@/components/alerting/AlertDashboard.vue'

export default {
  name: 'AlertingView',
  components: {
    AlertDashboard
  },
  setup() {
    // 响应式数据
    const activeTab = ref('dashboard')
    const isRefreshing = ref(false)
    const refreshKey = ref(0)
    const autoRefreshInterval = ref(null)

    // 告警规则数据
    const alertRules = ref([
      {
        id: 1,
        name: 'CPU使用率过高告警',
        description: '当CPU使用率超过80%时触发告警',
        type: 'threshold',
        typeText: '阈值告警',
        status: 'active',
        statusText: '正常',
        statusIcon: 'fas fa-check-circle',
        enabled: true,
        lastTriggered: '2小时前'
      },
      {
        id: 2,
        name: '内存使用率告警',
        description: '内存使用率超过90%时触发',
        type: 'threshold',
        typeText: '阈值告警',
        status: 'firing',
        statusText: '触发中',
        statusIcon: 'fas fa-exclamation-triangle',
        enabled: true,
        lastTriggered: '15分钟前'
      },
      {
        id: 3,
        name: '磁盘空间不足告警',
        description: '磁盘使用率超过85%时告警',
        type: 'threshold',
        typeText: '阈值告警',
        status: 'inactive',
        statusText: '已禁用',
        statusIcon: 'fas fa-pause-circle',
        enabled: false,
        lastTriggered: '1天前'
      }
    ])

    // 通知渠道数据
    const notificationChannels = ref([
      {
        id: 1,
        name: '邮件通知',
        type: 'email',
        typeText: '邮件',
        icon: 'fas fa-envelope',
        status: 'active',
        description: '通过邮件发送告警通知',
        config: [
          { key: 'SMTP服务器', value: 'smtp.company.com' },
          { key: '端口', value: '587' },
          { key: '发件人', value: 'alerts@company.com' }
        ]
      },
      {
        id: 2,
        name: '钉钉群通知',
        type: 'dingtalk',
        typeText: '钉钉',
        icon: 'fab fa-slack',
        status: 'active',
        description: '发送告警消息到钉钉群',
        config: [
          { key: 'Webhook URL', value: 'https://oapi.dingtalk.com/...' },
          { key: '群名称', value: '运维告警群' }
        ]
      },
      {
        id: 3,
        name: '短信通知',
        type: 'sms',
        typeText: '短信',
        icon: 'fas fa-sms',
        status: 'inactive',
        description: '通过短信发送紧急告警',
        config: [
          { key: '服务商', value: '阿里云短信' },
          { key: '签名', value: '运维平台' }
        ]
      }
    ])

    // 消息模板数据
    const messageTemplates = ref([
      {
        id: 1,
        name: 'CPU告警模板',
        type: '阈值告警',
        subject: '【告警】CPU使用率过高',
        body: '服务器 {{hostname}} 的CPU使用率已达到 {{value}}%，超过阈值 {{threshold}}%，请及时处理。'
      },
      {
        id: 2,
        name: '内存告警模板',
        type: '阈值告警',
        subject: '【告警】内存使用率异常',
        body: '服务器 {{hostname}} 的内存使用率为 {{value}}%，已超过告警阈值，请检查内存使用情况。'
      },
      {
        id: 3,
        name: '服务异常模板',
        type: '服务告警',
        subject: '【严重】服务不可用',
        body: '服务 {{service_name}} 在 {{hostname}} 上不可用，错误信息：{{error_message}}'
      }
    ])

    // 事件数据
    const incidents = ref([
      {
        id: 'INC-001',
        title: '数据库连接超时',
        severity: 'critical',
        severityText: '严重',
        status: 'open',
        statusText: '处理中',
        assignee: '张三',
        createdAt: '2024-01-15 14:30'
      },
      {
        id: 'INC-002',
        title: 'API响应时间过长',
        severity: 'warning',
        severityText: '警告',
        status: 'resolved',
        statusText: '已解决',
        assignee: '李四',
        createdAt: '2024-01-15 13:15'
      },
      {
        id: 'INC-003',
        title: '磁盘空间不足',
        severity: 'info',
        severityText: '信息',
        status: 'open',
        statusText: '待处理',
        assignee: '王五',
        createdAt: '2024-01-15 12:00'
      }
    ])

    // 升级策略数据
    const escalationPolicies = ref([
      {
        id: 1,
        name: '标准升级策略',
        description: '适用于一般告警的升级流程',
        enabled: true,
        steps: [
          { action: '通知值班人员', delay: '立即' },
          { action: '通知团队负责人', delay: '15分钟' },
          { action: '通知部门经理', delay: '30分钟' }
        ]
      },
      {
        id: 2,
        name: '紧急升级策略',
        description: '适用于严重告警的快速升级',
        enabled: true,
        steps: [
          { action: '同时通知值班人员和负责人', delay: '立即' },
          { action: '通知部门经理', delay: '5分钟' },
          { action: '通知技术总监', delay: '10分钟' }
        ]
      }
    ])

    // 当前值班信息
    const currentOnCall = ref({
      name: '张三',
      contact: '13800138000',
      avatar: '/avatars/zhangsan.jpg'
    })

    // 值班安排数据
    const onCallSchedules = ref([
      {
        id: 1,
        date: '2024-01-15',
        period: '09:00-18:00',
        person: '张三',
        role: '主值班',
        contact: '13800138000'
      },
      {
        id: 2,
        date: '2024-01-15',
        period: '18:00-09:00',
        person: '李四',
        role: '夜班值班',
        contact: '13800138001'
      },
      {
        id: 3,
        date: '2024-01-16',
        period: '09:00-18:00',
        person: '王五',
        role: '主值班',
        contact: '13800138002'
      }
    ])

    // 告警历史数据
    const alertHistory = ref([
      {
        id: 1,
        timestamp: '2024-01-15 14:30:00',
        name: 'CPU使用率过高',
        severity: 'warning',
        severityText: '警告',
        status: 'resolved',
        statusText: '已解决',
        duration: '25分钟'
      },
      {
        id: 2,
        timestamp: '2024-01-15 13:15:00',
        name: '内存使用率异常',
        severity: 'critical',
        severityText: '严重',
        status: 'resolved',
        statusText: '已解决',
        duration: '1小时15分钟'
      },
      {
        id: 3,
        timestamp: '2024-01-15 12:00:00',
        name: '磁盘空间不足',
        severity: 'info',
        severityText: '信息',
        status: 'acknowledged',
        statusText: '已确认',
        duration: '进行中'
      }
    ])

    // 分析数据
    const analyticsData = ref({
      avgResponseTime: '5.2分钟',
      minResponseTime: '1.5分钟',
      maxResponseTime: '45分钟'
    })

    // 频繁告警TOP10
    const topAlerts = ref([
      { id: 1, name: 'CPU使用率过高', count: 45 },
      { id: 2, name: '内存使用率异常', count: 32 },
      { id: 3, name: '磁盘空间不足', count: 28 },
      { id: 4, name: 'API响应超时', count: 24 },
      { id: 5, name: '数据库连接失败', count: 18 }
    ])

    // 标签页名称映射
    const tabNames = {
      dashboard: '告警仪表板',
      rules: '告警规则',
      channels: '通知渠道',
      templates: '消息模板',
      incidents: '事件处理',
      escalation: '升级策略',
      oncall: '值班安排',
      history: '告警历史',
      analytics: '告警分析'
    }

    // 标签页功能特性
    const tabFeatures = {
      rules: [
        '告警规则创建和编辑',
        '规则条件配置',
        '阈值设置',
        '规则测试和验证'
      ],
      channels: [
        '邮件通知配置',
        '短信通知设置',
        '钉钉/企业微信集成',
        'Webhook通知'
      ],
      templates: [
        '告警消息模板',
        '通知内容自定义',
        '模板变量支持',
        '多语言模板'
      ],
      incidents: [
        '事件创建和跟踪',
        '事件状态管理',
        '事件分配和处理',
        '事件时间线'
      ],
      escalation: [
        '升级规则配置',
        '升级时间设置',
        '升级通知策略',
        '升级路径管理'
      ],
      oncall: [
        '值班人员安排',
        '值班轮换计划',
        '值班日历管理',
        '紧急联系人'
      ],
      history: [
        '历史告警查询',
        '告警统计报表',
        '趋势分析',
        '数据导出'
      ],
      analytics: [
        '告警分析报告',
        '性能指标统计',
        '告警模式识别',
        '优化建议'
      ]
    }

    /**
     * 获取当前标签页名称
     */
    const getCurrentTabName = () => {
      return tabNames[activeTab.value] || activeTab.value
    }

    /**
     * 获取标签页功能特性
     */
    const getTabFeatures = (tab) => {
      return tabFeatures[tab] || []
    }

    /**
     * 设置活跃标签页
     */
    const setActiveTab = (tab) => {
      activeTab.value = tab
      console.log('切换到标签页:', getCurrentTabName())
    }

    /**
     * 刷新数据
     */
    const refreshData = async () => {
      isRefreshing.value = true
      try {
        // 通过更新key来强制重新渲染组件
        refreshKey.value++
        console.log('刷新告警数据')
        
        // 模拟刷新延迟
        await new Promise(resolve => setTimeout(resolve, 1000))
      } catch (error) {
        console.error('刷新数据失败:', error)
      } finally {
        isRefreshing.value = false
      }
    }

    /**
     * 创建告警规则
     */
    const createRule = () => {
      console.log('创建告警规则')
      // TODO: 实现创建告警规则逻辑
    }

    /**
     * 创建通知渠道
     */
    const createChannel = () => {
      console.log('创建通知渠道')
      // TODO: 实现创建通知渠道逻辑
    }

    /**
     * 创建消息模板
     */
    const createTemplate = () => {
      console.log('创建消息模板')
      // TODO: 实现创建消息模板逻辑
    }

    /**
     * 启动自动刷新
     */
    const startAutoRefresh = () => {
      autoRefreshInterval.value = setInterval(() => {
        if (activeTab.value === 'dashboard') {
          refreshData()
        }
      }, 30000) // 30秒自动刷新
    }

    /**
     * 停止自动刷新
     */
    const stopAutoRefresh = () => {
      if (autoRefreshInterval.value) {
        clearInterval(autoRefreshInterval.value)
        autoRefreshInterval.value = null
      }
    }

    // 生命周期钩子
    onMounted(() => {
      console.log('告警管理页面已加载')
      startAutoRefresh()
    })

    onUnmounted(() => {
      stopAutoRefresh()
    })

    return {
      activeTab,
      isRefreshing,
      refreshKey,
      alertRules,
      notificationChannels,
      messageTemplates,
      incidents,
      escalationPolicies,
      currentOnCall,
      onCallSchedules,
      alertHistory,
      analyticsData,
      topAlerts,
      getCurrentTabName,
      getTabFeatures,
      setActiveTab,
      refreshData,
      createRule,
      createChannel,
      createTemplate
    }
  }
}
</script>

<style scoped>
.alerting-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f9fafb;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.breadcrumb-item {
  color: #6b7280;
}

.breadcrumb-item.active {
  color: #1f2937;
  font-weight: 500;
}

.breadcrumb i {
  font-size: 12px;
  color: #9ca3af;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.fa-spin {
  animation: fa-spin 1s infinite linear;
}

/* 子标签页导航 */
.sub-tabs {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 24px;
}

.tab-group {
  display: flex;
  gap: 32px;
  overflow-x: auto;
  padding: 16px 0;
}

.tab-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: fit-content;
}

.tab-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: none;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.tab-btn.active {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

.tab-btn i {
  font-size: 14px;
}

/* 内容区域 */
.tab-content {
  flex: 1;
  overflow: hidden;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .content-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-actions {
    justify-content: flex-end;
  }

  .tab-group {
    gap: 16px;
  }

  .tab-section {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .content-header {
    padding: 12px 16px;
  }

  .sub-tabs {
    padding: 0 16px;
  }

  .tab-group {
    flex-direction: column;
    gap: 12px;
  }

  .tab-section {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 8px;
  }

  .tab-section-title {
    width: 100%;
    margin-bottom: 8px;
  }

  .tab-btn {
    padding: 6px 12px;
    font-size: 13px;
  }

  .header-actions {
    flex-direction: column;
    gap: 8px;
  }

  .btn {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .breadcrumb {
    font-size: 13px;
  }

  .tab-btn {
    padding: 6px 10px;
    font-size: 12px;
  }

  .btn {
    padding: 8px 12px;
    font-size: 13px;
  }
}
</style>