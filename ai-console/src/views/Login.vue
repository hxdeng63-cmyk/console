<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-avatar">
        <img :src="'/data/head-portrait/admin.jpg'" alt="avatar" />
      </div>
      <div class="login-title">AI 控制台</div>
      <div class="login-subtitle">欢迎回来，请登录您的账号</div>

      <el-form ref="formRef" :model="form" :rules="rules" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入登录账号"
            size="large"
            clearable
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            placeholder="请输入密码"
            size="large"
            type="password"
            show-password
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="loading"
          @click="handleLogin"
        >
          登 录
        </el-button>
      </el-form>
    </div>

    <div class="login-bg">
      <div class="bg-circle c1"></div>
      <div class="bg-circle c2"></div>
      <div class="bg-circle c3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '@/api/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const data = await login(form)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user_info', JSON.stringify(data.user))
    ElMessage.success('登录成功')
    router.push('/monitor/single')
  } catch (error: any) {
    ElMessage.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #010e1f;
  overflow: hidden;
}

.login-card {
  position: relative;
  z-index: 10;
  width: 400px;
  padding: 48px 40px;
  background: rgba(10, 30, 60, 0.85);
  border: 1px solid rgba(24, 144, 255, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
}

.login-avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.login-avatar img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid #00E5FF;
  object-fit: cover;
}

.login-title {
  text-align: center;
  font-size: 22px;
  font-weight: 600;
  color: #e6f7ff;
  margin-bottom: 6px;
  letter-spacing: 2px;
}

.login-subtitle {
  text-align: center;
  font-size: 13px;
  color: #8AAFC8;
  margin-bottom: 32px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.login-btn {
  width: 100%;
  margin-top: 8px;
  background: #00E5FF;
  border-color: #00E5FF;
  font-size: 15px;
  letter-spacing: 4px;
}

.login-btn:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

/* 背景装饰圆 */
.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}

.c1 {
  width: 400px;
  height: 400px;
  background: #00E5FF;
  top: -100px;
  left: -100px;
}

.c2 {
  width: 300px;
  height: 300px;
  background: #00E5FF;
  bottom: -80px;
  right: -80px;
}

.c3 {
  width: 200px;
  height: 200px;
  background: #00E5FF;
  bottom: 100px;
  left: 200px;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(24, 144, 255, 0.25);
  box-shadow: none !important;
}

:deep(.el-input__wrapper:hover) {
  border-color: #00E5FF;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #00E5FF;
}

:deep(.el-input__inner) {
  color: #e6f7ff;
}

:deep(.el-input__inner::placeholder) {
  color: #8AAFC8;
}

:deep(.el-input__prefix-icon) {
  color: #8AAFC8;
}
</style>
