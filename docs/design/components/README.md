# 公共组件库

本目录包含AIOps系统的公共组件，提供统一的UI组件和交互功能。

## 组件列表

### 1. Navigation 导航组件

**文件：**
- `navigation.js` - 导航组件JavaScript实现
- `navigation.css` - 导航组件样式文件

**功能特性：**
- 统一的导航菜单结构
- 自动高亮当前页面
- 键盘导航支持
- 响应式设计
- 无障碍访问支持
- 深色主题支持

**使用方法：**

#### 1. 引入文件
```html
<link rel="stylesheet" href="./components/navigation.css">
<script src="./components/navigation.js"></script>
```

#### 2. HTML结构
```html
<div id="nav-container" data-nav-container data-current-page="dashboard"></div>
```

#### 3. JavaScript初始化
```javascript
// 自动初始化（推荐）
// 组件会自动查找带有 data-nav-container 属性的元素并初始化

// 手动初始化
const nav = new NavigationManager('nav-container', 'dashboard');

// 或使用工厂函数
const nav = createNavigation('nav-container', 'dashboard');
```

#### 4. API方法
```javascript
// 设置当前活动页面
nav.setActivePage('monitoring');

// 添加菜单项
nav.addMenuItem({
    id: 'reports',
    icon: 'fas fa-file-alt',
    text: '报告中心',
    href: './reports.html'
});

// 移除菜单项
nav.removeMenuItem('reports');

// 更新菜单项
nav.updateMenuItem('dashboard', {
    text: '控制台',
    icon: 'fas fa-desktop'
});
```

**配置选项：**
- `containerId`: 导航容器的ID
- `currentPage`: 当前页面标识，用于高亮显示

**样式变量：**
组件使用CSS自定义属性，可通过修改根变量来自定义样式：
```css
:root {
    --primary-color: #3b82f6;
    --gray-600: #4b5563;
    --gray-100: #f3f4f6;
    --spacing-2: 0.5rem;
    --spacing-4: 1rem;
    --radius-md: 0.375rem;
    --transition-fast: 0.15s ease-in-out;
}
```

## 开发指南

### 添加新组件

1. 在 `components` 目录下创建组件文件
2. 遵循命名规范：`component-name.js` 和 `component-name.css`
3. 添加完整的JSDoc注释
4. 提供使用示例和API文档
5. 更新本README文件

### 样式规范

- 使用CSS自定义属性进行主题化
- 支持响应式设计
- 考虑无障碍访问
- 支持深色主题
- 遵循BEM命名规范

### JavaScript规范

- 使用ES6+语法
- 提供完整的JSDoc注释
- 支持模块化导入
- 提供错误处理
- 考虑性能优化

## 浏览器支持

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## 更新日志

### v1.0.0 (2025-01-23)
- 初始版本
- 添加Navigation导航组件
- 支持自动初始化和手动初始化
- 提供完整的API和样式定制功能