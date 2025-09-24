<!--
  系统设置主页面
  提供系统配置、用户管理、安全设置等功能
  @author AI Assistant
  @date 2024-01-24
-->
<template>
  <div class="settings-view">
    <!-- 内容头部 -->
    <div class="content-header">
      <div class="breadcrumb">
        <span class="breadcrumb-item">系统设置</span>
        <i class="fas fa-chevron-right"></i>
        <span class="breadcrumb-item active">{{ currentTabTitle }}</span>
      </div>
      
      <div class="header-actions">
        <button class="btn btn-secondary" @click="resetSettings">
          <i class="fas fa-undo"></i>
          重置设置
        </button>
        <button class="btn btn-primary" @click="saveSettings">
          <i class="fas fa-save"></i>
          保存设置
        </button>
      </div>
    </div>

    <div class="settings-container">
      <!-- 左侧菜单 -->
      <div class="settings-sidebar">
        <div class="menu-group">
          <div class="menu-title">基础设置</div>
          <div 
            class="menu-item" 
            :class="{ active: activeTab === 'general' }"
            @click="switchTab('general')"
          >
            <i class="fas fa-cog"></i>
            <span>常规设置</span>
          </div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'appearance' }"
            @click="switchTab('appearance')"
          >
            <i class="fas fa-palette"></i>
            <span>外观主题</span>
          </div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'notifications' }"
            @click="switchTab('notifications')"
          >
            <i class="fas fa-bell"></i>
            <span>通知设置</span>
          </div>
        </div>
        
        <div class="menu-group">
          <div class="menu-title">系统配置</div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'monitoring' }"
            @click="switchTab('monitoring')"
          >
            <i class="fas fa-chart-line"></i>
            <span>监控配置</span>
          </div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'ai-models' }"
            @click="switchTab('ai-models')"
          >
            <i class="fas fa-brain"></i>
            <span>AI模型配置</span>
          </div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'data-sources' }"
            @click="switchTab('data-sources')"
          >
            <i class="fas fa-database"></i>
            <span>数据源管理</span>
          </div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'integrations' }"
            @click="switchTab('integrations')"
          >
            <i class="fas fa-plug"></i>
            <span>集成配置</span>
          </div>
        </div>
        
        <div class="menu-group">
          <div class="menu-title">安全管理</div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'users' }"
            @click="switchTab('users')"
          >
            <i class="fas fa-users"></i>
            <span>用户管理</span>
          </div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'roles' }"
            @click="switchTab('roles')"
          >
            <i class="fas fa-user-shield"></i>
            <span>角色权限</span>
          </div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'audit' }"
            @click="switchTab('audit')"
          >
            <i class="fas fa-clipboard-list"></i>
            <span>审计日志</span>
          </div>
        </div>
        
        <div class="menu-group">
          <div class="menu-title">系统维护</div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'backup' }"
            @click="switchTab('backup')"
          >
            <i class="fas fa-save"></i>
            <span>备份恢复</span>
          </div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'maintenance' }"
            @click="switchTab('maintenance')"
          >
            <i class="fas fa-tools"></i>
            <span>系统维护</span>
          </div>
          <div 
            class="menu-item"
            :class="{ active: activeTab === 'about' }"
            @click="switchTab('about')"
          >
            <i class="fas fa-info-circle"></i>
            <span>关于系统</span>
          </div>
        </div>
      </div>

      <!-- 右侧内容区域 -->
      <div class="settings-content">
        <!-- 常规设置 -->
        <GeneralSettings v-if="activeTab === 'general'" />
        
        <!-- 外观主题 -->
        <AppearanceSettings v-else-if="activeTab === 'appearance'" />
        
        <!-- 通知设置 -->
        <NotificationSettings v-else-if="activeTab === 'notifications'" />
        
        <!-- 监控配置 -->
        <div v-else-if="activeTab === 'monitoring'" class="settings-panel">
          <div class="panel-header">
            <h2>监控配置</h2>
            <p>配置系统监控参数和告警阈值</p>
          </div>
          <div class="panel-content">
            <div class="form-group">
              <label>数据采集间隔</label>
              <select v-model="monitoringSettings.collectInterval" class="form-control">
                <option value="10">10秒</option>
                <option value="30">30秒</option>
                <option value="60">1分钟</option>
                <option value="300">5分钟</option>
              </select>
            </div>
            <div class="form-group">
              <label>数据保留时间</label>
              <select v-model="monitoringSettings.retentionPeriod" class="form-control">
                <option value="7">7天</option>
                <option value="30">30天</option>
                <option value="90">90天</option>
                <option value="365">1年</option>
              </select>
            </div>
            <div class="form-group">
              <label>告警阈值配置</label>
              <div class="threshold-config">
                <div class="threshold-item">
                  <span>CPU使用率</span>
                  <input v-model="monitoringSettings.thresholds.cpu" type="number" class="form-control" min="0" max="100">
                  <span>%</span>
                </div>
                <div class="threshold-item">
                  <span>内存使用率</span>
                  <input v-model="monitoringSettings.thresholds.memory" type="number" class="form-control" min="0" max="100">
                  <span>%</span>
                </div>
                <div class="threshold-item">
                  <span>磁盘使用率</span>
                  <input v-model="monitoringSettings.thresholds.disk" type="number" class="form-control" min="0" max="100">
                  <span>%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- AI模型配置 -->
        <div v-else-if="activeTab === 'ai-models'" class="settings-panel">
          <div class="panel-header">
            <h2>AI模型配置</h2>
            <p>管理和配置AI预测模型</p>
          </div>
          <div class="panel-content">
            <div class="model-list">
              <div v-for="model in aiModels" :key="model.id" class="model-item">
                <div class="model-info">
                  <h4>{{ model.name }}</h4>
                  <p>{{ model.description }}</p>
                  <span class="model-status" :class="model.status">{{ model.status === 'active' ? '运行中' : '已停止' }}</span>
                </div>
                <div class="model-actions">
                  <button class="btn btn-sm btn-secondary" @click="configureModel(model.id)">配置</button>
                  <button class="btn btn-sm" :class="model.status === 'active' ? 'btn-danger' : 'btn-success'" @click="toggleModel(model.id)">
                    {{ model.status === 'active' ? '停止' : '启动' }}
                  </button>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>模型训练参数</label>
              <div class="training-params">
                <div class="param-item">
                  <label>学习率</label>
                  <input v-model="aiSettings.learningRate" type="number" class="form-control" step="0.001" min="0.001" max="1">
                </div>
                <div class="param-item">
                  <label>批次大小</label>
                  <input v-model="aiSettings.batchSize" type="number" class="form-control" min="1" max="1000">
                </div>
                <div class="param-item">
                  <label>训练轮数</label>
                  <input v-model="aiSettings.epochs" type="number" class="form-control" min="1" max="1000">
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 数据源管理 -->
        <div v-else-if="activeTab === 'data-sources'" class="settings-panel">
          <div class="panel-header">
            <h2>数据源管理</h2>
            <p>配置和管理系统数据源连接</p>
            <button class="btn btn-primary" @click="addDataSource">
              <i class="fas fa-plus"></i>
              添加数据源
            </button>
          </div>
          <div class="panel-content">
            <div class="datasource-list">
              <div v-for="ds in dataSources" :key="ds.id" class="datasource-item">
                <div class="datasource-info">
                  <div class="datasource-header">
                    <h4>{{ ds.name }}</h4>
                    <span class="datasource-type">{{ ds.type }}</span>
                    <span class="connection-status" :class="ds.status">
                      <i class="fas" :class="ds.status === 'connected' ? 'fa-check-circle' : 'fa-times-circle'"></i>
                      {{ ds.status === 'connected' ? '已连接' : '连接失败' }}
                    </span>
                  </div>
                  <p>{{ ds.description }}</p>
                  <div class="datasource-details">
                    <span>主机: {{ ds.host }}</span>
                    <span>端口: {{ ds.port }}</span>
                    <span>数据库: {{ ds.database }}</span>
                  </div>
                </div>
                <div class="datasource-actions">
                  <button class="btn btn-sm btn-secondary" @click="testConnection(ds.id)">测试连接</button>
                  <button class="btn btn-sm btn-primary" @click="editDataSource(ds.id)">编辑</button>
                  <button class="btn btn-sm btn-danger" @click="deleteDataSource(ds.id)">删除</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 集成配置 -->
        <div v-else-if="activeTab === 'integrations'" class="settings-panel">
          <div class="panel-header">
            <h2>集成配置</h2>
            <p>配置第三方系统集成</p>
          </div>
          <div class="panel-content">
            <div class="integration-grid">
              <div v-for="integration in integrations" :key="integration.id" class="integration-card">
                <div class="integration-icon">
                  <i class="fab" :class="integration.icon"></i>
                </div>
                <div class="integration-info">
                  <h4>{{ integration.name }}</h4>
                  <p>{{ integration.description }}</p>
                  <div class="integration-status">
                    <span :class="integration.enabled ? 'status-enabled' : 'status-disabled'">
                      {{ integration.enabled ? '已启用' : '未启用' }}
                    </span>
                  </div>
                </div>
                <div class="integration-actions">
                  <button class="btn btn-sm" :class="integration.enabled ? 'btn-danger' : 'btn-success'" @click="toggleIntegration(integration.id)">
                    {{ integration.enabled ? '禁用' : '启用' }}
                  </button>
                  <button class="btn btn-sm btn-primary" @click="configureIntegration(integration.id)">配置</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 用户管理 -->
        <div v-else-if="activeTab === 'users'" class="settings-panel">
          <div class="panel-header">
            <h2>用户管理</h2>
            <p>管理系统用户账户</p>
            <button class="btn btn-primary" @click="addUser">
              <i class="fas fa-user-plus"></i>
              添加用户
            </button>
          </div>
          <div class="panel-content">
            <div class="user-table">
              <table class="table">
                <thead>
                  <tr>
                    <th>用户名</th>
                    <th>邮箱</th>
                    <th>角色</th>
                    <th>状态</th>
                    <th>最后登录</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in users" :key="user.id">
                    <td>
                      <div class="user-info">
                        <img :src="user.avatar" :alt="user.username" class="user-avatar">
                        <span>{{ user.username }}</span>
                      </div>
                    </td>
                    <td>{{ user.email }}</td>
                    <td>
                      <span class="role-badge" :class="user.role">{{ user.roleName }}</span>
                    </td>
                    <td>
                      <span class="status-badge" :class="user.status">
                        {{ user.status === 'active' ? '活跃' : '禁用' }}
                      </span>
                    </td>
                    <td>{{ user.lastLogin }}</td>
                    <td>
                      <button class="btn btn-sm btn-secondary" @click="editUser(user.id)">编辑</button>
                      <button class="btn btn-sm" :class="user.status === 'active' ? 'btn-warning' : 'btn-success'" @click="toggleUserStatus(user.id)">
                        {{ user.status === 'active' ? '禁用' : '启用' }}
                      </button>
                      <button class="btn btn-sm btn-danger" @click="deleteUser(user.id)">删除</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <!-- 角色权限 -->
        <div v-else-if="activeTab === 'roles'" class="settings-panel">
          <div class="panel-header">
            <h2>角色权限</h2>
            <p>管理用户角色和权限</p>
            <button class="btn btn-primary" @click="addRole">
              <i class="fas fa-plus"></i>
              添加角色
            </button>
          </div>
          <div class="panel-content">
            <div class="role-list">
              <div v-for="role in roles" :key="role.id" class="role-item">
                <div class="role-info">
                  <h4>{{ role.name }}</h4>
                  <p>{{ role.description }}</p>
                  <div class="role-stats">
                    <span>用户数: {{ role.userCount }}</span>
                    <span>权限数: {{ role.permissions.length }}</span>
                  </div>
                </div>
                <div class="role-permissions">
                  <div class="permission-grid">
                    <div v-for="permission in role.permissions" :key="permission" class="permission-tag">
                      {{ getPermissionName(permission) }}
                    </div>
                  </div>
                </div>
                <div class="role-actions">
                  <button class="btn btn-sm btn-primary" @click="editRole(role.id)">编辑</button>
                  <button class="btn btn-sm btn-danger" @click="deleteRole(role.id)" :disabled="role.isSystem">删除</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 审计日志 -->
        <div v-else-if="activeTab === 'audit'" class="settings-panel">
          <div class="panel-header">
            <h2>审计日志</h2>
            <p>查看系统操作审计记录</p>
            <div class="audit-filters">
              <select v-model="auditFilter.type" class="form-control">
                <option value="">所有类型</option>
                <option value="login">登录</option>
                <option value="config">配置变更</option>
                <option value="user">用户操作</option>
                <option value="system">系统操作</option>
              </select>
              <input v-model="auditFilter.user" type="text" placeholder="用户名" class="form-control">
              <input v-model="auditFilter.dateFrom" type="date" class="form-control">
              <input v-model="auditFilter.dateTo" type="date" class="form-control">
              <button class="btn btn-primary" @click="searchAuditLogs">搜索</button>
            </div>
          </div>
          <div class="panel-content">
            <div class="audit-table">
              <table class="table">
                <thead>
                  <tr>
                    <th>时间</th>
                    <th>用户</th>
                    <th>操作类型</th>
                    <th>操作描述</th>
                    <th>IP地址</th>
                    <th>结果</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="log in auditLogs" :key="log.id">
                    <td>{{ log.timestamp }}</td>
                    <td>{{ log.username }}</td>
                    <td>
                      <span class="type-badge" :class="log.type">{{ getAuditTypeName(log.type) }}</span>
                    </td>
                    <td>{{ log.description }}</td>
                    <td>{{ log.ipAddress }}</td>
                    <td>
                      <span class="result-badge" :class="log.result">
                        <i class="fas" :class="log.result === 'success' ? 'fa-check' : 'fa-times'"></i>
                        {{ log.result === 'success' ? '成功' : '失败' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <!-- 备份恢复 -->
        <div v-else-if="activeTab === 'backup'" class="settings-panel">
          <div class="panel-header">
            <h2>备份恢复</h2>
            <p>管理系统数据备份和恢复</p>
            <button class="btn btn-primary" @click="createBackup">
              <i class="fas fa-download"></i>
              创建备份
            </button>
          </div>
          <div class="panel-content">
            <div class="backup-config">
              <div class="form-group">
                <label>自动备份</label>
                <div class="toggle-switch">
                  <input v-model="backupSettings.autoBackup" type="checkbox" id="autoBackup">
                  <label for="autoBackup"></label>
                </div>
              </div>
              <div class="form-group" v-if="backupSettings.autoBackup">
                <label>备份频率</label>
                <select v-model="backupSettings.frequency" class="form-control">
                  <option value="daily">每日</option>
                  <option value="weekly">每周</option>
                  <option value="monthly">每月</option>
                </select>
              </div>
              <div class="form-group">
                <label>备份保留数量</label>
                <input v-model="backupSettings.retentionCount" type="number" class="form-control" min="1" max="100">
              </div>
            </div>
            <div class="backup-list">
              <h4>备份历史</h4>
              <div class="backup-item" v-for="backup in backups" :key="backup.id">
                <div class="backup-info">
                  <h5>{{ backup.name }}</h5>
                  <p>创建时间: {{ backup.createdAt }}</p>
                  <p>大小: {{ backup.size }}</p>
                  <span class="backup-status" :class="backup.status">{{ getBackupStatusName(backup.status) }}</span>
                </div>
                <div class="backup-actions">
                  <button class="btn btn-sm btn-success" @click="restoreBackup(backup.id)" :disabled="backup.status !== 'completed'">恢复</button>
                  <button class="btn btn-sm btn-primary" @click="downloadBackup(backup.id)" :disabled="backup.status !== 'completed'">下载</button>
                  <button class="btn btn-sm btn-danger" @click="deleteBackup(backup.id)">删除</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 系统维护 -->
        <div v-else-if="activeTab === 'maintenance'" class="settings-panel">
          <div class="panel-header">
            <h2>系统维护</h2>
            <p>系统维护和优化工具</p>
          </div>
          <div class="panel-content">
            <div class="maintenance-tools">
              <div class="tool-card">
                <div class="tool-icon">
                  <i class="fas fa-broom"></i>
                </div>
                <div class="tool-info">
                  <h4>清理缓存</h4>
                  <p>清理系统缓存文件，释放存储空间</p>
                  <button class="btn btn-primary" @click="clearCache">清理缓存</button>
                </div>
              </div>
              <div class="tool-card">
                <div class="tool-icon">
                  <i class="fas fa-database"></i>
                </div>
                <div class="tool-info">
                  <h4>数据库优化</h4>
                  <p>优化数据库性能，重建索引</p>
                  <button class="btn btn-primary" @click="optimizeDatabase">优化数据库</button>
                </div>
              </div>
              <div class="tool-card">
                <div class="tool-icon">
                  <i class="fas fa-chart-line"></i>
                </div>
                <div class="tool-info">
                  <h4>性能检测</h4>
                  <p>检测系统性能瓶颈</p>
                  <button class="btn btn-primary" @click="runPerformanceCheck">运行检测</button>
                </div>
              </div>
              <div class="tool-card">
                <div class="tool-icon">
                  <i class="fas fa-sync"></i>
                </div>
                <div class="tool-info">
                  <h4>系统重启</h4>
                  <p>重启系统服务</p>
                  <button class="btn btn-warning" @click="restartSystem">重启系统</button>
                </div>
              </div>
            </div>
            <div class="system-info">
              <h4>系统信息</h4>
              <div class="info-grid">
                <div class="info-item">
                  <label>系统版本</label>
                  <span>{{ systemInfo.version }}</span>
                </div>
                <div class="info-item">
                  <label>运行时间</label>
                  <span>{{ systemInfo.uptime }}</span>
                </div>
                <div class="info-item">
                  <label>CPU使用率</label>
                  <span>{{ systemInfo.cpuUsage }}%</span>
                </div>
                <div class="info-item">
                  <label>内存使用率</label>
                  <span>{{ systemInfo.memoryUsage }}%</span>
                </div>
                <div class="info-item">
                  <label>磁盘使用率</label>
                  <span>{{ systemInfo.diskUsage }}%</span>
                </div>
                <div class="info-item">
                  <label>活跃用户</label>
                  <span>{{ systemInfo.activeUsers }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 关于系统 -->
        <div v-else-if="activeTab === 'about'" class="settings-panel">
          <div class="panel-header">
            <h2>关于系统</h2>
            <p>系统版本信息和许可证</p>
          </div>
          <div class="panel-content">
            <div class="about-content">
              <div class="system-logo">
                <i class="fas fa-cogs"></i>
                <h3>AIOps 智能运维平台</h3>
              </div>
              <div class="version-info">
                <div class="info-row">
                  <label>版本号:</label>
                  <span>{{ aboutInfo.version }}</span>
                </div>
                <div class="info-row">
                  <label>构建时间:</label>
                  <span>{{ aboutInfo.buildDate }}</span>
                </div>
                <div class="info-row">
                  <label>许可证:</label>
                  <span>{{ aboutInfo.license }}</span>
                </div>
                <div class="info-row">
                  <label>开发团队:</label>
                  <span>{{ aboutInfo.team }}</span>
                </div>
              </div>
              <div class="feature-list">
                <h4>主要功能</h4>
                <ul>
                  <li>智能监控和告警</li>
                  <li>AI驱动的异常检测</li>
                  <li>自动化故障修复</li>
                  <li>性能优化建议</li>
                  <li>可视化数据分析</li>
                  <li>多维度系统监控</li>
                </ul>
              </div>
              <div class="contact-info">
                <h4>联系我们</h4>
                <p>邮箱: support@aiops.com</p>
                <p>官网: https://www.aiops.com</p>
                <p>文档: https://docs.aiops.com</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 保存确认模态框 -->
    <div v-if="showSaveModal" class="modal" @click="closeSaveModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>保存设置</h3>
          <button class="modal-close" @click="closeSaveModal">&times;</button>
        </div>
        <div class="modal-body">
          <p>确定要保存当前设置吗？某些设置可能需要重启系统才能生效。</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeSaveModal">取消</button>
          <button class="btn btn-primary" @click="confirmSave">确认保存</button>
        </div>
      </div>
    </div>

    <!-- 重置确认模态框 -->
    <div v-if="showResetModal" class="modal" @click="closeResetModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>重置设置</h3>
          <button class="modal-close" @click="closeResetModal">&times;</button>
        </div>
        <div class="modal-body">
          <p>确定要重置所有设置到默认值吗？此操作不可撤销。</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeResetModal">取消</button>
          <button class="btn btn-danger" @click="confirmReset">确认重置</button>
        </div>
      </div>
    </div>

    <!-- 成功提示 -->
    <div v-if="showSuccessToast" class="toast success">
      <i class="fas fa-check-circle"></i>
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<script>
import GeneralSettings from '@/components/settings/GeneralSettings.vue'
import AppearanceSettings from '@/components/settings/AppearanceSettings.vue'
import NotificationSettings from '@/components/settings/NotificationSettings.vue'

export default {
  name: 'SettingsView',
  components: {
    GeneralSettings,
    AppearanceSettings,
    NotificationSettings
  },
  data() {
    return {
      activeTab: 'general',
      showSaveModal: false,
      showResetModal: false,
      showSuccessToast: false,
      toastMessage: '',
      tabTitles: {
        general: '常规设置',
        appearance: '外观主题',
        notifications: '通知设置',
        monitoring: '监控配置',
        'ai-models': 'AI模型配置',
        'data-sources': '数据源管理',
        integrations: '集成配置',
        users: '用户管理',
        roles: '角色权限',
        audit: '审计日志',
        backup: '备份恢复',
        maintenance: '系统维护',
        about: '关于系统'
      },
      // 监控配置数据
      monitoringSettings: {
        collectInterval: 60,
        retentionPeriod: 30,
        thresholds: {
          cpu: 80,
          memory: 85,
          disk: 90
        }
      },
      // AI模型数据
      aiModels: [
        {
          id: 1,
          name: '异常检测模型',
          description: '基于机器学习的系统异常检测',
          status: 'active'
        },
        {
          id: 2,
          name: '性能预测模型',
          description: '预测系统性能趋势',
          status: 'inactive'
        },
        {
          id: 3,
          name: '故障诊断模型',
          description: '智能故障根因分析',
          status: 'active'
        }
      ],
      aiSettings: {
        learningRate: 0.001,
        batchSize: 32,
        epochs: 100
      },
      // 数据源数据
      dataSources: [
        {
          id: 1,
          name: 'MySQL主库',
          type: 'MySQL',
          description: '主要业务数据库',
          host: '192.168.1.100',
          port: 3306,
          database: 'aiops_main',
          status: 'connected'
        },
        {
          id: 2,
          name: 'Redis缓存',
          type: 'Redis',
          description: '缓存数据库',
          host: '192.168.1.101',
          port: 6379,
          database: '0',
          status: 'connected'
        },
        {
          id: 3,
          name: 'Elasticsearch',
          type: 'Elasticsearch',
          description: '日志搜索引擎',
          host: '192.168.1.102',
          port: 9200,
          database: 'logs',
          status: 'disconnected'
        }
      ],
      // 集成配置数据
      integrations: [
        {
          id: 1,
          name: 'Slack',
          description: '团队协作通知',
          icon: 'fa-slack',
          enabled: true
        },
        {
          id: 2,
          name: 'Jira',
          description: '问题跟踪系统',
          icon: 'fa-jira',
          enabled: false
        },
        {
          id: 3,
          name: 'PagerDuty',
          description: '事件响应平台',
          icon: 'fa-pager',
          enabled: true
        },
        {
          id: 4,
          name: 'Grafana',
          description: '监控仪表板',
          icon: 'fa-chart-line',
          enabled: true
        }
      ],
      // 用户数据
      users: [
        {
          id: 1,
          username: 'admin',
          email: 'admin@aiops.com',
          role: 'admin',
          roleName: '管理员',
          status: 'active',
          lastLogin: '2024-01-24 10:30:00',
          avatar: '/api/placeholder/32/32'
        },
        {
          id: 2,
          username: 'operator',
          email: 'operator@aiops.com',
          role: 'operator',
          roleName: '运维员',
          status: 'active',
          lastLogin: '2024-01-24 09:15:00',
          avatar: '/api/placeholder/32/32'
        },
        {
          id: 3,
          username: 'viewer',
          email: 'viewer@aiops.com',
          role: 'viewer',
          roleName: '查看者',
          status: 'inactive',
          lastLogin: '2024-01-23 16:45:00',
          avatar: '/api/placeholder/32/32'
        }
      ],
      // 角色数据
      roles: [
        {
          id: 1,
          name: '管理员',
          description: '系统管理员，拥有所有权限',
          userCount: 1,
          permissions: ['system.manage', 'user.manage', 'config.manage', 'monitor.view', 'alert.manage'],
          isSystem: true
        },
        {
          id: 2,
          name: '运维员',
          description: '运维人员，负责系统监控和维护',
          userCount: 3,
          permissions: ['monitor.view', 'alert.manage', 'config.view', 'system.maintain'],
          isSystem: false
        },
        {
          id: 3,
          name: '查看者',
          description: '只读用户，只能查看监控数据',
          userCount: 5,
          permissions: ['monitor.view', 'dashboard.view'],
          isSystem: false
        }
      ],
      // 审计日志数据
      auditLogs: [
        {
          id: 1,
          timestamp: '2024-01-24 10:30:15',
          username: 'admin',
          type: 'config',
          description: '修改监控阈值配置',
          ipAddress: '192.168.1.50',
          result: 'success'
        },
        {
          id: 2,
          timestamp: '2024-01-24 10:25:30',
          username: 'operator',
          type: 'user',
          description: '创建新用户账户',
          ipAddress: '192.168.1.51',
          result: 'success'
        },
        {
          id: 3,
          timestamp: '2024-01-24 10:20:45',
          username: 'viewer',
          type: 'login',
          description: '用户登录失败',
          ipAddress: '192.168.1.52',
          result: 'failed'
        }
      ],
      auditFilter: {
        type: '',
        user: '',
        dateFrom: '',
        dateTo: ''
      },
      // 备份数据
      backupSettings: {
        autoBackup: true,
        frequency: 'daily',
        retentionCount: 7
      },
      backups: [
        {
          id: 1,
          name: 'backup_2024-01-24_10-00-00',
          createdAt: '2024-01-24 10:00:00',
          size: '2.5 GB',
          status: 'completed'
        },
        {
          id: 2,
          name: 'backup_2024-01-23_10-00-00',
          createdAt: '2024-01-23 10:00:00',
          size: '2.3 GB',
          status: 'completed'
        },
        {
          id: 3,
          name: 'backup_2024-01-22_10-00-00',
          createdAt: '2024-01-22 10:00:00',
          size: '2.4 GB',
          status: 'completed'
        }
      ],
      // 系统信息
      systemInfo: {
        version: 'v1.2.3',
        uptime: '15天 8小时 32分钟',
        cpuUsage: 45,
        memoryUsage: 68,
        diskUsage: 32,
        activeUsers: 12
      },
      // 关于信息
      aboutInfo: {
        version: 'v1.2.3',
        buildDate: '2024-01-20 14:30:00',
        license: 'MIT License',
        team: 'AIOps开发团队'
      }
    }
  },
  computed: {
    /**
     * 获取当前标签页标题
     */
    currentTabTitle() {
      return this.tabTitles[this.activeTab] || '设置'
    }
  },
  methods: {
    /**
     * 切换标签页
     */
    switchTab(tab) {
      this.activeTab = tab
    },

    /**
     * 保存设置
     */
    saveSettings() {
      this.showSaveModal = true
    },

    /**
     * 重置设置
     */
    resetSettings() {
      this.showResetModal = true
    },

    /**
     * 关闭保存模态框
     */
    closeSaveModal() {
      this.showSaveModal = false
    },

    /**
     * 关闭重置模态框
     */
    closeResetModal() {
      this.showResetModal = false
    },

    /**
     * 确认保存
     */
    confirmSave() {
      this.showSaveModal = false
      this.showToast('设置保存成功！')
      // TODO: 实际保存逻辑
    },

    /**
     * 确认重置
     */
    confirmReset() {
      this.showResetModal = false
      this.showToast('设置重置成功！')
      // TODO: 实际重置逻辑
    },

    /**
     * 显示提示消息
     */
    showToast(message) {
      this.toastMessage = message
      this.showSuccessToast = true
      setTimeout(() => {
        this.showSuccessToast = false
      }, 3000)
    },

    // 监控配置方法
    /**
     * 保存监控配置
     */
    saveMonitoringConfig() {
      this.showToast('监控配置保存成功！')
    },

    // AI模型方法
    /**
     * 切换模型状态
     */
    toggleModelStatus(modelId) {
      const model = this.aiModels.find(m => m.id === modelId)
      if (model) {
        model.status = model.status === 'active' ? 'inactive' : 'active'
        this.showToast(`模型${model.name}状态已更新`)
      }
    },

    /**
     * 训练模型
     */
    trainModel(modelId) {
      this.showToast('模型训练已开始')
    },

    /**
     * 保存AI设置
     */
    saveAISettings() {
      this.showToast('AI设置保存成功！')
    },

    // 数据源方法
    /**
     * 测试数据源连接
     */
    testConnection(sourceId) {
      const source = this.dataSources.find(s => s.id === sourceId)
      if (source) {
        this.showToast(`正在测试${source.name}连接...`)
        // 模拟连接测试
        setTimeout(() => {
          source.status = 'connected'
          this.showToast(`${source.name}连接测试成功`)
        }, 2000)
      }
    },

    /**
     * 添加数据源
     */
    addDataSource() {
      this.showToast('添加数据源功能开发中')
    },

    /**
     * 编辑数据源
     */
    editDataSource(sourceId) {
      this.showToast('编辑数据源功能开发中')
    },

    /**
     * 删除数据源
     */
    deleteDataSource(sourceId) {
      const index = this.dataSources.findIndex(s => s.id === sourceId)
      if (index > -1) {
        this.dataSources.splice(index, 1)
        this.showToast('数据源删除成功')
      }
    },

    // 集成配置方法
    /**
     * 切换集成状态
     */
    toggleIntegration(integrationId) {
      const integration = this.integrations.find(i => i.id === integrationId)
      if (integration) {
        integration.enabled = !integration.enabled
        this.showToast(`${integration.name}集成已${integration.enabled ? '启用' : '禁用'}`)
      }
    },

    /**
     * 配置集成
     */
    configureIntegration(integrationId) {
      this.showToast('集成配置功能开发中')
    },

    // 用户管理方法
    /**
     * 添加用户
     */
    addUser() {
      this.showToast('添加用户功能开发中')
    },

    /**
     * 编辑用户
     */
    editUser(userId) {
      this.showToast('编辑用户功能开发中')
    },

    /**
     * 删除用户
     */
    deleteUser(userId) {
      const index = this.users.findIndex(u => u.id === userId)
      if (index > -1) {
        this.users.splice(index, 1)
        this.showToast('用户删除成功')
      }
    },

    /**
     * 重置用户密码
     */
    resetPassword(userId) {
      this.showToast('密码重置邮件已发送')
    },

    // 角色权限方法
    /**
     * 添加角色
     */
    addRole() {
      this.showToast('添加角色功能开发中')
    },

    /**
     * 编辑角色
     */
    editRole(roleId) {
      this.showToast('编辑角色功能开发中')
    },

    /**
     * 删除角色
     */
    deleteRole(roleId) {
      const role = this.roles.find(r => r.id === roleId)
      if (role && !role.isSystem) {
        const index = this.roles.findIndex(r => r.id === roleId)
        this.roles.splice(index, 1)
        this.showToast('角色删除成功')
      } else {
        this.showToast('系统角色不能删除')
      }
    },

    // 审计日志方法
    /**
     * 搜索审计日志
     */
    searchAuditLogs() {
      this.showToast('搜索功能开发中')
    },

    /**
     * 导出审计日志
     */
    exportAuditLogs() {
      this.showToast('导出功能开发中')
    },

    /**
     * 清空过滤条件
     */
    clearAuditFilter() {
      this.auditFilter = {
        type: '',
        user: '',
        dateFrom: '',
        dateTo: ''
      }
      this.showToast('过滤条件已清空')
    },

    // 备份恢复方法
    /**
     * 创建备份
     */
    createBackup() {
      this.showToast('备份创建已开始')
    },

    /**
     * 恢复备份
     */
    restoreBackup(backupId) {
      this.showToast('备份恢复功能开发中')
    },

    /**
     * 删除备份
     */
    deleteBackup(backupId) {
      const index = this.backups.findIndex(b => b.id === backupId)
      if (index > -1) {
        this.backups.splice(index, 1)
        this.showToast('备份删除成功')
      }
    },

    /**
     * 保存备份设置
     */
    saveBackupSettings() {
      this.showToast('备份设置保存成功！')
    },

    // 系统维护方法
    /**
     * 清理缓存
     */
    clearCache() {
      this.showToast('缓存清理已开始')
    },

    /**
     * 重启服务
     */
    restartService() {
      this.showToast('服务重启功能需要管理员权限')
    },

    /**
     * 检查更新
     */
    checkUpdate() {
      this.showToast('正在检查更新...')
    },

    /**
     * 优化数据库
     */
    optimizeDatabase() {
      this.showToast('数据库优化已开始')
    }
  }
}
</script>

<style scoped>
.settings-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.breadcrumb-item.active {
  color: #111827;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.settings-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.settings-sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e5e7eb;
  padding: 1.5rem 0;
  overflow-y: auto;
}

.menu-group {
  margin-bottom: 2rem;
}

.menu-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #6b7280;
  padding: 0 1.5rem;
  margin-bottom: 0.5rem;
  letter-spacing: 0.05em;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.menu-item:hover {
  background: #f3f4f6;
  color: #111827;
}

.menu-item.active {
  background: #eff6ff;
  color: #2563eb;
  border-right: 3px solid #2563eb;
}

.menu-item i {
  width: 1.25rem;
  text-align: center;
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  background: #f9fafb;
}

/* 模态框样式 */
.modal {
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

.modal-content {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

/* 提示消息样式 */
.toast {
  position: fixed;
  top: 2rem;
  right: 2rem;
  background: #10b981;
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 1001;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 按钮样式 */
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  background: white;
  color: #374151;
  border-color: #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.btn-danger {
  background: #dc2626;
  color: white;
}

.btn-danger:hover {
  background: #b91c1c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    flex-direction: column;
  }
  
  .settings-sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .content-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
}
</style>