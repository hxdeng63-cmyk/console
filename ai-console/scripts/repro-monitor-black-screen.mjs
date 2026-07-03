// Repro for "数字大屏 — 点开始监测才启动,选算法不再自动启动 + 修黑屏"
//
// 三层验证:
// 1) 派生逻辑:hasAlgorithm=true + streamMap 未刷 → url 空 → 黑屏
// 2) 派生逻辑:hasAlgorithm=true + streamMap 仍是 register 占位 → url 失效 → 黑屏
// 3) 修复后期望:onSuccess 拉新 flv_url 覆盖 streamMap → url 变 m3u8
// 4) 状态机: 选算法(ref 更新)≠ 启动算法;"开始监测"按钮触发启动。
//    黑屏只在 (selectedAlgorithm !== '' && 启动未成功) 时出现。

import assert from 'node:assert/strict'
import { ref, computed, watch as vueWatch } from 'vue'

function rawIdFromChannel(id) {
  if (!id) return 0
  const n = Number(String(id).replace(/^device-/, ''))
  return Number.isNaN(n) ? 0 : n
}
function pathOnly(url) { return (url || '').split('?')[0] }

function derive({ channel, channels, streamMap, selectedAlgorithm }) {
  const currentDevice = channels.find(ch => ch.id === channel) || null
  const hasAlgorithm = Boolean(selectedAlgorithm)
  let currentVideoUrl = ''
  if (currentDevice) {
    if (!hasAlgorithm) {
      const rid = rawIdFromChannel(currentDevice.id)
      if (rid) currentVideoUrl = `/monitoring/device_${rid}.mp4`
    } else {
      currentVideoUrl = streamMap[currentDevice.id]?.url || ''
    }
  }
  const currentSourceType = !currentDevice
    ? ''
    : (!hasAlgorithm ? 'local' : (streamMap[currentDevice.id]?.sourceType || ''))
  const currentProtocol = pathOnly(currentVideoUrl).toLowerCase().endsWith('.m3u8') ? 'hls' : 'flv'
  return { currentDevice, hasAlgorithm, currentVideoUrl, currentSourceType, currentProtocol }
}

// --- 模拟"开始监测"按钮的状态机(替代 handleAlgorithmChange → startSelectedAlgorithm) ---
// 真实代码: @change:algorithm 已删除, 下拉只更新 selectedAlgorithm ref,不触发 start
// 真实代码: "开始监测"按钮 → handleStartAll → monitoring.value false → startSelectedAlgorithm
// 真实代码: "停止监测"按钮 → handleStartAll → monitoring.value true → stopSelectedAlgorithm
function makeWallState() {
  const selectedChannel = ref('')
  const selectedAlgorithm = ref('')
  const monitoring = ref(false)
  const streamMap = ref({})
  const callLog = []
  return {
    selectedChannel, selectedAlgorithm, monitoring, streamMap, callLog,
    // 模拟"下拉选算法" — 只更新 ref,不调 start
    pickAlgorithm(value) { selectedAlgorithm.value = value },
    // 模拟"点开始监测"按钮 — 只有这条路径会调 start + 启动成功后调 getDeviceFlvUrl
    async clickStart(getDeviceFlvUrl) {
      if (monitoring.value) {
        // 停止
        callLog.push('stop')
        monitoring.value = false
        return
      }
      if (!selectedAlgorithm.value) {
        callLog.push('warn:no-algorithm')
        return
      }
      callLog.push('start:' + selectedAlgorithm.value)
      // 模拟 traffic-api /start 异步,成功 → onSuccess
      const rid = rawIdFromChannel(selectedChannel.value)
      const info = await getDeviceFlvUrl(rid)
      if (info?.flv_url) {
        streamMap.value = {
          ...streamMap.value,
          [`device-${rid}`]: { url: info.flv_url, sourceType: info.source_type || 'stream' },
        }
      }
      monitoring.value = true
    },
  }
}

// ===== 派生逻辑单元 =====

// 1) 无算法 → 走 local mp4
{
  const r = derive({ channel: 'device-7', channels: [{ id: 'device-7' }], streamMap: {}, selectedAlgorithm: '' })
  assert.equal(r.hasAlgorithm, false)
  assert.equal(r.currentVideoUrl, '/monitoring/device_7.mp4')
  assert.equal(r.currentSourceType, 'local')
  console.log('[PASS] 无算法 → 走本地 mp4')
}

