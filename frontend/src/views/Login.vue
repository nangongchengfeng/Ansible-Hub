<template>
  <div class="login-container">
    <div class="global-blobs" aria-hidden="true">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <div class="login-box">
      <div class="login-header">
        <div class="logo-blob">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="white" fill-opacity="0.9"/>
              <path d="M2 17L12 22L22 17V7L12 12L2 7V17Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <h1 class="title">Ansible 作业平台</h1>
        <p class="subtitle">企业级自动化运维解决方案</p>
      </div>

      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form">
        <el-form-item prop="username">
          <div class="input-wrapper">
            <div class="input-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              class="custom-input"
              @keyup.enter="handleLogin"
            />
          </div>
        </el-form-item>

        <el-form-item prop="password">
          <div class="input-wrapper">
          <div class="input-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 11H5C3.89543 11 3 11.8954 3 13V20C3 21.1046 3.89543 22 5 22H19C20.1046 22 21 21.1046 21 20V13C21 11.8954 20.1046 11 19 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            class="custom-input"
            show-password
            @keyup.enter="handleLogin"
          />
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
          type="primary"
          class="login-button"
          :loading="authStore.loading"
          @click="handleLogin"
        >
          <span v-if="!authStore.loading">登 录</span>
          <span v-else>登录中...</span>
        </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p class="hint">测试账号：admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref(null)
const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await authStore.login(loginForm)
        ElMessage.success('登录成功')
        router.push({ name: 'dashboard' })
      } catch (error) {
        // Error handled in interceptor
      }
    }
  })
}
</script>

