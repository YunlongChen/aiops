/**
 * 监控中心页面脚本
 * 实现监控数据的实时更新、图表渲染和交互功能
 */

class MonitoringManager {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        this.currentTab = 'infrastructure';
        this.timeRange = '1h';
        
        this.init();
    }

    /**
     * 初始化监控管理器
     */
    init() {
        this.bindEvents();
        this.initCharts();
        this.startDataUpdate();
        this.loadInitialData();
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 侧边栏标签切换
        document.querySelectorAll('.menu-item[data-tab]').forEach(item => {
            item.addEventListener('click', (e) => {
                this.switchTab(e.currentTarget.dataset.tab);
            });
        });

        // 时间范围选择
        const timeRangeSelect = document.getElementById('time-range');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', (e) => {
                this.timeRange = e.target.value;
                this.refreshData();
            });
        }

        // 刷新按钮
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // 导出按钮
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportReport();
            });
        }

        // 进程操作按钮
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-icon')) {
                const btn = e.target.closest('.btn-icon');
                const action = btn.title;
                const row = btn.closest('tr');
                
                if (action === '重启' || action === '停止') {
                    this.handleProcessAction(action, row);
                }
            }
        });
    }

    /**
     * 切换监控标签
     * @param {string} tabName - 标签名称
     */
    switchTab(tabName) {
        // 更新侧边栏激活状态
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // 切换内容区域
        document.querySelectorAll('.monitoring-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // 更新面包屑
        const breadcrumbMap = {
            'infrastructure': '基础设施监控',
            'network': '网络监控',
            'storage': '存储监控',
            'applications': '应用监控',
            'containers': '容器监控',
            'microservices': '微服务监控',
            'databases': '数据库监控',
            'cache': '缓存监控',
            'message-queue': '消息队列监控',
            'business-metrics': '业务指标监控',
            'user-experience': '用户体验监控',
            'logs': '日志分析'
        };
        
        const currentTabElement = document.getElementById('current-tab');
        if (currentTabElement) {
            currentTabElement.textContent = breadcrumbMap[tabName] || '监控';
        }

        this.currentTab = tabName;
        this.loadTabData(tabName);
    }

    /**
     * 初始化图表
     */
    initCharts() {
        // CPU使用率图表
        const cpuCtx = document.getElementById('cpu-chart');
        if (cpuCtx) {
            this.charts.cpu = new Chart(cpuCtx, {
                type: 'line',
                data: {
                    labels: this.generateTimeLabels(),
                    datasets: [{
                        label: 'CPU使用率',
                        data: this.generateRandomData(20, 30, 80),
                        borderColor: '#4f46e5',
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: this.getChartOptions('CPU使用率 (%)')
            });
        }

        // 内存使用率图表
        const memoryCtx = document.getElementById('memory-chart');
        if (memoryCtx) {
            this.charts.memory = new Chart(memoryCtx, {
                type: 'line',
                data: {
                    labels: this.generateTimeLabels(),
                    datasets: [{
                        label: '内存使用率',
                        data: this.generateRandomData(20, 60, 85),
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: this.getChartOptions('内存使用率 (%)')
            });
        }

        // 网络流量图表
        const networkCtx = document.getElementById('network-chart');
        if (networkCtx) {
            this.charts.network = new Chart(networkCtx, {
                type: 'line',
                data: {
                    labels: this.generateTimeLabels(),
                    datasets: [
                        {
                            label: '入站流量',
                            data: this.generateRandomData(20, 20, 60),
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.4
                        },
                        {
                            label: '出站流量',
                            data: this.generateRandomData(20, 15, 50),
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.4
                        }
                    ]
                },
                options: this.getChartOptions('网络流量 (MB/s)')
            });
        }

        // 磁盘I/O图表
        const diskCtx = document.getElementById('disk-chart');
        if (diskCtx) {
            this.charts.disk = new Chart(diskCtx, {
                type: 'line',
                data: {
                    labels: this.generateTimeLabels(),
                    datasets: [
                        {
                            label: '读取',
                            data: this.generateRandomData(20, 500, 2000),
                            borderColor: '#8b5cf6',
                            backgroundColor: 'rgba(139, 92, 246, 0.1)',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.4
                        },
                        {
                            label: '写入',
                            data: this.generateRandomData(20, 300, 1500),
                            borderColor: '#06b6d4',
                            backgroundColor: 'rgba(6, 182, 212, 0.1)',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.4
                        }
                    ]
                },
                options: this.getChartOptions('磁盘I/O (IOPS)')
            });
        }
    }

    /**
     * 获取图表配置选项
     * @param {string} yAxisLabel - Y轴标签
     * @returns {Object} 图表配置选项
     */
    getChartOptions(yAxisLabel) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: yAxisLabel
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            elements: {
                point: {
                    radius: 0,
                    hoverRadius: 4
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        };
    }

    /**
     * 生成时间标签
     * @returns {Array} 时间标签数组
     */
    generateTimeLabels() {
        const labels = [];
        const now = new Date();
        
        for (let i = 19; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 3 * 60 * 1000); // 每3分钟一个点
            labels.push(time.toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit' 
            }));
        }
        
        return labels;
    }

    /**
     * 生成随机数据
     * @param {number} count - 数据点数量
     * @param {number} min - 最小值
     * @param {number} max - 最大值
     * @returns {Array} 随机数据数组
     */
    generateRandomData(count, min, max) {
        const data = [];
        let lastValue = (min + max) / 2;
        
        for (let i = 0; i < count; i++) {
            // 生成相对平滑的随机数据
            const change = (Math.random() - 0.5) * (max - min) * 0.1;
            lastValue = Math.max(min, Math.min(max, lastValue + change));
            data.push(Math.round(lastValue * 100) / 100);
        }
        
        return data;
    }

    /**
     * 开始数据更新
     */
    startDataUpdate() {
        // 每30秒更新一次数据
        this.updateInterval = setInterval(() => {
            this.updateCharts();
            this.updateServerMetrics();
        }, 30000);
    }

    /**
     * 更新图表数据
     */
    updateCharts() {
        Object.keys(this.charts).forEach(chartKey => {
            const chart = this.charts[chartKey];
            if (chart) {
                // 移除第一个数据点
                chart.data.labels.shift();
                chart.data.datasets.forEach(dataset => {
                    dataset.data.shift();
                });

                // 添加新的数据点
                const now = new Date();
                chart.data.labels.push(now.toLocaleTimeString('zh-CN', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                }));

                chart.data.datasets.forEach(dataset => {
                    const lastValue = dataset.data[dataset.data.length - 1] || 50;
                    let newValue;
                    
                    if (chartKey === 'cpu' || chartKey === 'memory') {
                        newValue = Math.max(0, Math.min(100, lastValue + (Math.random() - 0.5) * 10));
                    } else if (chartKey === 'network') {
                        newValue = Math.max(0, lastValue + (Math.random() - 0.5) * 20);
                    } else if (chartKey === 'disk') {
                        newValue = Math.max(0, lastValue + (Math.random() - 0.5) * 200);
                    }
                    
                    dataset.data.push(Math.round(newValue * 100) / 100);
                });

                chart.update('none');
            }
        });
    }

    /**
     * 更新服务器指标
     */
    updateServerMetrics() {
        const serverCards = document.querySelectorAll('.server-card');
        
        serverCards.forEach(card => {
            const metrics = card.querySelectorAll('.metric');
            
            metrics.forEach(metric => {
                const fill = metric.querySelector('.metric-fill');
                const value = metric.querySelector('.metric-value');
                
                if (fill && value) {
                    const currentValue = parseFloat(value.textContent);
                    const newValue = Math.max(0, Math.min(100, currentValue + (Math.random() - 0.5) * 5));
                    const roundedValue = Math.round(newValue);
                    
                    fill.style.width = `${roundedValue}%`;
                    value.textContent = `${roundedValue}%`;
                    
                    // 更新颜色状态
                    fill.className = 'metric-fill';
                    if (roundedValue > 80) {
                        fill.classList.add('critical');
                    } else if (roundedValue > 60) {
                        fill.classList.add('warning');
                    }
                }
            });
        });
    }

    /**
     * 加载初始数据
     */
    loadInitialData() {
        // 模拟加载数据
        console.log('加载监控数据...');
        
        // 更新当前值显示
        this.updateCurrentValues();
    }

    /**
     * 更新当前值显示
     */
    updateCurrentValues() {
        const currentValues = document.querySelectorAll('.current-value');
        const values = ['65%', '72%', '45 MB/s', '1.2K IOPS'];
        
        currentValues.forEach((element, index) => {
            if (values[index]) {
                element.textContent = values[index];
            }
        });
    }

    /**
     * 加载标签页数据
     * @param {string} tabName - 标签名称
     */
    loadTabData(tabName) {
        console.log(`加载 ${tabName} 标签页数据...`);
        
        // 这里可以根据不同的标签页加载不同的数据
        // 目前只有基础设施标签页有完整实现
        if (tabName === 'infrastructure') {
            this.updateCharts();
            this.updateServerMetrics();
        }
    }

    /**
     * 刷新数据
     */
    refreshData() {
        console.log('刷新监控数据...');
        
        // 显示加载状态
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            const icon = refreshBtn.querySelector('i');
            icon.classList.add('fa-spin');
            
            setTimeout(() => {
                icon.classList.remove('fa-spin');
            }, 1000);
        }
        
        // 重新加载数据
        this.loadTabData(this.currentTab);
        this.updateCharts();
        this.updateServerMetrics();
    }

    /**
     * 导出报告
     */
    exportReport() {
        console.log('导出监控报告...');
        
        // 模拟导出功能
        const reportData = {
            timestamp: new Date().toISOString(),
            timeRange: this.timeRange,
            currentTab: this.currentTab,
            servers: this.getServerData(),
            metrics: this.getMetricsData()
        };
        
        // 创建并下载JSON文件
        const blob = new Blob([JSON.stringify(reportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `monitoring-report-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // 显示成功消息
        this.showNotification('报告导出成功', 'success');
    }

    /**
     * 获取服务器数据
     * @returns {Array} 服务器数据数组
     */
    getServerData() {
        const servers = [];
        const serverCards = document.querySelectorAll('.server-card');
        
        serverCards.forEach(card => {
            const name = card.querySelector('h4').textContent;
            const ip = card.querySelector('.server-ip').textContent;
            const status = card.querySelector('.status-text').textContent;
            
            const metrics = {};
            card.querySelectorAll('.metric').forEach(metric => {
                const label = metric.querySelector('.metric-label').textContent;
                const value = metric.querySelector('.metric-value').textContent;
                metrics[label] = value;
            });
            
            servers.push({ name, ip, status, metrics });
        });
        
        return servers;
    }

    /**
     * 获取指标数据
     * @returns {Object} 指标数据对象
     */
    getMetricsData() {
        const metrics = {};
        
        Object.keys(this.charts).forEach(chartKey => {
            const chart = this.charts[chartKey];
            if (chart) {
                metrics[chartKey] = {
                    labels: chart.data.labels,
                    datasets: chart.data.datasets.map(dataset => ({
                        label: dataset.label,
                        data: dataset.data
                    }))
                };
            }
        });
        
        return metrics;
    }

    /**
     * 处理进程操作
     * @param {string} action - 操作类型
     * @param {HTMLElement} row - 表格行元素
     */
    handleProcessAction(action, row) {
        const processName = row.querySelector('.process-info span').textContent;
        const pid = row.cells[1].textContent;
        
        console.log(`${action}进程: ${processName} (PID: ${pid})`);
        
        // 模拟操作
        const statusBadge = row.querySelector('.status-badge');
        
        if (action === '重启') {
            statusBadge.textContent = '重启中';
            statusBadge.className = 'status-badge pending';
            
            setTimeout(() => {
                statusBadge.textContent = '运行中';
                statusBadge.className = 'status-badge running';
                this.showNotification(`进程 ${processName} 重启成功`, 'success');
            }, 2000);
        } else if (action === '停止') {
            statusBadge.textContent = '已停止';
            statusBadge.className = 'status-badge stopped';
            this.showNotification(`进程 ${processName} 已停止`, 'info');
        }
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
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // 添加样式
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#4f46e5'};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 绑定关闭事件
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });
        
        // 自动关闭
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * 销毁监控管理器
     */
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        Object.keys(this.charts).forEach(chartKey => {
            if (this.charts[chartKey]) {
                this.charts[chartKey].destroy();
            }
        });
    }
}

// 页面加载完成后初始化监控管理器
document.addEventListener('DOMContentLoaded', () => {
    window.monitoringManager = new MonitoringManager();
});

// 页面卸载时清理资源
window.addEventListener('beforeunload', () => {
    if (window.monitoringManager) {
        window.monitoringManager.destroy();
    }
});