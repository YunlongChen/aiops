/**
 * 导航组件 - 公共导航菜单组件
 * 提供统一的导航菜单结构和交互功能
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @date 2025-01-23
 */

/**
 * 导航菜单管理器类
 * 负责导航菜单的渲染、状态管理和交互处理
 */
class NavigationManager {
    /**
     * 构造函数
     * @param {string} containerId - 导航容器的ID
     * @param {string} currentPage - 当前页面标识
     */
    constructor(containerId, currentPage = '') {
        this.container = document.getElementById(containerId);
        this.currentPage = currentPage;
        this.menuItems = [
            {
                id: 'dashboard',
                icon: 'fas fa-tachometer-alt',
                text: '仪表板',
                href: './index.html'
            },
            {
                id: 'monitoring',
                icon: 'fas fa-chart-line',
                text: '监控中心',
                href: './monitoring.html'
            },
            {
                id: 'ai-engine',
                icon: 'fas fa-brain',
                text: 'AI引擎',
                href: './ai-engine.html'
            },
            {
                id: 'alerting',
                icon: 'fas fa-bell',
                text: '告警管理',
                href: './alerting.html'
            },
            {
                id: 'self-healing',
                icon: 'fas fa-magic',
                text: '自愈系统',
                href: './self-healing.html'
            },
            {
                id: 'settings',
                icon: 'fas fa-cog',
                text: '系统设置',
                href: './settings.html'
            }
        ];
        
        this.init();
    }

    /**
     * 初始化导航组件
     */
    init() {
        this.render();
        this.bindEvents();
    }

    /**
     * 渲染导航菜单
     */
    render() {
        if (!this.container) {
            console.error('Navigation container not found');
            return;
        }

        const navMenu = document.createElement('div');
        navMenu.className = 'nav-menu';

        this.menuItems.forEach(item => {
            const navItem = document.createElement('div');
            navItem.className = `nav-item${item.id === this.currentPage ? ' active' : ''}`;
            navItem.setAttribute('data-page', item.id);

            navItem.innerHTML = `
                <i class="${item.icon}"></i>
                <span><a href="${item.href}">${item.text}</a></span>
            `;

            navMenu.appendChild(navItem);
        });

        this.container.appendChild(navMenu);
    }

    /**
     * 绑定事件处理器
     */
    bindEvents() {
        const navItems = this.container.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                // 如果点击的是链接，让浏览器处理导航
                if (e.target.tagName === 'A') {
                    return;
                }
                
                // 否则手动触发链接点击
                const link = item.querySelector('a');
                if (link) {
                    link.click();
                }
            });

            // 添加键盘支持
            item.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const link = item.querySelector('a');
                    if (link) {
                        link.click();
                    }
                }
            });

            // 设置可访问性属性
            item.setAttribute('tabindex', '0');
            item.setAttribute('role', 'button');
        });
    }

    /**
     * 设置当前活动页面
     * @param {string} pageId - 页面ID
     */
    setActivePage(pageId) {
        const navItems = this.container.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-page') === pageId) {
                item.classList.add('active');
            }
        });
        
        this.currentPage = pageId;
    }

    /**
     * 添加菜单项
     * @param {Object} menuItem - 菜单项配置
     */
    addMenuItem(menuItem) {
        this.menuItems.push(menuItem);
        this.render();
    }

    /**
     * 移除菜单项
     * @param {string} itemId - 菜单项ID
     */
    removeMenuItem(itemId) {
        this.menuItems = this.menuItems.filter(item => item.id !== itemId);
        this.render();
    }

    /**
     * 更新菜单项
     * @param {string} itemId - 菜单项ID
     * @param {Object} updates - 更新内容
     */
    updateMenuItem(itemId, updates) {
        const itemIndex = this.menuItems.findIndex(item => item.id === itemId);
        if (itemIndex !== -1) {
            this.menuItems[itemIndex] = { ...this.menuItems[itemIndex], ...updates };
            this.render();
        }
    }
}

/**
 * 创建导航组件实例
 * @param {string} containerId - 容器ID
 * @param {string} currentPage - 当前页面
 * @returns {NavigationManager} 导航管理器实例
 */
function createNavigation(containerId, currentPage = '') {
    return new NavigationManager(containerId, currentPage);
}

/**
 * 自动初始化导航组件
 * 在DOM加载完成后自动查找并初始化导航容器
 */
function autoInitNavigation() {
    document.addEventListener('DOMContentLoaded', () => {
        const navContainer = document.querySelector('[data-nav-container]');
        if (navContainer) {
            const currentPage = navContainer.getAttribute('data-current-page') || '';
            new NavigationManager(navContainer.id, currentPage);
        }
    });
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NavigationManager, createNavigation, autoInitNavigation };
}

// 全局暴露
window.NavigationManager = NavigationManager;
window.createNavigation = createNavigation;
window.autoInitNavigation = autoInitNavigation;

// 自动初始化
autoInitNavigation();