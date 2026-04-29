# Ansible Job Platform - Frontend

企业级 Ansible 自动化作业平台前端项目

## 技术栈

- Vue 3 + Vite
- Element Plus
- Vue Router
- Pinia
- Axios

## 开发

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 代码检查

```bash
npm run lint
```

### 代码格式化

```bash
npm run format
```

## 测试账号

- 用户名：admin
- 密码：admin123

## 项目结构

```
src/
├── api/              # API 接口
├── layout/           # 布局组件
├── router/           # 路由配置
├── stores/           # Pinia 状态管理
├── utils/            # 工具函数
├── views/            # 页面组件
├── App.vue           # 根组件
└── main.js           # 入口文件
```

## Mock API

当前使用 Mock API 进行开发，后端 API 完成后可修改 `src/api/auth.js` 中的 `useMock` 为 `false`。
