1. ## 技术栈

   ```
   Vue 3 + Vite 5 + TypeScript + Vue Router 4 + Pinia + Element Plus + UnoCSS + SCSS + Axios + ECharts 5
   ```

   ---

   ## 一、设计理念

   ### 核心定位

   **反传统后台**：以有机曲线承载数据，以柔和渐变传递状态，以形变动效暗示生命力

   ### 视觉原则

   - ✅ 多值不对称圆角、曲线 clip-path、平滑渐变
   - ✅ 微妙视觉偏移，避免严格对称
   - ✅ 6-10s 缓慢形态形变，如有机物呼吸
   - ✅ 文字/表格区域保持矩形，确保可读性
   - ❌ 禁止直角、硬阴影、弹性动效、纯白背景

   ---

   ## 二、颜色系统

   ```css
   :root {
     /* 背景 */
     --bg-base: #f5f3f7;
     --bg-surface: #faf8fc;
     --bg-elevated: #ffffff;
   
     /* 主色调 - 粉紫渐变 */
     --color-primary: #9b7fe8;
     --color-primary-light: #c4aeef;
     --color-primary-dark: #7158c1;
   
     /* 辅助色 */
     --color-teal: #7ecec4;
     --color-rose: #e8a4b8;
     --color-sand: #d4c5a9;
     --color-sky: #a8cfe0;
   
     /* 状态色 */
     --color-success: #8ecba8;
     --color-warning: #e8cc8a;
     --color-error: #e8968c;
     --color-info: #8ab4e8;
   
     /* 文字 */
     --text-primary: #2d2640;
     --text-secondary: #6b5f80;
     --text-muted: #a398b8;
   
     /* 渐变 */
     --gradient-primary: linear-gradient(135deg, #9b7fe8 0%, #c4aeef 60%, #e8a4b8 100%);
     --gradient-teal: linear-gradient(135deg, #7ecec4 0%, #a8cfe0 100%);
     --gradient-warm: linear-gradient(135deg, #e8a4b8 0%, #e8cc8a 100%);
     --gradient-surface: linear-gradient(160deg, #faf8fc 0%, #f0edf8 100%);
   
     /* 阴影 */
     --shadow-sm: 0 2px 12px rgba(155, 127, 232, 0.08);
     --shadow-md: 0 6px 28px rgba(155, 127, 232, 0.13);
     --shadow-lg: 0 16px 48px rgba(155, 127, 232, 0.18);
     --shadow-blob: 0 20px 60px rgba(155, 127, 232, 0.22);
   
     /* 圆角 */
     --radius-organic-sm: 18px 12px 16px 10px;
     --radius-organic-md: 32px 18px 28px 22px;
     --radius-organic-lg: 48px 28px 42px 32px;
     --radius-pill: 50px 28px 44px 30px;
     --radius-blob: 62% 38% 54% 46% / 48% 52% 48% 52%;
   
     /* 动效 */
     --duration-morph: 8s;
     --duration-hover: 0.4s;
     --duration-active: 0.2s;
     --duration-enter: 0.6s;
     --easing-organic: cubic-bezier(0.34, 0.8, 0.56, 1.02);
     --easing-smooth: cubic-bezier(0.4, 0, 0.2, 1);
   }
   ```

   ---

   ## 三、排版系统

   ```css
   /* 字体栈 */
   --font-display: 'Sora', 'PingFang SC', sans-serif;
   --font-body: 'DM Sans', 'PingFang SC', sans-serif;
   --font-mono: 'JetBrains Mono', monospace;
   
   /* 字号 */
   --text-xs: 11px;
   --text-sm: 13px;
   --text-base: 15px;
   --text-lg: 18px;
   --text-xl: 22px;
   --text-2xl: 28px;
   --text-3xl: 36px;
   ```

   - 标题/KPI数字：`font-display`，字重 700-800
   - 正文/表格：`font-body`，字重 400-500

   ---

   ## 四、动效规范

   ### Blob 形变（核心）

   ```css
   @keyframes morphBlob {
     0% { border-radius: 62% 38% 54% 46% / 48% 52% 48% 52%; }
     25% { border-radius: 42% 58% 38% 62% / 55% 45% 58% 42%; }
     50% { border-radius: 54% 46% 66% 34% / 42% 58% 44% 56%; }
     75% { border-radius: 38% 62% 48% 52% / 60% 40% 52% 48%; }
     100% { border-radius: 58% 42% 40% 60% / 46% 54% 50% 50%; }
   }
   ```

   - 时长：6-10s，ease-in-out，infinite alternate
   - 不同 blob 使用不同时长，避免同步

   ### 页面入场

   ```css
   @keyframes fadeSlideUp {
     from { opacity: 0; transform: translateY(20px); }
     to { opacity: 1; transform: translateY(0); }
   }
   ```

   - 卡片列表错开入场，延迟 0.1s 递增

   ---

   ## 五、组件规范

   ### 5.1 卡片 (OrgCard)

   ```vue
   <template>
     <div class="org-card">
       <slot />
     </div>
   </template>
   
   <style scoped>
   .org-card {
     background: var(--gradient-surface);
     border-radius: var(--radius-organic-md);
     box-shadow: var(--shadow-md);
     padding: 24px 28px;
     border: 1px solid rgba(155, 127, 232, 0.1);
     transition: all var(--duration-hover) var(--easing-organic);
     position: relative;
     overflow: hidden;
   }
   
   .org-card:nth-child(2n) { border-radius: 28px 38px 22px 32px; }
   .org-card:nth-child(3n) { border-radius: 36px 22px 38px 18px; }
   
   .org-card::before {
     content: '';
     position: absolute;
     width: 180px;
     height: 180px;
     top: -60px;
     right: -50px;
     background: var(--gradient-primary);
     opacity: 0.06;
     border-radius: var(--radius-blob);
     animation: morphBlob var(--duration-morph) ease-in-out infinite alternate;
     pointer-events: none;
   }
   
   .org-card:hover {
     transform: translateY(-3px) scale(1.008);
     box-shadow: var(--shadow-lg);
   }
   </style>
   ```

   ### 5.2 按钮

   ```css
   .btn-primary {
     background: var(--gradient-primary);
     border-radius: var(--radius-pill);
     border: none;
     padding: 10px 28px;
     color: white;
     font-weight: 600;
     box-shadow: 0 4px 16px rgba(155, 127, 232, 0.35);
     transition: all var(--duration-hover) var(--easing-organic);
   }
   .btn-primary:hover { transform: translateY(-2px) scale(1.03); }
   .btn-primary:active { transform: translateY(0) scale(0.98); }
   ```

   ### 5.3 数据表格

   > 表格内容保持矩形，仅容器使用有机圆角

   ```css
   .table-container {
     border-radius: var(--radius-organic-md);
     overflow: hidden;
     box-shadow: var(--shadow-sm);
     background: var(--bg-surface);
   }
   
   thead tr {
     background: linear-gradient(90deg, rgba(155,127,232,0.08), rgba(126,206,196,0.08));
   }
   
   tbody tr:hover { background: rgba(155,127,232,0.04); }
   ```

   ### 5.4 侧边栏

   ```css
   .sidebar {
     width: 240px;
     background: linear-gradient(180deg, #2d2640 0%, #1e1a30 100%);
     clip-path: path('M 0 0 L 220 0 Q 240 20 240 40 L 240 calc(100% - 40px) Q 240 100% 220 100% L 0 100% Z');
   }
   ```

   ---

   ## 六、全局装饰 Blob

   在 `AppLayout` 中引入 `GlobalBlobs` 组件：

   ```vue
   <template>
     <div class="global-blobs" aria-hidden="true">
       <div class="blob blob-1" />
       <div class="blob blob-2" />
       <div class="blob blob-3" />
     </div>
   </template>
   
   <style scoped>
   .global-blobs {
     position: fixed;
     inset: 0;
     pointer-events: none;
     z-index: 0;
     overflow: hidden;
   }
   
   .blob {
     position: absolute;
     border-radius: var(--radius-blob);
     animation: morphBlob var(--duration-morph) ease-in-out infinite alternate;
     filter: blur(60px);
     opacity: 0.5;
   }
   
   .blob-1 {
     width: 520px; height: 520px;
     top: -200px; right: -100px;
     background: radial-gradient(circle, rgba(155,127,232,0.18), transparent 70%);
     animation-duration: 9s;
   }
   
   .blob-2 {
     width: 380px; height: 380px;
     bottom: 10%; left: -80px;
     background: radial-gradient(circle, rgba(126,206,196,0.15), transparent 70%);
     animation-duration: 7s;
     animation-delay: -3s;
   }
   </style>
   ```

   ---

   ## 七、布局规范

   ### 整体结构

   ```
   AppLayout
   ├── Sidebar (240px，有机曲线右侧)
   └── MainArea
       ├── TopBar (搜索、头像、通知)
       └── PageContent (padding: 24px 28px)
   ```

   ### 网格系统

   ```css
   .content-grid {
     display: grid;
     grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
     gap: 20px;
   }
   
   .kpi-grid {
     display: grid;
     grid-template-columns: repeat(4, 1fr);
     gap: 16px;
   }
   ```

   ---

   ## 八、代码规范

   1. 使用 `<script setup>` + Composition API
   2. 组件名 `PascalCase`，文件名同
   3. CSS 变量统一在 `src/assets/styles/variables.css` 声明
   4. 装饰 blob 必须加 `aria-hidden="true"` 和 `pointer-events: none`
   5. 文字/表格区域保持矩形，不使用有机圆角

   ---

   ## 九、检查清单

   - [ ] 卡片使用多值不对称圆角
   - [ ] 至少 1 个缓慢形变的背景 blob
   - [ ] 颜色使用 CSS 变量，无硬编码
   - [ ] 阴影使用 `--shadow-*` 变量
   - [ ] 按钮为有机圆角
   - [ ] 文字/表格区域保持矩形
   - [ ] Hover 只有位移+缩放，无跳动
   - [ ] 使用 `font-display` 用于标题
   - [ ] 入场动效有错开延迟
   - [ ] 装饰 blob 有无障碍属性

   ---

   ## 十、快速参考

   | 要素       | 规范                                |
   | ---------- | ----------------------------------- |
   | **圆角**   | 多值不对称，避免正圆/直角           |
   | **形变**   | 6-10s 缓慢 morph                    |
   | **颜色**   | 蓝色，浅蓝色 白色，灰白等等组合设计 |
   | **动效**   | 平稳，禁用 bounce                   |
   | **文字区** | 保持矩形，确保可读                  |
   | **氛围**   | 柔软、自然、设计感                  |