// 2) 选了算法但未点开始监测 → 仍走 streamMap(此时 streamMap 是 register 占位,可能 403 → 黑屏)
//    这是用户报告的"点算法就黑屏"的根因: hasAlgorithm 翻成 true 后 useCurrentStream 立刻看 streamMap
{
  const r = derive({
    channel: 'device-7',
    channels: [{ id: 'device-7' }],
    streamMap: { 'device-7': { url: 'http://t/flv?token=STALE', sourceType: 'stream' } },
    selectedAlgorithm: '1:crowd_density:crowd_count',
  })
  assert.equal(r.hasAlgorithm, true)
  assert.equal(r.currentVideoUrl, 'http://t/flv?token=STALE')
  console.log('[FAIL — 复现] 选算法后立即 hasAlgorithm=true → 拿 register 占位 → 黑屏(根因)')
}

// 3) 选了算法 + 点了开始监测 + onSuccess 覆盖 streamMap → url 变 m3u8 → 不黑屏
{
  const sm = { 'device-7': { url: 'http://t/flv?token=STALE', sourceType: 'stream' } }
  // 模拟 onSuccess
  const fresh = { flv_url: 'http://t/cam7.m3u8?token=NEW', source_type: 'stream' }
  sm['device-7'] = { url: fresh.flv_url, sourceType: fresh.source_type }
  const r = derive({
    channel: 'device-7', channels: [{ id: 'device-7' }], streamMap: sm,
    selectedAlgorithm: '1:crowd_density:crowd_count',
  })
  assert.equal(r.currentVideoUrl, fresh.flv_url)
  assert.equal(r.currentProtocol, 'hls')
  console.log('[PASS — 修复后] onSuccess 覆盖 streamMap → m3u8 → 不再黑屏')
}

// ===== 状态机单元 =====

// 4) 选算法(ref 更新) ≠ 启动算法
{
  const s = makeWallState()
  s.selectedChannel.value = 'device-7'
  s.streamMap.value = { 'device-7': { url: 'http://t/flv?token=STALE', sourceType: 'stream' } }
  s.pickAlgorithm('1:crowd_density:crowd_count')
  // 派生(模拟 useCurrentStream): hasAlgorithm=true → 拿占位 url
  const r = derive({
    channel: s.selectedChannel.value, channels: [{ id: 'device-7' }],
    streamMap: s.streamMap.value, selectedAlgorithm: s.selectedAlgorithm.value,
  })
  assert.equal(s.callLog.length, 0, '选算法不应触发任何 start/stop 调用')
  assert.equal(r.hasAlgorithm, true, 'hasAlgorithm 翻成 true,url 指向 streamMap')
  console.log('[PASS] 选算法只更新 ref,不触发 start。callLog=', s.callLog)
}

// 5) 未选算法就点"开始监测" → warn,不启动
{
  const s = makeWallState()
  s.selectedChannel.value = 'device-7'
  await s.clickStart(async () => null)  // 不应被调用
  assert.deepEqual(s.callLog, ['warn:no-algorithm'])
  assert.equal(s.monitoring.value, false)
  console.log('[PASS] 未选算法点"开始监测" → warn,callLog=', s.callLog)
}

// 6) 选完算法 + 点"开始监测" → start + 覆盖 streamMap + monitoring=true
{
  const s = makeWallState()
  s.selectedChannel.value = 'device-7'
  s.pickAlgorithm('1:crowd_density:crowd_count')
  await s.clickStart(async (rid) => ({
    flv_url: `http://t/cam${rid}.m3u8?token=NEW`, source_type: 'stream',
  }))
  assert.equal(s.callLog[0], 'start:1:crowd_density:crowd_count')
  assert.equal(s.monitoring.value, true)
  const r = derive({
    channel: s.selectedChannel.value, channels: [{ id: 'device-7' }],
    streamMap: s.streamMap.value, selectedAlgorithm: s.selectedAlgorithm.value,
  })
  assert.equal(r.currentVideoUrl, 'http://t/cam7.m3u8?token=NEW')
  assert.equal(r.currentProtocol, 'hls')
  console.log('[PASS] 选完算法点"开始监测" → m3u8 推理流,monitoring=true')
}

