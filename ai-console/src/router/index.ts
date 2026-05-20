import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/monitor/single'
    },
    {
      path: '/login',
      component: () => import('../views/Login.vue'),
      meta: { title: '登录' }
    },
    // MenuPanel 容器 - 承载 Tab 1-6
    {
      path: '/monitor',
      component: () => import('../views/MenuPanel.vue'),
      children: [
        {
          path: '',
          component: () => import('../views/monitor/MonitorSingle.vue'),
          meta: { title: '实时监控' }
        },
        {
          path: 'single',
          component: () => import('../views/monitor/MonitorSingle.vue'),
          meta: { title: '实时监控' }
        },
        {
          path: 'wall',
          component: () => import('../views/monitor/MonitorWall.vue'),
          meta: { title: '实时监控' }
        }
      ]
    },
    {
      path: '/event-stats',
      component: () => import('../views/MenuPanel.vue'),
      children: [
        {
          path: '',
          component: () => import('../views/event-stats/EventStats.vue'),
          meta: { title: '事件统计' }
        }
      ]
    },
    {
      path: '/event-manage',
      component: () => import('../views/MenuPanel.vue'),
      children: [
        {
          path: '',
          component: () => import('../views/Events.vue'),
          meta: { title: '事件管理' }
        }
      ]
    },
    {
      path: '/deployment',
      component: () => import('../components/layout/DeploymentLayout.vue'),
      children: [
        {
          path: '',
          component: () => import('../views/deployment/Deployment.vue'),
          meta: { title: '布控管理' }
        },
        {
          path: 'annotation',
          component: () => import('../views/deployment/Annotation.vue'),
          meta: { title: '标注管理' }
        }
      ]
    },
    {
      path: '/file-analysis',
      component: () => import('../views/MenuPanel.vue'),
      children: [
        {
          path: '',
          component: () => import('../views/monitor/FileAnalysis.vue'),
          meta: { title: '文件分析' }
        }
      ]
    },
    // Console 容器 - 承载 Tab 7 (控制台)
    {
      path: '/console',
      component: () => import('../views/Console.vue'),
      redirect: '/console/super-admin/menu-manage',
      children: [
        {
          path: 'super-admin/menu-manage',
          component: () => import('../views/super-admin/MenuManage.vue'),
          meta: { title: '菜单管理' }
        },
        {
          path: 'super-admin/resource-manage',
          component: () => import('../views/super-admin/ResourceManage.vue'),
          meta: { title: '资源管理' }
        },
        {
          path: 'super-admin/microservice',
          component: () => import('../views/super-admin/Microservice.vue'),
          meta: { title: '微服务' }
        },
        {
          path: 'super-admin/ui-customize',
          component: () => import('../views/super-admin/UICustomize.vue'),
          meta: { title: 'UI定制' }
        },
        {
          path: 'super-admin/license-file',
          component: () => import('../views/super-admin/LicenseFile.vue'),
          meta: { title: '授权文件' }
        },
        {
          path: 'user-center/user-manage',
          component: () => import('../views/user-center/UserManage.vue'),
          meta: { title: '用户管理' }
        },
        {
          path: 'user-center/org-manage',
          component: () => import('../views/user-center/OrgManage.vue'),
          meta: { title: '组织管理' }
        },
        {
          path: 'user-center/role-manage',
          component: () => import('../views/user-center/RoleManage.vue'),
          meta: { title: '角色管理' }
        },
        {
          path: 'user-center/operation-history',
          component: () => import('../views/user-center/OperationHistory.vue'),
          meta: { title: '操作历史' }
        },
        {
          path: 'device/data-source',
          component: () => import('../views/device/DataSource.vue'),
          meta: { title: '数据源' }
        },
        {
          path: 'device/device-group',
          component: () => import('../views/device/DeviceGroup.vue'),
          meta: { title: '设备组管理' }
        },
        {
          path: 'device/region',
          component: () => import('../views/device/Region.vue'),
          meta: { title: '区域' }
        },
        {
          path: 'device/device-access/platform-list',
          component: () => import('../views/device/access/PlatformList.vue'),
          meta: { title: '平台列表' }
        },
        {
          path: 'device/device-access/gb28181',
          component: () => import('../views/device/access/Gb28181.vue'),
          meta: { title: 'GB28181' }
        },
        {
          path: 'device/device-access/onvif',
          component: () => import('../views/device/access/Onvif.vue'),
          meta: { title: 'ONVIF' }
        },
        {
          path: 'linkage/send-notify',
          component: () => import('../views/linkage/TaskEdit.vue'),
          meta: { title: '发送通知' }
        },
        {
          path: 'linkage/linkage-rule',
          component: () => import('../views/linkage/LinkageRule.vue'),
          meta: { title: '联动规则' }
        },
        {
          path: 'linkage/push-history',
          component: () => import('../views/linkage/PushHistory.vue'),
          meta: { title: '推送历史' }
        },
        {
          path: 'system/video-setting',
          component: () => import('../views/system/VideoSetting.vue'),
          meta: { title: '录像设置' }
        },
        {
          path: 'system/file-manager',
          component: () => import('../views/system/FileManager.vue'),
          meta: { title: '文件管理' }
        },
        {
          path: 'system/help-center',
          component: () => import('../views/system/HelpCenter.vue'),
          meta: { title: '帮助中心' }
        },
        {
          path: 'system/popup-setting',
          component: () => import('../views/system/PopupSetting.vue'),
          meta: { title: '弹窗设置' }
        },
        {
          path: 'system/dispose-tag',
          component: () => import('../views/system/DisposeTag.vue'),
          meta: { title: '处置标签' }
        },
        {
          path: 'data-clean',
          component: () => import('../views/DataClean.vue'),
          meta: { title: '数据清理' }
        },
        {
          path: 'algorithm/algorithm-manage',
          component: () => import('../views/algorithm/AlgorithmManage.vue'),
          meta: { title: '算法管理' }
        },
        {
          path: 'algorithm/event-manage',
          component: () => import('../views/Events.vue'),
          meta: { title: '事件管理' }
        },
        {
          path: 'algorithm/algorithm-service',
          component: () => import('../views/algorithm/AlgorithmService.vue'),
          meta: { title: '算法服务' }
        },
        {
          path: 'firmware',
          component: () => import('../views/Firmware.vue'),
          meta: { title: '固件中心' }
        },
        {
          path: 'events',
          component: () => import('../views/Events.vue'),
          meta: { title: '预警事件' }
        },
        {
          path: 'profile',
          component: () => import('../views/Profile.vue'),
          meta: { title: '个人中心' }
        }
      ]
    },
    // 旧路由重定向到新路由（兼容性）
    {
      path: '/layout',
      redirect: '/monitor'
    },
    {
      path: '/layout/monitor',
      redirect: '/monitor'
    },
    {
      path: '/layout/event-stats',
      redirect: '/event-stats'
    },
    {
      path: '/layout/event-manage',
      redirect: '/event-manage'
    },
    {
      path: '/layout/deployment',
      redirect: '/deployment'
    },
    {
      path: '/layout/deployment/annotation',
      redirect: '/deployment/annotation'
    },
    {
      path: '/layout/file-analysis',
      redirect: '/file-analysis'
    }
  ]
})

export default router
