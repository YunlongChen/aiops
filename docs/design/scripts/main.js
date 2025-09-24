/**
 * AIOps Platform - 主JavaScript文件
 * 负责页面导航、交互功能和动态数据更新
 */

class AIOpsApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.currentSubpage = null;
        this.refreshInterval = null;
        this.init();
    }

    /**
     * 初始化应用程序
     */
    init() {
        this.bindEvents();
        this.startDataRefresh();
        this.loadInitialData();
        console.log('AIOps Platform initialized');
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 导航菜单点击事件
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                if (page) {
                    this.navigateToPage(page);
                }
            });
        });

        // 侧边栏菜单点击事件
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const subpage = e.currentTarget.dataset.subpage;
                if (subpage) {
                    this.navigateToSubpage(subpage);
                }
            });
        });

        // 时间范围选择器变化事件
        const timeRangeSelect = document.querySelector('.time-range');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', (e) => {
                this.updateChartData(e.target.value);
            });
        }

        // 响应式侧边栏切换
        this.setupResponsiveSidebar();

        // 用户菜单点击事件
        document.querySelector('.user-info')?.addEventListener('click', () => {
            this.toggleUserMenu();
        });
    }

    /**
     * 页面导航
     * @param {string} pageName - 页面名称
     */
    navigateToPage(pageName) {
        // 更新导航状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageName}"]`)?.classList.add('active');

        // 更新页面显示
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById(`${pageName}-page`)?.classList.add('active');

        // 更新面包屑
        this.updateBreadcrumb(pageName);

        // 更新当前页面
        this.currentPage = pageName;

        // 加载页面特定数据
        this.loadPageData(pageName);

        console.log(`Navigated to page: ${pageName}`);
    }

    /**
     * 子页面导航
     * @param {string} subpageName - 子页面名称
     */
    navigateToSubpage(subpageName) {
        // 更新侧边栏状态
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-subpage="${subpageName}"]`)?.classList.add('active');

        this.currentSubpage = subpageName;
        this.loadSubpageData(subpageName);

        console.log(`Navigated to subpage: ${subpageName}`);
    }

    /**
     * 更新面包屑导航
     * @param {string} pageName - 页面名称
     */
    updateBreadcrumb(pageName) {
        const pageNames = {
            'dashboard': '仪表板',
            'monitoring': '监控中心',
            'ai-engine': 'AI引擎',
            'alerting': '告警管理',
            'self-healing': '自愈系统',
            'settings': '系统设置'
        };

        const breadcrumbItem = document.querySelector('.breadcrumb-item.active');
        if (breadcrumbItem) {
            breadcrumbItem.textContent = pageNames[pageName] || pageName;
        }
    }

    /**
     * 加载页面数据
     * @param {string} pageName - 页面名称
     */
    loadPageData(pageName) {
        switch (pageName) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'monitoring':
                this.loadMonitoringData();
                break;
            case 'ai-engine':
                this.loadAIEngineData();
                break;
            case 'alerting':
                this.loadAlertingData();
                break;
            case 'self-healing':
                this.loadSelfHealingData();
                break;
            case 'settings':
                this.loadSettingsData();
                break;
        }
    }

    /**
     * 加载子页面数据
     * @param {string} subpageName - 子页面名称
     */
    loadSubpageData(subpageName) {
        // 根据子页面加载相应数据
        console.log(`Loading data for subpage: ${subpageName}`);
        // 这里可以添加具体的子页面数据加载逻辑
    }

    /**
     * 加载仪表板数据
     */
    loadDashboardData() {
        // 更新状态卡片
        this.updateStatusCards();
        
        // 更新图表
        this.updatePerformanceChart();
        
        // 更新资源指标
        this.updateResourceMetrics();
        
        // 更新表格数据
        this.updateRecentAlerts();
        this.updateSelfHealingRecords();
    }

    /**
     * 更新状态卡片
     */
    updateStatusCards() {
        // 模拟实时数据更新
        const statusData = {
            systemStatus: {
                status: 'healthy',
                availability: '99.9%'
            },
            activeAlerts: {
                count: Math.floor(Math.random() * 10),
                highPriority: Math.floor(Math.random() * 5)
            },
            monitoringNodes: {
                total: 24,
                online: 23 + Math.floor(Math.random() * 2)
            },
            selfHealingEvents: {
                today: Math.floor(Math.random() * 20) + 5
            }
        };

        // 更新DOM元素
        this.updateStatusCard('system-status', statusData.systemStatus);
        this.updateStatusCard('active-alerts', statusData.activeAlerts);
        this.updateStatusCard('monitoring-nodes', statusData.monitoringNodes);
        this.updateStatusCard('self-healing-events', statusData.selfHealingEvents);
    }

    /**
     * 更新单个状态卡片
     * @param {string} cardType - 卡片类型
     * @param {Object} data - 数据对象
     */
    updateStatusCard(cardType, data) {
        // 这里可以根据cardType更新对应的DOM元素
        // 由于是演示版本，暂时使用console.log
        console.log(`Updating ${cardType}:`, data);
    }

    /**
     * 更新性能图表
     */
    updatePerformanceChart() {
        // 这个方法将在charts.js中实现
        if (window.updatePerformanceChart) {
            window.updatePerformanceChart();
        }
    }

    /**
     * 更新资源指标
     */
    updateResourceMetrics() {
        const metrics = {
            cpu: Math.floor(Math.random() * 40) + 40,
            memory: Math.floor(Math.random() * 30) + 60,
            disk: Math.floor(Math.random() * 20) + 30,
            network: Math.floor(Math.random() * 40) + 20
        };

        // 更新进度条
        this.updateProgressBar('cpu', metrics.cpu);
        this.updateProgressBar('memory', metrics.memory);
        this.updateProgressBar('disk', metrics.disk);
        this.updateProgressBar('network', metrics.network);
    }

    /**
     * 更新进度条
     * @param {string} type - 指标类型
     * @param {number} value - 数值
     */
    updateProgressBar(type, value) {
        const progressBars = document.querySelectorAll('.progress-fill');
        const metricValues = document.querySelectorAll('.metric-value span');
        
        // 根据类型找到对应的进度条和数值
        // 这里简化处理，实际应用中需要更精确的选择器
        progressBars.forEach((bar, index) => {
            if (index < 4) { // 假设前4个是资源指标
                const randomValue = Math.floor(Math.random() * 40) + 30;
                bar.style.width = `${randomValue}%`;
                if (metricValues[index]) {
                    metricValues[index].textContent = `${randomValue}%`;
                }
            }
        });
    }

    /**
     * 更新最近告警
     */
    updateRecentAlerts() {
        // 模拟告警数据
        const alerts = [
            {
                time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
                level: 'critical',
                service: '数据库服务',
                description: '连接池耗尽',
                status: 'active'
            },
            {
                time: new Date(Date.now() - 4 * 60000).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
                level: 'warning',
                service: 'Web服务',
                description: '响应时间过长',
                status: 'resolved'
            }
        ];

        console.log('Updated recent alerts:', alerts);
    }

    /**
     * 更新自愈操作记录
     */
    updateSelfHealingRecords() {
        // 模拟自愈记录数据
        const records = [
            {
                time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
                trigger: '数据库连接异常',
                action: '重启连接池',
                result: 'success'
            },
            {
                time: new Date(Date.now() - 15 * 60000).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
                trigger: '磁盘空间不足',
                action: '清理临时文件',
                result: 'success'
            }
        ];

        console.log('Updated self-healing records:', records);
    }

    /**
     * 更新图表数据
     * @param {string} timeRange - 时间范围
     */
    updateChartData(timeRange) {
        console.log(`Updating chart data for time range: ${timeRange}`);
        
        // 调用图表更新函数
        if (window.updateChartTimeRange) {
            window.updateChartTimeRange(timeRange);
        }
    }

    /**
     * 设置响应式侧边栏
     */
    setupResponsiveSidebar() {
        // 添加移动端菜单切换按钮
        if (window.innerWidth <= 1024) {
            this.createMobileMenuToggle();
        }

        // 监听窗口大小变化
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 1024) {
                this.createMobileMenuToggle();
            } else {
                this.removeMobileMenuToggle();
            }
        });
    }

    /**
     * 创建移动端菜单切换按钮
     */
    createMobileMenuToggle() {
        if (document.querySelector('.mobile-menu-toggle')) return;

        const toggleButton = document.createElement('button');
        toggleButton.className = 'mobile-menu-toggle';
        toggleButton.innerHTML = '<i class="fas fa-bars"></i>';
        toggleButton.style.cssText = `
            position: fixed;
            top: 16px;
            left: 16px;
            z-index: 1001;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            cursor: pointer;
        `;

        toggleButton.addEventListener('click', () => {
            document.querySelector('.sidebar').classList.toggle('open');
        });

        document.body.appendChild(toggleButton);
    }

    /**
     * 移除移动端菜单切换按钮
     */
    removeMobileMenuToggle() {
        const toggleButton = document.querySelector('.mobile-menu-toggle');
        if (toggleButton) {
            toggleButton.remove();
        }
    }

    /**
     * 切换用户菜单
     */
    toggleUserMenu() {
        // 这里可以实现用户菜单的显示/隐藏逻辑
        console.log('Toggle user menu');
    }

    /**
     * 开始数据刷新
     */
    startDataRefresh() {
        // 每30秒刷新一次数据
        this.refreshInterval = setInterval(() => {
            if (this.currentPage === 'dashboard') {
                this.updateResourceMetrics();
                this.updateStatusCards();
            }
        }, 30000);
    }

    /**
     * 停止数据刷新
     */
    stopDataRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * 加载初始数据
     */
    loadInitialData() {
        // 加载初始页面数据
        this.loadPageData(this.currentPage);
    }

    /**
     * 加载监控数据
     */
    loadMonitoringData() {
        console.log('Loading monitoring data...');
        // 这里将在后续的监控页面中实现
    }

    /**
     * 加载AI引擎数据
     */
    loadAIEngineData() {
        console.log('Loading AI engine data...');
        // 这里将在后续的AI引擎页面中实现
    }

    /**
     * 加载告警数据
     */
    loadAlertingData() {
        console.log('Loading alerting data...');
        // 这里将在后续的告警管理页面中实现
    }

    /**
     * 加载自愈系统数据
     */
    loadSelfHealingData() {
        console.log('Loading self-healing data...');
        // 这里将在后续的自愈系统页面中实现
    }

    /**
     * 加载设置数据
     */
    loadSettingsData() {
        console.log('Loading settings data...');
        // 这里将在后续的设置页面中实现
    }

    /**
     * 销毁应用程序
     */
    destroy() {
        this.stopDataRefresh();
        // 清理事件监听器等
        console.log('AIOps Platform destroyed');
    }
}

// 工具函数
const Utils = {
    /**
     * 格式化时间
     * @param {Date} date - 日期对象
     * @returns {string} 格式化后的时间字符串
     */
    formatTime(date) {
        return date.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    },

    /**
     * 格式化数字
     * @param {number} num - 数字
     * @returns {string} 格式化后的数字字符串
     */
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    },

    /**
     * 生成随机颜色
     * @returns {string} 十六进制颜色值
     */
    randomColor() {
        return '#' + Math.floor(Math.random() * 16777215).toString(16);
    },

    /**
     * 防抖函数
     * @param {Function} func - 要防抖的函数
     * @param {number} wait - 等待时间
     * @returns {Function} 防抖后的函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * 节流函数
     * @param {Function} func - 要节流的函数
     * @param {number} limit - 限制时间
     * @returns {Function} 节流后的函数
     */
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// 全局变量
let app;

// DOM加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    app = new AIOpsApp();
});

// 页面卸载时清理资源
window.addEventListener('beforeunload', () => {
    if (app) {
        app.destroy();
    }
});

// 导出到全局作用域供其他脚本使用
window.AIOpsApp = AIOpsApp;
window.Utils = Utils;


/**
 * 初始化子标签页功能
 * 为主仪表板的子标签页添加切换功能
 */
function initSubTabs() {
    const subTabs = document.querySelectorAll('.sub-tab');
    const subtabContents = document.querySelectorAll('.subtab-content');
    
    subTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.getAttribute('data-target');
            
            // 移除所有活动状态
            subTabs.forEach(t => t.classList.remove('active'));
            subtabContents.forEach(content => content.classList.remove('active'));
            
            // 添加活动状态
            tab.classList.add('active');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

/**
 * 初始化监控指标刷新功能
 * 为监控卡片添加刷新按钮功能
 */
function initMonitoringRefresh() {
    const refreshBtns = document.querySelectorAll('.refresh-btn');
    
    refreshBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const card = btn.closest('.monitoring-card');
            
            // 添加加载状态
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            // 模拟数据刷新
            setTimeout(() => {
                btn.innerHTML = '<i class="fas fa-sync-alt"></i>';
                updateMonitoringMetrics(card);
            }, 1000);
        });
    });
}

/**
 * 更新监控指标数据
 * @param {Element} card - 监控卡片元素
 */
function updateMonitoringMetrics(card) {
    const metricBoxes = card.querySelectorAll('.metric-box');
    
    metricBoxes.forEach(box => {
        const valueElement = box.querySelector('.metric-value');
        const trendElement = box.querySelector('.metric-trend');
        
        if (valueElement) {
            // 生成随机数据
            const currentValue = parseFloat(valueElement.textContent);
            const variation = (Math.random() - 0.5) * 10;
            const newValue = Math.max(0, Math.min(100, currentValue + variation));
            
            valueElement.textContent = newValue.toFixed(1) + '%';
            
            // 更新趋势
            if (trendElement) {
                if (variation > 2) {
                    trendElement.textContent = '↑ 上升';
                    trendElement.className = 'metric-trend up';
                } else if (variation < -2) {
                    trendElement.textContent = '↓ 下降';
                    trendElement.className = 'metric-trend down';
                } else {
                    trendElement.textContent = '→ 稳定';
                    trendElement.className = 'metric-trend stable';
                }
            }
        }
    });
}

/**
 * 初始化服务健康状态
 * 为服务列表添加状态切换功能
 */
function initServiceHealth() {
    const serviceItems = document.querySelectorAll('.service-item');
    
    serviceItems.forEach(item => {
        // 随机设置服务状态
        const statuses = ['healthy', 'warning', 'error'];
        const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
        
        item.className = `service-item ${randomStatus}`;
        
        // 添加点击事件查看详情
        item.addEventListener('click', () => {
            const serviceName = item.querySelector('.service-name').textContent;
            showServiceDetails(serviceName, randomStatus);
        });
    });
}

/**
 * 显示服务详情
 * @param {string} serviceName - 服务名称
 * @param {string} status - 服务状态
 */
function showServiceDetails(serviceName, status) {
    const statusText = {
        'healthy': '健康',
        'warning': '警告',
        'error': '错误'
    };
    
    alert(`服务详情：\n服务名称：${serviceName}\n当前状态：${statusText[status]}`);
}

/**
 * 初始化分析筛选器
 * 为性能分析页面添加筛选功能
 */
function initAnalysisFilters() {
    const timeSelector = document.querySelector('.time-selector');
    const serviceSelector = document.querySelector('.service-selector');
    
    if (timeSelector) {
        timeSelector.addEventListener('change', () => {
            updateAnalysisCharts();
        });
    }
    
    if (serviceSelector) {
        serviceSelector.addEventListener('change', () => {
            updateAnalysisCharts();
        });
    }
}

/**
 * 更新分析图表
 */
function updateAnalysisCharts() {
    const chartCards = document.querySelectorAll('.chart-card canvas');
    
    chartCards.forEach(canvas => {
        // 模拟图表更新
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#f3f4f6';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // 添加简单的图表效果
        ctx.fillStyle = '#4f46e5';
        ctx.fillText('图表数据更新中...', 10, 30);
    });
}

/**
 * 初始化日志搜索功能
 * 为日志查看页面添加搜索和筛选功能
 */
function initLogSearch() {
    const searchInput = document.querySelector('.search-input input');
    const logLevelFilter = document.querySelector('.log-level');
    const logSourceFilter = document.querySelector('.log-source');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterLogs, 300));
    }
    
    if (logLevelFilter) {
        logLevelFilter.addEventListener('change', filterLogs);
    }
    
    if (logSourceFilter) {
        logSourceFilter.addEventListener('change', filterLogs);
    }
}

/**
 * 筛选日志条目
 */
function filterLogs() {
    const searchTerm = document.querySelector('.search-input input')?.value.toLowerCase() || '';
    const levelFilter = document.querySelector('.log-level')?.value || '';
    const sourceFilter = document.querySelector('.log-source')?.value || '';
    
    const logEntries = document.querySelectorAll('.log-entry');
    
    logEntries.forEach(entry => {
        const message = entry.querySelector('.log-message')?.textContent.toLowerCase() || '';
        const level = entry.classList.contains('error') ? 'error' : 
                     entry.classList.contains('warning') ? 'warning' : 'info';
        const source = entry.querySelector('.log-source')?.textContent || '';
        
        const matchesSearch = !searchTerm || message.includes(searchTerm);
        const matchesLevel = !levelFilter || level === levelFilter;
        const matchesSource = !sourceFilter || source.includes(sourceFilter);
        
        if (matchesSearch && matchesLevel && matchesSource) {
            entry.style.display = 'grid';
        } else {
            entry.style.display = 'none';
        }
    });
}

/**
 * 初始化日志导出功能
 */
function initLogExport() {
    const exportBtn = document.querySelector('.btn-secondary');
    
    if (exportBtn && exportBtn.textContent.includes('导出')) {
        exportBtn.addEventListener('click', () => {
            const visibleLogs = Array.from(document.querySelectorAll('.log-entry'))
                .filter(entry => entry.style.display !== 'none')
                .map(entry => {
                    const time = entry.querySelector('.log-time')?.textContent || '';
                    const level = entry.querySelector('.log-level')?.textContent || '';
                    const source = entry.querySelector('.log-source')?.textContent || '';
                    const message = entry.querySelector('.log-message')?.textContent || '';
                    return `${time}\t${level}\t${source}\t${message}`;
                })
                .join('\n');
            
            const blob = new Blob([visibleLogs], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `logs_${new Date().toISOString().split('T')[0]}.txt`;
            a.click();
            URL.revokeObjectURL(url);
        });
    }
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间
 * @returns {Function} 防抖后的函数
 */
function debounce(func, wait) {
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

// 在页面加载完成后初始化所有功能
document.addEventListener('DOMContentLoaded', function() {
    // ... existing initialization code ...
    
    // 初始化子标签页功能
    initSubTabs();
    
    // 初始化监控功能
    initMonitoringRefresh();
    initServiceHealth();
    
    // 初始化分析功能
    initAnalysisFilters();
    
    // 初始化日志功能
    initLogSearch();
    initLogExport();
});