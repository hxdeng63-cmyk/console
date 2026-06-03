<template>
  <div class="form-container">
    <el-form :model="form" label-width="140px" class="linkage-form" ref="formRef" :rules="rules">
      <el-form-item label="联动规则名称" prop="ruleName">
        <el-input v-model="form.ruleName" placeholder="请输入联动规则名称" />
      </el-form-item>
      <el-form-item label="链接" prop="link">
        <el-input v-model="form.link" placeholder="请输入链接" />
      </el-form-item>
      <el-form-item label="内容" prop="content">
        <el-input v-model="form.content" type="textarea" :rows="4" maxlength="500" placeholder="请输入内容（最多500字）" show-word-limit />
      </el-form-item>
      <el-form-item label="重要等级" prop="importanceLevel">
        <el-radio-group v-model="form.importanceLevel">
          <el-radio label="低">低</el-radio>
          <el-radio label="中">中</el-radio>
          <el-radio label="高">高</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="发送频率" prop="sendFrequency">
        <el-radio-group v-model="form.sendFrequency">
          <el-radio label="immediate">立即</el-radio>
          <el-radio label="delayed">延时</el-radio>
          <el-radio label="scheduled">定时</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 延时配置 -->
      <el-form-item v-if="form.sendFrequency === 'delayed'" label="延迟时长" prop="delayValue">
        <el-input-number v-model="form.delayValue" :min="1" :precision="0" style="width: 120px" />
        <el-select v-model="form.delayUnit" style="width: 100px; margin-left: 8px">
          <el-option label="分钟" value="minute" />
          <el-option label="小时" value="hour" />
          <el-option label="天" value="day" />
        </el-select>
      </el-form-item>

      <!-- 定时配置 -->
      <el-form-item v-if="form.sendFrequency === 'scheduled'" label="定时时间" prop="scheduledTime">
        <el-date-picker v-model="form.scheduledTime" type="datetime" placeholder="选择日期时间" style="width: 100%" />
      </el-form-item>

      <el-form-item label="推送渠道" prop="pushChannel">
        <el-radio-group v-model="form.pushChannel">
          <el-radio label="wechat">微信</el-radio>
          <el-radio label="wechat_work">企业微信</el-radio>
          <el-radio label="dingtalk">钉钉</el-radio>
          <el-radio label="sms">短信</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 微信配置 -->
      <template v-if="form.pushChannel === 'wechat'">
        <el-form-item label="AppID" prop="wechatAppId">
          <el-input v-model="form.wechatAppId" placeholder="请输入AppID" />
        </el-form-item>
        <el-form-item label="AppSecret" prop="wechatAppSecret">
          <el-input v-model="form.wechatAppSecret" type="password" placeholder="请输入AppSecret" show-password />
        </el-form-item>
        <el-form-item label="模板ID" prop="wechatTemplateId">
          <el-input v-model="form.wechatTemplateId" placeholder="请输入模板ID" />
        </el-form-item>
      </template>

      <!-- 企业微信配置 -->
      <template v-if="form.pushChannel === 'wechat_work'">
        <el-form-item label="CorpID" prop="wechatWorkCorpId">
          <el-input v-model="form.wechatWorkCorpId" placeholder="请输入CorpID" />
        </el-form-item>
        <el-form-item label="AppSecret" prop="wechatWorkAppSecret">
          <el-input v-model="form.wechatWorkAppSecret" type="password" placeholder="请输入AppSecret" show-password />
        </el-form-item>
        <el-form-item label="AgentID" prop="wechatWorkAgentId">
          <el-input v-model="form.wechatWorkAgentId" placeholder="请输入AgentID" />
        </el-form-item>
      </template>

      <!-- 钉钉配置 -->
      <template v-if="form.pushChannel === 'dingtalk'">
        <el-form-item label="AppKey" prop="dingtalkAppKey">
          <el-input v-model="form.dingtalkAppKey" placeholder="请输入AppKey" />
        </el-form-item>
        <el-form-item label="AppSecret" prop="dingtalkAppSecret">
          <el-input v-model="form.dingtalkAppSecret" type="password" placeholder="请输入AppSecret" show-password />
        </el-form-item>
        <el-form-item label="AgentID" prop="dingtalkAgentId">
          <el-input v-model="form.dingtalkAgentId" placeholder="请输入AgentID" />
        </el-form-item>
      </template>

      <!-- 短信配置 -->
      <template v-if="form.pushChannel === 'sms'">
        <el-form-item label="短信ID" prop="smsId">
          <el-input v-model="form.smsId" placeholder="请输入短信ID" />
        </el-form-item>
      </template>

      <el-form-item label="推送目标" prop="pushTarget">
        <el-input v-model="form.pushTarget" type="textarea" :rows="3" placeholder="请输入推送目标，多个目标请用分号隔开" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="3" maxlength="500" placeholder="请输入备注（最多500字）" show-word-limit />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="createRule">立即创建</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createLinkageRule } from '@/api/linkage-rules'

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  ruleName: '',
  link: '',
  content: '',
  importanceLevel: '中',
  sendFrequency: 'immediate',
  delayValue: 5,
  delayUnit: 'minute',
  scheduledTime: null,
  pushChannel: 'wechat',
  wechatAppId: '',
  wechatAppSecret: '',
  wechatTemplateId: '',
  wechatWorkCorpId: '',
  wechatWorkAppSecret: '',
  wechatWorkAgentId: '',
  dingtalkAppKey: '',
  dingtalkAppSecret: '',
  dingtalkAgentId: '',
  smsId: '',
  pushTarget: '',
  remark: ''
})