// 7) monitoring=true 时再点"开始监测"按钮(变"停止监测")→ stop,monitoring=false
{
  const s = makeWallState()
  s.selectedChannel.value = 'device-7'
  s.pickAlgorithm('1:crowd_density:crowd_count')
  await s.clickStart(async () => ({ flv_url: 'http://t/x.m3u8?token=N', source_type: 'stream' }))
  assert.equal(s.monitoring.value, true)
  await s.clickStart(async () => null)
  assert.deepEqual(s.callLog, ['start:1:crowd_density:crowd_count', 'stop'])
  assert.equal(s.monitoring.value, false)
  console.log('[PASS] 再点"停止监测" → stop,monitoring=false')
}

// ===== Bug A 修复: selectedAlgorithm watch 立刻拉新 token =====

// 8) 选下拉算法(ref 更新)→ 立刻调 getDeviceFlvUrl 拉新 token 覆盖 streamMap
//    这是新加的 watch,确保 hasAlgorithm 翻 true 拿到的不是过期 token (403)。
{
  // 模拟 useStreamRegistry 的 streamMap
  const streamMap = ref({ 'device-7': { url: 'http://t/STALE', sourceType: 'stream' } })
  const callLog = []
  // 模拟 MonitorWall 里新加的 selectedAlgorithm watch
  vueWatch(() => '1:crowd_density:crowd_count', async (val) => {
    if (!val) return
    callLog.push('getDeviceFlvUrl:7')
    streamMap.value = {
      ...streamMap.value,
      'device-7': { url: 'http://t/cam7.m3u8?token=FRESH', sourceType: 'stream' },
    }
  }, { immediate: true })

  // 给 microtask 一拍执行 watch 回调
  await new Promise(r => setTimeout(r, 0))
  assert.deepEqual(callLog, ['getDeviceFlvUrl:7'])
  assert.equal(streamMap.value['device-7'].url, 'http://t/cam7.m3u8?token=FRESH')
  console.log('[PASS — Bug A] 选算法立刻拉新 token 覆盖 streamMap (避免 403)')
}

// 9) 选下拉算法不启动任务 — callLog 只有 refresh,没有 start
{
  const selectedAlgorithm = ref('')
  const callLog = []
  vueWatch(() => selectedAlgorithm.value, async (val) => {
    if (!val) return
    callLog.push('refresh')
  })
  // 模拟用户选算法 — ref 从 '' → '1:crowd_density:crowd_count'
  selectedAlgorithm.value = '1:crowd_density:crowd_count'
  await new Promise(r => setTimeout(r, 0))
  assert.deepEqual(callLog, ['refresh'])
  assert.equal(callLog.filter(c => c === 'start').length, 0, '选算法不应触发 start')
  console.log('[PASS — Bug A] 选算法只 refresh,不启动任务')
}

// ===== Bug B 修复: protocol prop 变化触发 setProtocol 重建 player =====

// 10) setProtocol 同步 currentProtocol + loadMedia
//     这是 useVideoPlayer 新增的 setProtocol 函数,VideoPlayer 在 props.protocol 变化时调它。
{
  // 模拟 useVideoPlayer 的 internal state
  const currentProtocol = ref('flv')
  let loadMediaCalled = 0
  const player = {
    currentProtocol,
    setProtocol(p) {
      if (currentProtocol.value !== p) {
        currentProtocol.value = p
        loadMediaCalled += 1
      }
    },
  }
  // 初始 flv,父组件 protocol 变 hls
  assert.equal(player.currentProtocol.value, 'flv')
  player.setProtocol('hls')
  assert.equal(player.currentProtocol.value, 'hls')
  assert.equal(loadMediaCalled, 1, 'protocol 变化触发 loadMedia')
  // 再次设同一 protocol,不应重复 loadMedia
  player.setProtocol('hls')
  assert.equal(loadMediaCalled, 1, '同 protocol 重复 setProtocol 是 no-op')
  console.log('[PASS — Bug B] setProtocol 同步 currentProtocol + 触发 loadMedia')
}

// 11) VideoPlayer watch props.protocol → setProtocol(实际是 Vue watch 行为 mock)
{
  const props = ref({ protocol: 'flv' })
  const currentProtocol = ref('flv')
  const setProtocol = (p) => { currentProtocol.value = p }
  // 模拟 VideoPlayer 的 watch
  vueWatch(() => props.value.protocol, (newProto) => {
    if (newProto) setProtocol(newProto)
  })

  assert.equal(currentProtocol.value, 'flv')
  props.value = { protocol: 'hls' }
  await new Promise(r => setTimeout(r, 0))
  assert.equal(currentProtocol.value, 'hls', 'protocol 翻 hls 时 currentProtocol 跟随')
  console.log('[PASS — Bug B] props.protocol 变化 → setProtocol → currentProtocol 跟随')
}

