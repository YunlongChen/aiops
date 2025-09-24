/**
 * 自愈系统管理器
 * 负责自愈系统页面的交互功能和数据管理
 */
class SelfHealingManager {
    constructor() {
        this.currentTab = 'dashboard';
        this.charts = {};
        this.updateInterval = null;
        this.init();
    }

    /**
     * 初始化自愈系统管理器
     */
    init() {
        this.bindEvents();
        this.initCharts();
        this.loadData();
        this.startAutoUpdate();
        
        // 显示加载完成通知
        this.showNotification('自愈系统已加载完成', 'success');
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 侧边栏标签页切换
        document.querySelectorAll('.sidebar .menu-item[data-tab]').forEach(item => {
            item.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });

        // 刷新按钮
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // 创建脚本按钮
        const createScriptBtn = document.getElementById('create-script-btn');
        if (createScriptBtn) {
            createScriptBtn.addEventListener('click', () => {
                this.showCreateScriptModal();
            });
        }

        // 时间范围选择器
        const timeRangeSelect = document.getElementById('time-range');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', (e) => {
                this.updateTimeRange(e.target.value);
            });
        }

        // 暂停全部按钮
        const pauseAllBtn = document.getElementById('pause-all-btn');
        if (pauseAllBtn) {
            pauseAllBtn.addEventListener('click', () => {
                this.pauseAllTasks();
            });
        }

        // 查看全部历史按钮
        const viewAllHistoryBtn = document.getElementById('view-all-history');
        if (viewAllHistoryBtn) {
            viewAllHistoryBtn.addEventListener('click', () => {
                this.switchTab('history');
            });
        }

        // 模态框事件
        this.bindModalEvents();

        // 任务操作按钮
        this.bindTaskActions();
    }

    /**
     * 绑定模态框事件
     */
    bindModalEvents() {
        const modal = document.getElementById('create-script-modal');
        const closeBtn = modal?.querySelector('.modal-close');
        const cancelBtn = document.getElementById('cancel-create');
        const form = document.getElementById('create-script-form');

        // 关闭模态框
        [closeBtn, cancelBtn].forEach(btn => {
            if (btn) {
                btn.addEventListener('click', () => {
                    this.hideCreateScriptModal();
                });
            }
        });

        // 点击背景关闭模态框
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideCreateScriptModal();
                }
            });
        }

        // 表单提交
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createScript();
            });
        }
    }

    /**
     * 绑定任务操作按钮事件
     */
    bindTaskActions() {
        // 任务操作按钮
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.task-actions .btn');
            if (!btn) return;

            const taskCard = btn.closest('.task-card');
            const taskId = taskCard?.querySelector('.task-id')?.textContent;

            if (btn.textContent.includes('暂停')) {
                this.pauseTask(taskId);
            } else if (btn.textContent.includes('停止')) {
                this.stopTask(taskId);
            } else if (btn.textContent.includes('详情')) {
                this.showTaskDetails(taskId);
            } else if (btn.textContent.includes('立即执行')) {
                this.executeTask(taskId);
            } else if (btn.textContent.includes('取消')) {
                this.cancelTask(taskId);
            }
        });

        // 历史记录操作按钮
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-icon');
            if (!btn) return;

            const row = btn.closest('.history-row');
            const taskId = row?.querySelector('.task-id')?.textContent;

            if (btn.title === '查看日志') {
                this.showTaskLogs(taskId);
            } else if (btn.title === '重新执行') {
                this.reExecuteTask(taskId);
            }
        });
    }

    /**
     * 切换标签页
     */
    switchTab(tab) {
        // 更新侧边栏激活状态
        document.querySelectorAll('.sidebar .menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`.sidebar .menu-item[data-tab="${tab}"]`)?.classList.add('active');

        // 更新标签页内容
        document.querySelectorAll('.healing-tab').forEach(tabContent => {
            tabContent.classList.remove('active');
        });
        document.getElementById(`${tab}-tab`)?.classList.add('active');

        // 更新面包屑
        const breadcrumbMap = {
            'dashboard': '自愈仪表板',
            'active-healing': '活跃修复',
            'scripts': '修复脚本',
            'workflows': '工作流程',
            'triggers': '触发器',
            'rules': '自愈规则',
            'policies': '策略管理',
            'conditions': '条件设置',
            'history': '修复历史',
            'analytics': '效果分析',
            'reports': '报告中心'
        };

        const currentTabElement = document.getElementById('current-tab');
        if (currentTabElement) {
            currentTabElement.textContent = breadcrumbMap[tab] || tab;
        }

        this.currentTab = tab;

        // 根据标签页加载相应数据
        this.loadTabData(tab);
    }

    /**
     * 初始化图表
     */
    initCharts() {
        this.initSuccessRateChart();
        this.initRepairTypeChart();
        this.initRepairTimeChart();
        this.initPreventionEffectChart();
    }

    /**
     * 初始化成功率趋势图表
     */
    initSuccessRateChart() {
        const ctx = document.getElementById('success-rate-chart');
        if (!ctx) return;

        this.charts.successRate = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                datasets: [{
                    label: '成功率',
                    data: [92, 94, 91, 96, 94, 95],
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
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
                        beginAtZero: false,
                        min: 85,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * 初始化修复类型分布图表
     */
    initRepairTypeChart() {
        const ctx = document.getElementById('repair-type-chart');
        if (!ctx) return;

        this.charts.repairType = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['CPU优化', '内存清理', '服务重启', '网络修复', '磁盘清理'],
                datasets: [{
                    data: [35, 25, 20, 12, 8],
                    backgroundColor: [
                        '#3B82F6',
                        '#10B981',
                        '#F59E0B',
                        '#EF4444',
                        '#8B5CF6'
                    ],
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
     * 初始化平均修复时间图表
     */
    initRepairTimeChart() {
        const ctx = document.getElementById('repair-time-chart');
        if (!ctx) return;

        this.charts.repairTime = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['CPU', '内存', '服务', '网络', '磁盘'],
                datasets: [{
                    label: '平均修复时间(分钟)',
                    data: [2.5, 1.8, 3.2, 4.1, 2.9],
                    backgroundColor: '#3B82F6',
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
                        ticks: {
                            callback: function(value) {
                                return value + 'min';
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * 初始化故障预防效果图表
     */
    initPreventionEffectChart() {
        const ctx = document.getElementById('prevention-effect-chart');
        if (!ctx) return;

        this.charts.preventionEffect = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                datasets: [{
                    label: '预防成功率',
                    data: [75, 78, 82, 79, 85, 81, 78],
                    borderColor: '#8B5CF6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
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
                        beginAtZero: false,
                        min: 70,
                        max: 90,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * 加载数据
     */
    loadData() {
        this.loadDashboardData();
    }

    /**
     * 加载仪表板数据
     */
    loadDashboardData() {
        // 模拟加载统计数据
        this.updateStats();
        
        // 模拟加载活跃任务
        this.updateActiveTasks();
        
        // 模拟加载历史记录
        this.updateHistory();
    }

    /**
     * 加载标签页数据
     */
    loadTabData(tab) {
        switch (tab) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'active-healing':
                this.loadActiveHealingData();
                break;
            case 'scripts':
                this.loadScriptsData();
                break;
            case 'history':
                this.loadHistoryData();
                break;
            // 其他标签页...
        }
    }

    /**
     * 更新统计数据
     */
    updateStats() {
        // 模拟实时统计数据更新
        const stats = {
            success: Math.floor(Math.random() * 10) + 45,
            running: Math.floor(Math.random() * 5) + 1,
            failed: Math.floor(Math.random() * 3) + 1,
            rate: Math.floor(Math.random() * 5) + 92
        };

        // 更新统计卡片
        const successCard = document.querySelector('.stat-card.success .stat-value');
        const runningCard = document.querySelector('.stat-card.running .stat-value');
        const failedCard = document.querySelector('.stat-card.failed .stat-value');
        const rateCard = document.querySelector('.stat-card.rate .stat-value');

        if (successCard) successCard.textContent = stats.success;
        if (runningCard) runningCard.textContent = stats.running;
        if (failedCard) failedCard.textContent = stats.failed;
        if (rateCard) rateCard.textContent = stats.rate + '%';
    }

    /**
     * 更新活跃任务
     */
    updateActiveTasks() {
        // 模拟更新任务进度
        const progressBars = document.querySelectorAll('.task-card.running .progress-fill');
        progressBars.forEach(bar => {
            const currentWidth = parseInt(bar.style.width) || 0;
            const newWidth = Math.min(currentWidth + Math.random() * 5, 100);
            bar.style.width = newWidth + '%';
            
            const progressText = bar.parentElement.nextElementSibling;
            if (progressText) {
                progressText.textContent = `${Math.floor(newWidth)}% - 正在执行修复操作`;
            }
        });
    }

    /**
     * 更新历史记录
     */
    updateHistory() {
        // 模拟历史记录数据更新
        console.log('更新历史记录数据');
    }

    /**
     * 刷新数据
     */
    refreshData() {
        this.showNotification('正在刷新数据...', 'info');
        
        // 模拟数据刷新
        setTimeout(() => {
            this.loadData();
            this.updateCharts();
            this.showNotification('数据刷新完成', 'success');
        }, 1000);
    }

    /**
     * 更新图表数据
     */
    updateCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.update) {
                chart.update();
            }
        });
    }

    /**
     * 更新时间范围
     */
    updateTimeRange(range) {
        this.showNotification(`时间范围已切换到: ${range}`, 'info');
        
        // 根据时间范围重新加载数据
        setTimeout(() => {
            this.loadData();
            this.updateCharts();
        }, 500);
    }

    /**
     * 显示创建脚本模态框
     */
    showCreateScriptModal() {
        const modal = document.getElementById('create-script-modal');
        if (modal) {
            modal.classList.add('active');
            
            // 重置表单
            const form = document.getElementById('create-script-form');
            if (form) {
                form.reset();
            }
        }
    }

    /**
     * 隐藏创建脚本模态框
     */
    hideCreateScriptModal() {
        const modal = document.getElementById('create-script-modal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    /**
     * 创建脚本
     */
    createScript() {
        const form = document.getElementById('create-script-form');
        if (!form) return;

        const formData = new FormData(form);
        const scriptData = {
            name: formData.get('scriptName'),
            description: formData.get('scriptDescription'),
            type: formData.get('scriptType'),
            targetType: formData.get('targetType'),
            content: formData.get('scriptContent')
        };

        // 验证表单数据
        if (!scriptData.name || !scriptData.type || !scriptData.targetType) {
            this.showNotification('请填写必填字段', 'error');
            return;
        }

        // 模拟创建脚本
        this.showNotification('正在创建脚本...', 'info');
        
        setTimeout(() => {
            this.hideCreateScriptModal();
            this.showNotification(`脚本 "${scriptData.name}" 创建成功`, 'success');
        }, 1000);
    }

    /**
     * 暂停所有任务
     */
    pauseAllTasks() {
        this.showNotification('正在暂停所有活跃任务...', 'warning');
        
        setTimeout(() => {
            this.showNotification('所有活跃任务已暂停', 'success');
        }, 1000);
    }

    /**
     * 暂停任务
     */
    pauseTask(taskId) {
        this.showNotification(`正在暂停任务 ${taskId}...`, 'warning');
        
        setTimeout(() => {
            this.showNotification(`任务 ${taskId} 已暂停`, 'success');
        }, 500);
    }

    /**
     * 停止任务
     */
    stopTask(taskId) {
        this.showNotification(`正在停止任务 ${taskId}...`, 'warning');
        
        setTimeout(() => {
            this.showNotification(`任务 ${taskId} 已停止`, 'success');
        }, 500);
    }

    /**
     * 显示任务详情
     */
    showTaskDetails(taskId) {
        this.showNotification(`正在加载任务 ${taskId} 详情...`, 'info');
        
        // 这里可以打开一个详情模态框或跳转到详情页面
        setTimeout(() => {
            this.showNotification(`任务 ${taskId} 详情已加载`, 'success');
        }, 500);
    }

    /**
     * 执行任务
     */
    executeTask(taskId) {
        this.showNotification(`正在执行任务 ${taskId}...`, 'info');
        
        setTimeout(() => {
            this.showNotification(`任务 ${taskId} 已开始执行`, 'success');
        }, 500);
    }

    /**
     * 取消任务
     */
    cancelTask(taskId) {
        this.showNotification(`正在取消任务 ${taskId}...`, 'warning');
        
        setTimeout(() => {
            this.showNotification(`任务 ${taskId} 已取消`, 'success');
        }, 500);
    }

    /**
     * 显示任务日志
     */
    showTaskLogs(taskId) {
        this.showNotification(`正在加载任务 ${taskId} 日志...`, 'info');
        
        // 这里可以打开一个日志查看器
        setTimeout(() => {
            this.showNotification(`任务 ${taskId} 日志已加载`, 'success');
        }, 500);
    }

    /**
     * 重新执行任务
     */
    reExecuteTask(taskId) {
        this.showNotification(`正在重新执行任务 ${taskId}...`, 'info');
        
        setTimeout(() => {
            this.showNotification(`任务 ${taskId} 已重新执行`, 'success');
        }, 500);
    }

    /**
     * 开始自动更新
     */
    startAutoUpdate() {
        // 每30秒更新一次数据
        this.updateInterval = setInterval(() => {
            if (this.currentTab === 'dashboard') {
                this.updateStats();
                this.updateActiveTasks();
            }
        }, 30000);
    }

    /**
     * 停止自动更新
     */
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        // 添加到页面
        document.body.appendChild(notification);

        // 显示动画
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // 自动隐藏
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    /**
     * 获取通知图标
     */
    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * 销毁管理器
     */
    destroy() {
        this.stopAutoUpdate();
        
        // 销毁图表
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        
        this.charts = {};
    }
}

// 通知样式
const notificationStyles = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 12px 16px;
    box-shadow: var(--shadow-lg);
    z-index: 1001;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    min-width: 300px;
}

.notification.show {
    transform: translateX(0);
}

.notification.success {
    border-left: 4px solid var(--success-color);
}

.notification.error {
    border-left: 4px solid var(--danger-color);
}

.notification.warning {
    border-left: 4px solid var(--warning-color);
}

.notification.info {
    border-left: 4px solid var(--info-color);
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 8px;
}

.notification-content i {
    font-size: 1rem;
}

.notification.success .notification-content i {
    color: var(--success-color);
}

.notification.error .notification-content i {
    color: var(--danger-color);
}

.notification.warning .notification-content i {
    color: var(--warning-color);
}

.notification.info .notification-content i {
    color: var(--info-color);
}
`;

// 添加通知样式到页面
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.selfHealingManager = new SelfHealingManager();
});

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    if (window.selfHealingManager) {
        window.selfHealingManager.destroy();
    }
});


    /**
     * 初始化标签页切换功能
     */
    initTabSwitching() {
        // 绑定标签页切换事件
        document.querySelectorAll('.sidebar .menu-item[data-tab]').forEach(item => {
            item.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchHealingTab(tab);
            });
        });
    }

    /**
     * 切换自愈系统标签页
     * @param {string} tabId - 标签页ID
     */
    switchHealingTab(tabId) {
        // 更新侧边栏激活状态
        document.querySelectorAll('.sidebar .menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`.sidebar .menu-item[data-tab="${tabId}"]`)?.classList.add('active');

        // 更新标签页内容显示
        document.querySelectorAll('.healing-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(`${tabId}-tab`)?.classList.add('active');

        // 更新面包屑
        this.updateBreadcrumb(tabId);

        // 加载对应标签页数据
        this.loadTabData(tabId);
        
        this.currentTab = tabId;
    }

    /**
     * 更新面包屑导航
     * @param {string} tabId - 标签页ID
     */
    updateBreadcrumb(tabId) {
        const breadcrumbMap = {
            'dashboard': '自愈仪表板',
            'active-healing': '活跃修复',
            'scripts': '修复脚本',
            'rules': '自愈规则',
            'history': '修复历史',
            'analytics': '效果分析',
            'reports': '报告中心'
        };
        
        const currentTabElement = document.getElementById('current-tab');
        if (currentTabElement) {
            currentTabElement.textContent = breadcrumbMap[tabId] || '未知页面';
        }
    }

    /**
     * 加载标签页数据
     * @param {string} tabId - 标签页ID
     */
    loadTabData(tabId) {
        switch (tabId) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'active-healing':
                this.loadActiveHealingData();
                break;
            case 'scripts':
                this.loadScriptsData();
                break;
            case 'rules':
                this.loadRulesData();
                break;
            case 'history':
                this.loadHistoryData();
                break;
            case 'analytics':
                this.loadAnalyticsData();
                break;
            case 'reports':
                this.loadReportsData();
                break;
        }
    }

    /**
     * 加载活跃修复数据
     */
    loadActiveHealingData() {
        const container = document.querySelector('#active-healing-tab .active-tasks-container');
        if (!container) return;

        // 模拟活跃修复任务数据
        const activeTasks = [
            {
                id: 'TASK-001',
                name: '数据库连接池修复',
                status: 'running',
                progress: 65,
                startTime: '2025-01-19 14:30:25',
                target: 'mysql-prod-01',
                script: 'db_connection_fix.py',
                estimatedTime: '2分钟'
            },
            {
                id: 'TASK-002',
                name: '内存泄漏清理',
                status: 'running',
                progress: 30,
                startTime: '2025-01-19 14:32:10',
                target: 'app-server-03',
                script: 'memory_cleanup.sh',
                estimatedTime: '5分钟'
            },
            {
                id: 'TASK-003',
                name: '磁盘空间清理',
                status: 'success',
                progress: 100,
                startTime: '2025-01-19 14:25:15',
                target: 'web-server-02',
                script: 'disk_cleanup.py',
                estimatedTime: '已完成'
            }
        ];

        container.innerHTML = activeTasks.map(task => `
            <div class="task-card ${task.status}">
                <div class="task-header">
                    <div class="task-info">
                        <h4>${task.name}</h4>
                        <div class="task-meta">
                            <span>任务ID: ${task.id}</span>
                            <span>目标: ${task.target}</span>
                            <span>脚本: ${task.script}</span>
                        </div>
                    </div>
                    <div class="task-status">
                        <div class="status-indicator ${task.status}"></div>
                        <span>${this.getStatusText(task.status)}</span>
                    </div>
                </div>
                <div class="task-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${task.progress}%"></div>
                    </div>
                    <div class="progress-text">${task.progress}% - ${task.estimatedTime}</div>
                </div>
                <div class="task-actions">
                    ${task.status === 'running' ? 
                        '<button class="btn btn-sm btn-secondary" onclick="selfHealingManager.pauseTask(\'' + task.id + '\')">暂停</button>' :
                        '<button class="btn btn-sm btn-primary" onclick="selfHealingManager.viewTaskLog(\'' + task.id + '\')">查看日志</button>'
                    }
                </div>
            </div>
        `).join('');
    }

    /**
     * 加载脚本管理数据
     */
    loadScriptsData() {
        const container = document.querySelector('#scripts-tab .scripts-grid');
        if (!container) return;

        // 模拟脚本数据
        const scripts = [
            {
                id: 'script-001',
                name: '数据库连接修复',
                type: 'python',
                description: '自动检测并修复数据库连接池问题，重启连接服务',
                executions: 45,
                successRate: 96,
                lastUsed: '2小时前'
            },
            {
                id: 'script-002',
                name: '内存清理脚本',
                type: 'shell',
                description: '清理系统内存缓存，释放未使用的内存空间',
                executions: 128,
                successRate: 89,
                lastUsed: '30分钟前'
            },
            {
                id: 'script-003',
                name: '服务重启脚本',
                type: 'powershell',
                description: '安全重启指定服务，确保服务正常运行',
                executions: 67,
                successRate: 94,
                lastUsed: '1天前'
            },
            {
                id: 'script-004',
                name: '磁盘空间清理',
                type: 'python',
                description: '清理临时文件和日志文件，释放磁盘空间',
                executions: 89,
                successRate: 98,
                lastUsed: '4小时前'
            }
        ];

        container.innerHTML = scripts.map(script => `
            <div class="script-card">
                <div class="script-header">
                    <div class="script-info">
                        <h4>${script.name}</h4>
                        <span class="script-type ${script.type}">${script.type.toUpperCase()}</span>
                    </div>
                </div>
                <div class="script-description">${script.description}</div>
                <div class="script-stats">
                    <span>执行次数: ${script.executions}</span>
                    <span>成功率: ${script.successRate}%</span>
                    <span>最后使用: ${script.lastUsed}</span>
                </div>
                <div class="script-actions">
                    <button class="btn btn-sm btn-primary" onclick="selfHealingManager.executeScript('${script.id}')">
                        <i class="fas fa-play"></i> 执行
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="selfHealingManager.editScript('${script.id}')">
                        <i class="fas fa-edit"></i> 编辑
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="selfHealingManager.viewScriptLog('${script.id}')">
                        <i class="fas fa-file-alt"></i> 日志
                    </button>
                </div>
            </div>
        `).join('');
    }

    /**
     * 加载规则配置数据
     */
    loadRulesData() {
        const container = document.querySelector('#rules-tab .rules-table tbody');
        if (!container) return;

        // 模拟规则数据
        const rules = [
            {
                id: 'rule-001',
                name: 'CPU使用率过高自动修复',
                condition: 'cpu_usage > 85%',
                action: 'restart_service.py',
                priority: 'high',
                enabled: true,
                lastTriggered: '2小时前'
            },
            {
                id: 'rule-002',
                name: '内存使用率告警处理',
                condition: 'memory_usage > 90%',
                action: 'memory_cleanup.sh',
                priority: 'high',
                enabled: true,
                lastTriggered: '1天前'
            },
            {
                id: 'rule-003',
                name: '磁盘空间不足处理',
                condition: 'disk_usage > 95%',
                action: 'disk_cleanup.py',
                priority: 'medium',
                enabled: true,
                lastTriggered: '3天前'
            },
            {
                id: 'rule-004',
                name: '数据库连接异常修复',
                condition: 'db_connection_failed',
                action: 'db_connection_fix.py',
                priority: 'high',
                enabled: false,
                lastTriggered: '从未'
            },
            {
                id: 'rule-005',
                name: '网络延迟优化',
                condition: 'network_latency > 500ms',
                action: 'network_optimize.sh',
                priority: 'low',
                enabled: true,
                lastTriggered: '1周前'
            }
        ];

        container.innerHTML = rules.map(rule => `
            <tr>
                <td>
                    <div class="rule-name">${rule.name}</div>
                </td>
                <td>
                    <code class="rule-condition">${rule.condition}</code>
                </td>
                <td>${rule.action}</td>
                <td>
                    <span class="rule-priority ${rule.priority}">${this.getPriorityText(rule.priority)}</span>
                </td>
                <td>
                    <div class="rule-status">
                        <div class="rule-toggle ${rule.enabled ? 'active' : ''}" 
                             onclick="selfHealingManager.toggleRule('${rule.id}')"></div>
                    </div>
                </td>
                <td>${rule.lastTriggered}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-icon" title="编辑规则" onclick="selfHealingManager.editRule('${rule.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon" title="测试规则" onclick="selfHealingManager.testRule('${rule.id}')">
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="btn-icon" title="删除规则" onclick="selfHealingManager.deleteRule('${rule.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    /**
     * 加载修复历史数据
     */
    loadHistoryData() {
        const container = document.querySelector('#history-tab .history-table tbody');
        if (!container) return;

        // 模拟历史数据
        const history = [
            {
                id: 'exec-001',
                timestamp: '2025-01-19 14:25:15',
                problem: 'CPU使用率过高',
                target: 'web-server-01',
                script: 'cpu_optimize.py',
                result: 'success',
                duration: '2分30秒',
                details: 'CPU使用率从92%降至45%'
            },
            {
                id: 'exec-002',
                timestamp: '2025-01-19 13:45:22',
                problem: '内存泄漏检测',
                target: 'app-server-02',
                script: 'memory_fix.sh',
                result: 'success',
                duration: '4分15秒',
                details: '释放内存2.3GB'
            },
            {
                id: 'exec-003',
                timestamp: '2025-01-19 12:30:08',
                problem: '数据库连接失败',
                target: 'mysql-prod-01',
                script: 'db_reconnect.py',
                result: 'error',
                duration: '1分45秒',
                details: '连接超时，需要手动干预'
            },
            {
                id: 'exec-004',
                timestamp: '2025-01-19 11:15:33',
                problem: '磁盘空间不足',
                target: 'file-server-01',
                script: 'disk_cleanup.py',
                result: 'success',
                duration: '8分20秒',
                details: '清理临时文件，释放15GB空间'
            },
            {
                id: 'exec-005',
                timestamp: '2025-01-19 10:22:17',
                problem: '服务响应超时',
                target: 'api-gateway',
                script: 'service_restart.sh',
                result: 'warning',
                duration: '3分10秒',
                details: '服务重启成功，但响应时间仍偏高'
            }
        ];

        container.innerHTML = history.map(item => `
            <tr>
                <td>${item.timestamp}</td>
                <td>
                    <div class="problem-info">
                        <div class="problem-title">${item.problem}</div>
                        <div class="problem-target">${item.target}</div>
                    </div>
                </td>
                <td>
                    <span class="script-name">${item.script}</span>
                </td>
                <td>
                    <div class="execution-result">
                        <div class="result-icon ${item.result}">
                            <i class="fas fa-${this.getResultIcon(item.result)}"></i>
                        </div>
                        <span>${this.getResultText(item.result)}</span>
                    </div>
                </td>
                <td>
                    <span class="execution-time">${item.duration}</span>
                </td>
                <td>${item.details}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-icon" title="查看详情" onclick="selfHealingManager.viewExecutionDetails('${item.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-icon" title="查看日志" onclick="selfHealingManager.viewExecutionLog('${item.id}')">
                            <i class="fas fa-file-alt"></i>
                        </button>
                        <button class="btn-icon" title="重新执行" onclick="selfHealingManager.reExecute('${item.id}')">
                            <i class="fas fa-redo"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    /**
     * 获取状态文本
     * @param {string} status - 状态
     * @returns {string} 状态文本
     */
    getStatusText(status) {
        const statusMap = {
            'running': '执行中',
            'success': '已完成',
            'error': '执行失败',
            'pending': '等待中'
        };
        return statusMap[status] || '未知';
    }

    /**
     * 获取优先级文本
     * @param {string} priority - 优先级
     * @returns {string} 优先级文本
     */
    getPriorityText(priority) {
        const priorityMap = {
            'high': '高',
            'medium': '中',
            'low': '低'
        };
        return priorityMap[priority] || '未知';
    }

    /**
     * 获取结果图标
     * @param {string} result - 结果
     * @returns {string} 图标类名
     */
    getResultIcon(result) {
        const iconMap = {
            'success': 'check',
            'error': 'times',
            'warning': 'exclamation-triangle'
        };
        return iconMap[result] || 'question';
    }

    /**
     * 获取结果文本
     * @param {string} result - 结果
     * @returns {string} 结果文本
     */
    getResultText(result) {
        const resultMap = {
            'success': '成功',
            'error': '失败',
            'warning': '警告'
        };
        return resultMap[result] || '未知';
    }

    /**
     * 暂停任务
     * @param {string} taskId - 任务ID
     */
    pauseTask(taskId) {
        this.showNotification(`任务 ${taskId} 已暂停`, 'info');
        // 这里可以添加实际的暂停逻辑
    }

    /**
     * 查看任务日志
     * @param {string} taskId - 任务ID
     */
    viewTaskLog(taskId) {
        this.showNotification(`正在打开任务 ${taskId} 的日志`, 'info');
        // 这里可以添加实际的日志查看逻辑
    }

    /**
     * 执行脚本
     * @param {string} scriptId - 脚本ID
     */
    executeScript(scriptId) {
        this.showNotification(`正在执行脚本 ${scriptId}`, 'info');
        // 这里可以添加实际的脚本执行逻辑
    }

    /**
     * 编辑脚本
     * @param {string} scriptId - 脚本ID
     */
    editScript(scriptId) {
        this.showNotification(`正在编辑脚本 ${scriptId}`, 'info');
        // 这里可以添加实际的脚本编辑逻辑
    }

    /**
     * 查看脚本日志
     * @param {string} scriptId - 脚本ID
     */
    viewScriptLog(scriptId) {
        this.showNotification(`正在查看脚本 ${scriptId} 的日志`, 'info');
        // 这里可以添加实际的日志查看逻辑
    }

    /**
     * 切换规则状态
     * @param {string} ruleId - 规则ID
     */
    toggleRule(ruleId) {
        const toggle = document.querySelector(`[onclick="selfHealingManager.toggleRule('${ruleId}')"]`);
        if (toggle) {
            toggle.classList.toggle('active');
            const isActive = toggle.classList.contains('active');
            this.showNotification(`规则 ${ruleId} 已${isActive ? '启用' : '禁用'}`, 'info');
        }
    }

    /**
     * 编辑规则
     * @param {string} ruleId - 规则ID
     */
    editRule(ruleId) {
        this.showNotification(`正在编辑规则 ${ruleId}`, 'info');
        // 这里可以添加实际的规则编辑逻辑
    }

    /**
     * 测试规则
     * @param {string} ruleId - 规则ID
     */
    testRule(ruleId) {
        this.showNotification(`正在测试规则 ${ruleId}`, 'info');
        // 这里可以添加实际的规则测试逻辑
    }

    /**
     * 删除规则
     * @param {string} ruleId - 规则ID
     */
    deleteRule(ruleId) {
        if (confirm('确定要删除这个规则吗？')) {
            this.showNotification(`规则 ${ruleId} 已删除`, 'success');
            // 这里可以添加实际的规则删除逻辑
        }
    }

    /**
     * 查看执行详情
     * @param {string} execId - 执行ID
     */
    viewExecutionDetails(execId) {
        this.showNotification(`正在查看执行 ${execId} 的详情`, 'info');
        // 这里可以添加实际的详情查看逻辑
    }

    /**
     * 查看执行日志
     * @param {string} execId - 执行ID
     */
    viewExecutionLog(execId) {
        this.showNotification(`正在查看执行 ${execId} 的日志`, 'info');
        // 这里可以添加实际的日志查看逻辑
    }

    /**
     * 重新执行
     * @param {string} execId - 执行ID
     */
    reExecute(execId) {
        this.showNotification(`正在重新执行 ${execId}`, 'info');
        // 这里可以添加实际的重新执行逻辑
    }

// ... existing code ...