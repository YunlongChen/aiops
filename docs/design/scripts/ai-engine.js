/**
 * AI引擎页面JavaScript文件
 * 实现AI模型管理、预测分析、决策引擎等功能的交互逻辑
 * 包含模型训练、部署管理、异常检测、容量规划、性能预测等功能
 * 作者: AIOps Team
 * 创建时间: 2024
 */

class AIEngineManager {
    constructor() {
        this.currentTab = 'models';
        this.models = [];
        this.charts = {};
        this.refreshInterval = null;
        this.trainingTasks = [];
        this.deployments = [];
        this.anomalies = [];
        this.init();
    }

    /**
     * 初始化AI引擎管理器
     */
    init() {
        this.bindEvents();
        this.loadModels();
        this.initCharts();
        this.initTabSwitching();
        this.startDataUpdates();
        this.loadInitialData();
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 侧边栏菜单切换
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.switchTab(e.currentTarget.dataset.tab);
            });
        });

        // 刷新按钮
        document.getElementById('refresh-btn')?.addEventListener('click', () => {
            this.refreshData();
        });

        // 创建模型按钮
        document.getElementById('create-model-btn')?.addEventListener('click', () => {
            this.showCreateModelModal();
        });

        // 模型过滤器
        document.getElementById('model-type-filter')?.addEventListener('change', (e) => {
            this.filterModels('type', e.target.value);
        });

        document.getElementById('model-status-filter')?.addEventListener('change', (e) => {
            this.filterModels('status', e.target.value);
        });

        // 模型搜索
        document.getElementById('model-search')?.addEventListener('input', (e) => {
            this.searchModels(e.target.value);
        });

        // 模态框事件
        this.bindModalEvents();

        // 模型操作按钮
        this.bindModelActions();
    }

    /**
     * 绑定模态框事件
     */
    bindModalEvents() {
        const modal = document.getElementById('create-model-modal');
        const closeBtn = modal?.querySelector('.modal-close');
        const cancelBtn = document.getElementById('cancel-create');
        const form = document.getElementById('create-model-form');

        closeBtn?.addEventListener('click', () => {
            this.hideCreateModelModal();
        });

        cancelBtn?.addEventListener('click', () => {
            this.hideCreateModelModal();
        });

        modal?.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideCreateModelModal();
            }
        });

        form?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createModel(new FormData(form));
        });
    }

    /**
     * 绑定模型操作按钮事件
     */
    bindModelActions() {
        document.addEventListener('click', (e) => {
            const button = e.target.closest('.btn-icon');
            if (!button) return;

            const modelCard = button.closest('.model-card');
            const modelName = modelCard?.querySelector('h4')?.textContent;
            const icon = button.querySelector('i');

            if (icon?.classList.contains('fa-eye')) {
                this.viewModelDetails(modelName);
            } else if (icon?.classList.contains('fa-edit')) {
                this.editModel(modelName);
            } else if (icon?.classList.contains('fa-redo')) {
                this.retrainModel(modelName);
            } else if (icon?.classList.contains('fa-stop')) {
                this.stopModel(modelName);
            } else if (icon?.classList.contains('fa-play')) {
                this.startModel(modelName);
            } else if (icon?.classList.contains('fa-trash')) {
                this.deleteModel(modelName);
            } else if (icon?.classList.contains('fa-pause')) {
                this.pauseTraining(modelName);
            } else if (icon?.classList.contains('fa-file-alt')) {
                this.viewTrainingLogs(modelName);
            }
        });
    }

    /**
     * 切换标签页
     * @param {string} tabId - 标签页ID
     */
    switchTab(tabId) {
        // 更新侧边栏活跃状态
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`)?.classList.add('active');

        // 更新标签页内容
        document.querySelectorAll('.ai-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(`${tabId}-tab`)?.classList.add('active');

        // 更新面包屑
        const tabNames = {
            'models': '模型库',
            'training': '模型训练',
            'deployment': '模型部署',
            'anomaly-detection': '异常检测',
            'capacity-planning': '容量规划',
            'performance-prediction': '性能预测',
            'decision-rules': '决策规则',
            'automation-policies': '自动化策略',
            'knowledge-base': '知识库',
            'insights': '智能洞察',
            'recommendations': '优化建议'
        };
        
        const currentTabElement = document.getElementById('current-tab');
        if (currentTabElement) {
            currentTabElement.textContent = tabNames[tabId] || tabId;
        }

        this.currentTab = tabId;
    }

    /**
     * 加载模型数据
     */
    loadModels() {
        // 模拟加载模型数据
        this.models = [
            {
                id: 1,
                name: 'CPU异常检测模型',
                type: 'anomaly',
                status: 'active',
                accuracy: 96.5,
                trainingTime: '2小时',
                lastUpdate: '2小时前',
                description: '基于历史CPU使用率数据训练的异常检测模型'
            },
            {
                id: 2,
                name: '内存使用预测模型',
                type: 'prediction',
                status: 'training',
                accuracy: null,
                trainingTime: null,
                lastUpdate: null,
                progress: 67,
                description: '预测系统内存使用趋势的回归模型'
            },
            {
                id: 3,
                name: '网络流量分类模型',
                type: 'classification',
                status: 'active',
                accuracy: 92.8,
                trainingTime: '4小时',
                lastUpdate: '1天前',
                description: '对网络流量进行分类和异常识别'
            },
            {
                id: 4,
                name: '磁盘容量预测模型',
                type: 'regression',
                status: 'stopped',
                accuracy: 89.2,
                trainingTime: '3小时',
                lastUpdate: '3天前',
                description: '预测磁盘空间使用趋势'
            }
        ];

        this.renderModels();
    }

    /**
     * 渲染模型列表
     * @param {Array} models - 要渲染的模型数组
     */
    renderModels(models = this.models) {
        const container = document.querySelector('.models-grid');
        if (!container) return;

        container.innerHTML = models.map(model => this.createModelCard(model)).join('');
    }

    /**
     * 创建模型卡片HTML
     * @param {Object} model - 模型对象
     * @returns {string} HTML字符串
     */
    createModelCard(model) {
        const typeNames = {
            'anomaly': '异常检测',
            'prediction': '性能预测',
            'classification': '分类模型',
            'regression': '回归模型'
        };

        const statusNames = {
            'active': '运行中',
            'training': '训练中',
            'stopped': '已停止'
        };

        let contentHtml = '';
        
        if (model.status === 'training') {
            contentHtml = `
                <div class="training-progress">
                    <div class="progress-info">
                        <span>训练进度</span>
                        <span>${model.progress}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${model.progress}%"></div>
                    </div>
                    <div class="progress-details">
                        <span>Epoch ${model.progress}/100</span>
                        <span>预计剩余: ${Math.round((100 - model.progress) * 0.7)}分钟</span>
                    </div>
                </div>
            `;
        } else {
            contentHtml = `
                <div class="model-metrics">
                    <div class="metric-row">
                        <span class="metric-label">准确率</span>
                        <span class="metric-value">${model.accuracy}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">训练时间</span>
                        <span class="metric-value">${model.trainingTime}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">最后更新</span>
                        <span class="metric-value">${model.lastUpdate}</span>
                    </div>
                </div>
            `;
        }

        let actionsHtml = '';
        if (model.status === 'active') {
            actionsHtml = `
                <button class="btn-icon" title="查看详情">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-icon" title="编辑">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon" title="重新训练">
                    <i class="fas fa-redo"></i>
                </button>
                <button class="btn-icon" title="停止">
                    <i class="fas fa-stop"></i>
                </button>
            `;
        } else if (model.status === 'training') {
            actionsHtml = `
                <button class="btn-icon" title="查看训练日志">
                    <i class="fas fa-file-alt"></i>
                </button>
                <button class="btn-icon" title="暂停训练">
                    <i class="fas fa-pause"></i>
                </button>
                <button class="btn-icon" title="停止训练">
                    <i class="fas fa-stop"></i>
                </button>
            `;
        } else if (model.status === 'stopped') {
            actionsHtml = `
                <button class="btn-icon" title="查看详情">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-icon" title="启动">
                    <i class="fas fa-play"></i>
                </button>
                <button class="btn-icon" title="删除">
                    <i class="fas fa-trash"></i>
                </button>
            `;
        }

        return `
            <div class="model-card ${model.status}">
                <div class="model-header">
                    <div class="model-info">
                        <h4>${model.name}</h4>
                        <span class="model-type">${typeNames[model.type]}</span>
                    </div>
                    <div class="model-status">
                        <span class="status-indicator ${model.status}"></span>
                        <span class="status-text">${statusNames[model.status]}</span>
                    </div>
                </div>
                
                ${contentHtml}
                
                <div class="model-actions">
                    ${actionsHtml}
                </div>
            </div>
        `;
    }

    /**
     * 过滤模型
     * @param {string} filterType - 过滤类型
     * @param {string} filterValue - 过滤值
     */
    filterModels(filterType, filterValue) {
        let filteredModels = this.models;

        if (filterValue) {
            filteredModels = this.models.filter(model => {
                return model[filterType] === filterValue;
            });
        }

        this.renderModels(filteredModels);
    }

    /**
     * 搜索模型
     * @param {string} searchTerm - 搜索词
     */
    searchModels(searchTerm) {
        if (!searchTerm.trim()) {
            this.renderModels();
            return;
        }

        const filteredModels = this.models.filter(model => {
            return model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                   model.description.toLowerCase().includes(searchTerm.toLowerCase());
        });

        this.renderModels(filteredModels);
    }

    /**
     * 显示创建模型模态框
     */
    showCreateModelModal() {
        const modal = document.getElementById('create-model-modal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * 隐藏创建模型模态框
     */
    hideCreateModelModal() {
        const modal = document.getElementById('create-model-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            
            // 重置表单
            const form = document.getElementById('create-model-form');
            if (form) {
                form.reset();
            }
        }
    }

    /**
     * 创建新模型
     * @param {FormData} formData - 表单数据
     */
    createModel(formData) {
        const modelData = {
            name: formData.get('modelName'),
            type: formData.get('modelType'),
            description: formData.get('modelDescription'),
            dataSource: formData.get('dataSource')
        };

        // 模拟创建模型
        console.log('创建模型:', modelData);
        
        // 显示成功消息
        this.showNotification('模型创建成功，开始训练...', 'success');
        
        // 隐藏模态框
        this.hideCreateModelModal();
        
        // 添加到模型列表（模拟）
        const newModel = {
            id: this.models.length + 1,
            name: modelData.name,
            type: modelData.type,
            status: 'training',
            accuracy: null,
            trainingTime: null,
            lastUpdate: null,
            progress: 0,
            description: modelData.description
        };
        
        this.models.push(newModel);
        this.renderModels();
        
        // 模拟训练进度
        this.simulateTraining(newModel.id);
    }

    /**
     * 模拟模型训练进度
     * @param {number} modelId - 模型ID
     */
    simulateTraining(modelId) {
        const model = this.models.find(m => m.id === modelId);
        if (!model) return;

        const interval = setInterval(() => {
            model.progress += Math.random() * 5;
            
            if (model.progress >= 100) {
                model.progress = 100;
                model.status = 'active';
                model.accuracy = (85 + Math.random() * 10).toFixed(1);
                model.trainingTime = '2小时';
                model.lastUpdate = '刚刚';
                clearInterval(interval);
                this.showNotification(`模型 ${model.name} 训练完成！`, 'success');
            }
            
            this.renderModels();
        }, 2000);
    }

    /**
     * 模型操作方法
     */
    viewModelDetails(modelName) {
        console.log('查看模型详情:', modelName);
        this.showNotification(`查看模型详情: ${modelName}`, 'info');
    }

    editModel(modelName) {
        console.log('编辑模型:', modelName);
        this.showNotification(`编辑模型: ${modelName}`, 'info');
    }

    retrainModel(modelName) {
        console.log('重新训练模型:', modelName);
        this.showNotification(`开始重新训练模型: ${modelName}`, 'info');
    }

    stopModel(modelName) {
        console.log('停止模型:', modelName);
        this.showNotification(`停止模型: ${modelName}`, 'warning');
    }

    startModel(modelName) {
        console.log('启动模型:', modelName);
        this.showNotification(`启动模型: ${modelName}`, 'success');
    }

    deleteModel(modelName) {
        if (confirm(`确定要删除模型 "${modelName}" 吗？`)) {
            console.log('删除模型:', modelName);
            this.showNotification(`删除模型: ${modelName}`, 'error');
        }
    }

    pauseTraining(modelName) {
        console.log('暂停训练:', modelName);
        this.showNotification(`暂停训练: ${modelName}`, 'warning');
    }

    viewTrainingLogs(modelName) {
        console.log('查看训练日志:', modelName);
        this.showNotification(`查看训练日志: ${modelName}`, 'info');
    }

    /**
     * 初始化图表
     */
    initCharts() {
        this.initAccuracyChart();
        this.initResponseTimeChart();
        this.initUsageChart();
        this.initAnomalyChart();
    }

    /**
     * 初始化准确率趋势图表
     */
    initAccuracyChart() {
        const ctx = document.getElementById('accuracy-chart');
        if (!ctx) return;

        this.charts.accuracy = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                datasets: [{
                    label: '模型准确率',
                    data: [92.1, 93.5, 94.2, 93.8, 94.5, 94.2],
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
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
                        min: 90,
                        max: 100,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }

    /**
     * 初始化响应时间图表
     */
    initResponseTimeChart() {
        const ctx = document.getElementById('response-time-chart');
        if (!ctx) return;

        this.charts.responseTime = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                datasets: [{
                    label: '响应时间 (ms)',
                    data: [110, 125, 135, 120, 115, 125],
                    borderColor: '#10b981',
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
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }

    /**
     * 初始化使用频率图表
     */
    initUsageChart() {
        const ctx = document.getElementById('usage-chart');
        if (!ctx) return;

        this.charts.usage = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['异常检测', '性能预测', '分类模型', '回归模型'],
                datasets: [{
                    label: '使用次数',
                    data: [1200, 800, 600, 400],
                    backgroundColor: [
                        'rgba(79, 70, 229, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)'
                    ],
                    borderColor: [
                        '#4f46e5',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444'
                    ],
                    borderWidth: 1
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
                            color: 'rgba(0, 0, 0, 0.1)'
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
     * 初始化异常检测统计图表
     */
    initAnomalyChart() {
        const ctx = document.getElementById('anomaly-chart');
        if (!ctx) return;

        this.charts.anomaly = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['正常', '异常', '警告'],
                datasets: [{
                    data: [85, 10, 5],
                    backgroundColor: [
                        '#10b981',
                        '#ef4444',
                        '#f59e0b'
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
     * 刷新数据
     */
    refreshData() {
        this.showNotification('正在刷新数据...', 'info');
        
        // 模拟数据刷新
        setTimeout(() => {
            this.loadModels();
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
     * 开始数据自动更新
     */
    startDataUpdates() {
        // 每30秒更新一次数据
        setInterval(() => {
            this.updateCharts();
        }, 30000);
    }

    /**
     * 显示通知消息
     * @param {string} message - 消息内容
     * @param {string} type - 消息类型
     */
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        // 添加到页面
        document.body.appendChild(notification);

        // 显示动画
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // 自动隐藏
        setTimeout(() => {
            this.hideNotification(notification);
        }, 3000);

        // 点击关闭
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.hideNotification(notification);
        });
    }

    /**
     * 隐藏通知
     * @param {Element} notification - 通知元素
     */
    hideNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    /**
      * 获取通知图标
      * @param {string} type - 通知类型
      * @returns {string} 图标类名
      */
     getNotificationIcon(type) {
         const icons = {
             'success': 'check-circle',
             'error': 'exclamation-circle',
             'warning': 'exclamation-triangle',
             'info': 'info-circle'
         };
         return icons[type] || 'info-circle';
     }

     /**
      * 加载模型库数据
      */
     loadModelLibraryData() {
         console.log('加载模型库数据...');
         this.loadModels();
     }

    /**
     * 切换AI标签页
     * @param {string} tabId - 目标标签页ID
     */
    switchAITab(tabId) {
        // 更新按钮状态
        document.querySelectorAll('.ai-tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`)?.classList.add('active');

        // 更新内容显示
        document.querySelectorAll('.ai-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(tabId)?.classList.add('active');

        this.currentTab = tabId;
        this.loadTabData(tabId);
    }

    /**
     * 加载标签页数据
     * @param {string} tabId - 标签页ID
     */
    loadTabData(tabId) {
        switch (tabId) {
            case 'model-library':
                this.loadModelLibraryData();
                break;
            case 'model-training':
                this.loadTrainingData();
                break;
            case 'model-deployment':
                this.loadDeploymentData();
                break;
            case 'anomaly-detection':
                this.loadAnomalyData();
                break;
            case 'capacity-planning':
                this.loadCapacityData();
                break;
            case 'performance-prediction':
                this.loadPerformanceData();
                break;
        }
    }

    /**
     * 加载初始数据
     */
    loadInitialData() {
        this.loadModelLibraryData();
        this.updateAIEngineStats();
        this.initTrainingTaskButtons();
        this.initDeploymentButtons();
        this.initAnomalyButtons();
    }

    /**
     * 加载训练数据
     */
    loadTrainingData() {
        console.log('加载训练数据...');
        this.updateTrainingProgress();
        this.initTrainingProgressChart();
    }

    /**
     * 加载部署数据
     */
    loadDeploymentData() {
        console.log('加载部署数据...');
        this.updateDeploymentStatus();
    }

    /**
     * 加载异常数据
     */
    loadAnomalyData() {
        console.log('加载异常检测数据...');
        this.initAnomalyDetectionChart();
    }

    /**
     * 加载容量数据
     */
    loadCapacityData() {
        console.log('加载容量规划数据...');
        this.initCapacityPredictionCharts();
    }

    /**
     * 加载性能数据
     */
    loadPerformanceData() {
        console.log('加载性能预测数据...');
        this.initPerformancePredictionChart();
    }

    /**
     * 初始化训练进度图表
     */
    initTrainingProgressChart() {
        const ctx = document.getElementById('trainingProgressChart');
        if (!ctx) return;

        this.charts.trainingProgress = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Epoch 1', 'Epoch 2', 'Epoch 3', 'Epoch 4', 'Epoch 5'],
                datasets: [{
                    label: '训练损失',
                    data: [0.8, 0.6, 0.4, 0.3, 0.2],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4
                }, {
                    label: '验证损失',
                    data: [0.9, 0.7, 0.5, 0.4, 0.3],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '模型训练进度'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
    }

    /**
     * 初始化异常检测图表
     */
    initAnomalyDetectionChart() {
        const ctx = document.getElementById('anomalyChart');
        if (!ctx) return;

        this.charts.anomalyDetection = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(24),
                datasets: [{
                    label: '正常值',
                    data: this.generateNormalData(24),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4
                }, {
                    label: '异常值',
                    data: this.generateAnomalyData(24),
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    pointBackgroundColor: '#dc3545',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '异常检测趋势'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    /**
     * 初始化容量预测图表
     */
    initCapacityPredictionCharts() {
        // CPU容量预测
        const cpuCtx = document.getElementById('cpuPredictionChart');
        if (cpuCtx) {
            this.charts.cpuPrediction = this.createPredictionChart(cpuCtx, 'CPU使用率预测', '%');
        }

        // 内存容量预测
        const memoryCtx = document.getElementById('memoryPredictionChart');
        if (memoryCtx) {
            this.charts.memoryPrediction = this.createPredictionChart(memoryCtx, '内存使用率预测', '%');
        }

        // 存储容量预测
        const storageCtx = document.getElementById('storagePredictionChart');
        if (storageCtx) {
            this.charts.storagePrediction = this.createPredictionChart(storageCtx, '存储使用率预测', '%');
        }
    }

    /**
     * 创建预测图表
     * @param {HTMLElement} ctx - 画布元素
     * @param {string} title - 图表标题
     * @param {string} unit - 数据单位
     */
    createPredictionChart(ctx, title, unit) {
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateFutureDates(30),
                datasets: [{
                    label: '历史数据',
                    data: this.generateHistoricalData(15),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }, {
                    label: '预测数据',
                    data: this.generatePredictionData(15),
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    borderDash: [5, 5],
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: title
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + unit;
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * 初始化性能预测图表
     */
    initPerformancePredictionChart() {
        const ctx = document.getElementById('performancePredictionChart');
        if (!ctx) return;

        this.charts.performancePrediction = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(24),
                datasets: [{
                    label: '响应时间',
                    data: this.generateResponseTimeData(24),
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y'
                }, {
                    label: '吞吐量',
                    data: this.generateThroughputData(24),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '性能预测趋势'
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: '响应时间 (ms)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: '吞吐量 (req/s)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    }

    /**
     * 初始化训练任务按钮
     */
    initTrainingTaskButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-pause-training')) {
                const taskId = e.target.getAttribute('data-task-id');
                this.pauseTraining(taskId);
            } else if (e.target.classList.contains('btn-stop-training')) {
                const taskId = e.target.getAttribute('data-task-id');
                this.stopTraining(taskId);
            } else if (e.target.classList.contains('btn-view-logs')) {
                const taskId = e.target.getAttribute('data-task-id');
                this.viewTrainingLogs(taskId);
            }
        });
    }

    /**
     * 初始化部署按钮
     */
    initDeploymentButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-start-deployment')) {
                const deploymentId = e.target.getAttribute('data-deployment-id');
                this.startDeployment(deploymentId);
            } else if (e.target.classList.contains('btn-stop-deployment')) {
                const deploymentId = e.target.getAttribute('data-deployment-id');
                this.stopDeployment(deploymentId);
            } else if (e.target.classList.contains('btn-scale-deployment')) {
                const deploymentId = e.target.getAttribute('data-deployment-id');
                this.scaleDeployment(deploymentId);
            }
        });
    }

    /**
     * 初始化异常处理按钮
     */
    initAnomalyButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-ignore-anomaly')) {
                const anomalyId = e.target.getAttribute('data-anomaly-id');
                this.ignoreAnomaly(anomalyId);
            } else if (e.target.classList.contains('btn-investigate-anomaly')) {
                const anomalyId = e.target.getAttribute('data-anomaly-id');
                this.investigateAnomaly(anomalyId);
            }
        });
    }

    /**
     * 更新AI引擎状态统计
     */
    updateAIEngineStats() {
        const stats = {
            activeModels: Math.floor(Math.random() * 20) + 10,
            accuracy: (Math.random() * 10 + 90).toFixed(1),
            predictions: Math.floor(Math.random() * 1000) + 5000,
            alerts: Math.floor(Math.random() * 5) + 1
        };

        // 更新DOM元素
        const activeModelsEl = document.querySelector('.stat-card:nth-child(1) .stat-value');
        const accuracyEl = document.querySelector('.stat-card:nth-child(2) .stat-value');
        const predictionsEl = document.querySelector('.stat-card:nth-child(3) .stat-value');
        const alertsEl = document.querySelector('.stat-card:nth-child(4) .stat-value');

        if (activeModelsEl) activeModelsEl.textContent = stats.activeModels;
        if (accuracyEl) accuracyEl.textContent = stats.accuracy + '%';
        if (predictionsEl) predictionsEl.textContent = stats.predictions.toLocaleString();
        if (alertsEl) alertsEl.textContent = stats.alerts;
    }

    /**
     * 更新训练进度
     */
    updateTrainingProgress() {
        const progressBars = document.querySelectorAll('.progress-fill');
        progressBars.forEach(bar => {
            const progress = Math.random() * 100;
            bar.style.width = progress + '%';
        });
    }

    /**
     * 更新部署状态
     */
    updateDeploymentStatus() {
        const statusIndicators = document.querySelectorAll('.status-indicator');
        statusIndicators.forEach(indicator => {
            const isActive = Math.random() > 0.3;
            indicator.classList.toggle('active', isActive);
            indicator.classList.toggle('stopped', !isActive);
        });
    }

    // 数据生成辅助方法
    generateTimeLabels(hours) {
        const labels = [];
        const now = new Date();
        for (let i = hours - 1; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            labels.push(time.getHours() + ':00');
        }
        return labels;
    }

    generateNormalData(count) {
        return Array.from({length: count}, () => Math.random() * 50 + 25);
    }

    generateAnomalyData(count) {
        const data = new Array(count).fill(null);
        // 随机添加一些异常点
        for (let i = 0; i < 3; i++) {
            const index = Math.floor(Math.random() * count);
            data[index] = Math.random() * 30 + 80;
        }
        return data;
    }

    generateFutureDates(days) {
        const dates = [];
        const now = new Date();
        for (let i = -15; i < days - 15; i++) {
            const date = new Date(now.getTime() + i * 24 * 60 * 60 * 1000);
            dates.push(date.getMonth() + 1 + '/' + date.getDate());
        }
        return dates;
    }

    generateHistoricalData(count) {
        const data = Array.from({length: count}, (_, i) => Math.random() * 30 + 40 + i * 2);
        return [...data, ...new Array(15).fill(null)];
    }

    generatePredictionData(count) {
        const data = new Array(15).fill(null);
        const predictionData = Array.from({length: count}, (_, i) => Math.random() * 20 + 60 + i * 1.5);
        return [...data, ...predictionData];
    }

    generateResponseTimeData(count) {
        return Array.from({length: count}, () => Math.random() * 200 + 100);
    }

    generateThroughputData(count) {
        return Array.from({length: count}, () => Math.random() * 500 + 1000);
    }

    // 操作方法
    pauseTraining(taskId) {
        console.log('暂停训练任务:', taskId);
        this.showNotification('训练任务已暂停', 'success');
    }

    stopTraining(taskId) {
        console.log('停止训练任务:', taskId);
        this.showNotification('训练任务已停止', 'warning');
    }

    viewTrainingLogs(taskId) {
        console.log('查看训练日志:', taskId);
        // 实现查看日志逻辑
    }

    startDeployment(deploymentId) {
        console.log('启动部署:', deploymentId);
        this.showNotification('部署已启动', 'success');
    }

    stopDeployment(deploymentId) {
        console.log('停止部署:', deploymentId);
        this.showNotification('部署已停止', 'warning');
    }

    scaleDeployment(deploymentId) {
        console.log('扩缩容部署:', deploymentId);
        this.showNotification('部署扩缩容操作已执行', 'info');
    }

    ignoreAnomaly(anomalyId) {
        console.log('忽略异常:', anomalyId);
        this.showNotification('异常已忽略', 'info');
    }

    investigateAnomaly(anomalyId) {
        console.log('调查异常:', anomalyId);
        this.showNotification('异常调查已开始', 'info');
    }
}


// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.aiEngineManager = new AIEngineManager();
});

// 添加通知样式
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 1001;
        transform: translateX(400px);
        opacity: 0;
        transition: all 0.3s ease;
        min-width: 300px;
        border-left: 4px solid #4f46e5;
    }

    .notification.show {
        transform: translateX(0);
        opacity: 1;
    }

    .notification-success {
        border-left-color: #10b981;
        color: #065f46;
    }

    .notification-error {
        border-left-color: #ef4444;
        color: #991b1b;
    }

    .notification-warning {
        border-left-color: #f59e0b;
        color: #92400e;
    }

    .notification-info {
        border-left-color: #3b82f6;
        color: #1e40af;
    }

    .notification-close {
        background: none;
        border: none;
        color: inherit;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        opacity: 0.7;
        transition: opacity 0.2s ease;
        margin-left: auto;
    }

    .notification-close:hover {
        opacity: 1;
    }
`;

// 添加样式到页面
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);