<template>
  <div class="form-container">
    <el-form :model="form" label-width="140px" class="linkage-form">
      <el-form-item label="联动规则名称" required>
        <el-input v-model="form.ruleName" placeholder="请输入联动规则名称" />
      </el-form-item>
      <el-form-item label="链接" required>
        <el-input v-model="form.link" placeholder="请输入链接" />
      </el-form-item>
      <el-form-item label="内容" required>
        <el-input v-model="form.content" type="textarea" :rows="4" maxlength="500" placeholder="请输入内容（最多500字）" />
      </el-form-item>
      <el-form-item label="重要等级">
        <el-radio-group v-model="form.importanceLevel">
          <el-radio value="低">低</el-radio>
          <el-radio value="中">中</el-radio>
          <el-radio value="高">高</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="发送频率">
        <el-radio-group v-model="form.sendFrequency">
          <el-radio value="立即">立即</el-radio>
          <el-radio value="延时">延时</el-radio>
          <el-radio value="定时">定时</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="推送渠道">
        <el-checkbox-group v-model="form.pushChannels">
          <el-checkbox value="微信">微信</el-checkbox>
          <el-checkbox value="企业微信">企业微信</el-checkbox>
          <el-checkbox value="钉钉">钉钉</el-checkbox>
          <el-checkbox value="短信">短信</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="AppID" required>
        <el-input v-model="form.appId" placeholder="请输入AppID" />
      </el-form-item>
      <el-form-item label="AppSecret" required>
        <el-input v-model="form.appSecret" type="password" placeholder="请输入AppSecret" show-password />
      </el-form-item>
      <el-form-item label="模板ID" required>
        <el-input v-model="form.templateId" placeholder="请输入模板ID" />
      </el-form-item>
      <el-form-item label="推送目标" required>
        <el-input v-model="form.pushTarget" type="textarea" :rows="3" placeholder="请输入推送目标" />
      </el-form-item>
      <el-form-item label="备注" required>
        <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="createRule">立即创建</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const form = reactive({
  ruleName: '',
  link: '',
  content: '',
  importanceLevel: '中',
  sendFrequency: '立即',
  pushChannels: [],
  appId: '',
  appSecret: '',
  templateId: '',
  pushTarget: '',
  remark: ''
})

const createRule = () => {
  if (!form.ruleName || !form.link || !form.content || !form.appId || !form.appSecret || !form.templateId) {
    ElMessage.error('请填写必填项')
    return
  }
  ElMessage.success('联动规则创建成功')
}
</script>

<style scoped>
.form-container {
  padding: 24px;
}
.linkage-form {
  max-width: 700px;
}
</style>