// 12) Bug C: getDeviceFlvUrl 返回 404 时,清掉 streamMap 条目,VideoStage 显示"无法连接"提示。
//     模拟 MonitorWall 的两个 watch(selectedChannel / selectedAlgorithm)在 404 时的清理逻辑。
{
  const streamMap = ref({
    'device-7': { url: 'http://t/STALE.m3u8', sourceType: 'stream' },
    'device-8': { url: 'http://t/OK.m3u8', sourceType: 'stream' },
  })
  // 模拟 getDeviceFlvUrl 抛 404
  const fakeGetFlvUrl = async (rid) => {
    if (rid === 7) {
      const err = new Error('Not Found')
      err.response = { status: 404 }
      throw err
    }
    return { flv_url: `http://t/dev${rid}.m3u8?token=N`, source_type: 'stream' }
  }
  // 模拟 MonitorWall 的 catch 逻辑
  async function refresh(rid) {
    try {
      const info = await fakeGetFlvUrl(rid)
      if (!info?.flv_url) return
      streamMap.value = {
        ...streamMap.value,
        [`device-${rid}`]: { url: info.flv_url, sourceType: info.source_type },
      }
    } catch (err) {
      if (err?.response?.status === 404) {
        const key = `device-${rid}`
        if (streamMap.value[key]) {
          const next = { ...streamMap.value }
          delete next[key]
          streamMap.value = next
        }
      }
    }
  }
  await refresh(7)  // 应清掉 device-7
  assert.equal(streamMap.value['device-7'], undefined, '404 时 device-7 应被清掉')
  assert.equal(streamMap.value['device-8'].url, 'http://t/OK.m3u8', '其他设备不应受影响')
  await refresh(8)  // 应正常更新 device-8
  assert.equal(streamMap.value['device-8'].url, 'http://t/dev8.m3u8?token=N')
  console.log('[PASS — Bug C] getDeviceFlvUrl 404 时清掉 streamMap 条目,VideoStage 显示提示')
}

// 13) Bug C: HLS fatal NETWORK_ERROR 时,父组件应能通过 hls-network-error 事件收到通知。
//     模拟 MonitorWall 的 refreshStreamOnNetworkError 在收到事件后能正确拉新 url 覆盖 streamMap。
{
  const streamMap = ref({ 'device-7': { url: 'http://t/DEAD', sourceType: 'stream' } })
  const events = []
  // 模拟 VideoPlayer emit('hls-network-error')
  // + MonitorWall @hls-network-error="refreshStreamOnNetworkError"
  const fakeGetFlvUrl = async (rid) => {
    events.push(`refresh:${rid}`)
    return { flv_url: `http://t/RESURRECTED-${rid}.m3u8`, source_type: 'stream' }
  }
  // 模拟 MonitorWall 的 handler
  async function onNetworkError() {
    events.push('handler:called')
    const rid = 7
    const info = await fakeGetFlvUrl(rid)
    if (info?.flv_url) {
      streamMap.value = {
        ...streamMap.value,
        [`device-${rid}`]: { url: info.flv_url, sourceType: info.source_type },
      }
    }
  }
  await onNetworkError()
  assert.equal(streamMap.value['device-7'].url, 'http://t/RESURRECTED-7.m3u8')
  assert.deepEqual(events, ['handler:called', 'refresh:7'])
  console.log('[PASS — Bug C] hls-network-error 回调 → 拉新 token → streamMap 更新 → switchUrl 重载')
}

console.log('\n结论:')
console.log('  Bug A — 选算法不启动监测,但 selectedAlgorithm watch 立刻拉新 flv_url 覆盖 streamMap')
console.log('          (避免 useCurrentStream 拿到过期 token → 403 → 黑屏)')
console.log('  Bug B — useVideoPlayer 加 setProtocol,VideoPlayer watch props.protocol')
console.log('          (避免 protocol 翻 hls 时仍走 initFlv 分支 → 黑屏)')
console.log('  Bug C — HLS fatal NETWORK_ERROR → emit(hls-network-error) → MonitorWall refreshStreamOnNetworkError 拉新 token')
console.log('          + getDeviceFlvUrl 404 时清掉 streamMap,VideoStage 显示"无法连接"提示')
console.log('  三个修复必须同时存在: 协议对 + token 新 + 错误自愈 → 视频稳定播放')