const getChannelConfig = () => {
  const channel = form.pushChannel
  if (channel === 'wechat') {
    return {
      channel_type: 'wechat',
      app_id: form.wechatAppId,
      app_secret: form.wechatAppSecret,
      template_id: form.wechatTemplateId
    }
  }
  if (channel === 'wechat_work') {
    return {
      channel_type: 'wechat_work',
      corp_id: form.wechatWorkCorpId,
      app_secret: form.wechatWorkAppSecret,
      agent_id: form.wechatWorkAgentId
    }
  }
  if (channel === 'dingtalk') {
    return {
      channel_type: 'dingtalk',
      app_key: form.dingtalkAppKey,
      app_secret: form.dingtalkAppSecret,
      agent_id: form.dingtalkAgentId
    }
  }
  if (channel === 'sms') {
    return {
      channel_type: 'sms',
      sms_id: form.smsId
    }
  }
  return {}
}

const rules = {
  ruleName: [{ required: true, message: '请输入联动规则名称', trigger: 'blur' }],
  pushTarget: [{ required: true, message: '请输入推送目标', trigger: 'blur' }],
  wechatAppId: [{ required: true, message: '请输入AppID', trigger: 'blur' }],
  wechatAppSecret: [{ required: true, message: '请输入AppSecret', trigger: 'blur' }],
  wechatTemplateId: [{ required: true, message: '请输入模板ID', trigger: 'blur' }],
  wechatWorkCorpId: [{ required: true, message: '请输入CorpID', trigger: 'blur' }],
  wechatWorkAppSecret: [{ required: true, message: '请输入AppSecret', trigger: 'blur' }],
  wechatWorkAgentId: [{ required: true, message: '请输入AgentID', trigger: 'blur' }],
  dingtalkAppKey: [{ required: true, message: '请输入AppKey', trigger: 'blur' }],
  dingtalkAppSecret: [{ required: true, message: '请输入AppSecret', trigger: 'blur' }],
  dingtalkAgentId: [{ required: true, message: '请输入AgentID', trigger: 'blur' }],
  smsId: [{ required: true, message: '请输入短信ID', trigger: 'blur' }]
}

const createRule = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const payload = {
      rule_name: form.ruleName,
      link: form.link,
      content: form.content,
      importance_level: form.importanceLevel === '低' ? 1 : form.importanceLevel === '中' ? 2 : 3,
      send_frequency: form.sendFrequency,
      delay_value: form.sendFrequency === 'delayed' ? form.delayValue : null,
      delay_unit: form.sendFrequency === 'delayed' ? form.delayUnit : null,
      scheduled_time: form.sendFrequency === 'scheduled' ? form.scheduledTime : null,
      push_channels: getChannelConfig(),
      push_target: form.pushTarget,
      remark: form.remark,
      status: 'active'
    }
    await createLinkageRule(payload)
    ElMessage.success('联动规则创建成功')
    resetForm()
  } catch (error) {
    ElMessage.error(error.message || '创建失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.ruleName = ''
  form.link = ''
  form.content = ''
  form.importanceLevel = '中'
  form.sendFrequency = 'immediate'
  form.delayValue = 5
  form.delayUnit = 'minute'
  form.scheduledTime = null
  form.pushChannel = 'wechat'
  form.wechatAppId = ''
  form.wechatAppSecret = ''
  form.wechatTemplateId = ''
  form.wechatWorkCorpId = ''
  form.wechatWorkAppSecret = ''
  form.wechatWorkAgentId = ''
  form.dingtalkAppKey = ''
  form.dingtalkAppSecret = ''
  form.dingtalkAgentId = ''
  form.smsId = ''
  form.pushTarget = ''
  form.remark = ''
  formRef.value?.clearValidate()
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
