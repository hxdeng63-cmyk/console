<template>
  <div class="profile-page">
    <!-- 固定信息 -->
    <div class="section">
      <div class="section-title">固定信息</div>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">登录账号</span>
          <span class="info-value">admin</span>
        </div>
        <div class="info-item">
          <span class="info-label">角色</span>
          <span class="info-value">系统管理员</span>
        </div>
        <div class="info-item">
          <span class="info-label">所属部门</span>
          <span class="info-value">一级部门</span>
        </div>
      </div>
    </div>

    <!-- 其他信息 -->
    <div class="section">
      <div class="section-title">其他信息</div>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px" class="profile-form">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" style="width: 300px" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="form.gender" placeholder="性别" style="width: 300px">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱账号" prop="email">
          <el-input v-model="form.email" placeholder="邮箱账号" style="width: 300px" />
        </el-form-item>
        <el-form-item label="照片">
          <div class="avatar-upload" @click="triggerUpload">
            <img v-if="avatarUrl" :src="avatarUrl" class="avatar-img" />
            <div v-else class="avatar-placeholder">
              <el-icon :size="32"><Plus /></el-icon>
            </div>
            <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileChange" />
          </div>
        </el-form-item>
        <el-form-item label="密码">
          <span class="password-mask">********</span>
          <el-button link style="color: #00E5FF; background: rgba(0, 229, 255, 0.15); border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 4px; padding: 2px 8px; font-weight: 600; text-shadow: none;" class="change-pwd-btn" @click="passwordVisible = true">修改密码</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 按钮 -->
    <div class="form-footer">
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleSubmit">修改</el-button>
    </div>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="passwordVisible" title="修改密码" width="400px" :close-on-click-modal="false">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="90px">
        <el-form-item label="原密码" prop="oldPwd">
          <el-input v-model="pwdForm.oldPwd" type="password" show-password placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPwd">
          <el-input v-model="pwdForm.newPwd" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPwd">
          <el-input v-model="pwdForm.confirmPwd" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePwdSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref()
const pwdFormRef = ref()
const fileInput = ref<HTMLInputElement>()
const avatarUrl = ref('/admin.jpg')
const passwordVisible = ref(false)

const form = reactive({
  phone: '18688888888',
  gender: '',
  email: ''
})

const rules = {
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  email: [{ required: true, message: '请输入邮箱账号', trigger: 'blur' }]
}

const pwdForm = reactive({ oldPwd: '', newPwd: '', confirmPwd: '' })

const pwdRules = {
  oldPwd: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPwd: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirmPwd: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_: any, value: string, cb: any) => {
        if (value !== pwdForm.newPwd) cb(new Error('两次密码不一致'))
        else cb()
      },
      trigger: 'blur'
    }
  ]
}

const triggerUpload = () => fileInput.value?.click()

const onFileChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) avatarUrl.value = URL.createObjectURL(file)
}

const handleCancel = () => router.back()

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  ElMessage.success('修改成功')
}

const handlePwdSubmit = async () => {
  const valid = await pwdFormRef.value?.validate().catch(() => false)
  if (!valid) return
  ElMessage.success('密码修改成功')
  passwordVisible.value = false
}
</script>

<style scoped>
.profile-page {
  padding: 24px;
  max-width: 700px;
}

.section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  padding-left: 10px;
  border-left: 3px solid #00E5FF;
  margin-bottom: 18px;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-left: 13px;
}

.info-item {
  display: flex;
  gap: 24px;
  font-size: 14px;
}

.info-label {
  color: var(--text-secondary);
  width: 70px;
  flex-shrink: 0;
}

.info-value {
  color: var(--text-primary);
}

.profile-form {
  padding-left: 0;
}

.avatar-upload {
  width: 90px;
  height: 90px;
  border: 2px dashed #00E5FF;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: border-color 0.2s;
}

.avatar-upload:hover {
  border-color: #00B4D8;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  color: #00E5FF;
}

.password-mask {
  color: var(--text-primary);
  font-size: 18px;
  letter-spacing: 3px;
  margin-right: 12px;
}

.change-pwd-btn {
  color: #00E5FF;
  padding: 0;
}

.form-footer {
  display: flex;
  gap: 12px;
  padding-left: 90px;
  margin-top: 8px;
}
</style>
