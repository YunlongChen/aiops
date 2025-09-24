<!--
  自愈系统主页面
  提供自愈仪表板、修复脚本、工作流程、触发器、自愈规则、策略管理、条件设置、修复历史、效果分析、报告中心等功能
-->
<template>
  <div class="self-healing-view">
    <!-- 内容头部 -->
    <!--    <div class="content-header">-->
    <!--      <div class="breadcrumb">-->
    <!--        <span class="breadcrumb-item">自愈系统</span>-->
    <!--        <i class="fas fa-chevron-right"></i>-->
    <!--        <span class="breadcrumb-item active">{{ getCurrentTabLabel() }}</span>-->
    <!--      </div>-->
    <!--      -->
    <!--      <div class="header-actions">-->
    <!--        <button class="btn btn-secondary" @click="refreshData">-->
    <!--          <i class="fas fa-sync-alt" :class="{ 'fa-spin': isRefreshing }"></i>-->
    <!--          刷新-->
    <!--        </button>-->
    <!--        <button class="btn btn-primary" @click="handleCreateAction">-->
    <!--          <i class="fas fa-plus"></i>-->
    <!--          {{ getCreateButtonText() }}-->
    <!--        </button>-->
    <!--      </div>-->
    <!--    </div>-->

    <!-- 子标签页导航 -->
    <div class="sub-tabs">
      <div class="tab-group">
        <div class="tab-group-title">自愈监控</div>
        <button
            v-for="tab in monitoringTabs"
            :key="tab.key"
            :class="['tab-button', { active: activeTab === tab.key }]"
            @click="setActiveTab(tab.key)"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>

      <div class="tab-group">
        <div class="tab-group-title">自动化管理</div>
        <button
            v-for="tab in automationTabs"
            :key="tab.key"
            :class="['tab-button', { active: activeTab === tab.key }]"
            @click="setActiveTab(tab.key)"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>

      <div class="tab-group">
        <div class="tab-group-title">规则配置</div>
        <button
            v-for="tab in rulesTabs"
            :key="tab.key"
            :class="['tab-button', { active: activeTab === tab.key }]"
            @click="setActiveTab(tab.key)"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>

      <div class="tab-group">
        <div class="tab-group-title">历史记录</div>
        <button
            v-for="tab in historyTabs"
            :key="tab.key"
            :class="['tab-button', { active: activeTab === tab.key }]"
            @click="setActiveTab(tab.key)"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 标签页内容 -->
    <div class="tab-content">
      <!-- 自愈仪表板 -->
      <div v-if="activeTab === 'dashboard'" class="dashboard-content">
        <HealingDashboard :key="activeTab" @refresh="refreshData"/>
      </div>

      <!-- 修复脚本 -->
      <div v-else-if="activeTab === 'scripts'" class="scripts-content">
        <div class="content-section">
          <div class="section-header">
            <h3>修复脚本管理</h3>
            <div class="section-actions">
              <button class="btn btn-primary" @click="createScript">
                <i class="fas fa-plus"></i>
                新建脚本
              </button>
            </div>
          </div>

          <div class="scripts-grid">
            <div v-for="script in repairScripts" :key="script.id" class="script-card">
              <div class="script-header">
                <div class="script-info">
                  <h4>{{ script.name }}</h4>
                  <p class="script-description">{{ script.description }}</p>
                </div>
                <div class="script-status">
                  <span :class="['status-badge', script.status]">{{ script.statusText }}</span>
                </div>
              </div>

              <div class="script-details">
                <div class="detail-item">
                  <span class="label">类型:</span>
                  <span class="value">{{ script.type }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">执行次数:</span>
                  <span class="value">{{ script.execCount }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">成功率:</span>
                  <span class="value">{{ script.successRate }}%</span>
                </div>
                <div class="detail-item">
                  <span class="label">最后执行:</span>
                  <span class="value">{{ script.lastExecution }}</span>
                </div>
              </div>

              <div class="script-actions">
                <button class="btn btn-sm btn-secondary">
                  <i class="fas fa-edit"></i>
                  编辑
                </button>
                <button class="btn btn-sm btn-primary">
                  <i class="fas fa-play"></i>
                  执行
                </button>
                <button class="btn btn-sm btn-danger">
                  <i class="fas fa-trash"></i>
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 工作流程 -->
      <div v-else-if="activeTab === 'workflows'" class="workflows-content">
        <div class="content-section">
          <div class="section-header">
            <h3>自愈工作流程</h3>
            <div class="section-actions">
              <button class="btn btn-primary" @click="createWorkflow">
                <i class="fas fa-plus"></i>
                创建工作流
              </button>
            </div>
          </div>

          <div class="workflows-list">
            <div v-for="workflow in workflows" :key="workflow.id" class="workflow-item">
              <div class="workflow-header">
                <div class="workflow-info">
                  <h4>{{ workflow.name }}</h4>
                  <p>{{ workflow.description }}</p>
                </div>
                <div class="workflow-status">
                  <span :class="['status-badge', workflow.status]">{{ workflow.statusText }}</span>
                </div>
              </div>

              <div class="workflow-steps">
                <div v-for="(step, index) in workflow.steps" :key="index" class="step-item">
                  <div class="step-number">{{ index + 1 }}</div>
                  <div class="step-content">
                    <div class="step-name">{{ step.name }}</div>
                    <div class="step-description">{{ step.description }}</div>
                  </div>
                  <div class="step-arrow" v-if="index < workflow.steps.length - 1">
                    <i class="fas fa-arrow-right"></i>
                  </div>
                </div>
              </div>

              <div class="workflow-actions">
                <button class="btn btn-sm btn-secondary">
                  <i class="fas fa-edit"></i>
                  编辑
                </button>
                <button class="btn btn-sm btn-primary">
                  <i class="fas fa-play"></i>
                  启动
                </button>
                <button class="btn btn-sm btn-info">
                  <i class="fas fa-eye"></i>
                  查看
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 触发器 -->
      <div v-else-if="activeTab === 'triggers'" class="triggers-content">
        <div class="content-section">
          <div class="section-header">
            <h3>自愈触发器</h3>
            <div class="section-actions">
              <button class="btn btn-primary" @click="createTrigger">
                <i class="fas fa-plus"></i>
                新建触发器
              </button>
            </div>
          </div>

          <div class="triggers-table">
            <table class="data-table">
              <thead>
              <tr>
                <th>触发器名称</th>
                <th>触发条件</th>
                <th>关联脚本</th>
                <th>状态</th>
                <th>最后触发</th>
                <th>操作</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="trigger in triggers" :key="trigger.id">
                <td>
                  <div class="trigger-name">
                    <i :class="trigger.icon"></i>
                    {{ trigger.name }}
                  </div>
                </td>
                <td>{{ trigger.condition }}</td>
                <td>{{ trigger.script }}</td>
                <td>
                  <span :class="['status-badge', trigger.status]">{{ trigger.statusText }}</span>
                </td>
                <td>{{ trigger.lastTriggered }}</td>
                <td>
                  <div class="action-buttons">
                    <button class="btn btn-sm btn-secondary">编辑</button>
                    <button class="btn btn-sm btn-primary">测试</button>
                    <button class="btn btn-sm btn-danger">删除</button>
                  </div>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 自愈规则 -->
      <div v-else-if="activeTab === 'rules'" class="rules-content">
        <div class="content-section">
          <div class="section-header">
            <h3>自愈规则配置</h3>
            <div class="section-actions">
              <button class="btn btn-primary" @click="createRule">
                <i class="fas fa-plus"></i>
                创建规则
              </button>
            </div>
          </div>

          <div class="rules-list">
            <div v-for="rule in healingRules" :key="rule.id" class="rule-card">
              <div class="rule-header">
                <div class="rule-info">
                  <h4>{{ rule.name }}</h4>
                  <p>{{ rule.description }}</p>
                </div>
                <div class="rule-toggle">
                  <label class="switch">
                    <input type="checkbox" :checked="rule.enabled">
                    <span class="slider"></span>
                  </label>
                </div>
              </div>

              <div class="rule-conditions">
                <div class="condition-group">
                  <h5>触发条件</h5>
                  <div class="conditions">
                    <div v-for="condition in rule.conditions" :key="condition.id" class="condition-item">
                      <span class="condition-metric">{{ condition.metric }}</span>
                      <span class="condition-operator">{{ condition.operator }}</span>
                      <span class="condition-value">{{ condition.value }}</span>
                    </div>
                  </div>
                </div>

                <div class="action-group">
                  <h5>执行动作</h5>
                  <div class="actions">
                    <div v-for="action in rule.actions" :key="action.id" class="action-item">
                      <i :class="action.icon"></i>
                      <span>{{ action.name }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="rule-stats">
                <div class="stat-item">
                  <span class="stat-label">触发次数</span>
                  <span class="stat-value">{{ rule.triggerCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">成功率</span>
                  <span class="stat-value">{{ rule.successRate }}%</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">最后执行</span>
                  <span class="stat-value">{{ rule.lastExecution }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 策略管理 -->
      <div v-else-if="activeTab === 'policies'" class="policies-content">
        <div class="content-section">
          <div class="section-header">
            <h3>自愈策略管理</h3>
            <div class="section-actions">
              <button class="btn btn-primary" @click="createPolicy">
                <i class="fas fa-plus"></i>
                新建策略
              </button>
            </div>
          </div>

          <div class="policies-grid">
            <div v-for="policy in policies" :key="policy.id" class="policy-card">
              <div class="policy-header">
                <div class="policy-info">
                  <h4>{{ policy.name }}</h4>
                  <p>{{ policy.description }}</p>
                </div>
                <div class="policy-priority">
                  <span :class="['priority-badge', policy.priority]">{{ policy.priorityText }}</span>
                </div>
              </div>

              <div class="policy-details">
                <div class="detail-row">
                  <span class="label">适用范围:</span>
                  <span class="value">{{ policy.scope }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">执行频率:</span>
                  <span class="value">{{ policy.frequency }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">超时时间:</span>
                  <span class="value">{{ policy.timeout }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">重试次数:</span>
                  <span class="value">{{ policy.retryCount }}</span>
                </div>
              </div>

              <div class="policy-actions">
                <button class="btn btn-sm btn-secondary">编辑</button>
                <button class="btn btn-sm btn-info">详情</button>
                <button class="btn btn-sm btn-danger">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 条件设置 -->
      <div v-else-if="activeTab === 'conditions'" class="conditions-content">
        <div class="content-section">
          <div class="section-header">
            <h3>触发条件设置</h3>
            <div class="section-actions">
              <button class="btn btn-primary" @click="addCondition">
                <i class="fas fa-plus"></i>
                添加条件
              </button>
            </div>
          </div>

          <div class="conditions-builder">
            <div v-for="condition in conditionGroups" :key="condition.id" class="condition-group">
              <div class="group-header">
                <h4>{{ condition.name }}</h4>
                <div class="group-actions">
                  <button class="btn btn-sm btn-secondary">编辑</button>
                  <button class="btn btn-sm btn-danger">删除</button>
                </div>
              </div>

              <div class="condition-rules">
                <div v-for="rule in condition.rules" :key="rule.id" class="condition-rule">
                  <div class="rule-field">
                    <label>监控指标</label>
                    <select class="form-control">
                      <option>{{ rule.metric }}</option>
                    </select>
                  </div>

                  <div class="rule-operator">
                    <label>比较操作</label>
                    <select class="form-control">
                      <option>{{ rule.operator }}</option>
                    </select>
                  </div>

                  <div class="rule-value">
                    <label>阈值</label>
                    <input type="text" class="form-control" :value="rule.value">
                  </div>

                  <div class="rule-actions">
                    <button class="btn btn-sm btn-danger">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 修复历史 -->
      <div v-else-if="activeTab === 'history'" class="history-content">
        <div class="content-section">
          <div class="section-header">
            <h3>自愈修复历史</h3>
            <div class="section-actions">
              <button class="btn btn-secondary">
                <i class="fas fa-download"></i>
                导出记录
              </button>
            </div>
          </div>

          <div class="history-filters">
            <div class="filter-group">
              <label>时间范围</label>
              <select class="form-control">
                <option>最近7天</option>
                <option>最近30天</option>
                <option>最近90天</option>
              </select>
            </div>

            <div class="filter-group">
              <label>执行状态</label>
              <select class="form-control">
                <option>全部</option>
                <option>成功</option>
                <option>失败</option>
                <option>部分成功</option>
              </select>
            </div>

            <div class="filter-group">
              <label>修复类型</label>
              <select class="form-control">
                <option>全部</option>
                <option>自动修复</option>
                <option>手动修复</option>
              </select>
            </div>
          </div>

          <div class="history-table">
            <table class="data-table">
              <thead>
              <tr>
                <th>执行时间</th>
                <th>问题描述</th>
                <th>修复脚本</th>
                <th>执行状态</th>
                <th>执行时长</th>
                <th>操作</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="record in repairHistory" :key="record.id">
                <td>{{ record.timestamp }}</td>
                <td>{{ record.issue }}</td>
                <td>{{ record.script }}</td>
                <td>
                  <span :class="['status-badge', record.status]">{{ record.statusText }}</span>
                </td>
                <td>{{ record.duration }}</td>
                <td>
                  <div class="action-buttons">
                    <button class="btn btn-sm btn-info">详情</button>
                    <button class="btn btn-sm btn-secondary">重新执行</button>
                  </div>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 效果分析 -->
      <div v-else-if="activeTab === 'analytics'" class="analytics-content">
        <div class="content-section">
          <div class="section-header">
            <h3>自愈效果分析</h3>
          </div>

          <div class="analytics-overview">
            <div class="metric-card">
              <div class="metric-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ analyticsData.totalRepairs }}</div>
                <div class="metric-label">总修复次数</div>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-icon">
                <i class="fas fa-percentage"></i>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ analyticsData.successRate }}%</div>
                <div class="metric-label">修复成功率</div>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-icon">
                <i class="fas fa-clock"></i>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ analyticsData.avgRepairTime }}</div>
                <div class="metric-label">平均修复时间</div>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-icon">
                <i class="fas fa-save"></i>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ analyticsData.timeSaved }}</div>
                <div class="metric-label">节省时间</div>
              </div>
            </div>
          </div>

          <div class="analytics-charts">
            <div class="chart-container">
              <h4>修复趋势分析</h4>
              <div class="chart-placeholder">
                <i class="fas fa-chart-line"></i>
                <p>修复次数趋势图</p>
              </div>
            </div>

            <div class="chart-container">
              <h4>问题类型分布</h4>
              <div class="chart-placeholder">
                <i class="fas fa-chart-pie"></i>
                <p>问题类型饼图</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 报告中心 -->
      <div v-else-if="activeTab === 'reports'" class="reports-content">
        <div class="content-section">
          <div class="section-header">
            <h3>自愈报告中心</h3>
            <div class="section-actions">
              <button class="btn btn-primary" @click="generateReport">
                <i class="fas fa-file-alt"></i>
                生成报告
              </button>
            </div>
          </div>

          <div class="reports-list">
            <div v-for="report in reports" :key="report.id" class="report-item">
              <div class="report-info">
                <div class="report-icon">
                  <i :class="report.icon"></i>
                </div>
                <div class="report-details">
                  <h4>{{ report.name }}</h4>
                  <p>{{ report.description }}</p>
                  <div class="report-meta">
                    <span>生成时间: {{ report.generatedAt }}</span>
                    <span>文件大小: {{ report.fileSize }}</span>
                  </div>
                </div>
              </div>

              <div class="report-actions">
                <button class="btn btn-sm btn-primary">
                  <i class="fas fa-download"></i>
                  下载
                </button>
                <button class="btn btn-sm btn-info">
                  <i class="fas fa-eye"></i>
                  预览
                </button>
                <button class="btn btn-sm btn-secondary">
                  <i class="fas fa-share"></i>
                  分享
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {ref, onMounted, onUnmounted} from 'vue'
import HealingDashboard from '@/components/self-healing/HealingDashboard.vue'

export default {
  name: 'SelfHealingView',
  components: {
    HealingDashboard
  },
  setup() {
    // 响应式数据
    const activeTab = ref('dashboard')
    const isRefreshing = ref(false)
    const autoRefreshInterval = ref(null)

    // 修复脚本数据
    const repairScripts = ref([
      {
        id: 1,
        name: 'CPU过载修复脚本',
        description: '当CPU使用率超过90%时自动重启相关服务',
        type: 'Shell脚本',
        status: 'active',
        statusText: '活跃',
        execCount: 45,
        successRate: 95,
        lastExecution: '2024-01-15 14:30:25'
      },
      {
        id: 2,
        name: '内存泄漏检测修复',
        description: '检测并修复应用程序内存泄漏问题',
        type: 'Python脚本',
        status: 'inactive',
        statusText: '未激活',
        execCount: 23,
        successRate: 87,
        lastExecution: '2024-01-14 09:15:10'
      }
    ])

    // 工作流程数据
    const workflows = ref([
      {
        id: 1,
        name: '数据库连接异常处理流程',
        description: '处理数据库连接超时和连接池耗尽问题',
        status: 'running',
        statusText: '运行中',
        steps: [
          {name: '检测连接状态', description: '监控数据库连接池状态'},
          {name: '重启连接池', description: '重新初始化连接池'},
          {name: '验证连接', description: '测试数据库连接可用性'},
          {name: '发送通知', description: '通知运维人员处理结果'}
        ]
      }
    ])

    // 触发器数据
    const triggers = ref([
      {
        id: 1,
        name: 'CPU使用率告警触发器',
        icon: 'fas fa-microchip',
        condition: 'CPU > 90% 持续5分钟',
        script: 'CPU过载修复脚本',
        status: 'active',
        statusText: '活跃',
        lastTriggered: '2024-01-15 14:25:00'
      },
      {
        id: 2,
        name: '磁盘空间不足触发器',
        icon: 'fas fa-hdd',
        condition: '磁盘使用率 > 85%',
        script: '磁盘清理脚本',
        status: 'inactive',
        statusText: '未激活',
        lastTriggered: '2024-01-10 08:30:00'
      }
    ])

    // 自愈规则数据
    const healingRules = ref([
      {
        id: 1,
        name: '服务自动重启规则',
        description: '当服务响应时间超过阈值时自动重启服务',
        enabled: true,
        conditions: [
          {id: 1, metric: '响应时间', operator: '>', value: '5秒'},
          {id: 2, metric: '错误率', operator: '>', value: '10%'}
        ],
        actions: [
          {id: 1, name: '重启服务', icon: 'fas fa-redo'},
          {id: 2, name: '发送告警', icon: 'fas fa-bell'}
        ],
        triggerCount: 12,
        successRate: 92,
        lastExecution: '2024-01-15 13:45:00'
      }
    ])

    // 策略数据
    const policies = ref([
      {
        id: 1,
        name: '高优先级修复策略',
        description: '针对关键业务系统的快速修复策略',
        priority: 'high',
        priorityText: '高优先级',
        scope: '生产环境',
        frequency: '实时监控',
        timeout: '30秒',
        retryCount: 3
      }
    ])

    // 条件组数据
    const conditionGroups = ref([
      {
        id: 1,
        name: '系统性能监控条件组',
        rules: [
          {id: 1, metric: 'CPU使用率', operator: '>', value: '80%'},
          {id: 2, metric: '内存使用率', operator: '>', value: '85%'}
        ]
      }
    ])

    // 修复历史数据
    const repairHistory = ref([
      {
        id: 1,
        timestamp: '2024-01-15 14:30:25',
        issue: 'CPU使用率过高',
        script: 'CPU过载修复脚本',
        status: 'success',
        statusText: '成功',
        duration: '2分30秒'
      },
      {
        id: 2,
        timestamp: '2024-01-15 12:15:10',
        issue: '内存泄漏检测',
        script: '内存清理脚本',
        status: 'failed',
        statusText: '失败',
        duration: '1分45秒'
      }
    ])

    // 分析数据
    const analyticsData = ref({
      totalRepairs: 156,
      successRate: 94,
      avgRepairTime: '2分15秒',
      timeSaved: '48小时'
    })

    // 报告数据
    const reports = ref([
      {
        id: 1,
        name: '月度自愈效果报告',
        description: '2024年1月自愈系统运行效果分析报告',
        icon: 'fas fa-file-pdf',
        generatedAt: '2024-01-31 23:59:59',
        fileSize: '2.5MB'
      }
    ])

    // 标签页配置
    const monitoringTabs = [
      {key: 'dashboard', label: '自愈仪表板', icon: 'fas fa-tachometer-alt'}
    ]

    const automationTabs = [
      {key: 'scripts', label: '修复脚本', icon: 'fas fa-code'},
      {key: 'workflows', label: '工作流程', icon: 'fas fa-project-diagram'},
      {key: 'triggers', label: '触发器', icon: 'fas fa-bolt'}
    ]

    const rulesTabs = [
      {key: 'rules', label: '自愈规则', icon: 'fas fa-list-ul'},
      {key: 'policies', label: '策略管理', icon: 'fas fa-shield-alt'},
      {key: 'conditions', label: '条件设置', icon: 'fas fa-filter'}
    ]

    const historyTabs = [
      {key: 'history', label: '修复历史', icon: 'fas fa-history'},
      {key: 'analytics', label: '效果分析', icon: 'fas fa-chart-bar'},
      {key: 'reports', label: '报告中心', icon: 'fas fa-file-alt'}
    ]

    // 方法
    /**
     * 设置活跃标签页
     * @param {string} tabKey - 标签页键值
     */
    const setActiveTab = (tabKey) => {
      activeTab.value = tabKey
    }

    /**
     * 获取当前标签页标签
     * @returns {string} 标签页标签
     */
    const getCurrentTabLabel = () => {
      const allTabs = [...monitoringTabs, ...automationTabs, ...rulesTabs, ...historyTabs]
      const currentTab = allTabs.find(tab => tab.key === activeTab.value)
      return currentTab ? currentTab.label : '自愈仪表板'
    }

    /**
     * 获取创建按钮文本
     * @returns {string} 按钮文本
     */
    const getCreateButtonText = () => {
      switch (activeTab.value) {
        case 'dashboard':
          return '创建脚本'
        case 'scripts':
          return '新建脚本'
        case 'workflows':
          return '创建工作流'
        case 'triggers':
          return '新建触发器'
        case 'rules':
          return '创建规则'
        case 'policies':
          return '新建策略'
        case 'conditions':
          return '添加条件'
        default:
          return '创建'
      }
    }

    /**
     * 处理创建操作
     */
    const handleCreateAction = () => {
      console.log(`创建操作: ${activeTab.value}`)
    }

    /**
     * 创建脚本
     */
    const createScript = () => {
      console.log('创建修复脚本')
    }

    /**
     * 创建工作流
     */
    const createWorkflow = () => {
      console.log('创建工作流程')
    }

    /**
     * 创建触发器
     */
    const createTrigger = () => {
      console.log('创建触发器')
    }

    /**
     * 创建规则
     */
    const createRule = () => {
      console.log('创建自愈规则')
    }

    /**
     * 创建策略
     */
    const createPolicy = () => {
      console.log('创建策略')
    }

    /**
     * 添加条件
     */
    const addCondition = () => {
      console.log('添加条件')
    }

    /**
     * 生成报告
     */
    const generateReport = () => {
      console.log('生成报告')
    }

    /**
     * 刷新数据
     */
    const refreshData = async () => {
      isRefreshing.value = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        console.log('自愈系统数据已刷新')
      } catch (error) {
        console.error('刷新数据失败:', error)
      } finally {
        isRefreshing.value = false
      }
    }

    /**
     * 启动自动刷新
     */
    const startAutoRefresh = () => {
      autoRefreshInterval.value = setInterval(() => {
        refreshData()
      }, 30000) // 30秒刷新一次
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

    // 生命周期
    onMounted(() => {
      refreshData()
      startAutoRefresh()
    })

    onUnmounted(() => {
      stopAutoRefresh()
    })

    return {
      activeTab,
      isRefreshing,
      monitoringTabs,
      automationTabs,
      rulesTabs,
      historyTabs,
      repairScripts,
      workflows,
      triggers,
      healingRules,
      policies,
      conditionGroups,
      repairHistory,
      analyticsData,
      reports,
      setActiveTab,
      getCurrentTabLabel,
      getCreateButtonText,
      handleCreateAction,
      createScript,
      createWorkflow,
      createTrigger,
      createRule,
      createPolicy,
      addCondition,
      generateReport,
      refreshData
    }
  }
}
</script>

<style scoped>
.self-healing-view {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}

.breadcrumb-item.active {
  color: #1890ff;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: #f0f0f0;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover {
  background: #40a9ff;
}

.sub-tabs {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.tab-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 120px;
}

.tab-group-title {
  font-size: 12px;
  color: #999;
  font-weight: 500;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tab-button {
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: #666;
  cursor: pointer;
  border-radius: 4px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.tab-button:hover {
  background: #f0f0f0;
  color: #1890ff;
}

.tab-button.active {
  background: #e6f7ff;
  color: #1890ff;
  font-weight: 500;
}

.tab-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 600px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sub-tabs {
    flex-wrap: wrap;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .self-healing-view {
    padding: 10px;
  }

  .content-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .header-actions {
    justify-content: center;
  }

  .sub-tabs {
    flex-direction: column;
    gap: 15px;
  }

  .tab-group {
    min-width: auto;
  }
}
</style>