<style>
:root {
  --bg-base: #f0f4f8;
  --bg-surface: #ffffff;
  --bg-elevated: #ffffff;

  --color-primary: #4a90d9;
  --color-primary-light: #7eb3e8;
  --color-primary-dark: #2d6cb0;

  --color-teal: #6ec5d4;
  --color-sky: #a8d4e8;
  --color-rose: #e8a4b8;

  --color-success: #7ecb9e;
  --color-warning: #e8d08a;
  --color-error: #e88c8c;
  --color-info: #8ab4e8;

  --text-primary: #1a365d;
  --text-secondary: #4a6b8a;
  --text-muted: #8fa8c0;

  --gradient-primary: linear-gradient(135deg, #4a90d9 0%, #7eb3e8 60%, #a8d4e8 100%);
  --gradient-sky: linear-gradient(135deg, #6ec5d4 0%, #a8d4e8 100%);
  --gradient-warm: linear-gradient(135deg, #a8d4e8 0%, #e8d08a 100%);
  --gradient-surface: linear-gradient(160deg, #ffffff 0%, #f0f4f8 100%);
  --gradient-bg: linear-gradient(180deg, #e8f0f8 0%, #f0f4f8 50%, #f8fafc 100%);

  --shadow-sm: 0 2px 12px rgba(74, 144, 217, 0.08);
  --shadow-md: 0 6px 28px rgba(74, 144, 217, 0.15);
  --shadow-lg: 0 16px 48px rgba(74, 144, 217, 0.2);
  --shadow-blob: 0 20px 60px rgba(74, 144, 217, 0.25);

  --radius-organic-sm: 18px 12px 16px 10px;
  --radius-organic-md: 32px 18px 28px 22px;
  --radius-organic-lg: 48px 28px 42px 32px;
  --radius-pill: 50px 28px 44px 30px;
  --radius-blob: 62% 38% 54% 46% / 48% 52% 48% 52%;

  --duration-morph: 8s;
  --duration-hover: 0.4s;
  --duration-active: 0.2s;
  --duration-enter: 0.6s;
  --easing-organic: cubic-bezier(0.34, 0.8, 0.56, 1.02);
  --easing-smooth: cubic-bezier(0.4, 0, 0.2, 1);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'DM Sans', 'PingFang SC', -apple-system, BlinkMacSystemFont, sans-serif;
}

@keyframes morphBlob {
  0% { border-radius: 62% 38% 54% 46% / 48% 52% 48% 52%; }
  25% { border-radius: 42% 58% 38% 62% / 55% 45% 58% 42%; }
  50% { border-radius: 54% 46% 66% 34% / 42% 58% 44% 56%; }
  75% { border-radius: 38% 62% 48% 52% / 60% 40% 52% 48%; }
  100% { border-radius: 58% 42% 40% 60% / 46% 54% 50% 50%; }
}

@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.login-container {
  width: 100%;
  height: 100vh;
  background: var(--gradient-bg);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

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
  filter: blur(70px);
  opacity: 0.45;
}

.blob-1 {
  width: 560px;
  height: 560px;
  top: -220px;
  right: -120px;
  background: radial-gradient(circle, rgba(74, 144, 217, 0.22), transparent 70%);
  animation-duration: 9s;
}

.blob-2 {
  width: 420px;
  height: 420px;
  bottom: -120px;
  left: -100px;
  background: radial-gradient(circle, rgba(110, 197, 212, 0.18), transparent 70%);
  animation-duration: 7s;
  animation-delay: -3s;
}

.blob-3 {
  width: 340px;
  height: 340px;
  top: 40%;
  left: 55%;
  background: radial-gradient(circle, rgba(168, 212, 232, 0.15), transparent 70%);
  animation-duration: 8s;
  animation-delay: -5s;
}

.login-box {
  width: 440px;
  background: var(--gradient-surface);
  border-radius: var(--radius-organic-lg);
  box-shadow: var(--shadow-lg);
  padding: 48px 44px;
  border: 1px solid rgba(74, 144, 217, 0.12);
  position: relative;
  z-index: 1;
  animation: fadeSlideUp var(--duration-enter) var(--easing-smooth);
  overflow: hidden;
}

.login-box::before {
  content: '';
  position: absolute;
  width: 220px;
  height: 220px;
  top: -80px;
  right: -70px;
  background: var(--gradient-primary);
  opacity: 0.06;
  border-radius: var(--radius-blob);
  animation: morphBlob 10s ease-in-out infinite alternate;
  pointer-events: none;
  z-index: -1;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}

.logo-blob {
  width: 88px;
  height: 88px;
  margin: 0 auto 24px;
  position: relative;
  animation: float 5s ease-in-out infinite;
}

.logo-icon {
  width: 100%;
  height: 100%;
  background: var(--gradient-primary);
  border-radius: var(--radius-blob);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
  animation: morphBlob 7s ease-in-out infinite alternate;
}

.logo-icon svg {
  width: 40px;
  height: 40px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.3px;
}

.subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 450;
}

.login-form {
  margin-top: 36px;
  position: relative;
  z-index: 1;
}

.input-wrapper {
  margin-bottom: 20px;
  position: relative;
}

.input-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--color-primary);
  z-index: 1;
  pointer-events: none;
}

.input-icon svg {
  width: 100%;
  height: 100%;
}

.custom-input {
  position: relative;
}

.custom-input :deep(.el-input__wrapper) {
  background: var(--bg-elevated);
  border-radius: 24px 18px 22px 20px;
  box-shadow: var(--shadow-sm);
  padding: 12px 18px 12px 52px;
  border: 1px solid rgba(74, 144, 217, 0.08);
  transition: all var(--duration-hover) var(--easing-organic);
}

.custom-input :deep(.el-input__wrapper:hover) {
  box-shadow: var(--shadow-md);
  border-color: rgba(74, 144, 217, 0.18);
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.12);
  border-color: var(--color-primary-light);
}

.custom-input :deep(.el-input__inner) {
  font-size: 15px;
  color: var(--text-primary);
}

.custom-input :deep(.el-input__inner::placeholder) {
  color: var(--text-muted);
}

.login-button {
  width: 100%;
  margin-top: 12px;
  background: var(--gradient-primary);
  border-radius: var(--radius-pill);
  border: none;
  padding: 14px 32px;
  color: white;
  font-weight: 600;
  font-size: 16px;
  box-shadow: 0 6px 20px rgba(74, 144, 217, 0.35);
  transition: all var(--duration-hover) var(--easing-organic);
  height: auto;
}

.login-button:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 10px 30px rgba(74, 144, 217, 0.45);
}

.login-button:active {
  transform: translateY(0) scale(0.98);
}

.login-button:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(74, 144, 217, 0.2), 0 6px 20px rgba(74, 144, 217, 0.35);
}

.login-footer {
  text-align: center;
  margin-top: 28px;
  position: relative;
  z-index: 1;
}

.hint {
  color: var(--text-muted);
  font-size: 13px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__error) {
  padding-top: 6px;
  font-size: 13px;
}
</style>
