/**
 * 告警管理页面脚本
 * 实现告警数据的动态更新、交互功能和图表渲染
 */

class AlertingManager {
    constructor() {
        this.currentTab = 'dashboard';
        this.alertData = [];
        this.charts = {};
        this.filters = {
            severity: '',
            source: '',
            search: ''
        };
        
        this.init();
    }

    /**
     * 初始化告警管理器
     */
    init() {
        this.bindEvents();
        this.loadAlertData();
        this.initCharts();
        this.startAutoRefresh();
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 侧边栏标签页切换
        document.querySelectorAll('.sidebar .menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                if (tab) {
                    this.switchTab(tab);
                }
            });
        });

        // 刷新按钮
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // 创建规则按钮
        const createRuleBtn = document.getElementById('create-rule-btn');
        if (createRuleBtn) {
            createRuleBtn.addEventListener('click', () => {
                this.showCreateRuleModal();
            });
        }

        // 过滤器
        const severityFilter = document.getElementById('severity-filter');
        const sourceFilter = document.getElementById('source-filter');
        const searchInput = document.getElementById('alert-search');

        if (severityFilter) {
            severityFilter.addEventListener('change', (e) => {
                this.filters.severity = e.target.value;
                this.filterAlerts();
            });
        }

        if (sourceFilter) {
            sourceFilter.addEventListener('change', (e) => {
                this.filters.source = e.target.value;
                this.filterAlerts();
            });
        }

        if (searchInput) {
            searchInput.addEventListener('input', Utils.debounce((e) => {
                this.filters.search = e.target.value;
                this.filterAlerts();
            }, 300));
        }

        // 时间范围选择器
        const timeRange = document.getElementById('time-range');
        if (timeRange) {
            timeRange.addEventListener('change', (e) => {
                this.updateTimeRange(e.target.value);
            });
        }

        // 模态框事件
        this.bindModalEvents();

        // 告警操作按钮
        this.bindAlertActions();
        
        // 新增：批量操作功能
        this.bindBatchActions();
        
        // 新增：告警选择功能
        this.bindAlertSelection();
    }

    /**
     * 绑定模态框事件
     */
    bindModalEvents() {
        // 关闭模态框
        document.querySelectorAll('.modal-close, .modal').forEach(element => {
            element.addEventListener('click', (e) => {
                if (e.target === element) {
                    this.closeModal();
                }
            });
        });

        // 创建规则表单提交
        const createRuleForm = document.getElementById('create-rule-form');
        if (createRuleForm) {
            createRuleForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createRule();
            });
        }
    }

    /**
     * 绑定告警操作按钮事件
     */
    bindAlertActions() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-action]');
            if (!target) return;

            const action = target.dataset.action;
            const alertId = target.dataset.alertId;

            switch (action) {
                case 'acknowledge':
                    this.acknowledgeAlert(alertId);
                    break;
                case 'silence':
                    this.silenceAlert(alertId);
                    break;
                case 'resolve':
                    this.resolveAlert(alertId);
                    break;
                case 'view-details':
                    this.viewAlertDetails(alertId);
                    break;
                case 'toggle-rule':
                    this.toggleRule(alertId);
                    break;
                case 'edit-rule':
                    this.editRule(alertId);
                    break;
                case 'delete-rule':
                    this.deleteRule(alertId);
                    break;
                case 'test-channel':
                    this.testChannel(alertId);
                    break;
                case 'edit-channel':
                    this.editChannel(alertId);
                    break;
            }
        });
    }

    /**
     * 切换标签页
     */
    switchTab(tabName) {
        // 更新当前标签
        this.currentTab = tabName;

        // 更新侧边栏激活状态
        document.querySelectorAll('.sidebar .menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // 更新面包屑
        const breadcrumbMap = {
            'dashboard': '告警仪表板',
            'active-alerts': '活跃告警',
            'rules': '告警规则',
            'channels': '通知渠道',
            'templates': '消息模板',
            'incidents': '事件处理',
            'escalation': '升级策略',
            'oncall': '值班安排',
            'history': '告警历史',
            'analytics': '告警分析'
        };
        
        const currentTabElement = document.getElementById('current-tab');
        if (currentTabElement) {
            currentTabElement.textContent = breadcrumbMap[tabName] || tabName;
        }

        // 显示对应的标签页内容
        document.querySelectorAll('.alert-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        const targetTab = document.getElementById(`${tabName}-tab`);
        if (targetTab) {
            targetTab.classList.add('active');
        }

        // 加载对应标签页的数据
        this.loadTabData(tabName);
    }

    /**
     * 加载标签页数据
     */
    loadTabData(tabName) {
        switch (tabName) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'active-alerts':
                this.loadActiveAlerts();
                break;
            case 'rules':
                this.loadAlertRules();
                break;
            case 'channels':
                this.loadNotificationChannels();
                break;
            case 'history':
                this.loadAlertHistory();
                break;
            default:
                console.log(`Loading data for ${tabName} tab`);
        }
    }

    /**
     * 加载仪表板数据
     */
    loadDashboardData() {
        // 更新统计卡片
        this.updateStatsCards();
        
        // 更新图表
        this.updateCharts();
        
        // 加载最近告警
        this.loadRecentAlerts();
    }

    /**
     * 更新统计卡片
     */
    updateStatsCards() {
        const stats = {
            critical: 5,
            warning: 12,
            info: 8,
            resolved: 23
        };

        // 更新各个统计卡片的数值
        Object.keys(stats).forEach(type => {
            const card = document.querySelector(`.stat-card.${type} .stat-content h4`);
            if (card) {
                card.textContent = stats[type];
            }
        });
    }

    /**
     * 加载活跃告警
     */
    loadActiveAlerts() {
        const mockAlerts = [
            {
                id: 'alert-001',
                title: 'CPU使用率过高',
                description: 'web-server-01 CPU使用率达到 95%',
                severity: 'critical',
                source: 'infrastructure',
                time: '2分钟前',
                duration: '5分钟',
                status: 'firing'
            },
            {
                id: 'alert-002',
                title: '内存使用率告警',
                description: 'database-01 内存使用率达到 85%',
                severity: 'warning',
                source: 'infrastructure',
                time: '5分钟前',
                duration: '12分钟',
                status: 'acknowledged'
            },
            {
                id: 'alert-003',
                title: '磁盘空间不足',
                description: '/var/log 分区使用率达到 90%',
                severity: 'warning',
                source: 'system',
                time: '10分钟前',
                duration: '25分钟',
                status: 'firing'
            },
            {
                id: 'alert-004',
                title: '网络延迟异常',
                description: '到外部API的响应时间超过 2000ms',
                severity: 'info',
                source: 'network',
                time: '15分钟前',
                duration: '8分钟',
                status: 'silenced'
            }
        ];

        this.renderActiveAlerts(mockAlerts);
    }

    /**
     * 渲染活跃告警列表
     */
    renderActiveAlerts(alerts) {
        const alertsList = document.querySelector('#active-alerts-tab .alerts-list');
        if (!alertsList) return;

        alertsList.innerHTML = alerts.map(alert => `
            <div class="alert-item">
                <div class="alert-severity ${alert.severity}"></div>
                <div class="alert-info">
                    <div class="alert-meta">
                        <span class="alert-time">${alert.time}</span>
                        <span class="source-tag ${alert.source}">${this.getSourceText(alert.source)}</span>
                    </div>
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-description">${alert.description}</div>
                </div>
                <div class="duration">${alert.duration}</div>
                <span class="status-badge ${alert.status}">${this.getStatusText(alert.status)}</span>
                <div class="action-buttons">
                    <button class="btn-icon" data-action="acknowledge" data-alert-id="${alert.id}" title="确认告警">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn-icon" data-action="silence" data-alert-id="${alert.id}" title="静默告警">
                        <i class="fas fa-volume-mute"></i>
                    </button>
                    <button class="btn-icon" data-action="view-details" data-alert-id="${alert.id}" title="查看详情">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    /**
     * 加载告警规则
     */
    loadAlertRules() {
        const mockRules = [
            {
                id: 'rule-001',
                name: 'CPU使用率告警',
                description: '当CPU使用率超过90%时触发告警',
                enabled: true,
                metric: 'cpu_usage',
                threshold: '> 90%',
                severity: 'critical',
                lastTriggered: '2小时前'
            },
            {
                id: 'rule-002',
                name: '内存使用率告警',
                description: '当内存使用率超过80%时触发告警',
                enabled: true,
                metric: 'memory_usage',
                threshold: '> 80%',
                severity: 'warning',
                lastTriggered: '1天前'
            },
            {
                id: 'rule-003',
                name: '磁盘空间告警',
                description: '当磁盘使用率超过85%时触发告警',
                enabled: false,
                metric: 'disk_usage',
                threshold: '> 85%',
                severity: 'warning',
                lastTriggered: '从未'
            },
            {
                id: 'rule-004',
                name: '网络延迟告警',
                description: '当网络延迟超过1000ms时触发告警',
                enabled: true,
                metric: 'network_latency',
                threshold: '> 1000ms',
                severity: 'info',
                lastTriggered: '30分钟前'
            }
        ];

        this.renderAlertRules(mockRules);
    }

    /**
     * 渲染告警规则列表
     */
    renderAlertRules(rules) {
        const rulesList = document.querySelector('#rules-tab .rules-list');
        if (!rulesList) return;

        rulesList.innerHTML = rules.map(rule => `
            <div class="rule-item">
                <div class="rule-status">
                    <div class="status-toggle">
                        <input type="checkbox" id="${rule.id}" ${rule.enabled ? 'checked' : ''}>
                        <label for="${rule.id}" class="toggle-label"></label>
                    </div>
                    <span class="${rule.enabled ? 'rule-enabled' : 'rule-disabled'}">
                        ${rule.enabled ? '已启用' : '已禁用'}
                    </span>
                </div>
                <div class="rule-content">
                    <div class="rule-name">${rule.name}</div>
                    <div class="rule-description">${rule.description}</div>
                    <div class="rule-meta">
                        <div class="rule-metric">
                            <i class="fas fa-chart-line"></i>
                            <span>${rule.metric}</span>
                        </div>
                        <div class="rule-threshold">
                            <i class="fas fa-exclamation-triangle"></i>
                            <span>${rule.threshold}</span>
                        </div>
                        <div class="rule-severity">
                            <i class="fas fa-flag"></i>
                            <span>${this.getSeverityText(rule.severity)}</span>
                        </div>
                        <div class="rule-last-triggered">
                            <i class="fas fa-clock"></i>
                            <span>最后触发: ${rule.lastTriggered}</span>
                        </div>
                    </div>
                </div>
                <div class="rule-actions">
                    <button class="btn-icon" data-action="edit-rule" data-alert-id="${rule.id}" title="编辑规则">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" data-action="test-rule" data-alert-id="${rule.id}" title="测试规则">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="btn-icon" data-action="delete-rule" data-alert-id="${rule.id}" title="删除规则">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    /**
     * 加载通知渠道
     */
    loadNotificationChannels() {
        const mockChannels = [
            {
                id: 'channel-001',
                name: '邮件通知',
                type: 'email',
                description: '发送告警邮件到运维团队',
                enabled: true,
                config: 'ops-team@company.com',
                stats: { sent: 156, failed: 2 }
            },
            {
                id: 'channel-002',
                name: 'Slack通知',
                type: 'slack',
                description: '发送消息到#alerts频道',
                enabled: true,
                config: '#alerts',
                stats: { sent: 89, failed: 0 }
            },
            {
                id: 'channel-003',
                name: 'Webhook通知',
                type: 'webhook',
                description: '发送到外部监控系统',
                enabled: false,
                config: 'http://localhost:8080/api/webhook',
                stats: { sent: 0, failed: 0 }
            },
            {
                id: 'channel-004',
                name: '短信通知',
                type: 'sms',
                description: '紧急告警短信通知',
                enabled: true,
                config: '+86 138****8888',
                stats: { sent: 12, failed: 1 }
            }
        ];

        this.renderNotificationChannels(mockChannels);
    }

    /**
     * 渲染通知渠道
     */
    renderNotificationChannels(channels) {
        const channelsGrid = document.querySelector('#channels-tab .channels-grid');
        if (!channelsGrid) return;

        channelsGrid.innerHTML = channels.map(channel => `
            <div class="channel-card">
                <div class="channel-header">
                    <div class="channel-icon ${channel.type}">
                        <i class="fas fa-${this.getChannelIcon(channel.type)}"></i>
                    </div>
                    <div class="channel-info">
                        <h4>${channel.name}</h4>
                        <p>${channel.description}</p>
                    </div>
                </div>
                <div class="channel-status">
                    <div class="channel-enabled">
                        <i class="fas fa-${channel.enabled ? 'check-circle' : 'times-circle'}"></i>
                        <span>${channel.enabled ? '已启用' : '已禁用'}</span>
                    </div>
                </div>
                <div class="channel-config">
                    <strong>配置:</strong> ${channel.config}
                </div>
                <div class="channel-stats">
                    <div>已发送: ${channel.stats.sent}</div>
                    <div>失败: ${channel.stats.failed}</div>
                </div>
                <div class="channel-actions">
                    <button class="btn-sm" data-action="test-channel" data-alert-id="${channel.id}">测试</button>
                    <button class="btn-sm" data-action="edit-channel" data-alert-id="${channel.id}">编辑</button>
                    <button class="btn-sm primary" data-action="toggle-channel" data-alert-id="${channel.id}">
                        ${channel.enabled ? '禁用' : '启用'}
                    </button>
                </div>
            </div>
        `).join('');
    }

    /**
     * 加载告警历史
     */
    loadAlertHistory() {
        const mockHistory = [
            {
                id: 'history-001',
                event: '告警触发',
                alert: 'CPU使用率过高',
                time: '2024-01-19 14:30:25',
                duration: '5分钟',
                status: 'triggered',
                details: 'web-server-01 CPU使用率达到 95%'
            },
            {
                id: 'history-002',
                event: '告警确认',
                alert: '内存使用率告警',
                time: '2024-01-19 14:25:10',
                duration: '2分钟',
                status: 'acknowledged',
                details: '运维人员已确认，正在处理中'
            },
            {
                id: 'history-003',
                event: '告警解决',
                alert: '磁盘空间不足',
                time: '2024-01-19 14:20:45',
                duration: '15分钟',
                status: 'resolved',
                details: '已清理日志文件，磁盘使用率降至 70%'
            },
            {
                id: 'history-004',
                event: '告警触发',
                alert: '网络延迟异常',
                time: '2024-01-19 14:15:30',
                duration: '8分钟',
                status: 'triggered',
                details: '到外部API的响应时间超过 2000ms'
            }
        ];

        this.renderAlertHistory(mockHistory);
    }

    /**
     * 渲染告警历史
     */
    renderAlertHistory(history) {
        const historyList = document.querySelector('#history-tab .history-list');
        if (!historyList) return;

        historyList.innerHTML = history.map((item, index) => `
            <div class="history-item">
                <div class="history-timeline">
                    <div class="timeline-dot ${item.status}"></div>
                    ${index < history.length - 1 ? '<div class="timeline-line"></div>' : ''}
                </div>
                <div class="history-content">
                    <div class="history-time">${item.time}</div>
                    <div class="history-event">${item.event}: ${item.alert}</div>
                    <div class="history-details">${item.details}</div>
                </div>
                <div class="history-duration">${item.duration}</div>
            </div>
        `).join('');
    }

    /**
     * 获取来源文本
     */
    getSourceText(source) {
        const sourceMap = {
            'system': '系统',
            'application': '应用',
            'infrastructure': '基础设施',
            'network': '网络'
        };
        return sourceMap[source] || source;
    }

    /**
     * 获取状态文本
     */
    getStatusText(status) {
        const statusMap = {
            'firing': '触发中',
            'acknowledged': '已确认',
            'silenced': '已静默',
            'resolved': '已解决'
        };
        return statusMap[status] || status;
    }

    /**
     * 获取严重级别文本
     */
    getSeverityText(severity) {
        const severityMap = {
            'critical': '严重',
            'warning': '警告',
            'info': '信息'
        };
        return severityMap[severity] || severity;
    }

    /**
     * 获取渠道图标
     */
    getChannelIcon(type) {
        const iconMap = {
            'email': 'envelope',
            'slack': 'slack',
            'webhook': 'link',
            'sms': 'sms'
        };
        return iconMap[type] || 'bell';
    }

    /**
     * 确认告警
     */
    acknowledgeAlert(alertId) {
        console.log(`Acknowledging alert: ${alertId}`);
        this.showNotification('告警已确认', 'success');
        // 这里应该调用API确认告警
        this.refreshData();
    }

    /**
     * 静默告警
     */
    silenceAlert(alertId) {
        console.log(`Silencing alert: ${alertId}`);
        this.showNotification('告警已静默', 'success');
        // 这里应该调用API静默告警
        this.refreshData();
    }

    /**
     * 解决告警
     */
    resolveAlert(alertId) {
        console.log(`Resolving alert: ${alertId}`);
        this.showNotification('告警已解决', 'success');
        // 这里应该调用API解决告警
        this.refreshData();
    }

    /**
     * 查看告警详情
     */
    viewAlertDetails(alertId) {
        console.log(`Viewing alert details: ${alertId}`);
        // 这里应该显示告警详情模态框
    }

    /**
     * 切换规则状态
     */
    toggleRule(ruleId) {
        console.log(`Toggling rule: ${ruleId}`);
        this.showNotification('规则状态已更新', 'success');
        // 这里应该调用API切换规则状态
        this.refreshData();
    }

    /**
     * 编辑规则
     */
    editRule(ruleId) {
        console.log(`Editing rule: ${ruleId}`);
        // 这里应该显示编辑规则模态框
    }

    /**
     * 删除规则
     */
    deleteRule(ruleId) {
        if (confirm('确定要删除这个规则吗？')) {
            console.log(`Deleting rule: ${ruleId}`);
            this.showNotification('规则已删除', 'success');
            // 这里应该调用API删除规则
            this.refreshData();
        }
    }

    /**
     * 测试通知渠道
     */
    testChannel(channelId) {
        console.log(`Testing channel: ${channelId}`);
        this.showNotification('测试消息已发送', 'info');
        // 这里应该调用API测试通知渠道
    }

    /**
     * 编辑通知渠道
     */
    editChannel(channelId) {
        console.log(`Editing channel: ${channelId}`);
        // 这里应该显示编辑渠道模态框
    }

    /**
     * 显示创建规则模态框
     */
    showCreateRuleModal() {
        const modal = document.getElementById('create-rule-modal');
        if (modal) {
            modal.classList.add('active');
        }
    }

    /**
     * 关闭模态框
     */
    closeModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    /**
     * 创建规则
     */
    createRule() {
        const form = document.getElementById('create-rule-form');
        const formData = new FormData(form);
        
        const ruleData = {
            name: formData.get('ruleName'),
            description: formData.get('ruleDescription'),
            metric: formData.get('metricSource'),
            condition: formData.get('condition'),
            threshold: formData.get('threshold'),
            severity: formData.get('severity')
        };

        console.log('Creating rule:', ruleData);
        this.showNotification('规则创建成功', 'success');
        this.closeModal();
        this.refreshData();
    }

    /**
     * 加载告警数据
     */
    loadAlertData() {
        // 模拟API调用
        setTimeout(() => {
            this.alertData = this.generateMockData();
            this.updateDashboard();
        }, 500);
    }

    /**
     * 生成模拟数据
     */
    generateMockData() {
        return {
            stats: {
                total: 48,
                critical: 5,
                warning: 12,
                info: 8,
                resolved: 23
            },
            trends: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                data: [12, 8, 15, 22, 18, 25]
            }
        };
    }

    /**
     * 初始化图表
     */
    initCharts() {
        this.initTrendChart();
        this.initSeverityChart();
        this.initSourceChart();
    }

    /**
     * 初始化趋势图表
     */
    initTrendChart() {
        const ctx = document.getElementById('alert-trend-chart');
        if (!ctx) return;

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                datasets: [{
                    label: '告警数量',
                    data: [12, 8, 15, 22, 18, 25],
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#f1f5f9'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    /**
     * 初始化严重级别分布图表
     */
    initSeverityChart() {
        const ctx = document.getElementById('severity-distribution-chart');
        if (!ctx) return;

        this.charts.severity = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['严重', '警告', '信息'],
                datasets: [{
                    data: [5, 12, 8],
                    backgroundColor: ['#dc2626', '#f59e0b', '#3b82f6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    /**
     * 初始化来源分析图表
     */
    initSourceChart() {
        const ctx = document.getElementById('source-analysis-chart');
        if (!ctx) return;

        this.charts.source = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['系统', '应用', '基础设施', '网络'],
                datasets: [{
                    label: '告警数量',
                    data: [8, 12, 15, 5],
                    backgroundColor: ['#dc2626', '#3b82f6', '#10b981', '#f59e0b'],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#f1f5f9'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    /**
     * 更新图表
     */
    updateCharts() {
        if (this.charts.trend) {
            this.charts.trend.data.datasets[0].data = [12, 8, 15, 22, 18, 25];
            this.charts.trend.update();
        }

        if (this.charts.severity) {
            this.charts.severity.data.datasets[0].data = [5, 12, 8];
            this.charts.severity.update();
        }

        if (this.charts.source) {
            this.charts.source.data.datasets[0].data = [8, 12, 15, 5];
            this.charts.source.update();
        }
    }

    /**
     * 更新仪表板
     */
    updateDashboard() {
        this.updateStatsCards();
        this.updateCharts();
    }

    /**
     * 刷新数据
     */
    refreshData() {
        this.showNotification('数据刷新中...', 'info');
        this.loadTabData(this.currentTab);
        setTimeout(() => {
            this.showNotification('数据已更新', 'success');
        }, 1000);
    }

    /**
     * 开始自动刷新
     */
    startAutoRefresh() {
        setInterval(() => {
            this.loadTabData(this.currentTab);
        }, 30000); // 每30秒刷新一次
    }

    /**
     * 绑定批量操作功能
     */
    bindBatchActions() {
        // 全选复选框
        const selectAllCheckbox = document.getElementById('select-all-alerts');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.handleSelectAll(e.target.checked);
            });
        }
        
        // 批量确认按钮
        const batchAcknowledgeBtn = document.getElementById('batch-acknowledge-btn');
        if (batchAcknowledgeBtn) {
            batchAcknowledgeBtn.addEventListener('click', () => {
                this.batchAcknowledgeAlerts();
            });
        }
        
        // 批量分配按钮
        const batchAssignBtn = document.getElementById('batch-assign-btn');
        if (batchAssignBtn) {
            batchAssignBtn.addEventListener('click', () => {
                this.batchAssignAlerts();
            });
        }
    }

    /**
     * 绑定告警选择功能
     */
    bindAlertSelection() {
        // 使用事件委托处理动态生成的复选框
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('alert-select')) {
                this.handleAlertSelection(e.target);
            }
        });
    }

    /**
     * 处理全选操作
     */
    handleSelectAll(isChecked) {
        const checkboxes = document.querySelectorAll('.alert-select');
        checkboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
        this.updateBatchActionButtons();
    }

    /**
     * 处理单个告警选择
     */
    handleAlertSelection(checkbox) {
        this.updateBatchActionButtons();
        this.updateSelectAllCheckbox();
    }

    /**
     * 更新批量操作按钮状态
     */
    updateBatchActionButtons() {
        const selectedCount = document.querySelectorAll('.alert-select:checked').length;
        const batchAcknowledgeBtn = document.getElementById('batch-acknowledge-btn');
        const batchAssignBtn = document.getElementById('batch-assign-btn');
        
        if (batchAcknowledgeBtn) {
            batchAcknowledgeBtn.disabled = selectedCount === 0;
        }
        if (batchAssignBtn) {
            batchAssignBtn.disabled = selectedCount === 0;
        }
    }

    /**
     * 更新全选复选框状态
     */
    updateSelectAllCheckbox() {
        const selectAllCheckbox = document.getElementById('select-all-alerts');
        const checkboxes = document.querySelectorAll('.alert-select');
        const checkedCount = document.querySelectorAll('.alert-select:checked').length;
        
        if (selectAllCheckbox && checkboxes.length > 0) {
            selectAllCheckbox.checked = checkedCount === checkboxes.length;
            selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
        }
    }

    /**
     * 批量确认告警
     */
    batchAcknowledgeAlerts() {
        const selectedAlerts = document.querySelectorAll('.alert-select:checked');
        if (selectedAlerts.length === 0) return;
        
        if (confirm(`确定要确认选中的 ${selectedAlerts.length} 个告警吗？`)) {
            selectedAlerts.forEach(checkbox => {
                const alertId = checkbox.closest('.alert-card').dataset.alertId;
                this.acknowledgeAlert(alertId, false); // false表示不显示单独的确认对话框
            });
            
            // 清空选择
            selectedAlerts.forEach(checkbox => checkbox.checked = false);
            this.updateBatchActionButtons();
            
            this.showNotification(`已批量确认 ${selectedAlerts.length} 个告警`, 'success');
        }
    }

    /**
     * 批量分配告警
     */
    batchAssignAlerts() {
        const selectedAlerts = document.querySelectorAll('.alert-select:checked');
        if (selectedAlerts.length === 0) return;
        
        const assignee = prompt(`请输入分配给的处理人 (共${selectedAlerts.length}个告警):`);
        if (assignee) {
            selectedAlerts.forEach(checkbox => {
                const alertId = checkbox.closest('.alert-card').dataset.alertId;
                this.assignAlert(alertId, assignee, false); // false表示不显示单独的确认对话框
            });
            
            // 清空选择
            selectedAlerts.forEach(checkbox => checkbox.checked = false);
            this.updateBatchActionButtons();
            
            this.showNotification(`已批量分配给 ${assignee}`, 'success');
        }
    }

    /**
     * 确认告警 - 增强版本
     */
    acknowledgeAlert(alertId, showConfirm = true) {
        const action = () => {
            console.log(`确认告警: ${alertId}`);
            
            // 更新UI状态
            const alertCard = document.querySelector(`[data-alert-id="${alertId}"]`);
            if (alertCard) {
                const statusBadge = alertCard.querySelector('.status-badge');
                if (statusBadge) {
                    statusBadge.className = 'status-badge acknowledged';
                    statusBadge.textContent = '已确认';
                }
                alertCard.classList.add('acknowledged');
            }
            
            if (showConfirm) {
                this.showNotification('告警已确认', 'success');
            }
        };
        
        if (showConfirm) {
            if (confirm('确定要确认这个告警吗？确认后告警状态将变为"已确认"。')) {
                action();
            }
        } else {
            action();
        }
    }

    /**
     * 分配告警 - 增强版本
     */
    assignAlert(alertId, assignee = null, showConfirm = true) {
        const action = (assigneeName) => {
            console.log(`分配告警 ${alertId} 给 ${assigneeName}`);
            
            // 更新UI状态
            const alertCard = document.querySelector(`[data-alert-id="${alertId}"]`);
            if (alertCard) {
                const assigneeElement = alertCard.querySelector('.meta-item .unassigned, .meta-item .assigned');
                if (assigneeElement) {
                    assigneeElement.className = 'assigned';
                    assigneeElement.textContent = assigneeName;
                }
            }
            
            if (showConfirm) {
                this.showNotification(`告警已分配给 ${assigneeName}`, 'success');
            }
        };
        
        if (assignee) {
            action(assignee);
        } else if (showConfirm) {
            const assigneeName = prompt('请输入分配给的处理人:');
            if (assigneeName) {
                action(assigneeName);
            }
        }
    }

    /**
     * 升级处理告警
     */
    escalateAlert(alertId) {
        const level = prompt('请输入升级级别:\n1 - 高级工程师\n2 - 技术主管\n3 - 技术总监');
        if (level && ['1', '2', '3'].includes(level)) {
            console.log(`升级告警 ${alertId} 到级别 ${level}`);
            this.showNotification('告警已升级处理', 'success');
        }
    }

    /**
     * 暂缓处理告警
     */
    snoozeAlert(alertId) {
        const duration = prompt('请输入暂缓时间（分钟）:', '30');
        if (duration && !isNaN(duration)) {
            console.log(`暂缓告警 ${alertId} ${duration} 分钟`);
            this.showNotification(`告警已暂缓 ${duration} 分钟`, 'info');
        }
    }

    /**
     * 静默告警
     */
    silenceAlert(alertId) {
        const duration = prompt('请输入静默时间（分钟）:', '60');
        const reason = prompt('请输入静默原因:');
        if (duration && reason && !isNaN(duration)) {
            console.log(`静默告警 ${alertId} ${duration} 分钟，原因: ${reason}`);
            this.showNotification(`告警已静默 ${duration} 分钟`, 'warning');
        }
    }

    /**
     * 解决告警
     */
    resolveAlert(alertId) {
        const resolution = prompt('请输入解决方案:');
        if (resolution) {
            console.log(`解决告警 ${alertId}，解决方案: ${resolution}`);
            
            // 更新UI状态
            const alertCard = document.querySelector(`[data-alert-id="${alertId}"]`);
            if (alertCard) {
                const statusBadge = alertCard.querySelector('.status-badge');
                if (statusBadge) {
                    statusBadge.className = 'status-badge resolved';
                    statusBadge.textContent = '已解决';
                }
            }
            
            this.showNotification('告警已标记为解决', 'success');
        }
    }

    /**
     * 更新处理进度
     */
    updateProgress(alertId) {
        const progress = prompt('请输入处理进度:');
        if (progress) {
            console.log(`更新告警 ${alertId} 进度: ${progress}`);
            this.showNotification('处理进度已更新', 'info');
        }
    }

    /**
     * 重新分配告警
     */
    reassignAlert(alertId) {
        this.assignAlert(alertId);
    }

    /**
     * 查看告警详情
     */
    viewAlertDetails(alertId) {
        // 模拟获取详细信息
        const alertDetails = {
            id: alertId,
            title: 'CPU使用率过高',
            description: '服务器 web-01 CPU使用率达到 95%，已超过阈值 90%',
            severity: 'critical',
            status: 'firing',
            source: 'web-01.production.com',
            category: '基础设施',
            createdAt: '2024-01-15 14:30:25',
            duration: '25分钟',
            metrics: {
                current: '95.2%',
                threshold: '90%'
            }
        };
        
        // 简化版本的详情显示
        const details = `
告警详情:
ID: ${alertDetails.id}
标题: ${alertDetails.title}
描述: ${alertDetails.description}
级别: ${alertDetails.severity}
状态: ${alertDetails.status}
来源: ${alertDetails.source}
分类: ${alertDetails.category}
创建时间: ${alertDetails.createdAt}
持续时间: ${alertDetails.duration}
当前值: ${alertDetails.metrics.current}
阈值: ${alertDetails.metrics.threshold}
        `;
        alert(details);
    }

    /**
     * 过滤告警
     */
    filterAlerts() {
        const severityFilter = document.getElementById('active-severity-filter');
        const statusFilter = document.getElementById('active-status-filter');
        const assigneeFilter = document.getElementById('active-assignee-filter');
        
        if (!severityFilter || !statusFilter || !assigneeFilter) return;
        
        const severity = severityFilter.value;
        const status = statusFilter.value;
        const assignee = assigneeFilter.value;
        
        const alertCards = document.querySelectorAll('.alert-card');
        
        alertCards.forEach(card => {
            let shouldShow = true;
            
            // 级别筛选
            if (severity && !card.classList.contains(severity)) {
                shouldShow = false;
            }
            
            // 状态筛选
            if (status) {
                const statusBadge = card.querySelector('.status-badge');
                if (!statusBadge || !statusBadge.classList.contains(status)) {
                    shouldShow = false;
                }
            }
            
            // 处理人筛选
            if (assignee) {
                const assigneeElement = card.querySelector('.meta-item .assigned, .meta-item .unassigned');
                if (assignee === 'unassigned' && !assigneeElement?.classList.contains('unassigned')) {
                    shouldShow = false;
                } else if (assignee !== 'unassigned' && assigneeElement?.classList.contains('unassigned')) {
                    shouldShow = false;
                }
            }
            
            card.style.display = shouldShow ? 'block' : 'none';
        });
        
        // 更新统计
        this.updateAlertSummary();
    }

    /**
     * 更新告警统计
     */
    updateAlertSummary() {
        const visibleCards = document.querySelectorAll('.alert-card:not([style*="display: none"])');
        const criticalCount = document.querySelectorAll('.alert-card.critical:not([style*="display: none"])').length;
        const warningCount = document.querySelectorAll('.alert-card.warning:not([style*="display: none"])').length;
        const infoCount = document.querySelectorAll('.alert-card.info:not([style*="display: none"])').length;
        const unassignedCount = document.querySelectorAll('.alert-card:not([style*="display: none"]) .unassigned').length;
        
        // 更新统计数字
        const totalElement = document.getElementById('total-alerts');
        const criticalElement = document.getElementById('critical-alerts');
        const warningElement = document.getElementById('warning-alerts');
        const infoElement = document.getElementById('info-alerts');
        const unassignedElement = document.getElementById('unassigned-alerts');
        
        if (totalElement) totalElement.textContent = visibleCards.length;
        if (criticalElement) criticalElement.textContent = criticalCount;
        if (warningElement) warningElement.textContent = warningCount;
        if (infoElement) infoElement.textContent = infoCount;
        if (unassignedElement) unassignedElement.textContent = unassignedCount;
    }

    /**
     * 过滤告警
     */
    filterAlerts() {
        // 实现告警过滤逻辑
        console.log('Filtering alerts with:', this.filters);
    }

    /**
     * 更新时间范围
     */
    updateTimeRange(range) {
        console.log('更新时间范围:', range);
        this.loadAlertData();
    }

    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type} show`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : 'info-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// 工具函数 - 检查是否已存在Utils对象
if (typeof Utils === 'undefined') {
    const Utils = {
        debounce: (func, wait) => {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    };
    window.Utils = Utils;
}

// 通知样式
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 16px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification.success {
        background: #10b981;
    }
    
    .notification.error {
        background: #dc2626;
    }
    
    .notification.info {
        background: #3b82f6;
    }
`;

// 添加通知样式到页面
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// 页面加载完成后初始化告警管理器
document.addEventListener('DOMContentLoaded', () => {
    window.alertingManager = new AlertingManager();
});