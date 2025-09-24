// 设置页面管理器
class SettingsManager {
    constructor() {
        this.currentPage = 'general';
        this.settings = this.loadSettings();
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCurrentSettings();
        this.updateBreadcrumb();
    }

    // 绑定事件
    bindEvents() {
        // 侧边栏菜单点击
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const subpage = e.currentTarget.dataset.subpage;
                if (subpage) {
                    this.switchPage(subpage);
                }
            });
        });

        // 保存按钮
        document.getElementById('saveBtn').addEventListener('click', () => {
            this.showSaveModal();
        });

        // 重置按钮
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.showResetModal();
        });

        // 模态框事件
        this.bindModalEvents();

        // 主题选择
        this.bindThemeEvents();

        // 颜色选择
        this.bindColorEvents();

        // 表单变更监听
        this.bindFormEvents();

        // 开关控件
        this.bindSwitchEvents();
    }

    // 页面切换
    switchPage(pageId) {
        // 更新菜单状态
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-subpage="${pageId}"]`).classList.add('active');

        // 更新页面显示
        document.querySelectorAll('.settings-page').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById(`${pageId}-page`).classList.add('active');

        this.currentPage = pageId;
        this.updateBreadcrumb();
    }

    // 更新面包屑导航
    updateBreadcrumb() {
        const pageNames = {
            'general': '常规设置',
            'appearance': '外观主题',
            'notifications': '通知设置',
            'monitoring': '监控配置',
            'ai-models': 'AI模型配置',
            'data-sources': '数据源管理',
            'integrations': '集成配置',
            'users': '用户管理',
            'roles': '角色权限',
            'audit': '审计日志',
            'backup': '备份恢复',
            'maintenance': '系统维护',
            'about': '关于系统'
        };

        const breadcrumb = document.querySelector('.breadcrumb');
        breadcrumb.innerHTML = `
            <span class="breadcrumb-item">系统设置</span>
            <i class="fas fa-chevron-right"></i>
            <span class="breadcrumb-item active">${pageNames[this.currentPage] || '设置'}</span>
        `;
    }

    // 绑定模态框事件
    bindModalEvents() {
        // 保存确认
        document.getElementById('confirmSave').addEventListener('click', () => {
            this.saveSettings();
        });

        document.getElementById('cancelSave').addEventListener('click', () => {
            this.hideSaveModal();
        });

        // 重置确认
        document.getElementById('confirmReset').addEventListener('click', () => {
            this.resetSettings();
        });

        document.getElementById('cancelReset').addEventListener('click', () => {
            this.hideResetModal();
        });

        // 关闭按钮
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                modal.classList.remove('active');
            });
        });

        // 点击背景关闭
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active');
                }
            });
        });
    }

    // 绑定主题事件
    bindThemeEvents() {
        document.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const theme = e.currentTarget.dataset.theme;
                this.selectTheme(theme);
            });
        });
    }

    // 绑定颜色事件
    bindColorEvents() {
        document.querySelectorAll('.color-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const color = e.currentTarget.dataset.color;
                this.selectColor(color);
            });
        });
    }

    // 绑定表单事件
    bindFormEvents() {
        const inputs = document.querySelectorAll('.form-input, .form-select');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                this.markAsModified(input);
                this.validateInput(input);
            });

            input.addEventListener('input', () => {
                this.markAsModified(input);
            });
        });
    }

    // 绑定开关事件
    bindSwitchEvents() {
        document.querySelectorAll('.switch input').forEach(switchInput => {
            switchInput.addEventListener('change', () => {
                this.markAsModified(switchInput);
            });
        });
    }

    // 选择主题
    selectTheme(theme) {
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.remove('active');
        });
        document.querySelector(`[data-theme="${theme}"]`).classList.add('active');

        // 应用主题
        this.applyTheme(theme);
        this.settings.appearance.theme = theme;
    }

    // 选择颜色
    selectColor(color) {
        document.querySelectorAll('.color-option').forEach(option => {
            option.classList.remove('active');
        });
        document.querySelector(`[data-color="${color}"]`).classList.add('active');

        // 应用颜色
        this.applyColor(color);
        this.settings.appearance.primaryColor = color;
    }

    // 应用主题
    applyTheme(theme) {
        document.body.className = document.body.className.replace(/theme-\w+/g, '');
        if (theme !== 'auto') {
            document.body.classList.add(`theme-${theme}`);
        } else {
            // 跟随系统主题
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.body.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
        }
    }

    // 应用颜色
    applyColor(color) {
        document.documentElement.style.setProperty('--primary-color', color);
        
        // 计算相关颜色
        const rgb = this.hexToRgb(color);
        const hsl = this.rgbToHsl(rgb.r, rgb.g, rgb.b);
        
        // 生成深色和浅色变体
        const darkColor = this.hslToHex(hsl.h, hsl.s, Math.max(hsl.l - 0.1, 0));
        const lightColor = this.hslToHex(hsl.h, hsl.s, Math.min(hsl.l + 0.1, 1));
        
        document.documentElement.style.setProperty('--primary-dark', darkColor);
        document.documentElement.style.setProperty('--primary-light', lightColor);
    }

    // 标记为已修改
    markAsModified(element) {
        const settingItem = element.closest('.setting-item');
        if (settingItem) {
            settingItem.classList.add('modified');
        }
    }

    // 验证输入
    validateInput(input) {
        const value = input.value;
        let isValid = true;
        let message = '';

        // 移除之前的验证状态
        input.classList.remove('error', 'success');
        const existingMessage = input.parentNode.querySelector('.error-message, .success-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // 根据输入类型进行验证
        switch (input.id) {
            case 'systemName':
                isValid = value.length >= 2 && value.length <= 50;
                message = isValid ? '' : '系统名称长度应在2-50个字符之间';
                break;
            case 'maxConcurrent':
                const num = parseInt(value);
                isValid = num >= 100 && num <= 10000;
                message = isValid ? '' : '并发连接数应在100-10000之间';
                break;
        }

        // 应用验证结果
        if (value && message) {
            input.classList.add(isValid ? 'success' : 'error');
            const messageEl = document.createElement('div');
            messageEl.className = isValid ? 'success-message' : 'error-message';
            messageEl.textContent = message;
            input.parentNode.appendChild(messageEl);
        }

        return isValid;
    }

    // 显示保存模态框
    showSaveModal() {
        document.getElementById('saveModal').classList.add('active');
    }

    // 隐藏保存模态框
    hideSaveModal() {
        document.getElementById('saveModal').classList.remove('active');
    }

    // 显示重置模态框
    showResetModal() {
        document.getElementById('resetModal').classList.add('active');
    }

    // 隐藏重置模态框
    hideResetModal() {
        document.getElementById('resetModal').classList.remove('active');
    }

    // 保存设置
    saveSettings() {
        // 收集所有设置
        this.collectSettings();

        // 验证设置
        if (!this.validateAllSettings()) {
            this.showToast('设置验证失败，请检查输入', 'error');
            this.hideSaveModal();
            return;
        }

        // 模拟保存过程
        const saveBtn = document.getElementById('confirmSave');
        const originalText = saveBtn.innerHTML;
        saveBtn.innerHTML = '<span class="loading"></span> 保存中...';
        saveBtn.disabled = true;

        setTimeout(() => {
            // 保存到本地存储
            localStorage.setItem('aiops_settings', JSON.stringify(this.settings));

            // 重置按钮状态
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = false;

            // 隐藏模态框
            this.hideSaveModal();

            // 显示成功提示
            this.showToast('设置保存成功！', 'success');

            // 移除修改标记
            document.querySelectorAll('.setting-item.modified').forEach(item => {
                item.classList.remove('modified');
            });
        }, 1500);
    }

    // 重置设置
    resetSettings() {
        // 重置到默认值
        this.settings = this.getDefaultSettings();
        
        // 更新界面
        this.loadCurrentSettings();

        // 隐藏模态框
        this.hideResetModal();

        // 显示提示
        this.showToast('设置已重置为默认值', 'success');

        // 移除修改标记
        document.querySelectorAll('.setting-item.modified').forEach(item => {
            item.classList.remove('modified');
        });
    }

    // 收集设置
    collectSettings() {
        // 基本信息
        this.settings.general = {
            systemName: document.getElementById('systemName').value,
            systemVersion: document.getElementById('systemVersion').value,
            timezone: document.getElementById('timezone').value,
            language: document.getElementById('language').value,
            refreshInterval: parseInt(document.getElementById('refreshInterval').value),
            dataRetention: parseInt(document.getElementById('dataRetention').value),
            maxConcurrent: parseInt(document.getElementById('maxConcurrent').value),
            enableCache: document.getElementById('enableCache').checked,
            sessionTimeout: parseInt(document.getElementById('sessionTimeout').value),
            passwordPolicy: document.getElementById('passwordPolicy').value,
            enable2FA: document.getElementById('enable2FA').checked,
            enableAudit: document.getElementById('enableAudit').checked
        };

        // 通知设置
        this.settings.notifications = {
            systemStartStop: document.getElementById('systemStartStop').checked,
            systemUpdate: document.getElementById('systemUpdate').checked,
            configChange: document.getElementById('configChange').checked,
            highPriorityAlert: document.getElementById('highPriorityAlert').checked,
            mediumPriorityAlert: document.getElementById('mediumPriorityAlert').checked,
            lowPriorityAlert: document.getElementById('lowPriorityAlert').checked
        };
    }

    // 验证所有设置
    validateAllSettings() {
        const inputs = document.querySelectorAll('.form-input');
        let allValid = true;

        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                allValid = false;
            }
        });

        return allValid;
    }

    // 加载当前设置
    loadCurrentSettings() {
        // 加载基本设置
        if (this.settings.general) {
            const general = this.settings.general;
            document.getElementById('systemName').value = general.systemName || 'AIOps 智能运维平台';
            document.getElementById('systemVersion').value = general.systemVersion || 'v2.1.0';
            document.getElementById('timezone').value = general.timezone || 'Asia/Shanghai';
            document.getElementById('language').value = general.language || 'zh-CN';
            document.getElementById('refreshInterval').value = general.refreshInterval || 10;
            document.getElementById('dataRetention').value = general.dataRetention || 30;
            document.getElementById('maxConcurrent').value = general.maxConcurrent || 1000;
            document.getElementById('enableCache').checked = general.enableCache !== false;
            document.getElementById('sessionTimeout').value = general.sessionTimeout || 60;
            document.getElementById('passwordPolicy').value = general.passwordPolicy || 'medium';
            document.getElementById('enable2FA').checked = general.enable2FA || false;
            document.getElementById('enableAudit').checked = general.enableAudit !== false;
        }

        // 加载外观设置
        if (this.settings.appearance) {
            const appearance = this.settings.appearance;
            this.selectTheme(appearance.theme || 'light');
            this.selectColor(appearance.primaryColor || '#4F46E5');
        }

        // 加载通知设置
        if (this.settings.notifications) {
            const notifications = this.settings.notifications;
            document.getElementById('systemStartStop').checked = notifications.systemStartStop !== false;
            document.getElementById('systemUpdate').checked = notifications.systemUpdate !== false;
            document.getElementById('configChange').checked = notifications.configChange || false;
            document.getElementById('highPriorityAlert').checked = notifications.highPriorityAlert !== false;
            document.getElementById('mediumPriorityAlert').checked = notifications.mediumPriorityAlert !== false;
            document.getElementById('lowPriorityAlert').checked = notifications.lowPriorityAlert || false;
        }
    }

    // 加载设置
    loadSettings() {
        const saved = localStorage.getItem('aiops_settings');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch (e) {
                console.error('Failed to parse saved settings:', e);
            }
        }
        return this.getDefaultSettings();
    }

    // 获取默认设置
    getDefaultSettings() {
        return {
            general: {
                systemName: 'AIOps 智能运维平台',
                systemVersion: 'v2.1.0',
                timezone: 'Asia/Shanghai',
                language: 'zh-CN',
                refreshInterval: 10,
                dataRetention: 30,
                maxConcurrent: 1000,
                enableCache: true,
                sessionTimeout: 60,
                passwordPolicy: 'medium',
                enable2FA: false,
                enableAudit: true
            },
            appearance: {
                theme: 'light',
                primaryColor: '#4F46E5'
            },
            notifications: {
                systemStartStop: true,
                systemUpdate: true,
                configChange: false,
                highPriorityAlert: true,
                mediumPriorityAlert: true,
                lowPriorityAlert: false
            }
        };
    }

    // 显示提示消息
    showToast(message, type = 'success') {
        const toast = document.getElementById('successToast');
        const icon = toast.querySelector('i');
        const text = toast.querySelector('span');

        // 更新内容
        text.textContent = message;
        
        // 更新样式
        toast.className = `toast ${type}`;
        if (type === 'success') {
            icon.className = 'fas fa-check-circle';
        } else if (type === 'error') {
            icon.className = 'fas fa-exclamation-circle';
        }

        // 显示提示
        toast.classList.add('show');

        // 自动隐藏
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // 颜色转换工具函数
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    rgbToHsl(r, g, b) {
        r /= 255;
        g /= 255;
        b /= 255;
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0;
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                case g: h = (b - r) / d + 2; break;
                case b: h = (r - g) / d + 4; break;
            }
            h /= 6;
        }

        return { h, s, l };
    }

    hslToHex(h, s, l) {
        const hue2rgb = (p, q, t) => {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1/6) return p + (q - p) * 6 * t;
            if (t < 1/2) return q;
            if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
            return p;
        };

        let r, g, b;

        if (s === 0) {
            r = g = b = l;
        } else {
            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = hue2rgb(p, q, h + 1/3);
            g = hue2rgb(p, q, h);
            b = hue2rgb(p, q, h - 1/3);
        }

        const toHex = (c) => {
            const hex = Math.round(c * 255).toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        };

        return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
    }
}

// 初始化设置管理器
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});

// 导出设置
function exportSettings() {
    const settings = window.settingsManager.settings;
    const dataStr = JSON.stringify(settings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = 'aiops-settings.json';
    link.click();
}

// 导入设置
function importSettings(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const settings = JSON.parse(e.target.result);
            window.settingsManager.settings = settings;
            window.settingsManager.loadCurrentSettings();
            window.settingsManager.showToast('设置导入成功！', 'success');
        } catch (error) {
            window.settingsManager.showToast('设置文件格式错误', 'error');
        }
    };
    reader.readAsText(file);
}